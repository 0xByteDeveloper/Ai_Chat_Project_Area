# SKILL — GOD MOD (10x) Stratejisi

**Amaç:** AI'ın aynı zaman bütçesinde 10 kat iş çıkarması — kalite düşmeden.
**Yanlış tanı:** GOD MOD = AI'a "daha çok çalış, daha uzun uğraş" demek.
**Doğru tanı:** GOD MOD = aynı saatte **daha çok KANITLI modül kapatmak**.

---

## 1) 10x'in 3 motoru

| # | Motor | Ne demek | Ölçüt |
|---|---|---|---|
| M1 | **Doğrulama sıkılığı** | AI kendi yazdığı testten geçince "bitti" DEMEZ; bağımsız kanıt (saha çıktısı, benchmark, diff) ister | kanıt/modül oranı = 1.0 |
| M2 | **Parça boyutu** | 40 dk'lık "dev işler" değil, 25-35 dk'lık kapatılabilir modüller; her modül kendi push'uyla kapanır | ortalama modül süresi ≤ 35 dk; push gecikmesi ≤ 5 dk |
| M3 | **Paralellik** | Bağımsız modüller farklı hesaplarda/ajanlarda eşzamanlı; 3 hesap = 3 uzman hattı (Araştırıcı / Uygulayıcı / Denetçi) | paralel modül oranı ≥ %40 |

Bu üç motor **birlikte** çalışır: paralel + parçalı ama kanıtsız üretim = "aynı bok, 10 kat
hacimli" (geçmişte yaşandı: %92 tamam → sahada çürüdü). Motorlar GLM_Tools'ün diğer
modülleri tarafından mekanik olarak zorlanır:

```
M1 → 05_MODULE_TEST_PROOF (kanıtsız task kapanamaz)
M2 → 03_WORKLOG_MANAGER + 02_LIVING_GITHUB (modül bitimi = push)
M3 → 01'deki rol ayrımı + GOD MOD master prompt kural 10
```

## 2) SSS TIER olgunluk merdiveni

| Seviye | Tanım | Ayırt edici özellik |
|---|---|---|
| D | Sohbet içi üretim | iş sandbox'ta yaşar, chat kapanınca ölür |
| C | Geçici kalıcılık | tmp/zip taşıma; AI hatırlamayınca kayıp |
| B | Push disiplinli | iş GitHub'da; ama tasklist amnezisi + worklog dolması sürer |
| A | Durumlü fabrika | STATE + tasks + worklog rotasyonu; yeni chat bootstrap ile devam eder |
| S | Kanıtlı fabrika | her modül test+kanıtla kapanır; audit otomatik; "tamamlandı illüzyonu" ölür |
| **SSS** | **Kendini ölçen fabrika** | her oturum SESSION_RECEIPT üretir; metrikler (kanıt/modül, push gecikmesi, amnezi olayı=0) izlenir; kırmızı-takım (Denetçi hattı) sürprizleri yakalar |

**GLM_Tools v1.0 = A+S seviyesini mekanikleştirir.** SSS için kalan tek şey: metrikleri
haftalık toplayıp trendini görmek (bkz. aşağı §4 ve SESSION_RECEIPTS/).

## 3) Rol ayrımı (3 hesap = 3 uzman hattı)

| Hesap | Rol | Çıktı |
|---|---|---|
| Hesap 1 | **Araştırıcı** — kaynak tarama, algoritma seçimi, prototip | RESEARCH notları + karar önerileri (worklog'a !KARAR satırları) |
| Hesap 2 | **Uygulayıcı** — modül kodu + test + kanıt + push | kapanan T-### taskler |
| Hesap 3 | **Denetçi (kırmızı takım)** — Uygulayıcının "bitti" dediğini kırmaya çalışır | KIRMIZI_RAPOR (başarısız saldırı/bulgu listesi) |

Denetçi hattı GAME CHANGER'dır: "AI kendi testinden geçti" sorununu kökten çözer, çünkü testi
**yazmayan** bir hat, ürünü kırmaya çalışır.

## 4) Fabrika metrikleri (her oturum sonunda toplanır)

```
SESSION_RECEIPT şablonuna yaz:
- kapanan_modül_sayısı:        n
- kanıt_üretilen_modül:        n_k  (hedef: n_k = n)
- push_sayısı / son_push_dk:   p / gecikme (hedef: gecikme ≤ 5 dk)
- amnezi_olayı:                0 olmalı (kaybolan task/dosya sayısı)
- tekrar_üretim:               0 olmalı (sandbox kaybından yeniden üretilen iş)
- kırmızı_takım_bulgusu:       k (bulgu = iyileştirme fırsatı, hata değil)
```

Haftalık: bu sayılar `SESSION_RECEIPTS/` klasöründen okunup trend grafiğine dökülür
(09_HTML_REPORT_STYLE ile). Trend kötüleşiyorsa MOTORLAR (M1-M3) hangisi gevşedi → ona müdahale.

## 5) Oturum akışı (özet — detay: god_mod_session_protocol.md)

```
START: STATE.json oku → worklog(n) son 40 satır → tasks.json açık taskler → STATE.active_repo klonla
LOOP : [plan 3 modüllük] → [modül: kod → test → kanıt → push] → [worklog append] → tekrar
END  : tasks reconcile → STATE.json → MEMORY_CARD tazele → push → SESSION_RECEIPT
```

## 6) Başarısızlık modları → hangi yapı kapatıyor

| Geçmişte yaşanan | Kök neden | Kapanan yapı |
|---|---|---|
| "testleri geçti, sahada çürüdü" | doğrulama AI-içi | 05 (kanıt) + Denetçi hattı |
| 8 restart turu, iş kaybı | push sona bırakıldı | 02 (modül sonu push) |
| x4'ün 3 task'i x5'te kayboldu | tasklist değiştirildi | 04 (birleştirme kuralı) |
| "worklogu okumuyor, son kısmı okuyor" | worklog tek parça ve şişkin | 03 (rotasyon + özet) |
| yeni chat = sıfır | hafıza yalnız bağlamda | 07 (MEMORY_CARD + bootstrap) |
| yandex linki ertesi gün ölü | geçici kaynak | 08 (aynı-mesajda mirror) |
| token unutuldu / push yapılmadı | talimat mesajda kaybolmuş | PROMPTS (her mesajda kalıcı blok) |
