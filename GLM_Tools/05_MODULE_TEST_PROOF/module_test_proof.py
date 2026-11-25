#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
module_test_proof.py — GLM_Tools/05: "modül + test + kanıt" disiplini aracı.

MODÜL = kod + test + kanıt. Kanıtsız modül bitmemiş modüldür.

Komutlar:
  new-module <ad>            modules/<ad>/ + tests/test_<ad>.py stub + proofs/<ad>/ + PROOF.md satırı
  prove <ad> --file <yol>    kanıt dosyasını proofs/<ad>/<tarih>_<saat>_<ad>'a kopyalar, PROOF.md'e indeksler
  audit [--root .]           tasks.json'daki 'done' taskler ↔ kanıt eşleşmesini denetler (exit 1 = ihlal)
Tamamen stdlib; Python 3.8+.
"""
import argparse
import datetime
import hashlib
import json
import os
import shutil


def now():
    return datetime.datetime.now()


def stamp():
    return now().strftime("%Y-%m-%d_%H%M")


def pj(root, *parts):
    return os.path.join(root, *parts)


def read(p):
    if not os.path.exists(p):
        return ""
    with open(p, encoding="utf-8") as f:
        return f.read()


def write(p, s):
    os.makedirs(os.path.dirname(p) or ".", exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(s)


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def ensure_proof_md(root):
    p = pj(root, "PROOF.md")
    if not os.path.exists(p):
        write(p, "# PROOF — kanıt indeksi\n\n"
                 "| Modül | Tarih | Task | Neyi kanıtlar | Dosya |\n"
                 "|---|---|---|---|---|\n")
    return p


def add_index_row(root, module, task, note, relpath):
    p = ensure_proof_md(root)
    row = f"| {module} | {now().strftime('%Y-%m-%d')} | {task or '-'} | {note or '-'} | {relpath} |\n"
    with open(p, "a", encoding="utf-8") as f:
        f.write(row)
    return row


def cmd_new_module(a):
    root = a.root
    mod = a.name
    os.makedirs(pj(root, "modules", mod), exist_ok=True)
    os.makedirs(pj(root, "proofs", mod), exist_ok=True)
    os.makedirs(pj(root, "tests"), exist_ok=True)
    t = pj(root, "tests", f"test_{mod}.py")
    if not os.path.exists(t):
        write(t, f'''# -*- coding: utf-8 -*-
"""test_{mod} — {mod} modülü testleri (GLM_Tools/05 standardı).

Kural: (1) testi modül kodu YOKKEN çalıştır → neden fail olması gerektiğini bil
(kırmızı). (2) modülü yaz → PASS (yeşil). Hep geçen test kanıt değildir.
"""
import sys


def test_placeholder():
    # TODO: modül fonksiyonlarını çağıran gerçek iddialarla değiştir
    assert True


if __name__ == "__main__":
    test_placeholder()
    print("1/1 PASS (placeholder — gerçek iddialarla değiştir!)")
    sys.exit(0)
''')
    src = pj(root, "modules", mod, "README.md")
    if not os.path.exists(src):
        write(src, f"# {mod}\n\nAmaç: (doldur)\nKapattığı task: (T-###)\nGirdi/çıktı: (doldur)\n")
    ensure_proof_md(root)
    print(f"[+] modül iskeleti: modules/{mod}, tests/test_{mod}.py, proofs/{mod}/")
    print("[!] sıradaki adım: kodu yaz → testi kırmızıdan yeşile getir → prove ile kanıtla")


def cmd_prove(a):
    root = a.root
    if not os.path.exists(a.file):
        raise SystemExit(f"HATA: kanıt dosyası yok: {a.file}")
    mod = a.module
    os.makedirs(pj(root, "proofs", mod), exist_ok=True)
    base = os.path.basename(a.file)
    dest = pj(root, "proofs", mod, f"{stamp()}_{base}")
    shutil.copy2(a.file, dest)
    digest = sha256(dest)
    rel = os.path.relpath(dest, root).replace(os.sep, "/")
    header = (
        f"=== KANIT: {mod} ===\n"
        f"Tarih    : {now().strftime('%Y-%m-%d %H:%M')}\n"
        f"Modül    : {mod}\n"
        f"Task     : {a.task or '-'}\n"
        f"Not      : {a.note or '-'}\n"
        f"Kaynak   : {a.file}\n"
        f"sha256   : {digest}\n"
        + "=" * 50 + "\n\n"
    )
    with open(dest, "r+", encoding="utf-8", errors="ignore") as f:
        old = f.read()
        f.seek(0)
        f.write(header + old)
    add_index_row(root, mod, a.task, a.note, rel)
    print(f"[+] kanıt kaydedildi: {rel}")
    print(f"    sha256={digest[:16]}...")
    # tasks.json'da taski kanıtlı kapat (varsa)
    tp = pj(root, "tasks.json")
    if a.task and os.path.exists(tp):
        with open(tp, encoding="utf-8") as f:
            t = json.load(f)
        for x in t.get("tasks", []):
            if x["id"] == a.task:
                x["status"] = "done"
                x["proof"] = rel
                x["updated"] = now().strftime("%Y-%m-%d %H:%M")
                print(f"[+] {a.task} kanıtla KAPANDI")
        with open(tp, "w", encoding="utf-8") as f:
            json.dump(t, f, ensure_ascii=False, indent=2)


def cmd_audit(a):
    root = a.root
    tp = pj(root, "tasks.json")
    problems = []
    total_done = 0
    if os.path.exists(tp):
        with open(tp, encoding="utf-8") as f:
            t = json.load(f)
        for x in t.get("tasks", []):
            if x.get("status") == "done":
                total_done += 1
                proof = x.get("proof")
                if not proof:
                    problems.append((x["id"], "proof alanı boş"))
                elif not os.path.exists(pj(root, proof)):
                    problems.append((x["id"], f"kanıt dosyası yok: {proof}"))
    else:
        print("(tasks.json yok — yalnız PROOF.md kontrolü)")
    # PROOF.md indeks var mı?
    if not os.path.exists(pj(root, "PROOF.md")) and total_done:
        problems.append(("PROOF.md", "indeks dosyası yok"))
    print(f"DENETİM: done task={total_done}, ihlal={len(problems)}")
    for tid, msg in problems:
        print(f"  [İHLAL] {tid}: {msg}")
    if problems:
        print("→ kanıtsız 'done' = bitmemiş: taski blocked'a çevir (task_state.py block) veya kanıt üret")
        raise SystemExit(1)
    print("OK: her 'done' taskin kanıtı mevcut.")


def main():
    p = argparse.ArgumentParser(description="modül+test+kanıt aracı (GLM_Tools/05)")
    sub = p.add_subparsers(dest="cmd", required=True)

    def add_root(sp):
        sp.add_argument("--root", default=".")
        return sp

    nm = add_root(sub.add_parser("new-module")); nm.add_argument("name")
    pv = add_root(sub.add_parser("prove"))
    pv.add_argument("module"); pv.add_argument("--file", required=True)
    pv.add_argument("--note", default=""); pv.add_argument("--task", default="")
    add_root(sub.add_parser("audit"))
    a = p.parse_args()
    {"new-module": cmd_new_module, "prove": cmd_prove, "audit": cmd_audit}[a.cmd](a)


if __name__ == "__main__":
    main()
