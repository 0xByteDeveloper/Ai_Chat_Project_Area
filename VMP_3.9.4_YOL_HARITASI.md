# VMP 3.5.1 → 3.9.4 — GERÇEK ÇIKIŞ YOL HARİTASI

**Bu belge x_vmp.1 / x_vmp.2 / x_vmpPlus sorularının cevabıdır** (kullanıcı itirazları üzerine
yeniden yazıldı; önceki "parite bırak" hükmünün düzeltilmiş, ölçülebilir hali).

---

## 0) İtirazlara doğrudan cevap

### x_vmp.1) "İnternette/GitHub'da devirt/unpack yöntemleri varsa, algoritmalar anlaşılır ve korumamıza eklenebilir mi?"
**EVET — ve bu tam da profesyonel koruma geliştirmenin nasıl çalıştığı.** Her açık (public)
saldırı aracı, savunmanın ÜCRETSİZ kalite güvence girdisidir. Canlı doğrulanmış envanter
(2026-11-26, GitHub arama):

| Araç/Repo | Teknik | Söylediği şey |
|---|---|---|
| `can1357/NoVmp` | VTIL tabanlı statik devirtualizer (VMP x64 3.x) | statik analizle VM bytecode'u x86'a lift edilebiliyor |
| `0xnobody/vmpattack` | VMP→VTIL lifter (angr/symbolic) | handler semantiği sembolik yürütmeyle çözülebiliyor |
| `JonathanSalwan/VMProtect-devirtualization` | Triton ile otomatik deobfuscation | iz simplification + symbolic execution zinciri |
| `YuroGod/VMPStaticUnpacker` | **statik unpacker, 3.9.5 destekli** (2026-07 aktif) | **en yeni sürümler bile statik çözülüyor** → senin iddianın kanıtı |
| `notsnakesilent/VMPStatic` | statik unpacker (VMP 1.x–3.x) | sürüm bağımsız yaklaşım |
| `BUnipendix/AnimeNoVMP` | NoVmp'in harden edilmiş fork'u (2026-10) | alan hâlâ aktif gelişiyor |
| `gmh5225/titan-1`, `wallds/NoVmpy`, `whowould/VMProtect-Unpacker`, `DarkBullNull/VMP.NET-Kill` | türev yaklaşımlar | yöntem çeşitliliği |

**Sonuç:** Sürüm ne kadar yükselirse yükselsin saldırı yüzeyi kapanmıyor (3.9.5'i çözen
araç var). Demek ki geliştirme modeli şu döngü olmalı:
**SALDIRI ENVANTERİ → ZAFİYET ANALİZİ → SAVUNMA HAMLESİ → ÖLÇÜM → tekrar.**
(Aşama A0.5 + A5 bunu mekanikleştirir.)

### x_vmp.2) "AI (GLM 5.3) bunu anlayacak ve kodlayacak güçte — veri setinde ya da yöntem bilgisinde."
**Kısmen katılıyorum — güç var, ama doğru kullanım şekliyle:**
- **Evet:** Sembolik yürütme, iz analiz, handler clustering, opcode map reconstruction gibi
  yöntemler eğitim dağıtımında mevcut; daha önemlisi SEN DAHA KANITLADIN: kendi
  `MVP_GOD_SSS_TIER_DECOMPILER`'ın PDB ile %48,5 devirt çözümü (Ghidra 12.2 headless: %35,4).
  AI bunu "yapabilir mi" sorusu değil, senin repounda DURAN bir sonuç.
- **Dürüst sınır:** 3.9.4'e "çıkış" tek bir 40 dakikalık oturumun işi değil; devasa bir C++
  kod tabanını tek bağlamda taşımak sıkıştırma altında erir. Doğru model: **AI mimar + AI
  kırmızı takım + AI sürücü**, insan derleme döngüsü, ölçüm odaklı sprint'ler (aşağıdaki
  aşamalar tam bu yüzden 25-35 dk'lık modüllere bölünmüş, GLM_Tools disipliniyle push'lu).

### Önceki hükmün düzeltmesi
"3.9.4 birebir parite gerçekçi değil ve gereksiz" → **Yarı yanlıştı.** İki parite türü var:
- **Parite-A (çıktı profili):** boyut/section/histogram — *mekanik olarak mümkün ve ölçülebilir*
  (motorları aşağıda). "Gereksiz" değil; GAUGE (ölçer) olarak değerli.
- **Parite-B (direnç profili):** bilinen saldırı sınıflarına dayanma — *asıl hedef*.
Doğru hedef ikisi birden: **A'yı ölçer olarak kullan, B'yi kalite olarak kovala.**

---

## 1) Önce eski hesap kapansın: neden 13kb → 118kb? (x1.4.1 / x1.4.3)

118kb "beceriksizlik" değil, **eksik katman sinyali**. Gerçek 3.5.1'in 3mb'lik çıktısı tek
bir şeyden değil, katman yığından gelir. Olası nedenler (Aşama 0-1 ölçümüyle AYRIŞTIRILACAK —
tahminle kalmayacağız):

| # | Hipotez | Nasıl anlaşılır |
|---|---|---|
| H1 | Yalnız mutation çalıştı, virtualization seçilmedi/handler'lar elendi | korunan region'ın disasm'ında VM enter/exit kalıbı aranır |
| H2 | Handler seti eksik taşındı → az handler + çok junk | handler tablosu sayımı (3.5.1 referansıyla diff) |
| H3 | Packer katmanı devrede değil (gerçek 3mb'ın ~%60'ı pack+şifreli section'lardır) | section listesi karşılaştırması |
| H4 | Import/resource şifreleme katmanı yok | IAT/section analizi |
| H5 | Alignment/padding politikası farklı | section boyut histogramı |

**Ölçmeden "yanlış kodladı" demek de "başarı" demek de yasak** (GLM_Tools kuralı). Aşama 0
bu tabloyu kanıta çevirir; H1-H5'ten hangileri gerçekse A2-A4 modülleri onları kapatır.

---

## 2) 8 Aşamalı plan — her aşama = modül + test + kanıt (GLM_Tools/05)

### A0 — Ölçüm Arenası (SÜPERKRİTİK; her şeyin ölçüsü buradan gelir)
- Girdi: `test_64.exe` (13kb, sabit referans — worklog'da !KARAR ile sabitlendi) + sabit
  fonksiyon seti (RVA 0xd7600 "MovePos" dahil).
- **3'lü harness:** aynı girdiyi (1) gerçek VMP 3.5.1 (2) gerçek VMP 3.9.4 (3) fork'umuzla
  koru → çıktıları aynı metrik tablosunda karşılaştır.
- Metrikler: çıktı boyutu · section tablosu (sayı/boyut/özellikler) · komut histogramı
  (mutation yoğunluğu) · handler sayısı + tablo boyutu · opcode uzayı genişliği · başlatma
  süresi · (sonra) unpacker davranışları.
- Çıktı: `KARSILASTIRMA_TABLOSU.html` (09 stili) + `GAP_LIST.md`.
- Kanıt: harness çıktı dosyaları (`proofs/a0-olcum/`).

### A0.5 — Saldırı Envanteri (yukarıdaki tablo → çalışır dokümana)
- Her aracı SANDBOX'TA ÇALIŞTIR (derle), kendi 3.5.1-çıktına ve 3.9.4-çıktına saldırt:
  hangisi ne kadar ilerledi? → `COUNTER_TECHNIQUE_MATRIX.md`
  (teknik | neyi sömürür | bizde işliyor mu | savunma hamlesi | durum).

### A1 — Delta Analizi (gerçek 3.5.1 ↔ gerçek 3.9.4 çıktı diff'i)
- Section bazlı diff, stub analizi, handler tablo boyutları, junk oranı, packer katman
  varlığı/yokluğu → `GAP_LIST.md`'yi somut farklara çevir: "3.9.4'te X section daha fazla,
  handler tablosu Y kat büyük, junk yoğunluğu Z").
- Kanıt: diff çıktıları + görsel histogram karşılaştırmaları.

### A2 — Mutation Motoru (boyutun ve histogramın ana motoru #1)
- Polimorfik junk üreteci: komut ikame tabloları, ölü-store ekleme, yığın jimnastiği,
  eşdeğer-jump zincirleri. `junk_rate` parametrik.
- Hedef: fork'un komut histogramı 3.9.4 profilinin ±%15'ine yakınsasın.
- Kanıt: A0 harness'ında histogram karşılaştırma tablosu (kanıt dosyası).

### A3 — Handler Seti + Yorumlayıcı (direncin ana motoru #1)
- Opcode uzayını genişlet (daha çok handler ailesi), handler chaining, dispatch tablosu
  build-başı anahtarla şifreli.
- **Kill-shot:** build başına **semantik eşdeğer handler üretimi** (add işlemini N farklı
  yol: sub-neg / xor-rotate / lea zinciri...). NoVmp/vmpattack sınıfı araçlar İMZA TAŞIMAYA
  çalışır; imza alanı her build'te değişince statik lifting maliyeti katlanır. Bu, VMP'nin
  bile tam yapmadığı hamle — senin farkın burada olabilir.
- Kanıt: aynı saldırı aracı önceki build'i X'te çözüyordu, yeni build'te çözemesin (A5 ölçer).

### A4 — Katmanlar (boyutun ana motoru #2: 13mb → 25-30mb burada kapanır)
- Pack katmanı + import obfuscation + resource şifreleme + anti-debug/anti-attach seti.
- Kanıt: GAP_LIST'teki boyut farkı %20'nin altına insin + Tools'a dayanıklılık (A5).

### A5 — Kırmızı Takım Döngüsü (kalitenin kalbi; Denetçi hesabı burada çalışır)
- Süit: kendi devirt aracın + NoVmp + vmpattack-türevi + Unicorn emülatör yaklaşımı +
  statik unpacker'lar. Her koruma sürümü için SKOR KARTI:
  `S1 statik S2 dinamik-iz S3 sembolik-lift S4 emülasyon S5 katman-kırma` → her sınıfta
  "kaç denemede ne kadar ilerledi".
- Her tur: saldırı sonucu → zafiyet notu → yama (A2/A3/A4'e task aç) → yeniden ölç.
- Kanıt: skor kartı trendi (her sürümde skor düşmeli = daha dirençli).

### A6 — Maze Heterojen Katmanlama (senin differentiator'ın — sektörde nadir)
- Zincir: fonksiyon (örn. RVA 0xd7600 "MovePos") → VMP full ayar → çıktı ikilisi →
  Maze'e korumaya sok. Saldırgan TEK VM mantığını çözmek yetmez; iki FARKLI VM mimarisini
  ardışık kırması gerekir → maliyet çarpımı.
- Kanıt: A5 süitinin VMP→Maze çıktısında önceki skordan belirgin düşük performans göstermesi.

### A7 — Sürüm Kartı + Sürüm Disiplini
- XPROTECT sürümü = saldırı sınıflarına karşı dayanma tablosu (hangi sınıfa hangi tarih,
  hangi testte dayandık). "3.9.4 çıktık" demek yerine "S3 sınıfına 3.x dayanıklılık
  sağlandı (kanıt: proofs/a5/...)" demek — bu senin güvenilirliğini de kurar.

**Paralellik / süre:** A0 ve A0.5 birlikte başlar (Araştırıcı hesabı); A2+A3 paralel
(Uygulayıcı); A4 A2'den sonra; A5 sürekli (Denetçi); A6 A3-A4'ten sonra. 3 hesaplı paralel
sprint ile gerçekçi bütçe: **8-12 hafta** (25-35 dk'lık modüllerle, her modül push'lu).

---

## 3) "rea" deposu — dürüst durum raporu

- GitHub'da arandı (2026-11-26): `rea+vmprotect`, `vmprotect+3.9`, `vmprotect+unpack` vb.
  6 sorguda **"rea" adıyla VMP bağlamlı sonuç çıkmadı (0 hit)**.
- Olası sebepler: (1) ad farklı yazılıyor/kısaltma (2) private repo (3) silindi/taşındı
  (4) farklı platform.
- **İstek:** Tam URL'yi ver → doğrudan A1/A3 girdisi yapılır (roadmap'te `REA_KAYNAK` slotu
  hazır; `STATE.json → blockers`'a "rea URL bekleniyor" yazıldı, task T-006'ya bağlandı).

## 4) Register-anahtarlı talimat şifreleme — varyasyon kataloğu (senin fikrin, A3'ün parçası)

Fikir: `MessageCLAS1: push 0; push ecx; push edx; push 0; call MessageBoxA` dizisini öyle
şifrele ki **anahtar = o andaki register değerleri** olsun → statik disassembly anlamsızlaşır.
Tüm varyasyonlar:

| # | Varyasyon | Güç | Zayıf yön |
|---|---|---|---|
| V1 | Tek register anahtar (ecx) | basit, hızlı | tek nokta: ECX'i izleyen çözücü yeter |
| V2 | Çoklu register XOR bileşimi (ebp^ecx^edx) | izleme maliyeti artar | sabit kombinasyon imzalanabilir |
| V3 | Alt-register varyantları (al/ah/ax) | aynı anahtar uzayı, izleri karıştırır | anlambilir dar (8/16 bit) |
| V4 | **Stack-adres-duyarlı** (anahtar = f(esp/ebp konumu)) | **en güçlü: taşınırsa bozulur (relocation-kırıcı)** | konum bağımlılığı → test vektörü şart |
| V5 | Rolling anahtar (her N talimatta anahtar evrimi: k=f(k)) | dinamik izleme zorunlu kılar | performans maliyeti |

**Savunma tarafında en iyi kombinasyon:** V4 tabanlı + V5 evrim + anahtar üretim zinciri
VM handler'ının İÇİNE gömülü (böylece anahtarı bulmak = VM'i çözmek). Risk yönetimi:
yanlış register durumunda kod çömer → her korunan fonksiyona **derleme-zamanı test vektörü**
(canlı register snapshot'ıyla şifre çözümü doğrulanır, başarısızsa derleme hata verir).

## 5) Bu planın GLM_Tools ile bağlanması

Her aşama = modül (25-35 dk) → kod+test+kanıt+push (02/05) → worklog append (03) →
taskler T-### ile tasks.json'da (04) → her oturum sonunda SESSION_RECEIPT + MEMORY_CARD.
**Yani bu yol haritası bir "belge" değil, çalıştırılabilir bir tasklist'tir:** ilk mesajla
`task_state.py add` ile A0/A0.5 taskleri açılır, GOD MOD protokolü işletir.
