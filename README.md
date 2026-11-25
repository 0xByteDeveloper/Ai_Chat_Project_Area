# Ai_Chat_Project_Area

Bu depo, chat.z.ai üzerindeki yapay zekâ oturumlarımda yaptırdığım projelerin **analiz alanıdır**. AI oturumlarından çekilen veriler (sohbet listeleri, mesajlar) burada analiz edilir; çıkan raporlar ve yol haritaları burada saklanır.

## Son Analiz: 26 Kasım 2026

Kapsam: 3 hesabın son **50 dolu sohbeti** (946 mesaj, ~46.400 araç çağrısı; 21 Ekim – 25 Kasım 2026) + `0xByteDeveloper` GitHub portföyü (20 public repo).

| Dosya | İçerik |
|---|---|
| [ANALIZ_RAPORU_2026-11-26.md](ANALIZ_RAPORU_2026-11-26.md) | Kapsamlı analiz: projelerim güçlü mü, ne yapıyorum / istiyorum / yapmalıyım, GOD MOD (10x) stratejisi, VMP port boyut analizi, 3.5.1→3.9.4 değerlendirmesi, register-kripto varyasyon analizi, VMP+Maze katmanlama, önerilen 10 proje |
| [KAFA_HARITASI.html](KAFA_HARITASI.html) | **Ana deliverable** — interaktif kategori haritası: kafamdaki tüm fikirler 6 kategoride (Koruma / Çözüm / UI Zekâsı / Derin Analiz / Oyun / Fabrika), durum göstergeleri, AI yorumları, filtre + arama, yol haritası takip kutuları |
| [CHAT_ENVANTERI.md](CHAT_ENVANTERI.md) | İncelenen 50 sohbetin tablosal envanteri (kullanıcı bazında, mesaj ve araç çağrısı sayıları) |
| [data/chat_stats.json](data/chat_stats.json) | Sohbet künyesinin makine-okunur özeti |

## GLM_Tools v1.0 (2026-11-26 eklendi) — Kalıcı AI Çalışma Sistemi

**Unutma + sandbox kaybı + tasklist amnezisini bitiren sistem:** 10 modül + 6 Python aracı
+ 4 kalıcı prompt. AI oturumları bu depodan durumunu okur, bu depoya push'lar.

| Dosya/Dizin | Ne |
|---|---|
| [GLM_Tools/README.md](GLM_Tools/README.md) | **Kullanım kılavuzu** — klasör haritası + altın kurallar |
| [GLM_Tools/PROMPTS/](GLM_Tools/PROMPTS/) | Her mesaja yapıştırılacak kalıcı promptlar: GOD MOD master (kısa+tam), sandbox hayatta kalma, yeni-chat bootstrap, token şablonu |
| [VMP_3.9.4_YOL_HARITASI.md](VMP_3.9.4_YOL_HARITASI.md) | x_vmp cevabı: 8 aşamalı ölçülebilir 3.9.4 çıkış planı + saldırı envanteri + "rea" durum raporu |
| [IDEAS_S_TIER.md](IDEAS_S_TIER.md) | 7 derin S-tier proje önerisi (kırmızı-takım otokapsülü, handler rastgeleci, MazeLink, imgui corpus sözlüğü...) |
| [REPO_HARITASI.md](REPO_HARITASI.md) | 20 reponun 6 hatta haritası (portföy değil çalışma-alanı çerçevesi) |
| [SESSION_RECEIPTS/](SESSION_RECEIPTS/) | Oturum fişleri (ne yapıldı + kanıt + açık kalemler + metrikler) |
| [proofs/glm_tools/](proofs/glm_tools/) | Kurulum kanıtı: 7/7 araç selftest + canlı API testi PASS |

Ham sohbet dökümleri (boyut ve hassasiyet nedeniyle) repoya konmadı; analist ortamda tutuldu.

## Öne çıkan sonuçlar (TL;DR)

1. **Teknoloji 85/100, Süreç 40/100, Sunum 20/100** — güç var, disiplin ve paketleme eksik.
2. **GOD MOD = daha uzun oturum değil:** bağımsız doğrulama (GOLDEN-BENCH) + parçacık boyutu + 3 hesap = 3 uzman hattı (Araştırıcı / Uygulayıcı / Denetçi) + CI.
3. **VMP 3.9.4 birebir parite bırakılmalı** → hedef "3.5.1-hardened": kendi devirt araçlarımla kırmızı takım testinden geçen fork.
4. **En büyük boşluklar:** UniversalUnpacker, ImGui corpus besleme + unknown obje tespiti, register-kripto motoru — üçü birbirini besleyen zincir.
5. **20 repo → 5 küme** birleştirme planı hazır (bkz. rapor bölüm 10).

## Yeniden çalıştırma

Analiz verisi chat.z.ai API'sinden (`/api/v1/chats/`, `/api/v1/chats/{id}`, `/api/v1/chats/{id}/messages/batch`) JWT ile çekilir; seçim kuralı: başlığı boş olmayan ve "New Chat" olmayan sohbetler, güncelleme tarihine göre son 20 (her hesap için).
