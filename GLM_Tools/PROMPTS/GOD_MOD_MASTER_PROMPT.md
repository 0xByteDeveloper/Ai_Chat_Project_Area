# GOD MOD MASTER PROMPT — her mesajın başına yapıştır

> **Kullanım:** [PROJE] ve [REPO] alanlarını doldur.
> Mesaj limiti darken → sadece BÖLÜM 2 (kısa sürüm) kullan; kritik/uzun işlerde BÖLÜM 1.

---

## BÖLÜM 1 — TAM SÜRÜM

```
[GOD MOD / KALICI PROTOKOL — proje: PROJE_ADI | repo: Ai_Chat_Project_Area/GLM_Tools]

1. BAŞLANGIÇ: İşe başlamadan sırayla oku: STATE.json → güncel WORKLOG_(n).md (INDEX.md gösterir)
   → tasks.json. Bunlar yoksa/boşsa: kullanıcıya bootstrap isteği sor, tahminle doldurma.
   Okumadan plan üretme; projeye özel repoları STATE.json'daki active_repo listesinden al.

2. KALICILIK (YAŞAYAN GITHUB): Her biten modül için aynı adımda: kod → test → kanıt → git push.
   "Sonda toplu push" YASAK. Sandbox geri dönerse kayıp en fazla 1 modül olmalı.

3. TASK DİSİPLİNİ: Yeni tasklist mevcut açık tasklerle BİRLEŞTİRİLİR (ID'ler T-### korunur,
   hiçbir açık task silinmez/unutulmaz). Bir task sadece KANITLA kapanır: "test çıktısı +
   /proofs/<modül>/ dosyası". "Next steps / honest notes / bu oturumda yapamadım" dumping YASAK —
   eksik iş tasks.json'a blocked + reason olarak yazılır, proza dökülmez.

4. WORKLOG: Her adım WORKLOG_(n).md'ye 1-3 satır append edilir. ~200 satır dolunca:
   eski worklog sıkıştırılıp WORKLOG_ARCHIVE_(n)_OZET.md olarak arşivlenir, WORKLOG_(n+1).md
   açılır, INDEX.md ve STATE.json güncellenir, push edilir.

5. MODÜL+TEST+KANIT: Her modülün /proofs/<modül>/ klasöründe tarihli kanıt olur (komut çıktısı,
   log, hash, ekran görüntüsü). Kanıtsız modül = bitmemiş modül; "tamamlandı" denmez.

6. DOSYA KALICILIĞI: Kullanıcının verdiği her link/dosya AYNI mesajda indirilir; sha256 + boyut
   + içerik tanımı FILE_REGISTRY.md'ye yazılır, dosya /assets'e mirror'lanır, push edilir.
   Sonraki mesajda "dosya yok artık" denmez — önce FILE_REGISTRY ve /assets kontrol edilir.

7. OTURUM SONU: STATE.json güncelle (current_worklog, açık taskler, son dosya durumları, son
   istek, test durumu, engeller) + MEMORY_CARD.md tazele (memory_snapshot.py) + push +
   SESSION_RECEIPT: (a) ne yapıldı (b) kanıt linkleri (c) açık taskler (d) sıradaki modül.

8. HATA PROTOKOLÜ: Aynı araç 2 kez üst üste başarısızsa worklog'a yaz, alternatif yola geç,
   kullanıcıyı bekleme. Token 401/403 verirse: token gerektirmeyen tüm modülleri bitir,
   STATE'e "token bekleniyor: <hangi iş>" yaz.

9. BÜTÜNLÜK: Bilmediğini varsayma — ölç, doğrula, kanıtla. Uydurma sayı/tarih/durum yok.
   "Muhtemelen tamam" diye kapanmaz; test çıktısı olmadan kapanmaz.

10. PARALELLİK: Birbirinden bağımsız modüller ayrı hesaplarda/ajanlarda paralel yürür;
    her hesap kendi ürettiği modülü KENDİ push'lar (STATE çakışmasını önlemek için farklı
    modül klasörlerinde çalışırlar).
```

---

## BÖLÜM 2 — KISA SÜRÜM (her mesaja yapıştır, 6 satır)

```
[GOD MOD: (1) STATE.json+tasks.json+güncel worklog'u oku, okumadan planlama. (2) Her biten
modül: kod+test+kanıt+push aynı adımda, sonda toplu push yok. (3) Yeni tasklist ESKİSİYLE
birleşir, açık task unutulmaz; task kanıtsız kapanmaz, eksikler tasks.json'a blocked yazılır.
(4) Worklog'a her adımı 1-3 satır yaz; 200 satırda sıkıştır+WORKLOG_(n+1)+INDEX+STATE+push.
(5) Verdiğim link/dosyayı aynı mesajda indir+sha256+/assets mirror+FILE_REGISTRY+push.
(6) Sonda: STATE+MEMORY_CARD tazele, push, SESSION_RECEIPT ver. Uydurma yok, ölç+kanıtle.]
```

---

## Neden bu prompt "kalıcı"?

GLM'in bağlam sıkıştırması eski mesajları özetledikçe görev tanımı yozlaşır. Bu blok **her
mesajın en üstünde yeniden girildiği için** sıkıştırma sırasında asla kaybolmaz — görev tanımı
her turda tazelenir. 6 satırlık kısa sürüm, sıkıştırmaya giren ilk 500 token içinde kalır.
