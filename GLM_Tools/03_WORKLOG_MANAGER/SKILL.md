# SKILL — WORKLOG MANAGER (worklog + str(n+1))

**Sorun:** Worklog tek dosya olarak şişince AI sadece son kısmı okuyor; baştaki kararlar,
hatalar ve bağlam kayboluyor. Dolunca da "okumuyor" → amnezi.

**Çözüm:** Worklog döner bir kalasın (rotating ledger):
`WORKLOG_1.md → (200 satır) → sıkıştır → WORKLOG_2.md → ...`
INDEX.md güncel worklog'u gösterir; STATE.json hangi worklogda kaldığını bilir.

---

## 1) Dosyalar (proje repo kökünde)

```
WORKLOG_1.md, WORKLOG_2.md, ...          güncel worklog (satır limiti: 200)
WORKLOG_ARCHIVE_1.md, ...                rotasyona uğrayan TAM içerik (tarihçe)
WORKLOG_ARCHIVE_1_OZET.md, ...           sıkıştırılmış özet (AI'ın sonra okuyacağı)
INDEX.md                                  tüm worklogların listesi + güncel işaretçisi
```

## 2) Append formatı (her iş adımı 1-3 satır)

```
- 2026-11-26 14:05 [mutasyon] junk-generator v2 yazıldı; 12/12 test PASS; proof: proofs/mutasyon/...
- 2026-11-26 14:20 !KARAR mutation yoğunluğu parametrik: junk_rate=0.35 (3.9.4 histogramına göre)
- 2026-11-26 14:25 !HATA linker LNK2019 scipy hatası → çözüm: derleme sırası değişti
- 2026-11-26 14:30 !AÇIK unicorn'da TEB simülasyonu thread local mi olmalı?
```

Etiketler: `!KARAR` (verilen karar + neden) · `!HATA` (hata + çözüm) · `!AÇIK` (açık soru).
Bu üç etiket **asla sıkıştırmada atılmaz** — kartların belleğidir.

## 3) Rotasyon protokolü (eşik: 200 satır / 8 KB)

`python GLM_Tools/03_WORKLOG_MANAGER/worklog_manager.py rotate` şunları yapar:

1. Güncel `WORKLOG_n.md` → `WORKLOG_ARCHIVE_n.md` (tam içerik korunur)
2. `WORKLOG_ARCHIVE_n_OZET.md` üretilir: hedefler + !KARAR/!HATA/!AÇIK satırları + son 10 satır
   (özet ≤ 60 satır → AI sonraki oturumlarda ÖZETİ okur, 500 satırlık geçmişi değil)
3. `WORKLOG_(n+1).md` açılır (üstbilgi + önceki özete bağlantı)
4. `INDEX.md` güncellenir (yeni satır + güncel işaretçisi)
5. `STATE.json` `current_worklog` alanı arttırılır
6. Push edilir (02 disiplini)

## 4) Okuma kuralları (AI için — hafıza yönetimi)

| Ne zaman | Ne okunur |
|---|---|
| Oturum başı | `INDEX.md` → güncel WORKLOG_(n) son 40 satırı |
| Rotasyon sonrası yeni oturum | önceki `WORKLOG_ARCHIVE_(n)_OZET.md` + güncel worklog |
| "Neden böyle yapmıştık?" sorusu | ilgili arşivin ÖZETİNDE `!KARAR` ara |
| Karar verirken | son 2 arşiv ÖZETİNDEki !KARAR satırları (çelişkiden kaçın) |

## 5) Komutlar

```bash
python GLM_Tools/03_WORKLOG_MANAGER/worklog_manager.py init [--root .]
python GLM_Tools/03_WORKLOG_MANAGER/worklog_manager.py status [--root .]
python GLM_Tools/03_WORKLOG_MANAGER/worklog_manager.py append "metin" [--module mutasyon] [--tags "karar"] [--root .]
python GLM_Tools/03_WORKLOG_MANAGER/worklog_manager.py rotate [--max-lines 200] [--root .]
```

`status` çıkışı: güncel worklog, satır sayısı, eşiğe kalan satır — oturum LOOP'unun L8
adımında her modül sonrası kontrol edilir; `%80+` → bir sonraki modül öncesi rotate.
