# REPO HARİTASI — 0xByteDeveloper (20 public repo)

> **Yaklaşım değişikliği (kullanıcı kararı):** "Repo sayısında sorun yok; 0 takipçi/1 yıldız
> umurumda değil — burası AI ile profesyonel çalışma alanım." → Portföy optimizasyonu DEĞİL,
> **navigasyon** problemi çözülür: sen ve AI'lar için tek bakışta "hangi hatta ne var, nerede
> güncel" haritası. (Repolar birleştirilmez; sadece haritalanır ve STATE.active_repo buradan
> beslenir.)

Veri: GitHub API, 2026-11-26 (push tarihleri canlı). Hattı gruplaması isim/önceki analiz
bazlıdır; tahmin işaretli satırları sen düzeltebilirsin.

## Koruma hattı (packer'ın)
| Repo | Dil | Son push | Not |
|---|---|---|---|
| XProtectArea | C++ | 2026-11-22 | ana gelişme deposu (XProtect) |
| XProtectAreaQ | — | 2026-11-12 | ikinci/paralel alan |
| xiangu | C++ | 2026-11-12 | — |
| MVP_VMP_ALGORTIHM | HTML | 2026-11-24 | VMP algoritma çalışma alanı |
| MVP_REVERSE | — | 2026-11-25 | tersine-mühendislik genel alan |

## Çözüm hattı (unpack / devirt / tespit)
| Repo | Dil | Son push | Not |
|---|---|---|---|
| MVP_GOD_SSS_TIER_PACKER_FINDER | C++ | 2026-11-25 | VMDETECT v4 (407/407 kör test) — en olgun |
| GelismisPDBREADER | — | 2026-11-25 | PDB okuyucu (devirt'in PDB bacağı) |
| ReverseALL | — | 2026-11-06 | genel RE arşivi |

## Derin analiz hattı (decompiler / simülasyon)
| Repo | Dil | Son push | Not |
|---|---|---|---|
| MVP_GOD_SSS_TIER_DECOMPILER | C++ | 2026-11-22 | 342/342 test; Ghidra kıyaslı |
| MVP_GOD_SSS_TIER_SIMULATION | — | 2026-11-25 | Unicorn K0-K10 çekirdeği |
| MVP_GOD_SSS_TIER_SIMULATOR_UI | C++ | 2026-11-25 | simülatör arayüzü |

## UI klonlama hattı
| Repo | Dil | Son push | Not |
|---|---|---|---|
| UniversalMVPUIAlgorithm | C++ | 2026-11-21 | imgui (7 sürüm hash/layout DB) |
| UniversalMVPUIAlgorithm_QT | C++ | 2026-11-24 | Qt 5.15/6.8 ABI replikaları |
| MVP_GOD_SSS_TIER_IMGUI_UI_EDITOR | C | 2026-11-22 | imgui analist/editör |
| CppGUICreatorWin32Api | C++ | 2026-10-24 | Win32 API form üretici |

## Oyun/hedef hattı
| Repo | Dil | Son push | Not |
|---|---|---|---|
| MyGameArea | Python | 2026-11-01 | oyun/hedef deneme alanı (tahmin) |
| aliens | — | 2026-05-19 | eski/kişisel |
| SolveMe | C++ | 2026-11-14 | çözüm alıştırma alanı (tahmin) |

## Fabrika/altyapı hattı
| Repo | Dil | Son push | Not |
|---|---|---|---|
| Ai_Chat_Project_Area | HTML | 2026-11-25 | **bu depo** — analiz + GLM_Tools merkezi |
| ai_Files | C++ | 2026-10-24 | dosya/donanım arşivi (tahmin) |

## Düzeltmeler (önceki analizden)
- **Z-Bridge:** "ürün" değil — chat.z.ai'in live-stream hatasını araştırmak/çözmek için
  yapılmış **altyapı/hata-ayıklama** aracı; hata artık çıkmadığı için şu an düşük öncelik.
  (Kullanıcı düzeltmesi 2026-11-26 ile.)
- "20 repo → 5 kümeye birleştir" önerisi **geri çekildi** — istenen tek şey bu haritadır.

## Kullanım (AI için)
- Yeni oturum: `STATE.json → active_repo` bu haritadan seçilir (hangi hat üzerinde
  çalışılıyorsa o repolar klonlanır).
- "X projesi nerede?" sorusu bu dosyadan cevaplanır — amnezi kapanır.
- Repo eklerken/silerken bu tabloyu güncelle (worklog'a !KARAR ile birlikte).
