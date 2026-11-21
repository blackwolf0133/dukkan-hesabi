# KAÇ SANİYEN VAR? — senaryo formatı (21 Kasım 2026)

Eski Dükkân Hesabı (@nekazanir.tr) hesabı bu kanala dönüştü (kullanıcı kararı). İlham: @tercihsenin3 — 20 Kasım'da
açılan hesabın İLK ve TEK videosu ("Tsunami geliyor! A: yer altı sığınağı mı, B: yüksek apartman mı?", 3D çizgi
film, 35 sn, POV) bir günde 5.594 beğeni, 6.357 yorum, 2.497 takipçi. @kaderini.sec'in "Sığınak" videosu 33 bin
beğeni. Yorum > beğeni: A/B oylaması algoritmayı patlatıyor.
ALINAN sadece format (tehlike anı + POV + A/B + 2. bölüm). ASLA alınmayacak: onların senaryoları (tsunami-sığınak/
apartman, siren-sığınak vb. aynı öncül), metinleri, adları.

## Bizim farkımız: 2. bölümde GERÇEK doğru cevap
Her senaryo iki video:
- **N01 — KARAR (12:00):** 30-40 sn. Tehlike anı, birinci/ikinci şahıs ("Araban suya düştü."), sonda A/B.
  Ekranda sağ üstte geri sayım (`sure_sn`, ör. 60 → 0), sonda A/B kartı. Seçeneklerin biri yaygın bir YANILGI
  (filmlerde görülen, "mantıklı gibi" duran), öbürü uzmanların doğru dediği şey olsun; hangisinin doğru olduğu
  belli olmasın, yorumlarda tartışma çıksın. Doğru cevap bazen A, bazen B olsun.
- **N02A / N02B — SONUÇ (21:30):** 40-55 sn. Robot karar videosunun yorumlarındaki A/B oylarını sayar, çoğunluğun
  dalını paylaşır. A dalı: A seçilseydi ne olurdu; B dalı: B seçilseydi. Sonra İKİ DALDA DA AYNI bilgi bölümü:
  uzman/kurum adıyla doğru davranış (2-4 kısa sahne) + "Bunu ... birine gönder" cümlesi.
  Sonda "DOĞRU CEVAP" kartı (`dogru` alanı: harf, kısa metin, kaynak).
- Yanlış seçim dalında kimse ölmez/yaralanmaz gösterilmez; "bu sefer şanslıydın, gerçekte en tehlikeli yol bu"
  gibi anlatılır. Kan, ceset, yaralanma ayrıntısı YOK.

## Konular
Hayatta kalma ve acil durum anları: suya düşen araç, sel, orman yangını, ev yangını (duman), asansörde mahsur
kalma, çığ, yıldırım, ormanda/dağda kaybolma, ayı/köpek/yılan karşılaşması, boğulan birini kurtarma, buz kırılması,
karbonmonoksit, gaz kaçağı, deprem anı (AFAD "çök-kapan-tutun" ve yaşam üçgeni yanılgısı — saygılı, yıkım/yaralı
gösterme), tsunami (aynı öncülü kullanma), sıcak çarpması, hipotermi, kalabalıkta ezilme, metroda/raylarda,
uçakta acil iniş, ilk yardım (Heimlich, kanamada değil — kan yok), kaybolan çocuk… 6 Şubat gibi yakın gerçek
felaketleri canlandırma YOK.

## DOĞRULUK (en önemli kural)
Her doğru cevabı en az 2 güvenilir kaynaktan doğrula (AFAD, Kızılay, İtfaiye, Sağlık Bakanlığı, 112, NOAA,
ready.gov, Red Cross, AAA, hakemli araştırma). Tartışmalı ya da "duruma göre değişir" olan konuları seçme.
`kaynaklar` alanına URL'ler; `dogru.kaynak` kısa kurum/kişi adı.

## Kimlik ve dosyalar (robot buna göre çalışır)
- Senaryo numarası yüzler basamağı: 1. senaryo 1xx, 2. senaryo 2xx …
- `N01_kisa_ad.json` (KARAR, "gece": 1, "secim", "sure_sn"), `N02A_…json` ve `N02B_…json` (SONUÇ, "gece": 2,
  "dal": "A"/"B", "dogru", "secim" YOK).
- Paylaşım sırası: her gün bir senaryo — 12:00 KARAR, 21:30 SONUÇ.

## JSON
```json
{"id": "101", "slug": "…", "title": "…", "dizi_adi": "Suya Düşen Araba", "gece": 1, "seed": 71011,
 "sure_sn": 60, "kanca_yazi": "≤ 5 kelime",
 "scenes": [{"text": "…", "prompt": "English, concrete…", "sicak": false, "telefon": {…}}],
 "secim": {"A": "≤ 6 kelime eylem", "B": "≤ 6 kelime eylem"},
 "caption": "Kanca + soru. Emoji.", "hashtags": ["#…","#…","#…","#…","#kaçsaniyenvar"],
 "kaynaklar": ["https://…"]}
```
SONUÇ dosyasında `secim` yerine `"dogru": {"harf": "B", "metin": "≤ 9 kelime", "kaynak": "kurum/kişi"}`.
`caption`'a A/B satırı ve "yorumlara yaz" YAZMA (robot ekler).

## Yazım
- KARAR: 6-8 sahne, 60-80 kelime. 1. sahne kanca: süre + tehlike, ≤ 8 kelime ("Araban suya düştü. Altmış saniyen
  var."). 2. sahne: nerede/nasıl, tek cümle. Sonra tehlike büyür, iki yol belirir. Son sahne iki seçeneği söyler.
- SONUÇ: 8-10 sahne, 80-110 kelime. 1. sahne seçimi hatırlatır ("Beklemeyi seçtin."), 3-4 sahne sonuç, sonra bilgi.
- `text`: sayılar yazıyla; kısa cümleler; ikinci şahıs.
- `prompt`: İngilizce, somut; 3D animasyon filmi sahnesi gibi (stil motorda ekleniyor). Yüzler net değil (arkadan,
  silüet, eller), yazı/tabela/logo yok, kan yok. POV (first-person view) sahneler etkili.
