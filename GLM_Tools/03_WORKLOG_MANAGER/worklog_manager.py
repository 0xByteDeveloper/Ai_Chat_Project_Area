#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
worklog_manager.py — GLM_Tools/03: worklog + str(n+1) rotasyon yöneticisi.

Komutlar:
  init                       WORKLOG_1.md + INDEX.md + STATE.json iskeleti
  status                     güncel worklog, satır sayısı, eşik durumu
  append "metin"             tarih damgalı satır ekle (--module, --tags ile)
  rotate [--max-lines 200]   arşivle + özet üret + WORKLOG_(n+1) + INDEX + STATE güncelle

Dosya düzeni (proje kökünde):
  WORKLOG_n.md / WORKLOG_ARCHIVE_n.md / WORKLOG_ARCHIVE_n_OZET.md / INDEX.md / STATE.json
Tamamen stdlib; Python 3.8+.
"""
import argparse
import datetime
import json
import os
import re

MARKERS = ("!KARAR", "!HATA", "!AÇIK")
TEMPLATE_HEAD = """# WORKLOG_{n} — {date}

> Bu dosya 200 satırı geçince `rotate` edilir (arşiv + özet + WORKLOG_{n2}).
> Önceki dönem özeti: {prev}

"""


def now_stamp():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")


def path(root, name):
    return os.path.join(root, name)


def read(p):
    if not os.path.exists(p):
        return ""
    with open(p, encoding="utf-8") as f:
        return f.read()


def write(p, s):
    os.makedirs(os.path.dirname(p) or ".", exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(s)


def load_state(root):
    p = path(root, "STATE.json")
    if os.path.exists(p):
        try:
            with open(p, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_state(root, st):
    st["updated_at"] = now_stamp()
    write(path(root, "STATE.json"), json.dumps(st, ensure_ascii=False, indent=2) + "\n")


def current_worklog(root):
    """INDEX.md'den; yoksa en yüksek numaralı WORKLOG_n.md; hiç yoksa None."""
    idx = read(path(root, "INDEX.md"))
    if idx:
        m = re.search(r"[Gg]üncel[^\n]*?[:=]\s*\*?\*?(WORKLOG_(\d+)\.md)", idx)
        if m:
            return m.group(1), int(m.group(2))
    best, bestn = None, 0
    if os.path.isdir(root):
        for f in sorted(os.listdir(root)):
            m = re.fullmatch(r"WORKLOG_(\d+)\.md", f)
            if m and int(m.group(1)) > bestn:
                best, bestn = f, int(m.group(1))
    return (best, bestn) if best else (None, 0)


def cmd_init(a):
    root = a.root
    os.makedirs(root, exist_ok=True)
    w = path(root, "WORKLOG_1.md")
    if not os.path.exists(w):
        write(w, TEMPLATE_HEAD.format(n=1, n2=2, date=now_stamp(), prev="(ilk dönem)"))
    idx = path(root, "INDEX.md")
    if not os.path.exists(idx):
        write(idx, "# WORKLOG INDEX\n\n| # | Dosya | Durum | Satır |\n|---|---|---|---|\n"
                    "| 1 | WORKLOG_1.md | GÜNCEL | 0 |\n\n**Güncel worklog: WORKLOG_1.md**\n")
    st = load_state(root)
    st.setdefault("project", "(proje adı)")
    st.setdefault("current_worklog", 1)
    st.setdefault("open_tasks", [])
    save_state(root, st)
    print("[+] init tamam:", os.path.abspath(root))


def cmd_status(a):
    name, n = current_worklog(a.root)
    if not name:
        raise SystemExit("worklog yok — önce 'init' çalıştır")
    p = path(a.root, name)
    lines = [l for l in read(p).splitlines() if l.strip()]
    kb = os.path.getsize(p) // 1024
    limit = a.max_lines
    pct = 100 * len(lines) // limit
    print(f"güncel      : {name} (n={n})")
    print(f"satır       : {len(lines)}/{limit} (%{pct})  |  boyut: {kb} KB")
    print(f"eşik durumu : {'ROTASYON GEREKLİ' if len(lines) >= limit or kb >= 8 else ('YAKLAŞIYOR' if pct >= 80 else 'normal')}")
    st = load_state(a.root)
    print(f"STATE.current_worklog: {st.get('current_worklog', '?')}")


def cmd_append(a):
    root = a.root
    name, n = current_worklog(root)
    if not name:
        raise SystemExit("worklog yok — önce 'init' çalıştır")
    tag = f"[{a.module}] " if a.module else ""
    tags = f" {','.join(a.tags)}" if a.tags else ""
    line = f"- {now_stamp()} {tag}{a.text}{tags}\n"
    with open(path(root, name), "a", encoding="utf-8") as f:
        f.write(line)
    print(f"[+] {name} <- {line.strip()[:100]}")


def compress(content, n, max_summary=60):
    """!KARAR/!HATA/!AÇIK satırlarını + ilk 8 + son 10 satırı koruyan özet üretir."""
    lines = [l for l in content.splitlines() if l.strip()]
    keep_head = lines[:8]
    keep_tail = lines[-10:] if len(lines) > 18 else []
    marked = [l for l in lines if any(m in l for m in MARKERS)]
    parts = [
        f"# WORKLOG_{n} — SIKIŞTIRILMIŞ ÖZET (üretim: {now_stamp()})",
        "",
        f"Orijinal: WORKLOG_ARCHIVE_{n}.md ({len(lines)} satır) — tam tarihçe orada.",
        "",
        "## Açılış satırları",
        *keep_head, "",
        "## Tüm kararlar / hatalar / açık sorular (asla atılmaz)",
        *(marked if marked else ["(işaretli satır yok)"]), "",
        "## Kapanış satırları",
        *keep_tail, "",
    ]
    out = "\n".join(parts)
    if len(out.splitlines()) > max_summary:  # güvenlik tıkaçı
        out = "\n".join(out.splitlines()[:max_summary]) + "\n…(kırpıldı — orijinale bak)\n"
    return out + "\n"


def cmd_rotate(a):
    root = a.root
    name, n = current_worklog(root)
    if not name:
        raise SystemExit("worklog yok — önce 'init' çalıştır")
    src = path(root, name)
    content = read(src)
    lines = [l for l in content.splitlines() if l.strip()]
    if len(lines) < 5 and n > 1:
        print("[=] worklog neredeyse boş, rotasyon anlamsız — iptal")
        return
    # 1) tam arşiv
    os.replace(src, path(root, f"WORKLOG_ARCHIVE_{n}.md"))
    # 2) özet
    write(path(root, f"WORKLOG_ARCHIVE_{n}_OZET.md"), compress(content, n))
    # 3) yeni worklog
    n2 = n + 1
    write(path(root, f"WORKLOG_{n2}.md"),
          TEMPLATE_HEAD.format(n=n2, n2=n2 + 1, date=now_stamp(),
                               prev=f"WORKLOG_ARCHIVE_{n}_OZET.md"))
    # 4) INDEX
    idx_p = path(root, "INDEX.md")
    idx = read(idx_p) or "# WORKLOG INDEX\n"
    idx = re.sub(r"\| \d+ \| (WORKLOG_\d+\.md) \| GÜNCEL \|", r"| \1 | arşiv |", idx)
    satir = f"| {n2} | WORKLOG_{n2}.md | GÜNCEL | 0 |"
    if satir not in idx:
        idx = idx.rstrip() + "\n" + satir + "\n"
    idx = re.sub(r"\*\*[Gg]üncel worklog:.*?\*\*", f"**Güncel worklog: WORKLOG_{n2}.md**", idx)
    if "Güncel worklog:" not in idx:
        idx = idx.rstrip() + f"\n\n**Güncel worklog: WORKLOG_{n2}.md**\n"
    write(idx_p, idx)
    # 5) STATE
    st = load_state(root)
    st["current_worklog"] = n2
    st.setdefault("worklog_history", []).append(f"WORKLOG_ARCHIVE_{n}_OZET.md")
    save_state(root, st)
    print(f"[+] rotasyon: WORKLOG_{n} → ARCHIVE(+ÖZET), yeni: WORKLOG_{n2}, INDEX+STATE güncel")


def main():
    p = argparse.ArgumentParser(description="worklog + str(n+1) yöneticisi (GLM_Tools/03)")
    sub = p.add_subparsers(dest="cmd", required=True)

    def add_root(sp):
        sp.add_argument("--root", default=".")
        return sp

    add_root(sub.add_parser("init"))
    add_root(sub.add_parser("status")).add_argument("--max-lines", type=int, default=200)
    ap_ = add_root(sub.add_parser("append"))
    ap_.add_argument("text")
    ap_.add_argument("--module", default="")
    ap_.add_argument("--tags", nargs="*", default=[])
    rt = add_root(sub.add_parser("rotate")); rt.add_argument("--max-lines", type=int, default=200)
    a = p.parse_args()
    {"init": cmd_init, "status": cmd_status, "append": cmd_append, "rotate": cmd_rotate}[a.cmd](a)


if __name__ == "__main__":
    main()
