# SKILL — HTML REPORT STYLE (analiz/rapor teslimlerinin ev stili)

**Neden HTML?** Kategorili, filtreli, açılır-kapanır bölümlü, linkli tek dosya: kafandaki
"her şey bir arada, kategorize, güncellenebilir" doküman isteğinin en iyi taşıyıcısı
(KAFA_HARITASI.html bu stile örnek). Tek dosya olduğu için GitHub'da açılır, offline taşınır.

## 1) Ev kuralları (hepsi ZORUNLU)

1. **Tek self-contained dosya** — CDN yok, harici font yok (sandbox offline dayanıklılığı).
   JS/CSS gömülü. Çıktı adı: `<KONU>_RAPOR_v<N>.html`.
2. **Koyu tema** — #0d1117 zemin, #e6edf3 metin, #58a6ff (bilgi) + #f78166 (vurgu/aksiyon)
   + #3fb950 (başarı) + #f85149 (risk) vurgu renkleri. (GitHub-dark paleti — uzun okumada
   yormuyor, "laboratuvar" hissi veriyor.)
3. **Sticky TOC** — sol tarafta sabit, aktif bölüm vurgulu, tıkla-git.
4. **Kart yapısı:** her soru/tespit = kart:
   `SORU/BAŞLIK → VERDICT (tek cümle, renk kodlu) → KANIT (sayı/dosya/örnek) → AKSİYON (checkbox)`.
5. **Açılır-kapanır detay** (`<details>`) — kart özeti kapalı, kanıt/örnek açılır.
6. **Filtre + arama** — üstte kategori çipleri + canlı metin araması (JS'siz sayfa ASLA;
   filtreler JS ile anında gizle/göster).
7. **Türkçe** — başlıklar, etiketler, açıklamalar dahil her şey.
8. **Kod blokları** — monospace, hafif syntax renklendirme (elle span, kütüphane yok).
9. **Sürüm başlığı** — `v1.2 · 2026-11-26 · üreten: GLM (chat.z.ai) · kaynak: <repolar>`.
10. **Boş bölüm YASAK** — her başlıkta en az 1 kart; yoksa bölümü koyma.

## 2) Şablon kullanımı

`template.html` kopyala → başlık/kategoriler/kartları doldur. Yapı hazır: sticky TOC,
çipler, arama, kart grid, `<details>` detaylar, kod bloğu stili.

## 3) Genel prompta (GOD MOD master) eklenecek satır

```
Deliverable kuralı: analiz/rapor/değerlendirme teslimleri GLM_Tools/09_HTML_REPORT_STYLE
ev stiliyle TEK HTML dosyası olarak verilir (template.html kullan); rapor repoya push'lanır
ve kullanıcıya link'i iletilir. v numarası artırılarak güncellenir (v1 → v2), eski sürüm
üzerine yazılmaz.
```

## 4) Teslim öncesi checklist (AI kendi denetimi)

- [ ] dosya `<KONU>_RAPOR_vN.html` adında ve self-contained (ağ gerektirmiyor)
- [ ] tüm bölümlerde en az 1 kart, boş başlık yok
- [ ] TOC linkleri çalışıyor (tıklanınca ilgili bölüme)
- [ ] filtre çipleri + arama gerçekten gizliyor/gösteriyor
- [ ] sayı/iddialar kanıt kartlarında kaynaklı (hangi sohbet/repo/ölçüm)
- [ ] Türkçe karakterler bozulmamış (UTF-8 charset meta)
- [ ] repoya push'landı + link kullanıcıya verildi
