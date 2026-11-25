#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
living_github.py — GLM_Tools/02 "Yaşayan GitHub" push aracı.

Komutlar:
  setup <repo-url> [--token PAT] [--dir D]   klonla (D yoksa repo adı) / varsa pull
  push  "<mesaj>" [--token PAT] [--dir D] [--add YOL]   add+commit+push (3 kez dener)
  receipt [--dir D]                           son 5 commit + durum + unpushed
  status [--dir D]                            kısa durum özeti

Güvenlik: token .git/config'e YAZILMAZ; push tek seferlik URL ile yapılır.
Tamamen stdlib; Python 3.8+.
"""
import argparse
import os
import subprocess
import sys
import time

DEFAULT_ID_NAME = "0xByteDeveloper"
DEFAULT_ID_MAIL = "0xByteDeveloper@users.noreply.github.com"


def sh(args, cwd, timeout=120, check=True):
    r = subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=timeout)
    if check and r.returncode != 0:
        raise RuntimeError(f"komut başarısız: {' '.join(args)}\nSTDOUT: {r.stdout[-1500:]}\nSTDERR: {r.stderr[-1500:]}")
    return r


def repo_dir(d):
    d = os.path.abspath(d or ".")
    if not os.path.isdir(os.path.join(d, ".git")):
        raise SystemExit(f"HATA: {d} bir git deposu değil (önce setup çalıştır)")
    return d


def with_token(url, token):
    if not token:
        return url
    if "@" in url.split("//", 1)[-1]:
        return url  # zaten kimlik içermiyor olabilir; dokunma
    return url.replace("https://", f"https://x-access-token:{token}@")


def cmd_setup(a):
    url = a.repo_url.rstrip("/")
    name = (a.dir or url.rsplit("/", 1)[-1].removesuffix(".git"))
    target = os.path.abspath(name)
    if not os.path.isdir(target):
        clone_url = with_token(url, a.token)
        print(f"[*] klonlanıyor: {name}")
        sh(["git", "clone", clone_url, target], cwd=os.path.abspath("."), timeout=600)
        # temiz remote (tokensız)
        sh(["git", "remote", "set-url", "origin", url], cwd=target)
    else:
        print(f"[*] mevcut depo güncelleniyor: {name}")
        sh(["git", "pull", "--rebase", with_token(url, a.token)], cwd=target, timeout=300)
        sh(["git", "remote", "set-url", "origin", url], cwd=target)
    ensure_identity(target)
    print(f"[+] hazır: {target}")


def ensure_identity(d):
    if not sh(["git", "config", "user.email"], cwd=d, check=False).stdout.strip():
        sh(["git", "config", "user.name", DEFAULT_ID_NAME], cwd=d)
        sh(["git", "config", "user.email", DEFAULT_ID_MAIL], cwd=d)


def cmd_push(a):
    d = repo_dir(a.dir)
    ensure_identity(d)
    if a.add:
        for p in a.add:
            sh(["git", "add", p], cwd=d)
    else:
        sh(["git", "add", "-A"], cwd=d)
    st = sh(["git", "status", "--porcelain"], cwd=d)
    if not st.stdout.strip():
        print("[=] değişiklik yok, push'a gerek yok")
        return
    # dirty durumu göster
    print("[*] değişen/eklenen (ilk 12):")
    for line in st.stdout.splitlines()[:12]:
        print("    " + line)
    if len(st.stdout.splitlines()) > 12:
        print(f"    ... +{len(st.stdout.splitlines()) - 12} satır daha")
    sh(["git", "commit", "-m", a.message], cwd=d, timeout=120)
    branch = sh(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=d).stdout.strip()
    url = sh(["git", "remote", "get-url", "origin"], cwd=d).stdout.strip()
    push_url = with_token(url, a.token)
    last_err = None
    for attempt in (1, 2, 3):
        try:
            sh(["git", "push", push_url, f"HEAD:{branch}"], cwd=d, timeout=300)
            print(f"[+] PUSH OK (deneme {attempt}) → {branch}")
            return
        except (RuntimeError, subprocess.TimeoutExpired) as e:
            last_err = e
            wait = 2 * attempt
            print(f"[!] push deneme {attempt} başarısız, {wait} sn sonra tekrar...")
            time.sleep(wait)
            sh(["git", "pull", "--rebase", push_url], cwd=d, timeout=300, check=False)
    print(f"[X] PUSH 3 DENEMEDE BAŞARISIZ — worklog'a !HATA yaz, BLOCKING: {last_err}", file=sys.stderr)
    sys.exit(1)


def cmd_receipt(a):
    d = repo_dir(a.dir)
    ensure_identity(d)
    log = sh(["git", "log", "-5", "--oneline", "--shortstat"], cwd=d).stdout
    st = sh(["git", "status", "--porcelain"], cwd=d).stdout
    up = sh(["git", "log", "@{u}..HEAD", "--oneline"], cwd=d, check=False).stdout
    print("== SON 5 COMMIT ==")
    print(log or "(commit yok)")
    print("== ÇALIŞMA DURUMU ==")
    print(st or "(temiz)")
    print("== PUSH'LANMAMIŞ ==")
    print(up.strip() or "(hepsi push'lu)" if up.strip() or up else "(upstream yok — push receipt'iyle kontrol et)")
    n_st = len([l for l in st.splitlines() if l.strip()])
    n_up = len([l for l in up.splitlines() if l.strip()])
    print(f"ÖZET: dirty={n_st} unpushed~={n_up}")


def cmd_status(a):
    d = repo_dir(a.dir)
    st = sh(["git", "status", "--porcelain"], cwd=d).stdout
    lines = [l for l in st.splitlines() if l.strip()]
    print(f"dirty dosya: {len(lines)}")
    for l in lines[:10]:
        print("    " + l)


def main():
    p = argparse.ArgumentParser(description="Yaşayan GitHub push aracı (GLM_Tools/02)")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("setup")
    s.add_argument("repo_url")
    s.add_argument("--token", default=os.environ.get("GH_PAT", ""))
    s.add_argument("--dir", default="")

    u = sub.add_parser("push")
    u.add_argument("message")
    u.add_argument("--token", default=os.environ.get("GH_PAT", ""))
    u.add_argument("--dir", default="")
    u.add_argument("--add", action="append")

    r = sub.add_parser("receipt")
    r.add_argument("--dir", default="")
    t = sub.add_parser("status")
    t.add_argument("--dir", default="")

    a = p.parse_args()
    {"setup": cmd_setup, "push": cmd_push, "receipt": cmd_receipt, "status": cmd_status}[a.cmd](a)


if __name__ == "__main__":
    main()
