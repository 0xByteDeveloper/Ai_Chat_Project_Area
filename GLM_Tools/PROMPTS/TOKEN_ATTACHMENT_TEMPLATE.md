# TOKEN EKLEME ŞABLONU — mesajlarına ekleyeceğin kalıcı token bloku

> **Kullanım:** Tokenlerini AI'a her seferinde dağınık vermektense bu tek biçimi kullan.
> Token rotate ettiğinde sadece değerleri değiştir; yapı sabit kalsın (AI, yapıyı tanır).
> Tokenleri kendin oluşturup rotate ettiğin için risk senin kontrolünde — yine de
> **bu blok asla repoya commit edilmez**, sadece mesaj içinde yaşar.

```
[TOKEN KASASI — geçerlilik: <örn. bugün 20:00'e kadar / 1 saat>]
GITHUB_PAT: <github_pat_...>              # Ai_Chat_Project_Area + proje repoları (push/pull)
ZAI_JWT_USER1: <eyJ...>                   # chat.z.ai hesap 1 (sohbet çekme — opsiyonel)
ZAI_JWT_USER2: <eyJ...>                   # chat.z.ai hesap 2 (opsiyonel)
ZAI_JWT_USER3: <eyJ...>                   # chat.z.ai hesap 3 (opsiyonel)
YANDEX/DRIVE LINK: <url>                  # geçici indirme linkleri (varsa)

KULLANIM KURALLARI (AI için):
1. Bu değerleri hiçbir dosyaya, loga, commite, echo çıktısına yazma — yalnızca kullan.
2. 401/403 görürsen işi durdurma: token gerektirmeyen tüm modülleri bitir,
   STATE.json'a "token bekleniyor: <hangi iş>" yaz; ben token yenileyince devam edersin.
3. tokens.json gerektiren araçlar için (06_ZAI_ACCOUNT_TOOLS) bu değerleri geçici
   tokens.json'a yazarsan işlem bitince SİL; .gitignore'da tokens.json zaten var.
4. Token geçerliliğini her oturum başında tek bir hafif istekle test et
   (örn. GET /api/v1/chats/ veya GitHub /user), sonucu worklog'a tek satır yaz.
```

---

## AI'ya özel not: tokenli araç kullanırken

- Endpoint'ler: `https://chat.z.ai/api/v1/chats/` (liste) · `/chats/{id}` (künye+mesaj ID'leri) ·
  `POST /chats/{id}/messages/batch` (`{"ids":[...]}` → tüm mesaj gövdeleri).
- Gerekli başlıklar: `Authorization: Bearer <JWT>`, `X-FE-Version: prod-fe-1.2.36`,
  `Origin/Referer: https://chat.z.ai`, tarayıcı User-Agent'i.
- İstekler arasında 0.5-0.8 sn uyku → rate limit nezaketi.
- Detaylı kullanım: `GLM_Tools/06_ZAI_ACCOUNT_TOOLS/SKILL.md`.
