# SKILL — ZAI ACCOUNT TOOLS (chat.z.ai hesap araçları)

**İki araç:**

| Araç | Girdi | Çıktı |
|---|---|---|
| `zai_profile_analyzer.py` | token (veya tokens.json) | hesabın son 20 **dolu** sohbeti → **TÜM mesajları** → transkriptler + `chats_summary.json` + `PROFILE_REPORT.md` (tema/istatistik) |
| `zai_chat_extractor.py` | **mesaj linki** (veya ID) + token | o sohbetin TÜM mesajları (`sohbet.md` + `sohbet.json`) + **dosyalar** (attachment URL'i varsa `dosyalar/` klasörüne indirilir) + `DOSYA_LISTESI.md` |

---

## 1) Kurulum

```bash
cd GLM_Tools/06_ZAI_ACCOUNT_TOOLS
cp tokens.example.json tokens.json   # (depodışı — .gitignore'da)
# tokens.json düzenle: {"users":[{"name":"User1","token":"eyJ..."}, ...]}
```

## 2) Kullanım örnekleri

```bash
# Profil analizi (3 hesap birden):
python zai_profile_analyzer.py --tokens tokens.json --out-dir ./zai_export

# Tek hesap, son 20 dolu sohbet değil 10:
python zai_profile_analyzer.py --token "eyJ..." --name User2 --limit 10 --out-dir ./zai_export

# Belirli bir sohbeti çek (mesaj linki ile):
python zai_chat_extractor.py --url "https://chat.z.ai/chats/<ID>" --token "eyJ..."

# tokens.json'dan kullanıcıyla:
python zai_chat_extractor.py --id <ID> --tokens tokens.json --user User3

# Ağsız doğrulama (pipeline kanıtı — token bile gerekmez):
python zai_profile_analyzer.py --selftest
python zai_chat_extractor.py --selftest
```

## 3) API künyesi (doğrulanmış: 2026-11-26)

```
GET  https://chat.z.ai/api/v1/chats/                    → sohbet listesi (dolu+New Chat hepsi)
GET  https://chat.z.ai/api/v1/chats/{id}                → künye + chat.history.messages = {id: meta}
POST https://chat.z.ai/api/v1/chats/{id}/messages/batch → {"ids": [...]} → {"data": {id: tam mesaj}}
```

Gerekli başlıklar (araç zaten gönderiyor):
`Authorization: Bearer <JWT>` · `X-FE-Version: prod-fe-1.2.36` ·
`Origin/Referer: https://chat.z.ai` · tarayıcı `User-Agent` · `Content-Type: application/json`

Seçim kuralı (profil analizörü): başlığı boş olmayan ve "New Chat" olmayan sohbetler,
`updated_at`'e göre azalan, ilk 20 — **söhbett** sayısıdır; her sohbetin TÜM mesajları
(100'lük batch'lerle) çekilir.

Mesaj şeması notları:
- kullanıcı mesajı: `role="user"`, `content` (metin) + `files` (attachment metadata).
- AI mesajı: `content_blocks[]` → `type: text | tool_calls | reasoning`.
- tool çağrı istatistikleri `tool_calls[].function.name`'den sayılır.

## 4) Davranış kuralları (araç içine gömülü)

- İstekler arası uyku (varsayılan 0.6 sn, `--sleep` ile ayarlanır) → rate-limit nezaketi.
- Her istek 2 kez yeniden denenir (artan beklemeyle).
- `--selftest`: gömülü fixture ile ağsız uçtan uca kanıt — token sızmaları olmadan
  pipeline'ın çalıştığını gösterir (05 disiplinine uygun).

## 5) Gizlilik ve güvenlik

1. `tokens.json` **asla repoya commit edilmez** (.gitignore hazır; commit öncesi `git status` kontrolü).
2. Token rotate edildiyse (sen sık rotate ediyorsun) araç `HTTP başarısız` hatası verir →
   yeni tokenla tekrar; data kaybolmaz (idempotent: aynı klasöre yazar).
3. Export klasörleri (`zai_export/`) hassas sohbet içeriği taşır → sadece yerel/özel depo.
4. AI oturumunda: bu araçları çağırdıktan sonra tokeni yok et; worklog'a token DEĞİL
   "token kullanıldı, X sohbet çekildi" yaz.
