# Günlük güncelleme talimatı

Bu dosya her sabah bulutta çalışan Claude görevinin izlediği adımlardır.

1. `python3 scripts/fetch.py` çalıştır. Yeni makaleler `data/pending.json` dosyasına yazılır.
2. `data/pending.json` içindeki **her** makale için Türkçe kısa özet yaz ve
   `data/summaries.json` dosyasına `{"<doi>": "<özet>"}` biçiminde kaydet.
   - 3–5 cümle, yaklaşık 60–110 kelime. Okuyucu bir psikiyatrist: tıbbi terimleri
     Türkçe klinik kullanımıyla yaz (ör. "RKÇ", "meta-analiz", "EKT", "TSSB"),
     ölçek ve belirteç kısaltmalarını olduğu gibi bırak (PHQ-9, EPDS, IL-6…).
   - Araştırma makalelerinde sırasıyla şunları ver:
     1. Soru/amaç: ne araştırılmış ve neden.
     2. Yöntem: çalışma türü (RKÇ, kohort, vaka-kontrol, meta-analiz, hayvan
        çalışması…), örneklem (sayı, ülke, popülasyon), temel ölçüm/müdahale.
     3. Ana bulgular: özetteki önemli sayılarla (OR/HR, %, AUC, etki büyüklüğü).
        Anlamlı çıkmayan önemli sonuçları da belirt.
     4. Yazarların vardığı sonuç ve varsa klinik anlamı veya belirttikleri sınırlılık.
   - Derleme, editoryal ve görüş yazılarında türünü başta belirt, ana argümanı ve
     ele alınan başlıkları 2–3 cümlede özetle.
   - Sadece özette/başlıkta yazanı aktar, yorum veya abartı ekleme.
   - Özet (abstract) boşsa ya da tek cümleyse (JAMA'da sık) başlıktan ve o cümleden
     ne ile ilgili olduğunu 1–2 cümlede yaz ve sonuna
     "(Ayrıntılı özet mevcut değil.)" ekle.
3. `python3 scripts/build.py` çalıştır. Sayfa `index.html` (ve `docs/index.html`) olarak üretilir.
4. Değişiklikleri commit'le ve aynı dala push et:
   `git add -A && git commit -m "Günlük güncelleme $(date +%F)" && git push`
   Yeni makale yoksa bile 3. ve 4. adımı yap (sayfadaki "son güncelleme" saati yenilenir).

`data/saved.json` kullanıcının sayfadan kaydettiği makalelerdir; bu dosyayı asla değiştirme.
Push reddedilirse (sayfa o arada kayıt eklemiş olabilir) `git pull --rebase` yapıp tekrar push et.

Bir derginin çekilmesi hata verirse diğerlerine devam et; hatayı son mesajında belirt.
