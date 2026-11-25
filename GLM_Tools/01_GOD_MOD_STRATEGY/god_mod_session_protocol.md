# GOD MOD Oturum Protokolü — adım adım (AI'nın izleyeceği checklist)

Bu dosya AI'ın her oturumda HARFİYEN izleyeceği operasyonel protokoldür.
(`01_GOD_MOD_STRATEGY/SKILL.md` neden anlatır; bu dosya NASIL.)

---

## START (oturumun ilk 5 dakikası)

- [ ] **S1.** `GLM_Tools/04_TASK_STATE_TRACKER/STATE.json` oku.
      - `active_repo` listesindeki proje repolarını klonla/güncelle (token STATE'te değil
        mesajda verilir; yoksa kullanıcıya sor).
- [ ] **S2.** `GLM_Tools/03_WORKLOG_MANAGER/INDEX.md` → güncel `WORKLOG_(n).md`; **son 40 satırı** oku
      (yoksa full — yeni worklog'lar kısa zaten).
- [ ] **S3.** `tasks.json` → `status ∈ {todo, doing, blocked}` taskleri listele (bunlar "kutsal" —
      hiçbir yeni plan bunları ezmeyebilir).
- [ ] **S4.** `MEMORY_CARD.md` → proje kimliği + kullanıcı tercihleri (çok hızlı tarama).
- [ ] **S5.** Durum raporu ver (6 satır): kaldığın yer / açık taskler / engeller / sıradaki
      modül / test durumu / emin olmadığın noktalar.

## LOOP (her modül — hedef 25-35 dk)

- [ ] **L1.** Modülü tanımla: hangi T-### task'ı kapatıyor? (kapamıyorsa yeni task aç: T-###).
- [ ] **L2.** Modül klasörünü oluştur (varsa gir): `modules/<modül_adı>/`.
- [ ] **L3.** KODU yaz.
- [ ] **L4.** TESTİ yaz ve çalıştır: (a) önce kırmızı (testin modülsüz失败 göstereceğini doğrula
      ya da mantıken göster) (b) sonra yeşil. Test çıktısını kaydet.
- [ ] **L5.** KANITI üret: `proofs/<modül>/<YYYY-AA-GG>_<saat>_<kanıt>.txt` — komut, çıktı,
      hash. `PROOF.md` indeksine satır ekle (`05_MODULE_TEST_PROOF/module_test_proof.py prove`).
- [ ] **L6.** PUSH: `python GLM_Tools/02_LIVING_GITHUB/living_github.py push "[<modül>] ... + n/n test PASS + proofs/<modül>/..."`.
- [ ] **L7.** WORKLOG'a 1-3 satır append: ne yapıldı, test sonucu, karar varsa `!KARAR`,
      hata varsa `!HATA`, açık soru varsa `!AÇIK` etiketiyle.
- [ ] **L8.** 200 satır eşiği aşıldıysa `worklog_manager.py rotate`.
- [ ] **L9.** Sonraki modüle geç.

## END (oturumun son 5 dakikası — ASLA atlanmaz)

- [ ] **E1.** `tasks.json` reconcile: "done" dediğin her taskin `proof` alanı dolu mu?
      (`module_test_proof.py audit` çalıştır). Dolmayan → `blocked` + reason.
- [ ] **E2.** `STATE.json` güncelle: current_worklog, açık taskler, son dosya durumları
      (değişen dosyaların yolu+hash), son istek, test durumu, engeller, updated_at.
- [ ] **E3.** `MEMORY_CARD.md` tazele: `memory_snapshot.py` (STATE+tasks+worklog kuyruğundan).
- [ ] **E4.** PUSH (son durum dosyaları).
- [ ] **E5.** `SESSION_RECEIPTS/<tarih>_<konu>.md` yaz:
      ne yapıldı / kanıt linkleri / açık taskler / sıradaki modül + fabrika metrikleri
      (kapanan modül, kanıt/modül, push sayısı, amnezi=0, tekrar üretim=0).
- [ ] **E6.** Push + kullanıcıya 6 satırlık özet.

---

## Zor durumlar

| Durum | Yapılacak |
|---|---|
| Sandbox geri döndü | son push'ı çek, worklog son satırlarıyla diff, kaybı tespit et, sadece kaybı üret |
| Token 401/403 | token gerekmeyen modüller → bitir; STATE'e "token bekleniyor: <iş>" |
| Aynı araç 2 kez çöktü | worklog'a !HATA yaz, alternatif yol, kullanıcıyı bekleme |
| Kullanıcı yeni tasklist verdi | `task_state.py merge` — eskiler silinmez |
| Worklog 500+ satır oldu (rotasyon atlandı) | acil rotate; sonra protokole dön |
| "Bitti ama kanıt yok" hissi | bitti DEĞİL: blocked yaz, kanıt üret, sonra kapat |
| Kullanıcı link verdi (yandex/drive/github) | aynı mesajda: indir → sha256 → /assets → FILE_REGISTRY → push |
