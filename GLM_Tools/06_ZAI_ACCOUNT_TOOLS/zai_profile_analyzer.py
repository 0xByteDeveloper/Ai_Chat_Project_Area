#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
zai_profile_analyzer.py — GLM_Tools/06: chat.z.ai hesap profil analizörü.

NE YAPAR: Verilen JWT token(lar) ile bir kullanıcının hesabından
  (1) sohbet listesini çeker (başlığı boş / "New Chat" olanlar hariç),
  (2) son N dolu sohbeti seçer (varsayılan 20 — SOHBET sayısı, mesaj değil),
  (3) her sohbetin TÜM mesajlarını çeker (batch, kaç mesaj varsa),
  (4) transkriptler + chats_summary.json + PROFILE_REPORT.md üretir.

ENDPOINT'LER (doğrulanmış, 2026-11-26):
  GET  https://chat.z.ai/api/v1/chats/                       → sohbet listesi
  GET  https://chat.z.ai/api/v1/chats/{id}                   → künye + mesaj ID'leri
  POST https://chat.z.ai/api/v1/chats/{id}/messages/batch    → {"ids":[...]} → {"data":{id:mesaj}}

KULLANIM:
  python zai_profile_analyzer.py --tokens tokens.json --out-dir ./zai_export
  python zai_profile_analyzer.py --token "eyJ..." --name User1 --out-dir ./zai_export
  python zai_profile_analyzer.py --selftest          # ağ gerektirmez, pipeline'ı kanıtlar
Tokenlar repoya ASLA commit edilmez (bkz. SKILL.md). Tamamen stdlib.
"""
import argparse
import json
import os
import re
import ssl
import time
import urllib.error
import urllib.request
from collections import Counter
from datetime import datetime, timezone

BASE = os.environ.get("ZAI_API_BASE", "https://chat.z.ai/api/v1")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")
CTX = ssl.create_default_context()
SKIP_TITLES = {"", "new chat", "yeni sohbet", "untitled"}

THEME_KEYWORDS = {
    "VMProtect/VMP": ["vmp", "vmprotect", "3.5.1", "3.9.4", "virtualiz", "devirt"],
    "XProtect/Maze": ["xprotect", "xguard", "maze", "packer", "unpack", "obfus"],
    "ImGui/UI klon": ["imgui", "universal", "qt ", "qt5", "qt6", "menu", "ui editor", "win32"],
    "Decompiler/RE": ["decompil", "ghidra", "pdb", "rtti", "ida", "reverse", "simbol"],
    "Simülasyon/Unicorn": ["unicorn", "simulat", "i4m", "consoleloader", "emulat", "qiling"],
    "Metin2/Oyun": ["metin2", "m2py", "m2god", "pvp", "farmbot", "cheat engine", "slot"],
    "AI fabrika": ["worklog", "sandbox", "github", "push", "tasklist", "checkpoint", "z-bridge", "glm"],
    "Altyapı": ["yandex", "drive", "zip", "derle", "compile", "cmake", "visual studio"],
}


def http(url, token, method="GET", body=None, timeout=180, retries=2):
    headers = {
        "User-Agent": UA,
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Accept-Language": "en-US",
        "X-FE-Version": "prod-fe-1.2.36",
        "Origin": "https://chat.z.ai",
        "Referer": "https://chat.z.ai/",
    }
    data = json.dumps(body).encode() if body is not None else None
    last = None
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, data=data, headers=headers, method=method)
            with urllib.request.urlopen(req, timeout=timeout, context=CTX) as resp:
                return json.loads(resp.read().decode("utf-8", errors="ignore"))
        except Exception as e:
            last = e
            if attempt < retries:
                time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"HTTP başarısız: {url} → {last}")


def safe_name(t):
    t = re.sub(r"[^A-Za-z0-9ÇĞİÖŞÜçğıöşü _\-.]+", "_", (t or "")[:60]).strip()
    return t or "untitled"


def ts_fmt(ts):
    try:
        return datetime.fromtimestamp(int(ts), tz=timezone.utc).strftime("%Y-%m-%d %H:%M")
    except Exception:
        return str(ts or "")


def message_brief(m):
    """Bir mesajın kısa metni (tool çağrıları + metin blokları)."""
    if m.get("role") == "user":
        return str(m.get("content") or "")
    texts, tools = [], Counter()
    for b in (m.get("content_blocks") or []):
        if b.get("type") == "text":
            txt = str(b.get("content") or "").strip()
            if txt:
                texts.append(txt)
        elif b.get("type") == "tool_calls":
            for call in (b.get("content") or []):
                try:
                    tools[call["function"]["name"]] += 1
                except Exception:
                    pass
    return "\n".join(texts), tools


def fetch_user(tok, label, out_dir, limit=20, sleep=0.6, live=True, fixture=None):
    udir = os.path.join(out_dir, label)
    tdir = os.path.join(udir, "transcripts")
    os.makedirs(tdir, exist_ok=True)

    # 1) liste
    if live:
        chats = http(f"{BASE}/chats/", tok)
        time.sleep(sleep)
    else:
        chats = fixture["chats"]
    good = [c for c in chats if (c.get("title") or "").strip().lower() not in SKIP_TITLES]
    good.sort(key=lambda c: c.get("updated_at") or 0, reverse=True)
    sel = good[:limit]
    print(f"[{label}] toplam={len(chats)} dolu={len(good)} seçilen={len(sel)}")

    summary = []
    for i, c in enumerate(sel, 1):
        cid = c["id"]
        title = c.get("title") or "(başlıksız)"
        if live:
            detail = http(f"{BASE}/chats/{cid}", tok)
            time.sleep(sleep)
        else:
            detail = fixture["detail"]
        ids = list(((detail.get("chat") or {}).get("history") or {}).get("messages") or {})
        # 2) TÜM mesajlar (100'lük batch'ler)
        data = {}
        if live:
            for j in range(0, len(ids), 100):
                chunk = ids[j:j + 100]
                res = http(f"{BASE}/chats/{cid}/messages/batch", tok, method="POST", body={"ids": chunk})
                data.update(res.get("data") or {})
                time.sleep(sleep)
        else:
            data = fixture["messages"]
        msgs = sorted(data.values(), key=lambda m: m.get("timestamp") or m.get("created_at") or 0)
        # 3) transkript
        tf = os.path.join(tdir, f"{i:02d}_{safe_name(title)}.txt")
        with open(tf, "w", encoding="utf-8") as f:
            f.write(f"### SOHBET: {title}\n")
            f.write(f"id={cid} | guncelleme={ts_fmt(detail.get('updated_at'))} | mesaj_sayisi={len(msgs)}\n")
            f.write("=" * 70 + "\n")
            for k, m in enumerate(msgs, 1):
                out, tools = message_brief(m) if m.get("role") != "user" else (str(m.get("content") or ""), Counter())
                f.write(f"\n--- MESAJ {k} [{m.get('role','?')}] {ts_fmt(m.get('timestamp'))}\n")
                body = out if isinstance(out, str) else "\n".join(out)
                f.write(((body or "").strip()[:4000] or "(boş)") + "\n")
                if tools:
                    f.write(f"(araç çağrıları: {dict(tools)})\n")
        # 4) istatistik
        roles = Counter(m.get("role") for m in msgs)
        tools_total = Counter()
        text_all = []
        for m in msgs:
            if m.get("role") == "user":
                text_all.append(str(m.get("content") or ""))
            else:
                for b in (m.get("content_blocks") or []):
                    if b.get("type") == "text":
                        text_all.append(str(b.get("content") or ""))
                    elif b.get("type") == "tool_calls":
                        for call in (b.get("content") or []):
                            try:
                                tools_total[call["function"]["name"]] += 1
                            except Exception:
                                pass
        summary.append({
            "no": i, "id": cid, "title": title,
            "updated_at": ts_fmt(detail.get("updated_at")),
            "messages": len(msgs), "roles": dict(roles),
            "tool_calls_total": sum(tools_total.values()),
            "top_tools": dict(tools_total.most_common(8)),
            "transcript": os.path.relpath(tf, out_dir).replace(os.sep, "/"),
            "text_korpus": "\n".join(text_all),
        })
        print(f"  [{label}] {i:02d} {title[:48]:50s} mesaj={len(msgs):4d}")
    with open(os.path.join(udir, "chats_summary.json"), "w", encoding="utf-8") as f:
        json.dump([{k: v for k, v in s.items() if k != "text_korpus"} for s in summary],
                  f, ensure_ascii=False, indent=2)
    return {"label": label, "summary": summary}


def build_report(users, out_dir):
    lines = ["# chat.z.ai PROFİL RAPORU", "", f"Üretim: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
             f"Kullanıcı sayısı: {len(users)}", ""]
    for u in users:
        s = u["summary"]
        if not s:
            lines += [f"## {u['label']}", "(dolu sohbet bulunamadı)", ""]
            continue
        corpus = " ".join(x["text_korpus"] for x in s).lower()
        themes = {name: sum(corpus.count(k) for k in keys) for name, keys in THEME_KEYWORDS.items()}
        top_themes = sorted(themes.items(), key=lambda kv: -kv[1])[:6]
        total_msgs = sum(x["messages"] for x in s)
        total_tools = sum(x["tool_calls_total"] for x in s)
        lines += [
            f"## {u['label']}",
            "",
            f"- İncelenen dolu sohbet: **{len(s)}** · toplam mesaj: **{total_msgs}** · toplam araç çağrısı: **~{total_tools}**",
            f"- Tarih aralığı: {s[-1]['updated_at']} → {s[0]['updated_at']}",
            f"- Ana temalar: " + ", ".join(f"**{t}** ({c})" for t, c in top_themes if c),
            "",
            "| # | Sohbet | Mesaj | Araç | Güncelleme |",
            "|---|---|---|---|---|",
        ]
        for x in s:
            lines.append(f"| {x['no']} | {x['title'][:60]} | {x['messages']} | {x['tool_calls_total']} | {x['updated_at']} |")
        lines.append("")
    p = os.path.join(out_dir, "PROFILE_REPORT.md")
    with open(p, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return p


def selftest():
    fixture = {
        "chats": [
            {"id": "c1", "title": "VMP 3.5.1 port sorunu", "updated_at": 1764000000},
            {"id": "c2", "title": "New Chat", "updated_at": 1764000100},
            {"id": "c3", "title": "", "updated_at": 1764000200},
            {"id": "c4", "title": "ImGui analyst", "updated_at": 1764000300},
        ],
        "detail": {
            "chat": {"history": {"messages": {"m1": {}, "m2": {}, "m3": {}}}, "models": "glm-5.3"},
            "created_at": 1763900000, "updated_at": 1764000000,
        },
        "messages": {
            "m1": {"role": "user", "content": "vmprotect 3.5.1 portunu nasıl iyileştirelim", "timestamp": 1},
            "m2": {"role": "assistant", "timestamp": 2, "content_blocks": [
                {"type": "text", "content": "XProtect için mutation motoru ekleyelim"},
                {"type": "tool_calls", "content": [
                    {"function": {"name": "Bash", "arguments": "{}"}},
                    {"function": {"name": "Bash", "arguments": "{}"}},
                ]},
            ]},
            "m3": {"role": "user", "content": "imgui tarafı ne durumda", "timestamp": 3},
        },
    }
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".selftest", "zai_profile")
    res = fetch_user("FIXTURE_TOKEN", "User1", out, limit=20, live=False, fixture=fixture)
    report = build_report([res], out)
    checks = [
        ("New Chat/boş başlık elendi", len(res["summary"]) == 2),
        ("TÜM mesajlar çekildi (3)", res["summary"][0]["messages"] == 3),
        ("araç çağrısı sayıldı (2)", res["summary"][0]["tool_calls_total"] == 2),
        ("rapor üretildi", os.path.exists(report)),
        ("transkript üretildi",
         os.path.exists(os.path.join(out, res["summary"][0]["transcript"]))),
    ]
    ok = True
    for name, cond in checks:
        print(("  [PASS] " if cond else "  [FAIL] ") + name)
        ok = ok and cond
    print("SELFTEST:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    p = argparse.ArgumentParser(description="chat.z.ai profil analizörü (GLM_Tools/06)")
    p.add_argument("--tokens", help="tokens.json: {\"users\":[{\"name\",\"token\"}]}")
    p.add_argument("--token", help="tek JWT")
    p.add_argument("--name", default="User1", help="tek JWT için etiket")
    p.add_argument("--limit", type=int, default=20, help="kaç dolu sohbet (varsayılan 20)")
    p.add_argument("--out-dir", default="./zai_export")
    p.add_argument("--sleep", type=float, default=0.6, help="istekler arası bekleme (sn)")
    p.add_argument("--selftest", action="store_true", help="ağsız pipeline kanıtı")
    a = p.parse_args()

    if a.selftest:
        raise SystemExit(selftest())

    users_cfg = []
    if a.tokens:
        with open(a.tokens, encoding="utf-8") as f:
            for u in json.load(f).get("users", []):
                users_cfg.append((u["name"], u["token"]))
    elif a.token:
        users_cfg = [(a.name, a.token)]
    else:
        raise SystemExit("token ver: --tokens tokens.json veya --token <JWT> --name <etiket>")

    os.makedirs(a.out_dir, exist_ok=True)
    results = []
    for name, tok in users_cfg:
        results.append(fetch_user(tok, name, a.out_dir, limit=a.limit, sleep=a.sleep))
    report = build_report(results, a.out_dir)
    print(f"\n[+] RAPOR: {report}")


if __name__ == "__main__":
    main()
