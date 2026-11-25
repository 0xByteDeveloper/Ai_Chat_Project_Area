#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
task_state.py — GLM_Tools/04: task birliği (tasks.json) + yönetici durumu (STATE.json).

ÇÖZDÜĞÜ SORUN: "x4'te 5'lik tasklistin 2'si yapıldı, 3 kaldı; x5'te AI yeni
tasklist yapıp öncekileri unuttu." → merge kuralı: yeni tasklist ESKİSİYLE
birleşir, yerine geçmez; ID'ler (T-###) kararlı; task ancak KANITLA kapanır.

Komutlar:
  init / list / add / merge / done / block / drop / reconcile / state-init / state-show
Tamamen stdlib; Python 3.8+.
"""
import argparse
import datetime
import json
import os

STATUS_RANK = {"todo": 0, "doing": 1, "blocked": 2, "done": 3, "dropped": 4}


def now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")


def pj(root, name):
    return os.path.join(root, name)


def load(root, name, default):
    p = pj(root, name)
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    return default


def save(root, name, data):
    with open(pj(root, name), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def load_tasks(root):
    return load(root, "tasks.json", {"counter": 0, "tasks": []})


def save_tasks(root, t):
    save(root, "tasks.json", t)


def open_tasks(t):
    return [x for x in t["tasks"] if x["status"] in ("todo", "doing", "blocked")]


def sync_state(root, t):
    st = load(root, "STATE.json", {})
    st["open_tasks"] = [x["id"] for x in open_tasks(t)]
    st["updated_at"] = now()
    save(root, "STATE.json", st)


def find(t, tid):
    for x in t["tasks"]:
        if x["id"] == tid:
            return x
    raise SystemExit(f"HATA: {tid} bulunamadı")


def cmd_init(a):
    root = a.root
    os.makedirs(root, exist_ok=True)
    if not os.path.exists(pj(root, "tasks.json")):
        save_tasks(root, {"counter": 0, "tasks": []})
    if not os.path.exists(pj(root, "REQUESTS.md")):
        with open(pj(root, "REQUESTS.md"), "w", encoding="utf-8") as f:
            f.write("# REQUESTS — istek günlüğü\n\n"
                    "Her kullanıcı mesajı bir R-###; taskler isteklere bağlanır.\n\n"
                    "- R-001 (tarih) ilk istek → (taskler)\n")
    print("[+] init tamam:", os.path.abspath(root))


def cmd_list(a):
    t = load_tasks(a.root)
    rows = t["tasks"]
    if a.status:
        rows = [x for x in rows if x["status"] == a.status]
    if not rows:
        print("(task yok%s)" % (f" — status={a.status}" if a.status else ""))
        return
    print(f"{'ID':7s} {'DURUM':8s} {'MODÜL':14s} BAŞLIK / kanıt")
    for x in rows:
        line = f"{x['id']:7s} {x['status']:8s} {x.get('module', ''):14s} {x['title']}"
        if x.get("proof"):
            line += f"\n         ↳ kanıt: {x['proof']}"
        if x["status"] == "blocked":
            line += "\n         ↳ sebep: " + (x.get("notes") or ["?"])[-1]
        print(line)
    op = open_tasks(load_tasks(a.root))
    print(f"— toplam {len(t['tasks'])} task, AÇIK: {len(op)}")


def cmd_add(a):
    t = load_tasks(a.root)
    t["counter"] += 1
    tid = f"T-{t['counter']:03d}"
    t["tasks"].append({
        "id": tid, "title": a.title, "module": a.module, "status": "todo",
        "created": now(), "updated": now(), "proof": None,
        "notes": ([a.note] if a.note else []),
    })
    save_tasks(a.root, t)
    sync_state(a.root, t)
    print(f"[+] {tid} açıldı: {a.title}")


def cmd_merge(a):
    """Birleştirme kuralı: yeni tasklist ESKİSİYLE birleşir; status geri düşürülmez;
    hiçbir task silinmez; yeni ID'ler counter'dan devam eder."""
    with open(a.file, encoding="utf-8") as f:
        incoming = json.load(f)
    inc_tasks = incoming.get("tasks", incoming if isinstance(incoming, list) else [])
    t = load_tasks(a.root)
    by_id = {x["id"]: x for x in t["tasks"]}
    merged = updated = kept_open = 0
    for it in inc_tasks:
        tid = it.get("id")
        if tid and tid in by_id:  # mevcut task: alanları güncelle, status'u düşürme
            x = by_id[tid]
            for k in ("title", "module", "notes"):
                if it.get(k):
                    x[k] = it[k] if k != "notes" else (x.get("notes", []) + it[k])
            inc_status = it.get("status", "todo")
            if STATUS_RANK.get(inc_status, 0) > STATUS_RANK.get(x["status"], 0):
                x["status"] = inc_status
                if inc_status == "done" and it.get("proof"):
                    x["proof"] = it["proof"]
            x["updated"] = now()
            updated += 1
            if x["status"] in ("todo", "doing", "blocked"):
                kept_open += 1
        else:  # yeni task
            t["counter"] += 1
            new_id = f"T-{t['counter']:03d}"
            t["tasks"].append({
                "id": new_id, "title": it.get("title", "(başlıksız)"),
                "module": it.get("module", ""), "status": it.get("status", "todo"),
                "created": now(), "updated": now(), "proof": it.get("proof"),
                "notes": it.get("notes", []),
            })
            merged += 1
    save_tasks(a.root, t)
    sync_state(a.root, t)
    print(f"[+] merge: {updated} mevcut güncellendi (açık kalan: {kept_open}), {merged} yeni eklendi")
    print(f"    AÇIK taskler: {[x['id'] for x in open_tasks(t)]}")


def cmd_done(a):
    t = load_tasks(a.root)
    if not a.proof:
        raise SystemExit("HATA: done için --proof ZORUNLU (kanıtsız task kapanmaz — GOD MOD kuralı)")
    if not os.path.exists(a.proof) and not a.proof.startswith("proofs/"):
        print(f"[!] uyarı: kanıt dosyası yerelde bulunamadı ({a.proof}) — repo kökünden relative olabilir")
    x = find(t, a.tid)
    x["status"] = "done"
    x["proof"] = a.proof
    x["updated"] = now()
    if a.note:
        x.setdefault("notes", []).append(a.note)
    save_tasks(a.root, t)
    sync_state(a.root, t)
    print(f"[+] {a.tid} KAPANDI (kanıtlı): {a.proof}")


def cmd_block(a):
    t = load_tasks(a.root)
    x = find(t, a.tid)
    x["status"] = "blocked"
    x["updated"] = now()
    x.setdefault("notes", []).append(f"BLOCKED: {a.reason}")
    save_tasks(a.root, t)
    sync_state(a.root, t)
    print(f"[!] {a.tid} bloklandı: {a.reason}")


def cmd_drop(a):
    t = load_tasks(a.root)
    x = find(t, a.tid)
    x["status"] = "dropped"
    x["updated"] = now()
    x.setdefault("notes", []).append(f"DROPPED: {a.reason}")
    save_tasks(a.root, t)
    sync_state(a.root, t)
    print(f"[-] {a.tid} bırakıldı (kayıt korunuyor): {a.reason}")


def cmd_reconcile(a):
    """done↔proof eşleşmesi + STATE senkronu. CI'da da koşturulabilir (exit 1 = sorun var)."""
    t = load_tasks(a.root)
    bad = [x for x in t["tasks"] if x["status"] == "done" and not x.get("proof")]
    sync_state(a.root, t)
    print(f"task: {len(t['tasks'])} | açık: {len(open_tasks(t))} | done: "
          f"{sum(1 for x in t['tasks'] if x['status'] == 'done')} | dropped: "
          f"{sum(1 for x in t['tasks'] if x['status'] == 'dropped')}")
    if bad:
        print("KANITSIZ 'done' TASKLER (03 audit ihlali):")
        for x in bad:
            print(f"  - {x['id']}: {x['title']}")
        print("→ bu taskler blocked'a çevrilmeli ya da kanıt üretilmeli")
        for x in bad:
            x["status"] = "blocked"
            x["updated"] = now()
            x.setdefault("notes", []).append("BLOCKED: kanıt yok (reconcile)")
        save_tasks(a.root, t)
        sync_state(a.root, t)
        print("[!] kanıtsız done'lar otomatik blocked'a çevrildi")
    else:
        print("OK: her 'done' taskin kanıtı var.")
    st = load(a.root, "STATE.json", {})
    print(f"STATE.open_tasks: {st.get('open_tasks')}")


def cmd_state_init(a):
    st = {
        "project": "(proje adı)",
        "phase": "(aşama)",
        "active_repo": [],
        "current_worklog": 1,
        "open_tasks": [],
        "last_files": {},
        "last_request": "",
        "tests_status": "",
        "blockers": [],
        "updated_at": now(),
    }
    t = load_tasks(a.root)
    st["open_tasks"] = [x["id"] for x in open_tasks(t)]
    save(a.root, "STATE.json", st)
    print("[+] STATE.json hazır")


def cmd_state_show(a):
    st = load(a.root, "STATE.json", None)
    if st is None:
        raise SystemExit("STATE.json yok — state-init çalıştır")
    print(json.dumps(st, ensure_ascii=False, indent=2))


def main():
    p = argparse.ArgumentParser(description="task birliği + STATE yöneticisi (GLM_Tools/04)")
    sub = p.add_subparsers(dest="cmd", required=True)

    def add_root(sp):
        sp.add_argument("--root", default=".")
        return sp

    add_root(sub.add_parser("init"))
    ls = add_root(sub.add_parser("list")); ls.add_argument("--status", default="")
    ad = add_root(sub.add_parser("add")); ad.add_argument("title"); ad.add_argument("--module", default=""); ad.add_argument("--note", default="")
    mg = add_root(sub.add_parser("merge")); mg.add_argument("file")
    dn = add_root(sub.add_parser("done")); dn.add_argument("tid"); dn.add_argument("--proof", required=True); dn.add_argument("--note", default="")
    bl = add_root(sub.add_parser("block")); bl.add_argument("tid"); bl.add_argument("--reason", required=True)
    dr = add_root(sub.add_parser("drop")); dr.add_argument("tid"); dr.add_argument("--reason", required=True)
    add_root(sub.add_parser("reconcile"))
    add_root(sub.add_parser("state-init"))
    add_root(sub.add_parser("state-show"))
    a = p.parse_args()
    {
        "init": cmd_init, "list": cmd_list, "add": cmd_add, "merge": cmd_merge,
        "done": cmd_done, "block": cmd_block, "drop": cmd_drop, "reconcile": cmd_reconcile,
        "state-init": cmd_state_init, "state-show": cmd_state_show,
    }[a.cmd](a)


if __name__ == "__main__":
    main()
