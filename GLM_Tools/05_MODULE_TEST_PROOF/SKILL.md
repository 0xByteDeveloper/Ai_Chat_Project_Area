# SKILL — MODULE + TEST + PROOF (modül + test + kanıt)

**Sorun:** AI "%92 tamamlandı" diyor → sen sahada test edince "aynı bok" çıkıyor.
**Kök neden:** "Bitti" tanımı yok; AI kendi yazdığı testten geçince tamam sanıyor;
kanıt artifact'i üretilmiyor; eksik iş "honest notes / next steps" olarak proza dökülüyor.

**Tanım (Definition of Done):** Bir modül ancak şu ÜÇLÜ tamamsa bitmiştir:

```
MODÜL = kod + test + kanıt
  kod    : modules/<modül>/ altında, push'lanmış
  test   : tests/test_<modül>.* — geçen çıktısı kayıtlı (n/n PASS)
  kanıt  : proofs/<modül>/<tarih>_<saat>_<ad>.txt — komut + çıktı + hash
```

**Kanıtsız modül = bitmemiş modül.** "Next steps / honest notes / bu oturumda
yapamadım" dumping'i YASAK: eksik iş `tasks.json`'a `blocked + reason` yazılır, proza değil.

---

## 1) Klasör düzeni

```
modules/<modül>/          çalışma alanı (kaynak)
tests/                    test dosyaları
proofs/<modül>/           tarihli kanıt dosyaları
PROOF.md                  tüm kanıtların İNDEKSİ (her satır: modül, tarih, neyi kanıtlar, dosya)
```

## 2) Kanıt dosyası standardı (proofs/<modül>/...)

```
=== KANIT: <modül> ===
Tarih    : 2026-11-26 14:20
Modül    : mutasyon
Task     : T-004
Komut    : ./bin/test_junkgen --all
Ortam    : (OS/toolchain sürümü)
SONUÇ    : 12/12 PASS
Ek kanıt : sha256(çıktı)=..., boyut=..., histogram karşılaştırma tablosu
Yorum    : junk_rate=0.35 ile 3.9.4 profil %92 yakınlık
```

Kanıt ne olabilir: test çıktısı, benchmark tablosu, derleyici logu, diff, ekran görüntüsü,
hash listesi, saha çıktısı (oyun içi log). **Ne olamaz:** "çalıştığına eminim" cümlesi.

## 3) Test standardı

- Testi YAZMAYAN biri de doğrulayabilsin (Denetçi hattı bunu yapar — bkz. 01).
- Kırmızı-yeşil: modül kodu olmadan testin neden fail olması gerektiği bilinir;
  eklendikten sonra PASS olur. "Hep geçen test" kanıt sayılmaz.
- Saha kritik işlerde (XProtect gibi): sandbox testi + kullanıcı sahada doğrulayana kadar
  task `doing` kalır, `done` olmaz; kullanıcı onayı not edilir.

## 4) Komutlar

```bash
# modül iskeleti (modules/ + tests/ stub + proofs/ klasörü):
python GLM_Tools/05_MODULE_TEST_PROOF/module_test_proof.py new-module mutasyon

# kanıt kaydı (dosyayı kopyalar + PROOF.md'e indeksler):
python GLM_Tools/05_MODULE_TEST_PROOF/module_test_proof.py prove mutasyon \
    --file /path/to/cikti.txt --note "12/12 PASS, histogram %92 yakınlık" --task T-004

# DENETİM (her oturum sonunda + CI'da):
python GLM_Tools/05_MODULE_TEST_PROOF/module_test_proof.py audit --root .
# exit 1 = kanıtsız 'done' task var → oturum kapatılamaz
```

## 5) PROOF.md indeks formatı

```
| Modül | Tarih | Task | Neyi kanıtlar | Dosya |
|---|---|---|---|---|
| mutasyon | 2026-11-26 | T-004 | 12/12 test PASS + histogram | proofs/mutasyon/2026-11-26_1420_junkgen.txt |
```

Bu tablo SESSION_RECEIPT'in ve haftalık fabrika metriklerinin (kanıt/modül oranı) kaynağıdır.
