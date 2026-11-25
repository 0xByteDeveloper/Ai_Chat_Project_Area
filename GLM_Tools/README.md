# GLM_Tools — Kalıcı AI Çalışma Sistemi (v1.0)

**Ne bu?** chat.z.ai'deki GLM 5.3 (ve türevleri) ile yaptığın projelerde tekrar tekrar yaşanan
**3 kronik sorunu** bitirmek için kurulan kalıcı prompt + skill + araç deposudur:

1. **Unutma** → bağlam sıkıştırma / worklog dolması / yeni chat açılınca her şeyin sıfırlanması
2. **Sandbox kaybı** → geri dönüşüm, silinme, yarım teslim; işin GitHub'a "yaşayacak kadar erken" push'lanmaması
3. **Tasklist amnezisi** → x4 mesajında kalan 3 task'in x5 mesajında yeni tasklist'in altında kaybolması

**Nasıl çalışır?** Bu depo GitHub'da yaşar (`0xByteDeveloper/Ai_Chat_Project_Area`).
AI her oturumun başında buradan **STATE + worklog + tasks** okur, her modül bitiminde buraya
**push** eder. Sandbox silinse bile iş kaybolmaz; yeni chat açılsa bile hafıza buradan geri yüklenir.

---

## Hızlı Başlangıç (30 saniye)

| Durum | Yapılacak |
|---|---|
| **Yeni chat açtım** | `PROMPTS/NEW_CHAT_BOOTSTRAP_PROMPT.md` içeriğini (token alanlarını doldurup) ilk mesaj olarak yapıştır |
| **Her görev mesajında** | `PROMPTS/GOD_MOD_MASTER_PROMPT.md` → BÖLÜM 2 (kısa sürüm, 5 satır) mesajın en üstüne |
| **Uzun/kritik iş başlattım** | `PROMPTS/GOD_MOD_MASTER_PROMPT.md` → BÖLÜM 1 (tam sürüm) + `PROMPTS/SANDBOX_SURVIVAL_PROMPT.md` |
| **Token veriyorum** | `PROMPTS/TOKEN_ATTACHMENT_TEMPLATE.md` biçimini kullan (AI'ya nasıl sunulacak) |
| **Chat zaten işliyor, araç lazım** | Aşağıdaki haritadan ilgili klasörün `SKILL.md`'sini AI'ya okut |

---

## Klasör Haritası

| Klasör | Ne barındırır | AI ne zaman kullanır |
|---|---|---|
| `PROMPTS/` | 4 kalıcı prompt: **GOD MOD master** (her mesaj), **sandbox hayatta kalma**, **yeni-chat bootstrap**, **token ekleme şablonu** | her mesaj / her yeni chat / her token değişimi |
| `01_GOD_MOD_STRATEGY/` | 10x çalışma doktrini: 3 motor (doğrulama sıkılığı + parça boyutu + paralellik), S→SSS olgunluk merdiveni, START/LOOP/END oturum protokolü | her oturumun başında ve sonunda |
| `02_LIVING_GITHUB/` | **"Yaşayan GitHub"** protokolü + `living_github.py` (push aracı) + CI workflow örneği | her modül bitiminde push |
| `03_WORKLOG_MANAGER/` | **worklog + str(n+1)** rotasyonu: bağlam sıkıştırma, `WORKLOG_ARCHIVE_n` + özet, INDEX, eşik kontrolü. `worklog_manager.py` | her iş adımında append; ~200 satırda otomatik rotate |
| `04_TASK_STATE_TRACKER/` | **Tasklist amnezisi çözümü**: `tasks.json` (birleştirme kuralıyla), `STATE.json` (yönetici: hangi worklog, proje durumu, son dosyalar, son istek, test durumu). `task_state.py` | her mesajda oku; her teslimde güncelle |
| `05_MODULE_TEST_PROOF/` | **"modül + test + kanıt"** disiplini: Definition of Done, `/proofs/` yapısı, PROOF.md indeksi, `audit` denetleyicisi. `module_test_proof.py` | her modül kapanışında; oturum sonunda audit |
| `06_ZAI_ACCOUNT_TOOLS/` | chat.z.ai araçları: `zai_profile_analyzer.py` (token→son 20 dolu sohbet→TÜM mesajlar→profil raporu) ve `zai_chat_extractor.py` (**mesaj linki + token → o chatin tüm mesajları ve dosyaları**) | sohbet analizi / chat çekme gerektiğinde |
| `07_CHAT_MEMORY_TRANSFER/` | **Yeni chate hafıza taşıma**: MEMORY_CARD şablonu + `memory_snapshot.py` (STATE+tasks+worklog kuyruğundan otomatik kart üretir) | oturum sonunda kart üret; yeni chat başında kartı yükle |
| `08_FILE_PERSISTENCE/` | **Yandex/Drive/link kaybı çözümü**: FILE_REGISTRY + aynı-mesajda-mirror protokolü | kullanıcı link/dosya verdiğinde ANINDA |
| `09_HTML_REPORT_STYLE/` | Analiz/rapor teslimlerinin HTML ev stili: tek dosya, koyu tema, sticky TOC, soru→verdict→kanıt→aksiyon kartları + `template.html` | her rapor/analiz tesliminde |

---

## Altın Kurallar (AI için tek bakışta)

1. **STATE.json olmadan işe başlama** — okumadan plan üretme; projenin repolarını STATE'ten al.
2. **Sandbox'a değil GitHub'a yaşa** — her biten modül: kod → test → kanıt → push (aynı adımda).
3. **Kanıtsız task kapanmaz** — "bitti" = test çıktısı + `/proofs/` dosyası var.
4. **Yeni tasklist eskisinin yerine geçmez, BİRLEŞİR** — ID'ler (T-###) korunur.
5. **Worklog dolunca sıkıştır ve WORKLOG_(n+1)'e geç** — INDEX + STATE güncellenir.
6. **Kullanıcı link/dosya verdiyse AYNI mesajda** indir → sha256 → `/assets` mirror → FILE_REGISTRY → push.
7. **Oturum sonu:** STATE.json + MEMORY_CARD tazele → push → 6 satırlık SESSION_RECEIPT (ne yapıldı / kanıt linkleri / açık taskler / sıradaki modül).

## Token Kasası

- **Gerçek tokenlar bu depoya ASLA commit edilmez** (geçmişte bir PAT'nin repoya commit'lendiği tespit edildi — tekrarlanmasın).
- Tokenler mesaj içinde `PROMPTS/TOKEN_ATTACHMENT_TEMPLATE.md` biçimiyle verilir; AI onları yalnızca bellekte kullanır, dosyaya/loga yazmaz.
- `06_ZAI_ACCOUNT_TOOLS/tokens.example.json` → kendi `tokens.json`'ını depo DIŞINDA tut (`.gitignore`'da `tokens.json` hazır).
- Token ömrü: senrotate ediyorsan AI 401/403 görünce işi durdurmasın → token gerektirmeyen modülleri bitirsin, STATE'e "token bekleniyor" yazsın.

## Sürüm Notları

- **v1.0 (2026-11-26):** İlk kurulum. 10 modül + 6 Python aracı + 4 kalıcı prompt + 3 doküman
  (VMP_3.9.4_YOL_HARITASI.md, IDEAS_S_TIER.md, REPO_HARITASI.md — repo kökünde) + tüm araçlar
  selftest'ten geçti (kanıt: `SESSION_RECEIPTS/2026-11-26_glm_tools_kurulum.md`).
