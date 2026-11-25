# Session Receipt — 2026-11-26 — KALICI MASTER PROMPT teslimi

## a) Ne yapıldı
- Kullanıcı talebi: bootstrap MD'sini doldurma + her görev mesajına BÖLÜM 2 yapıştırma derdini bitiren, TEK yapıştırmalık kalıcı prompt.
- `GLM_Tools/PROMPTS/KALICI_MASTER_PROMPT.md` oluşturuldu ve push edildi: 1. satırda `*REPO*` (yeni proje reposu), en altta `*GÖREV*` (boş bırakılırsa AI tasks.json'daki açık görevden devam eder), PAT satırı (bu repodaki şablonda `*TOKEN*` yer tutucu — repo public), 6 KALICI KURAL, BÖLÜM 2 gömülü, gerçek dosya linkleri (doğrulandı: GLM_Tools ağacı @ main).
- `GLM_Tools/README.md` Hızlı Başlangıç tablosunun "Yeni chat açtım" satırı KALICI_MASTER_PROMPT'a yönlendirildi; `NEW_CHAT_BOOTSTRAP_PROMPT.md` emekliye ayrıldı (dosya silinmedi, geçmiş için duruyor).
- Kullanıcının yapıştırmaya hazır kopyası (gerçek token gömülü) sohbette ve sandbox `download/` klasöründe teslim edildi.

## b) Kanıt linkleri
- `GLM_Tools/PROMPTS/KALICI_MASTER_PROMPT.md` (bu commit)
- `GLM_Tools/README.md` güncellenmiş "Yeni chat açtım" satırı (bu commit)
- `SESSION_RECEIPTS/2026-11-26_kalici_master_prompt.md` (bu dosya)

## c) Açık taskler
- Bu oturum tek teslimattı; açık task bırakılmadı. VMP roadmap'in A0 aşaması (ölçüm arenası) hâlâ sıradaki en değerli hamle.

## d) Sıradaki modül
- Kullanıcı yeni bir proje reposu açıp yeni chatte KALICI_MASTER_PROMPT'u yapıştırarak A0'ı (VMP_3.9.4_YOL_HARITASI.md) başlatır; AI GLM_Tools iskeletini o repoya kurar ve döngü işler.
