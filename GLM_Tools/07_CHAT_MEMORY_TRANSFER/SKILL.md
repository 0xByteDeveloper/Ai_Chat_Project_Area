# SKILL — CHAT MEMORY TRANSFER (yeni chate hafıza taşıma)

**Sorun:** Bir sohbette birkaç düzine mesaj sonra AI "proje ruhuna" giriyor (terimleri,
tercihleri, kararları biliyor; "o dosya" deyince anlıyor). Yeni chat açınca bu SIFIR.
Her seferinde "şunu şunu yaptık" diye uzun prompt yazmak zorunda kalıyorsun.

**Teknik gerçek (önemli — yanlış modeli düzelt):** Modelin **ağırlıkları** (weights/bias)
sohbet başına GÜNCELLENMİYOR. Chat ürünlerinde güncellenen şey bağlam penceresi; senin
hissettiğin "yatkınlık" = **bağlam-içi öğrenme** (in-context learning). Bu iyi haber:
bağlam serileştirilebilir. Ağırlıkları taşıyamazsın ama **etkisini** taşıyabilirsin —
çünkü o etki zaten bağlamdan geliyor.

**Çözüm:** MEMORY_CARD.md — projenin "kimlik kartı". Oturum sonunda otomatik üretilir
(`memory_snapshot.py`), yeni chat başında bootstrap promptuyla yüklenir.

---

## 1) MEMORY_CARD bileşenleri (≤ 200 satır disiplini)

```
1. PROJE KİMLİĞİ      proje adı, repo(lar), dil, toolchain, aşama
2. KALINAN YER        STATE.json özeti: current_worklog, phase, last_request
3. AÇIK TASKLER       tasks.json'daki todo/doing/blocked (T-### + başlık + engel)
4. KARARLAR           son 2 worklog döneminden !KARAR satırları (özet)
5. DOSYA DURUMU       değişen kritik dosyalar (yol + tarih, hash)
6. KULLANICI TERCİHLERİ  GOD MOD çalışma tarzı, HTML rapor teslimi, Türkçe,
                         "kanıtsız bitti demeyiz", kısa-direct ton, 3 hesap stratejisi…
7. SÖZLÜK             proje terimleri: XProtect, Maze, i4mconsoleloader, rea(?), 0xd7600,
                         UniversalMVPUIAlgorithm, GOD MOD, worklog+str(n+1)…
8. SIRADAKİ MODÜL     net tek cümle
```

**Boyut kuralı:** Kart ≤ 200 satır. Detay worklogta/arşiv özetlerinde yaşar; kart yalnız
yön gösterir. Şişen kart = sıkışan bağlam = yine amnezi.

## 2) Akış

```
OTURUM SONU (END protokolü E3):
  python GLM_Tools/07_CHAT_MEMORY_TRANSFER/memory_snapshot.py --root <proje>
  → STATE + tasks + worklog kuyruğu + REQUESTS kuyruğundan MEMORY_CARD.md üretilir
  → push

YENİ CHAT AÇILIŞI:
  1) GLM_Tools/PROMPTS/NEW_CHAT_BOOTSTRAP_PROMPT.md doldur → ilk mesaj olarak gönder
  2) AI: STATE → worklog son 40 satır → tasks → MEMORY_CARD → FILE_REGISTRY okur
  3) 6 satırlık durum raporu verir → kaldığı modülden devam eder
```

## 3) Kullanım

```bash
# kart üret (yazmak yerine önce görmek için --dry-run):
python memory_snapshot.py --root /yol/proje --dry-run
python memory_snapshot.py --root /yol/proje            # MEMORY_CARD.md yazar

# parametreler:
#   --tasks tasks.json --state STATE.json --worklog WORKLOG_3.md --requests REQUESTS.md
#   (dosya adları STATE/INDEX'ten otomatik bulunur; yoksa parametreyle ver)
```

## 4) Neden prompt yeterli değil de hem klasör hem prompt var

- **Prompt (bootstrap):** AI'a "neyi okuyacağını" söyler — her yeni chatta sen yapıştırırsın.
- **Klasör (araç + şablon):** okunacak İÇERİĞİ her zaman güncel üretir — AI'ın kendisi
  oturum sonunda `memory_snapshot.py` çağırır, senin elin hiç gitmez.
- İkisi birlikte: "ben unuturum, sistem unutmaz" prensibi. Senin de dediğin gibi:
  "her mesajda kontrol etmesi için komut prompt vermek yerine GLM_Tools'a yapı ekle."

## 5) Sık yapılan hatalar

| Hata | Sonuç | Doğrusu |
|---|---|---|
| Kartı elle yazıp güncellememek | bayat hafıza → yanlış devam | otomatik snapshot (E3) |
| Karta tüm worklogu kopyalamak | kart 1000+ satır → sıkışma | ≤ 200 satır, detay arşivde |
| Sadece prompt, dosyasız | token limitlerinde biçim bozulur | dosya + prompt birlikte |
| Yeni chatta bootstrap atlamak | "sıfırdan başla" döngüsü | her yeni chat ilk mesajı bootstrap |
