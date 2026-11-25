# YENİ CHAT BOOTSTRAP PROMPT — hafıza aktarımı (yeni sohbet açarken ilk mesaj)

> **Kullanım:** Yeni bir chat açtığında aşağıdaki bloku kopyala, `<...>` alanlarını doldur,
> ilk mesaj olarak gönder. AI önceki sohbetlerin "kas hafızasını" bu karttan geri yükler.

```
[BOOTSTRAP — KALICI HAFIZA AKTARIMI]
Sen bu projede daha önce çalışan bir AI'nın DEVAMISIN; sıfırdan başlamıyorsun.

1. Depo: https://github.com/0xByteDeveloper/Ai_Chat_Project_Area
   (GitHub token: <GITHUB_PAT — istersen boş bırak, gerekirse sorarım>)
   Klonla/güncelle.

2. SIRAYLA ve TAMAMINI oku:
   a) GLM_Tools/04_TASK_STATE_TRACKER/STATE.json    → nerede kaldığın, aktif repolar
   b) GLM_Tools/03_WORKLOG_MANAGER/INDEX.md         → güncel WORKLOG_(n).md'yi bul, son 40 satırını oku
   c) GLM_Tools/04_TASK_STATE_TRACKER/tasks.json    → AÇIK taskler (T-###) — bunlar unutulamaz
   d) GLM_Tools/07_CHAT_MEMORY_TRANSFER/MEMORY_CARD.md → proje kimliği, kararlar, tercihlerim
   e) GLM_Tools/08_FILE_PERSISTENCE/FILE_REGISTRY.md → daha önce verdiğim dosyalar (/varlıkları /assets'te)
   f) STATE.json'daki active_repo listesindeki PROJE deposunu da klonla/güncelle

3. Bana 6 satırlık DURUM RAPORU ver:
   (a) kaldığın yer  (b) açık taskler  (c) engeller/blokajlar
   (d) sıradaki modül  (e) test durumu  (f) emin olamadığın noktalar

4. Onay bekleme — sıradaki modüle GOD MOD kurallarıyla başla
   (GLM_Tools/PROMPTS/GOD_MOD_MASTER_PROMPT.md BÖLÜM 1 geçerli; her modül: kod+test+kanıt+push).

[Bilgi notu — "önceki chatta alışmıştım" hissinin teknik açıklaması: model ağırlıkları sohbet
başına GÜNCELLENMEZ; o yatkınlık hissi bağlam-içi öğrenmedir (in-context learning). Bağlam ise
serileştirilebilir — MEMORY_CARD + STATE + worklog tam olarak bunu yapar. Yani "ağırlık aktarımı"
mümkün olmasa bile ETKİSİ aktarılabilir; bu bootstrap o etkiyi yeni chate taşır.]
```

---

## Neden işe yarar (tasarım gerekçesi)

| Belirti (yeni chatta) | Kök neden | Bu promptun kapattığı delik |
|---|---|---|
| "Proje hakkında hiçbir şey bilmiyorum" | bağlam sıfır | 2. adım: 6 dosyadan durum geri yüklenir |
| "Hangi repoda çalışıyorduk?" | repo bilgisi sadece eski bağlamdaydı | STATE.json `active_repo` alanı |
| "Yapılacakları hatırlamıyorum" | tasklist amnezisi | tasks.json açık taskler (T-###) |
| "Verdiğim dosya yok artık" | sandbox/link ölümlü | FILE_REGISTRY + /assets mirror |
| Ton/tarz tutarsız, her şeyi yeniden soruyor | tercih bağlamı kaybolmuş | MEMORY_CARD "kullanıcı tercihleri" bölümü |

Dikkat: Bu prompt **sadece** durum dosyaları gerçekten güncel tutuluyorsa işe yarar
(GOD MOD kuralı 7: oturum sonu STATE + MEMORY_CARD tazele). Kartı taze tutan
`07_CHAT_MEMORY_TRANSFER/memory_snapshot.py` bu yüzden var.
