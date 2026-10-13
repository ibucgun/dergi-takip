# Dergi Takibi

Takip edilen psikiyatri dergilerinde her gün yeni çıkan (online-first / in press dahil)
makaleleri toplayıp Türkçe kısa özetleriyle tek sayfada gösterir.

- `journals.json` — takip edilen dergiler (ad, ISSN'ler, dergi sayfası, grup; isteğe bağlı `title_filter`)
- `groups.json` — sayfadaki dergi grupları ve sırası
- `scripts/fetch.py` — CrossRef'ten yeni makaleleri çeker, özetleri PubMed/OpenAlex'ten tamamlar
- `scripts/build.py` — özetleri birleştirir, `docs/index.html` sayfasını üretir
- `ROUTINE.md` — her sabah bulutta çalışan Claude görevinin talimatı
- `data/articles.json` — son 90 günün arşivi
- `data/recheck.json` — özeti eksik makaleler; 14 gün boyunca her gün PubMed, Europe PMC, OpenAlex ve Cambridge'de yeniden aranır
- `claude/dergi-veri` dalı — sayfadan kaydedilenler (`data/saved.json`) ve okundu işaretleri (`data/read.json`); sayfa GitHub API ile yazar, böylece tüm cihazlar eşit kalır

## Dergi eklemek

`journals.json` dosyasına bir satır ekleyin: `id` (kısa, benzersiz), `name`, `issn`
(basılı ve elektronik ISSN), `url`, `group` (`groups.json`'daki bir grup). Renk gruptan gelir.
Kongre bildirileri (tamamı büyük harf başlıklar, "ID# …") otomatik elenir.
