# Günlük güncelleme talimatı

Bu dosya her sabah bulutta çalışan Claude görevinin izlediği adımlardır.

1. `python3 scripts/fetch.py` çalıştır. Yeni makaleler `data/pending.json` dosyasına yazılır.
2. `data/pending.json` içindeki **her** makale için Türkçe kısa özet yaz ve
   `data/summaries.json` dosyasına `{"<doi>": "<özet>"}` biçiminde kaydet.
   - 1–2 cümle, en fazla ~45 kelime. Okuyucu bir psikiyatrist: tıbbi terimleri
     Türkçe klinik kullanımıyla yaz (ör. "RKÇ", "meta-analiz", "EKT", "TSSB").
   - Makalenin ne ile ilgili olduğunu söyle: çalışma türü (RKÇ, kohort,
     derleme, meta-analiz, hayvan çalışması, görüş yazısı…), örneklem
     büyüklüğü ve ana bulgu varsa kısaca ekle.
   - Sadece özette/başlıkta yazanı aktar, yorum veya abartı ekleme.
   - Özet (abstract) boşsa başlıktan ne ile ilgili olduğunu yaz ve sonuna
     "(Özet mevcut değil, başlıktan çıkarıldı.)" ekle.
3. `python3 scripts/build.py` çalıştır. Sayfa `docs/index.html` olarak üretilir.
4. Değişiklikleri commit'le ve aynı dala push et:
   `git add -A && git commit -m "Günlük güncelleme $(date +%F)" && git push`
   Yeni makale yoksa bile 3. ve 4. adımı yap (sayfadaki "son güncelleme" saati yenilenir).

Bir derginin çekilmesi hata verirse diğerlerine devam et; hatayı son mesajında belirt.
