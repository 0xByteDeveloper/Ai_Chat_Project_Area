#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
memory_snapshot.py — GLM_Tools/07: STATE + tasks + worklog + REQUESTS'ten
MEMORY_CARD.md üretir (yeni chate taşınacak kimlik kartı).

Kullanım:
  python memory_snapshot.py --root <proje-klasörü> [--dry-run]
  (dosya adları --tasks/--state/--worklog/--requests ile elle verilebilir;
   verilmezse STATE.json, INDEX.md üzerinden otomatik bulunur)

Kural: kart ≤ 200 satır (detay worklog arşivlerinde yaşar).
Tamamen stdlib; Python 3.8+.
"""
import argparse
import datetime
import json
import os
import re

MAX_LINES = 200


def read(p):
    if not os.path.exists(p):
        return ""
    with open(p, encoding="utf-8") as f:
        return f.read()


def find_worklog(root, explicit):
    if explicit and os.path.exists(explicit):
        return explicit
    idx = read(os.path.join(root, "INDEX.md"))
    if idx:
        m = re.search(r"[Gg]üncel[^\n]*?[:=]\s*\*?\*?(WORKLOG_(\d+)\.md)", idx)
        if m:
            return os.path.join(root, m.group(1))
    best, bestn = None, 0
    for f in sorted(os.listdir(root)) if os.path.isdir(root) else []:
        m = re.fullmatch(r"WORKLOG_(\d+)\.md", f)
        if m and int(m.group(1)) > bestn:
            best, bestn = os.path.join(root, f), int(m.group(1))
    return best


def marked_lines(text, markers=("!KARAR", "!HATA", "!AÇIK"), limit=15):
    out = []
    for line in text.splitlines():
        if any(m in line for m in markers):
            out.append(line.strip()[:160])
        if len(out) >= limit:
            break
    return out


def build_card(root, a):
    state = {}
    sp = a.state if (a.state and os.path.exists(a.state)) else os.path.join(root, "STATE.json")
    if os.path.exists(sp):
        try:
            state = json.load(open(sp, encoding="utf-8"))
        except Exception:
            pass

    tasks = {"tasks": []}
    tp = a.tasks if (a.tasks and os.path.exists(a.tasks)) else os.path.join(root, "tasks.json")
    if os.path.exists(tp):
        try:
            tasks = json.load(open(tp, encoding="utf-8"))
        except Exception:
            pass

    wl_path = find_worklog(root, a.worklog)
    wl_tail = read(wl_path).splitlines()[-15:] if wl_path else []
    wl_name = os.path.basename(wl_path) if wl_path else "?"

    rp = a.requests if (a.requests and os.path.exists(a.requests)) else os.path.join(root, "REQUESTS.md")
    req_tail = read(rp).splitlines()[-8:] if os.path.exists(rp) else []

    # arşiv özetlerinden kararlar (mükerrer satırlar ayıklanır)
    decisions, seen = [], set()
    for f in sorted(os.listdir(root)) if os.path.isdir(root) else []:
        if re.fullmatch(r"WORKLOG_ARCHIVE_\d+_OZET\.md", f):
            for line in marked_lines(read(os.path.join(root, f)), limit=8):
                key = line[-120:]
                if key not in seen:
                    seen.add(key)
                    decisions.append(line)
    for line in marked_lines(read(wl_path) if wl_path else "", limit=8):
        key = line[-120:]
        if key not in seen:
            seen.add(key)
            decisions.append(line)
    decisions = [d[2:] if d.startswith("- ") else d for d in decisions]

    open_tasks = [t for t in tasks.get("tasks", [])
                  if t.get("status") in ("todo", "doing", "blocked")]

    L = []
    L.append(f"# MEMORY_CARD — {state.get('project', '(proje)')}")
    L.append(f"_otomatik üretim: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')} (memory_snapshot.py)_")
    L.append("")
    L.append("## 1) Proje kimliği")
    L.append(f"- proje: **{state.get('project', '?')}** · aşama: {state.get('phase', '?')}")
    repos = state.get("active_repo") or []
    L.append(f"- aktif repolar: {', '.join(repos) if repos else '?'}")
    L.append(f"- worklog: {wl_name} (STATE: WORKLOG_{state.get('current_worklog', '?')})")
    L.append("")
    L.append("## 2) Kalınan yer")
    L.append(f"- son istek: {state.get('last_request', '?')}")
    L.append(f"- test durumu: {state.get('tests_status', '?')}")
    L.append(f"- engeller: {state.get('blockers') or 'yok'}")
    L.append(f"- güncelleme: {state.get('updated_at', '?')}")
    L.append("")
    L.append("## 3) Açık taskler (UNUTULAMAZ)")
    if open_tasks:
        for t in open_tasks:
            note = ""
            if t.get("status") == "blocked" and t.get("notes"):
                note = " — " + str(t["notes"][-1])[:80]
            L.append(f"- `{t['id']}` [{t['status']}] {t['title'][:80]}{note}")
    else:
        L.append("- (açık task yok — yeni istek R-### ile tasks.json'a girilmeli)")
    L.append("")
    L.append("## 4) Son kararlar / hatalar / açık sorular")
    if decisions:
        L += [f"- {d}" for d in decisions[:16]]
    else:
        L.append("- (kayıt yok)")
    L.append("")
    L.append("## 5) Dosya durumu (kritik)")
    lf = state.get("last_files") or {}
    if lf:
        for k, v in list(lf.items())[:10]:
            L.append(f"- `{k}` → {v}")
    else:
        L.append("- (STATE.last_files boş — doldurulmalı)")
    L.append("")
    L.append("## 6) Kullanıcı tercihleri")
    L += [
        "- GOD MOD çalışma tarzı: her modül kod+test+kanıt+push; kanıtsız task kapanmaz",
        "- Dil: Türkçe · ton: direkt, derin, uydurmasız",
        "- Teslim formatı: analiz/raporlar HTML (GLM_Tools/09 ev stili)",
        "- 3 hesap = 3 uzman hattı: Araştırıcı / Uygulayıcı / Denetçi",
        "- Tokenler kullanıcıda; rotate edilir; dosyaya commit edilmez",
    ]
    L.append("")
    L.append("## 7) Sözlük (proje terimleri)")
    L += [
        "- XProtect: kullanıcının kendi packer'ı (VMP 3.5.1 port tabanlı)",
        "- MazeProtector: kullanıcının AI ile yazdığı ikinci packer (GLM 5.3)",
        "- i4mconsoleloader: dosya→süreç→bellek simülasyonu (Unicorn 'god' varyantları var)",
        "- UniversalMVPUIAlgorithm(_QT): imgui/Qt UI klonlama motoru",
        "- GOD MOD: 10x üretim disiplini (GLM_Tools/01)",
        "- worklog+str(n+1): worklog rotasyonu (GLM_Tools/03)",
    ]
    L.append("")
    L.append("## 8) Sıradaki modül")
    L.append(f"- {open_tasks[0]['title'] if open_tasks else '(netleşmemiş — STATE.phase alanına bak)'}")
    L.append("")
    if wl_tail:
        L.append("## Ek: güncel worklogun son 15 satırı")
        L += [f"> {l.strip()[:150]}" for l in wl_tail if l.strip()]
    if req_tail:
        L.append("")
        L.append("## Ek: son istekler")
        L += [f"> {l.strip()[:150]}" for l in req_tail if l.strip()]
    L.append("")
    L.append("---")
    L.append("_Detay: WORKLOG arşiv özetleri + tasks.json + STATE.json. Kart 200 satırı geçmemeli._")

    # satır limiti güvenliği
    if len(L) > MAX_LINES:
        L = L[:MAX_LINES - 3] + ["", "…(kırpıldı — detay dosyalarda)", ""]
    return "\n".join(L) + "\n"


def main():
    p = argparse.ArgumentParser(description="MEMORY_CARD üretici (GLM_Tools/07)")
    p.add_argument("--root", default=".")
    p.add_argument("--state", default="")
    p.add_argument("--tasks", default="")
    p.add_argument("--worklog", default="")
    p.add_argument("--requests", default="")
    p.add_argument("--out", default="")
    p.add_argument("--dry-run", action="store_true")
    a = p.parse_args()
    root = os.path.abspath(a.root)
    card = build_card(root, a)
    if a.dry_run:
        print(card)
        print(f"[dry-run] {len(card.splitlines())} satır")
        return
    out = a.out or os.path.join(root, "MEMORY_CARD.md")
    with open(out, "w", encoding="utf-8") as f:
        f.write(card)
    print(f"[+] MEMORY_CARD.md yazıldı: {out} ({len(card.splitlines())} satır)")


if __name__ == "__main__":
    main()
