# Dergi Takibi

Takip edilen psikiyatri dergilerinde her gün yeni çıkan (online-first / in press dahil)
makaleleri toplayıp Türkçe kısa özetleriyle tek sayfada gösterir.

- `journals.json` — takip edilen dergiler (ad, ISSN'ler, dergi sayfası)
- `scripts/fetch.py` — CrossRef'ten yeni makaleleri çeker, özetleri PubMed/OpenAlex'ten tamamlar
- `scripts/build.py` — özetleri birleştirir, `docs/index.html` sayfasını üretir
- `ROUTINE.md` — her sabah bulutta çalışan Claude görevinin talimatı
- `data/articles.json` — son 90 günün arşivi
- `data/saved.json` — sayfadan "Kaydet" ile kaydedilen makaleler (sayfa GitHub API ile yazar)

## Dergi eklemek

`journals.json` dosyasına bir satır ekleyin: `id` (kısa, benzersiz), `name`, `issn`
(basılı ve elektronik ISSN), `url`. Yeni dergiye renk vermek için
`scripts/template.html` içindeki `--j-<id>` değişkenini ekleyin (yoksa varsayılan renk kullanılır).
