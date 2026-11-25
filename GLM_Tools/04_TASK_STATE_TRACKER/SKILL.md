# SKILL — TASK STATE TRACKER (tasklist amnezisi çözümü + STATE yöneticisi)

**Sorun (gerçek senaryo):**
```
x1.mesaj  : projeyi anlattım
x2.mesaj  : AI yaptı
x3.mesaj  : v2 update
x4.mesaj  : AI 5'lik tasklist hazırladı → 2'sini yaptı → 3'ü KALDI
x5.mesaj  : AI BAŞKA tasklistler yapıyor → önceki 3 task UNUTULDU
```
**Kök neden:** her yeni "yapılacaklar" listesi eskisinin yerine geçiyor; açık tasklerin
kalıcı, ID'li, tek bir kaydı yok.

**Çözüm:** `tasks.json` — tek task birliği. **Birleştirme kuralı:** yeni tasklist ESKİSİYLE
birleşir, yerine geçmez. ID'ler (T-001…) kararlıdır; bir task yalnızca KANITLA kapanır.

---

## 1) tasks.json şeması

```json
{
  "counter": 7,
  "tasks": [
    {
      "id": "T-001",
      "title": "junk-generator v2 (histogram hedefli)",
      "module": "mutasyon",
      "status": "done",            // todo | doing | blocked | done | dropped
      "created": "2026-11-26 10:00",
      "updated": "2026-11-26 14:20",
      "proof": "proofs/mutasyon/2026-11-26_1420_junkgen.txt",
      "request_id": "R-003",
      "notes": ["12/12 test PASS", "!KARAR junk_rate=0.35"]
    }
  ]
}
```

Kurallar:
- `id` bir daha asla değişmez/yeniden kullanılmaz; `counter` yalnız artar.
- `status=done` için `proof` alanı DOLU olmalı (05 audit'i bunu mekanik kontrol eder).
- `blocked` mutlaka `notes` içinde sebep taşır ("token bekleniyor", "link ölü"…).
- `dropped` = bilinçli vazgeçme (sebep notes'ta); silme yok — tarihçe kalır.

## 2) REQUESTS.md — istek günlüğü (x1..x5 mesaj akışının kaydı)

```
- R-001 (2026-11-26 10:00) kullanıcının x1 mesajı → T-001, T-002 açıldı
- R-002 (2026-11-26 11:30) "v2 yap" → T-003 açıldı; T-001 done (proof)
- R-003 (2026-11-26 13:00) 5'lik tasklist → T-004..T-008 AÇILDI (T-001..T-003 korunarak)
- R-004 (2026-11-26 15:00) yeni tasklist → T-009, T-010; T-005..T-008 hâlâ AÇIK, TAŞINDI
```
Her kullanıcı mesajı bir `R-###`; taskler isteklere bağlanır. Böylece "hangi istekte ne
kalmtış" her zaman cevaplanabilir — amnezi denetlenebilir hale gelir.

## 3) STATE.json — yönetici (manager) durumu

```json
{
  "project": "MVP_3.5.1_TO_3.9.4",
  "phase": "A1-delta-analizi",
  "active_repo": ["https://github.com/0xByteDeveloper/..."],
  "current_worklog": 3,
  "open_tasks": ["T-005", "T-006", "T-008"],
  "last_files": {"src/mutation.cpp": "sha256:ab12...  (2026-11-26 14:20)"},
  "last_request": "R-004",
  "tests_status": "12/12 PASS (proofs/mutasyon/...)",
  "blockers": ["rea repo URL'i bekleniyor"],
  "updated_at": "2026-11-26 15:10"
}
```

**AI zorunluluğu:** her mesajda işe başlamadan STATE'i oku; "hangi worklogda kaldım, proje
durumu ne, son dosya durumu, istek durumu, tasklist tamamlandı mı, testler tamamlandı mı"
sorusunun CEVABI buradadır. Oturum sonunda mutlaka güncelle (END protokolü E2).

## 4) Komutlar

```bash
python GLM_Tools/04_TASK_STATE_TRACKER/task_state.py init [--root .]
python GLM_Tools/04_TASK_STATE_TRACKER/task_state.py list [--status todo] [--root .]
python GLM_Tools/04_TASK_STATE_TRACKER/task_state.py add "başlık" --module mutasyon [--note "..."] [--root .]
python GLM_Tools/04_TASK_STATE_TRACKER/task_state.py merge yeni_tasklist.json [--root .]   # BİRLEŞTİR, ezme!
python GLM_Tools/04_TASK_STATE_TRACKER/task_state.py done T-001 --proof proofs/.../kanıt.txt [--root .]
python GLM_Tools/04_TASK_STATE_TRACKER/task_state.py block T-005 --reason "token bekleniyor" [--root .]
python GLM_Tools/04_TASK_STATE_TRACKER/task_state.py drop T-007 --reason "kapsam dışı" [--root .]
python GLM_Tools/04_TASK_STATE_TRACKER/task_state.py reconcile [--root .]   # done↔proof eşleşmesi + STATE senkron
python GLM_Tools/04_TASK_STATE_TRACKER/task_state.py state-init [--root .]
python GLM_Tools/04_TASK_STATE_TRACKER/task_state.py state-show [--root .]
```

## 5) Birleştirme kuralı (MERGE — bu skillin kalbi)

`merge yeni.json` çağrıldığında:
1. Aynı `id` görürse: alanları güncelle AMA mevcut status daha "ileri" ise (done/dropped >
   blocked > doing > todo sırasıyla) status düşürülmez; açık task açık kalır.
2. Yeni ID'ler: `counter`'dan devam ederek atanır (T-011, T-012…).
3. Hiçbir task SİLİNMEZ. "Eski tasklist" diye bir kavram artık yoktur — tek bir birlik vardır.

Bu kural GOD MOD master prompt kural 3'ün mekanik halidir: **"yeni tasklist eskisinin yerine
geçmez, birleşir."**
