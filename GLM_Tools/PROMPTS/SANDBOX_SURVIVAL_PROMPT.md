# SANDBOX SURVIVAL PROMPT — sandbox kırılması / silinmesi / geri dönüşüne karşı

> **Kullanım:** GOD MOD master promptuna ek olarak; yeni sistem kurulumu, uzun derleme,
> sandbox'ın yenilenme ihtimali yüksek işlerde mesaja dahil et.

```
[SANDBOX KALICILIK KURALLARI]

1. /tmp YASAK BÖLGE: Deliverable ve proje dosyası /tmp'de durmaz. /tmp yalnızca bir dakikalık
   ara çıktı içindir; tüm iş proje klasöründe ve repoda yaşar.

2. OTURUM BAŞI RİTÜELİ: (a) projeyi klonla/çek, (b) STATE.json + güncel worklog'u oku,
   (c) sandbox boş görünüyorsa "yeni mi başlıyoruz?" deme — ÖNCE STATE'ten geri yükle;
   gerçekten yoksa kullanıcıya sor.

3. PUSH RİTİMİ: Modül bitti = push. Commit formatı:
   [modül] ne-yapıldı + test-sonucu + kanıt-yolu
   Örnek: [mutasyon] junk-generator v2 + 12/12 test PASS + proofs/mutasyon/2026-11-26_x.txt

4. TOKEN HİJYENİ: Token mesajdan/env'den okunur; dosyaya, loga, commite, echo'ya YAZILMAZ.
   401/403 → token gerektirmeyen işleri bitir, STATE'e "token bekleniyor" düş.

5. UZUN İŞ PARÇALAMA: 40+ dakika sürecek işi 25-35 dk'lık modüllere böl; her modül kendi
   push'uyla kapanır. Yarım kalma riskini "oturum bazından" "modül bazına" indir.

6. GERİ DÖNÜŞ PROTOKOLÜ: Sandbox geri döndüyse kayıp = en fazla son push'tan sonraki 1 modül.
   Önce GitHub'taki durumu çekip worklog'un son satırlarıyla karşılaştır; FARKI tespit et,
   hiçbir şeyi körlemesine yeniden üretme. (Geçmişte 46.400 araç çağrısının ~%70'i tam da
   bu yüzden tekrar üretilmişti — bu sayı bir daha yaşanmasın.)

7. DERLEME ÇIKTILARI: Derlenen ikili + sembol + log üçlüsü repoya girer (büyükse Releases'e
   asset olarak); "derledim, sandbox'ta duruyor" teslim sayılmaz.

8. BEKLEYEN İNDİRME KUYRUĞU: İndirilemeyen linkler WAITING_DOWNLOADS.md'ye (url + neden)
   yazılır; sonraki oturum ilk iş kuyruğu temizler.
```

---

## Arka plan (neden bu kurallar var)

Sohbet dökümlerinden tespit edilen gerçek olaylar:
- XProtect 1.2.0 tamamen kayboldu (sandbox ölümü; 8 "restart" turu atıldı).
- SIMULATOR_UI v2 kodu iki kez silinip sohbet bağlamından satır satır geri kazanıldı.
- cp300 zip'i bayat exe'lerle teslim edildi (aynı hata 3 kez).
- Yandex/Drive linkleri bir sonraki mesajda ölü bulundu ("artık yok" denildi).

Bu dört olayın ortak kökü: **iş, kalıcı olmayan bir yerde yaşadı**. Yukarıdaki 8 kural her birini
tek tek kapatır (sırasıyla: 1, 3+5, 3+7, 8).
