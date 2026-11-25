# SKILL — LIVING GITHUB (Yaşayan GitHub)

**İlke:** "İş sandbox'a değil, GitHub'a yaşar." Depo = tek gerçek kaynak
(single source of truth). AI oturumları depoya okur/yazar; sandbox bir önbellektir.

---

## 1) Push disiplini

| Kural | Detay |
|---|---|
| Ne zaman | HER MODÜL BİTİMİNDE (kod+test+kanıt hazır olunca) — oturum sonunda toplu push YASAK |
| Commit mesajı | `[<modül>] ne-yapıldı + test-sonucu + kanıt-yolu` (tek satır, kanıt linkli) |
| Branch | günlük iş `main` üzerinde (tek kişilik fabrika; PR seremonisi gerekmez); deneysel iş `exp/<konu>` |
| Force push | kendi main'inde bile YASAK (geçmiş kanıtlar kaybolmasın) |
| Çakışma | `git pull --rebase` → çakışmayı çöz → tekrar push; çözülemezse `exp/` dalına yedekle ve worklog'a !HATA yaz |

## 2) Depo düzeni (tüm proje repolarında aynı iskelet)

```
<proje-repo>/
├── README.md            # ne, nasıl çalışır, nasıl derlenir
├── docs/                # tasarım notları, kararlar
├── src/                 # kaynak
├── tests/               # testler (her modülün testi burada)
├── modules/<modül>/     # modül bazlı çalışma alanları
├── proofs/<modül>/      # KANITLAR (tarihli çıktılar, loglar, hashler)
├── PROOF.md             # kanıt indeksi (tüm modüller)
├── assets/              # kullanıcı tarafından verilen dosyaların mirror'ı (bkz. 08)
├── STATE.json           # yönetici durumu (bkz. 04)
├── tasks.json           # task birliği (bkz. 04)
├── WORKLOG_1.md ...     # dönenen workloglar + INDEX.md (bkz. 03)
├── FILE_REGISTRY.md     # verilen dosyaların kaydı (bkz. 08)
└── GLM_Tools/           # (yalnız Ai_Chat_Project_Area'da) bu sistem
```

## 3) Aracı kullanım

```bash
# Kurulum (sandbox yeni geldiyse):
python GLM_Tools/02_LIVING_GITHUB/living_github.py setup https://github.com/0xByteDeveloper/<REPO>.git --token <PAT>

# Push (token her seferinde mesajdan alınır; .git/config'e YAZILMAZ):
python GLM_Tools/02_LIVING_GITHUB/living_github.py push "[modül] ... + 12/12 test PASS + proofs/..." --token <PAT>

# Oturum fişi (son 5 commit + durum):
python GLM_Tools/02_LIVING_GITHUB/living_github.py receipt

# Kaçınılmaz durum kontrolü:
python GLM_Tools/02_LIVING_GITHUB/living_github.py status
```

Araç 3 kez (artan beklemeyle) yeniden dener; hâlâ başarısızsa çıkış kodu 1 + net hata mesajı.

## 4) CI zinciri (push → derle → test)

`ci_workflow_example.yml` dosyasını repo köküne kopyala:
`mkdir -p .github/workflows && cp GLM_Tools/02_LIVING_GITHUB/ci_workflow_example.yml .github/workflows/ci.yml`

Sonuç: her push'ta GitHub Actions derler + testleri koşturur. AI "testler geçti" der ama
kırmızıysa Actions kanıtı yalanı anında yakalar → "tamamlandı illüzyonu" mekanik olarak ölür.
(AI oturumunda: push sonrası Actions durumunu sonraki modülün START adımında kontrol et.)

## 5) Neden tmp/github-token-hafızası yetmiyordu (arıza kaydı)

Geçmiş çözümler ve neden kırıldılar:
- **tmp taşıma** → yeni sandbox başka makine; tmp git gitti. (S1 çözümü: repo = ev)
- **"chate github token ver"** → token mesaj bağlamında kayboldu / AI push'u unuttu / yarıda
  kaldı. (S2-3 çözümü: token şablonu her mesajda + push modül-sonu zorunlu + retry'lı araç)
- **Sadece worklog** → dolunca AI sonunu okudu, başını kaybetti. (S4 çözümü: rotasyon+özet)

## 6) Büyük dosyalar

- >50 MB: git LFS veya Releases asset; koda dokunma.
- İkili/derleme çıktıları: `Releases` asset + PROOF.md'ye sürüm+sha256 — repoya değil.
