#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
zai_chat_extractor.py — GLM_Tools/06: mesaj linki + token → o sohbetin TÜM mesajları ve dosyaları.

NE YAPAR: Kullanıcı bir chat.z.ai sohbet linki (veya ID) + token verir;
  (1) sohbet künyesini çeker, (2) TÜM mesajlarını (batch) çeker,
  (3) markdown + json export üretir, (4) mesajlardaki dosya/attachment
  kayıtlarını toplar ve URL'i varsa indirir (dosyalar/ klasörüne).

ENDPOINT'LER (doğrulanmış, 2026-11-26):
  GET  https://chat.z.ai/api/v1/chats/{id}
  POST https://chat.z.ai/api/v1/chats/{id}/messages/batch   {"ids":[...]}

KULLANIM:
  python zai_chat_extractor.py --url "https://chat.z.ai/chats/<ID>" --token "eyJ..."
  python zai_chat_extractor.py --id <ID> --tokens tokens.json --user User1
  python zai_chat_extractor.py --selftest            # ağsız pipeline kanıtı

Not: URL formatı chat.z.ai arayüzünde /chats/<id> veya ?chat=<id> olabilir;
araç regex ile ID'yi kendisi çıkarır. Tamamen stdlib.
"""
import argparse
import json
import os
import re
import ssl
import time
import urllib.request
from datetime import datetime, timezone

BASE = os.environ.get("ZAI_API_BASE", "https://chat.z.ai/api/v1")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")
CTX = ssl.create_default_context()

ID_RE = re.compile(r"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})", re.I)


def http(url, token, method="GET", body=None, timeout=180, binary=False):
    headers = {
        "User-Agent": UA,
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "X-FE-Version": "prod-fe-1.2.36",
        "Origin": "https://chat.z.ai",
        "Referer": "https://chat.z.ai/",
    }
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=timeout, context=CTX) as resp:
        raw = resp.read()
        if binary:
            return raw
        return json.loads(raw.decode("utf-8", errors="ignore"))


def extract_id(s):
    m = ID_RE.search(s or "")
    if m:
        return m.group(1)
    # GUID değilse: son path parçası / query parametresi dene
    m2 = re.search(r"(?:chats/|chat=|c/)([A-Za-z0-9_-]+)", s or "")
    return m2.group(1) if m2 else None


def ts_fmt(ts):
    try:
        return datetime.fromtimestamp(int(ts), tz=timezone.utc).strftime("%Y-%m-%d %H:%M")
    except Exception:
        return str(ts or "")


def safe_name(t):
    return re.sub(r"[^A-Za-z0-9ÇĞİÖŞÜçğıöşü _\-.]+", "_", (t or "")[:60]).strip() or "untitled"


def collect_files(m):
    """Mesaj gövdesinden dosya/attachment kayıtlarını topla (URL varsa indirilebilir)."""
    found = []
    files = m.get("files")
    if isinstance(files, list):
        for f in files:
            if isinstance(f, dict):
                found.append({"name": f.get("name") or f.get("id") or "?",
                              "url": f.get("url") or f.get("download_url") or f.get("path"),
                              "size": f.get("size"), "id": f.get("id")})
    # assistant bloklarında da dosya kaydı olabilir
    for b in (m.get("content_blocks") or []):
        for key in ("files", "attachments", "file"):
            v = b.get(key)
            if isinstance(v, list):
                for f in v:
                    if isinstance(f, dict):
                        found.append({"name": f.get("name") or f.get("id") or "?",
                                      "url": f.get("url") or f.get("download_url"),
                                      "size": f.get("size"), "id": f.get("id")})
    return [f for f in found if f.get("name") or f.get("url")]


def render_message(k, m):
    role = m.get("role", "?")
    t = ts_fmt(m.get("timestamp") or m.get("created_at"))
    head = f"\n--- MESAJ {k} [{role}] {t}\n"
    parts = [head]
    if role == "user":
        c = str(m.get("content") or "").strip()
        parts.append((c or "(boş)") + "\n")
    else:
        for b in (m.get("content_blocks") or []):
            bt = b.get("type")
            if bt == "text":
                txt = str(b.get("content") or "").strip()
                if txt:
                    parts.append(txt + "\n")
            elif bt == "tool_calls":
                for call in (b.get("content") or []):
                    try:
                        fn = call.get("function", {})
                        parts.append(f"  [ARAÇ {fn.get('name','?')}] {str(fn.get('arguments',''))[:180]}\n")
                    except Exception:
                        pass
            elif bt == "reasoning":
                pass  # uzun akıl yürütmeleri exporta girmiyor (kısaltmak için)
        if m.get("error"):
            parts.append(f"[HATA: {str(m.get('error'))[:200]}]\n")
    return "".join(parts)


def fetch_chat(cid, token, out_root, sleep=0.6, download_files=True, live=True, fixture=None):
    detail = http(f"{BASE}/chats/{cid}", token) if live else fixture["detail"]
    time.sleep(sleep)
    title = detail.get("title") or (detail.get("chat") or {}).get("title") or "(başlıksız)"
    ids = list(((detail.get("chat") or {}).get("history") or {}).get("messages") or {})
    data = {}
    if live:
        for j in range(0, len(ids), 100):
            chunk = ids[j:j + 100]
            res = http(f"{BASE}/chats/{cid}/messages/batch", token, method="POST", body={"ids": chunk})
            data.update(res.get("data") or {})
            time.sleep(sleep)
    else:
        data = fixture["messages"]
    msgs = sorted(data.values(), key=lambda m: m.get("timestamp") or m.get("created_at") or 0)

    # çıktı klasörü
    cdir = os.path.join(out_root, f"{safe_name(title)}_{cid[:8]}")
    fdir = os.path.join(cdir, "dosyalar")
    os.makedirs(fdir, exist_ok=True)

    # markdown export
    md = [
        f"# {title}\n",
        "\n",
        f"id: {cid}\n",
        f"oluşturulma: {ts_fmt(detail.get('created_at'))} · güncelleme: {ts_fmt(detail.get('updated_at'))}\n",
        f"mesaj sayısı: {len(msgs)}\n",
        "\n",
        "=" * 60 + "\n",
        "",
    ]
    files_meta = []
    for k, m in enumerate(msgs, 1):
        md.append(render_message(k, m))
        for f in collect_files(m):
            files_meta.append(f)
            md.append(f"  [DOSYA: {f.get('name')}{' — ' + str(f.get('url')) if f.get('url') else ''}]\n")
    with open(os.path.join(cdir, "sohbet.md"), "w", encoding="utf-8") as f:
        f.write("".join(md))

    # json export (ham, yeniden işlenebilir)
    with open(os.path.join(cdir, "sohbet.json"), "w", encoding="utf-8") as f:
        json.dump({"id": cid, "title": title, "detail": detail, "messages": msgs},
                  f, ensure_ascii=False, indent=1)

    # dosyaları indir (URL varsa)
    downloaded, failed = [], []
    if download_files:
        for f in files_meta:
            url = f.get("url")
            if not url:
                continue
            dest = os.path.join(fdir, safe_name(str(f.get("name"))))
            try:
                raw = http(url, token, binary=True, timeout=300) if url.startswith("http") else None
                if raw:
                    with open(dest, "wb") as fh:
                        fh.write(raw)
                    downloaded.append(dest)
            except Exception as e:
                failed.append((f.get("name"), str(e)[:100]))

    with open(os.path.join(cdir, "DOSYA_LISTESI.md"), "w", encoding="utf-8") as f:
        f.write(f"# Dosyalar — {title}\n\n")
        if not files_meta:
            f.write("(sohbette dosya kaydı yok)\n")
        for x in files_meta:
            f.write(f"- {x.get('name')} | url: {x.get('url') or '-'} | boyut: {x.get('size') or '-'}\n")
        if downloaded:
            f.write("\nİndirilenler:\n" + "\n".join(f"- {os.path.relpath(d, cdir)}" for d in downloaded))
        if failed:
            f.write("\nİndirilemeyenler:\n" + "\n".join(f"- {n}: {e}" for n, e in failed))

    return {"dir": cdir, "title": title, "messages": len(msgs), "files": len(files_meta),
            "downloaded": len(downloaded), "failed": len(failed)}


def selftest():
    fixture = {
        "detail": {
            "id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
            "title": "Test Sohbeti (fixture)",
            "created_at": 1763900000, "updated_at": 1764000000,
            "chat": {"history": {"messages": {"m1": {}, "m2": {}}}, "models": "glm-5.3"},
        },
        "messages": {
            "m1": {"role": "user", "timestamp": 1, "content": "bu dosyaya bak",
                   "files": [{"name": "hedef.exe", "id": "f1", "size": 13312}]},
            "m2": {"role": "assistant", "timestamp": 2, "content_blocks": [
                {"type": "text", "content": "analiz edildi"},
                {"type": "tool_calls", "content": [{"function": {"name": "Bash", "arguments": "{}"}}]},
            ]},
        },
    }
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".selftest", "zai_extractor")
    r = fetch_chat(fixture["detail"]["id"], "FIXTURE", out, download_files=False, live=False, fixture=fixture)
    checks = [
        ("tüm mesajlar çekildi (2)", r["messages"] == 2),
        ("dosya kaydı bulundu (1)", r["files"] == 1),
        ("sohbet.md üretildi", os.path.exists(os.path.join(r["dir"], "sohbet.md"))),
        ("sohbet.json üretildi", os.path.exists(os.path.join(r["dir"], "sohbet.json"))),
        ("DOSYA_LISTESI.md üretildi", os.path.exists(os.path.join(r["dir"], "DOSYA_LISTESI.md"))),
    ]
    ok = True
    for name, cond in checks:
        print(("  [PASS] " if cond else "  [FAIL] ") + name)
        ok = ok and cond
    print("SELFTEST:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    p = argparse.ArgumentParser(description="chat.z.ai sohbet çekici (GLM_Tools/06)")
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--url", help="sohbet linki (ID kendisi çıkarılır)")
    src.add_argument("--id", help="sohbet ID'si")
    src.add_argument("--selftest", action="store_true")
    p.add_argument("--token", default="")
    p.add_argument("--tokens", help="tokens.json (—user ile birlikte)")
    p.add_argument("--user", default="", help="tokens.json içindeki kullanıcı adı")
    p.add_argument("--out-dir", default="./zai_export")
    p.add_argument("--no-download", action="store_true", help="dosyaları indirme (yalnız listele)")
    a = p.parse_args()

    if a.selftest:
        raise SystemExit(selftest())

    token = a.token
    if not token and a.tokens and a.user:
        with open(a.tokens, encoding="utf-8") as f:
            token = next(u["token"] for u in json.load(f)["users"] if u["name"] == a.user)
    if not token:
        raise SystemExit("token ver: --token <JWT> veya --tokens tokens.json --user <ad>")

    cid = extract_id(a.url) if a.url else a.id
    if not cid:
        raise SystemExit("ID çıkarılamadı — tam linki veya ID'yi ver")
    print(f"[*] sohbet: {cid}")
    r = fetch_chat(cid, token, a.out_dir, download_files=not a.no_download)
    print(f"[+] '{r['title']}' → {r['messages']} mesaj, {r['files']} dosya kaydı, "
          f"{r['downloaded']} indirildi")
    print(f"    klasör: {r['dir']}")


if __name__ == "__main__":
    main()
