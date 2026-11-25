# SKILL — FILE PERSISTENCE (verdiğin dosyalar/linkler bir sonraki mesajda kaybolmasın)

**Sorun (gerçek olaylar):** Yandex Disk / Google Drive / geçici indirme linki veriyorsun;
AI aynı mesajda indiriyor, işliyor. Sonraki mesajda link süresi dolmuş ya da sandbox
dönmüş → AI "artık yok" diyor → iş baştan yapılıyor.

**Çözüm: 6 adımlı AYNI-MESAJDA mirror protokolü + kalıcı kayıt defteri (FILE_REGISTRY.md).**

---

## 1) Protokol (AI, kullanıcı link/dosya verdiği AN uygular — ertesi mesaj değil)

```
P1. İNDİR   : linki AYNI mesajda indir (indiremediyse → P6)
P2. DOĞRULA : boyut + sha256 + içerik tanımı (ne olduğu, kaç dosya/satır, format)
P3. MIRROR  : dosyayı proje reposunun /assets/ klasörüne kopyala
              (>50 MB → Releases asset veya git LFS; repoya değil)
P4. KAYDET  : FILE_REGISTRY.md'ye satır düş (aşağıdaki format)
P5. PUSH    : mirror + registry birlikte push'lanır (02 disiplini)
P6. KUYRUK  : indirilemeyen link → WAITING_DOWNLOADS.md'ye (url + neden + tarih);
              sonraki oturumun İLK işi kuyruğu temizlemek
```

**Altın kural:** "Dosya yok artık" DEMEK YASAK. Kullanıcı "şu dosyaya bak" dediğinde AI önce
`FILE_REGISTRY.md` + `/assets/` kontrol eder; mirror oradaysa linkin ölmesi önemsizdir.

## 2) FILE_REGISTRY.md formatı

```
| # | Veriliş | Kaynak | Dosya (mirror) | sha256 | Boyut | Ne olduğu | Not |
|---|---|---|---|---|---|---|---|
| 1 | 2026-11-26 R-012 | yandex disk linki (ölü) | assets/metin2_pvp_src.zip | ab12cd… | 84 MB | Metin2 PVP kaynak paketi, 3 proje | indirme P1'de yapıldı |
```

- Kaynak sütunundaki link ölmüş olsa bile satır asla silinmez (hangi kaynak neyin nereden
  geldiğinin tarihidir).
- sha256 sayesinde "bu zip bayat mı / değişmiş mi" sorusu her zaman cevaplanır
  (geçmişte bayat exe'lerle zip teslimi 3 kez yaşandı — bu sütun onu bitirir).

## 3) Kullanıcı (sen) için pratik notlar

- Link verirken süre uzat: Yandex'te indirme linkinin ömrünü maksimum yap.
- Aynı dosyayı tekrar vereceksen aynı ada ver → AI sha256 ile "aynı dosya mı, yeni sürüm mü"
  ayırt eder (registry'de karşılaştırır).
- Tokenli/kişisel linkler: AI önce indirir, registry'ye linki MASKELEYEREK yazar
  (tam tokenli URL yazılmaz — log sızıntısı olmasın).

## 4) Sandbox değişince (devir senaryosu)

Yeni sandbox + yeni oturum:
1. Repo pull → `/assets/` geri gelir (git zaten taşıyor).
2. AI dosyayı bulamazsa (repo dışıydıysa): FILE_REGISTRY'deki sha256+boyutla kullanıcıya
   "şu dosyayı tekrar ver, hash eşleşeceğini doğrulayacağım" der — körlemesine yeniden
   analiz ETMEZ.

## 5) Büyük dosya politikası

| Boyut | Politika |
|---|---|
| < 25 MB | direkt `/assets/` + git |
| 25-50 MB | `/assets/` + git (uyarı: repo şişer; düzenli arşiv düşün) |
| 50 MB-2 GB | GitHub **Releases asset** (tag: asset-<tarih>) + registry'ye sürüm+sha256 |
| > 2 GB | parçala (split -b 100m) → Releases; registry'ye birleştirme komutu + birleşik sha256 |
