# Dükkân Hesabı — Bölüm Senaryo Formatı

Dosya: `episodes/NNN_konu.json` (ASCII, küçük harf). Sıradaki (paylaşılmamış, en küçük numara) bölüm her akşam 19:30'da paylaşılır.

## Fikir
"Bu dükkânı açsak ayda cebimize ne kalır?" Gerçek 2026 fiyatlarıyla, kalem kalem, esnaf ağzıyla hesap. İzleyici sonunu merak edip
sonuna kadar izlesin, yorumda kendi semtinin fiyatını yazsın. **Yatırım/iş tavsiyesi değil, örnek hesaptır** (caption'da yaz).

## Üst alanlar
`id`, `series` ("DÜKKÂN HESABI"), `title` ("<Dükkân> Açsak Ne Kazanırız?" ya da benzeri, ≤ 32 karakter),
`country` {"name": "Berber"} (sol üst etiket; `code` VERME), `kaynaklar` (liste: her rakamın kaynağı ya da "örnek varsayım"),
`instagram_caption`: kanca (fiyat + soru) + 1-2 cümle + "(Rakamlar örnek hesaptır; semte ve dükkâna göre değişir.)" +
izleyiciye TEK soru ("Senin mahallende … kaç lira? 👇") + "Her akşam 19:30'da yeni bir dükkân hesabı için takip et 🧮" +
TAM 5 etiket, sonuncusu #dükkanhesabı.

## Bölüm yapısı (8 sahne, 120–135 kelime, ~55–60 sn)
1. **Kanca** (`narrator`, `"emotion":"şaşkın"`): "Mahallede bir X açsak, ayda cebimize kaç lira kalır? Hesaplayalım!" + `pop`.
2. **Fiyat** (`bg:"dukkan"`, `tabela`, `rakam`): gerçek, kaynaklı satış fiyatı ve ortalama müşteri harcaması.
3. **Ciro** (`bg:"kasa"`, `rakam` yeşil): günlük adet × fiyat × 26 gün.
4. **Giderler** (`bg:"kasa"`, `fis`): kira, personel (asgari ücretin işverene maliyeti), malzeme, fatura, Bağ-Kur, vergi+muhasebe → `total` KALAN.
   Satırların `f` değerleri, okunan cümleyle aynı ana denk gelsin.
5. **İlk şaşkınlık**: kalan iyi mi kötü mü? Saat başına kazanç ya da benzeri çarpıcı bir oran (`rakam`).
6. **Ters köşe**: işin gizli riski (müşteri azalırsa, fire, sezon, kira zammı…). İki `rakam` kartıyla karşılaştır.
7. **Ders** (`"emotion":"sakin"`): tek cümle, akılda kalan ("Kazanç makasta değil, koltuğun dolu kalmasında.") + `pop` + `sfx` rimshot.
8. **Kapanış** (`narrator`): "Rakamlar örnek, senin mahallende … kaç lira? Yarın akşam: <sonraki dükkân> açsak ne kazanırız?" + `pop` "YARIN: …".
   Sonraki dükkân, sıradaki bölümün konusu olmalı (zincir).

## Sahne alanları ve nesneler
`say` (okunacak; sayılar rakamla, noktasız: 312 bin, 45 bin, 600), `text` (altyazı; 312.000 ₺ gibi), `bg` (`dukkan` `sokak` `kasa` `vault`),
`emotion` (`şaşkın` `sakin` `mutlu`), `voice_delay`, `actors` (pose: hips think open shock push point wave; face: happy think shock surprised smug wink),
`props`:
- `tabela` {"text":"Berber Salonu","delay":0} — sadece `bg:"dukkan"` ile
- `rakam` {"label":"AYLIK CİRO","value":312000,"color":"green|red|gold","x":0.55,"y":0.28,"scale":0.85,"f":0.4} — sayarak büyür; `yazi` ile serbest metin
- `fis` {"title":"AYLIK HESAP","x":0.6,"y":0.47,"scale":0.9,"rows":[{"ad":"Kira","tutar":-45000,"f":0.1}],"total":{"ad":"KALAN","tutar":154000,"f":0.95}}
  — en fazla 7 satır; `ad` ≤ 10 karakter
- `pop` `bubble` `coin` `coins` `banknote` `wallet` `piggy` `sfx`
- Zamanlama: `delay` (sn) ya da `f` (konuşmanın oranı)

## Doğruluk kuralları
- Satış fiyatları, asgari ücret, Bağ-Kur, vergi oranları gibi resmi/haberleşmiş rakamları WebSearch ile **en az 2 kaynaktan** doğrula, `kaynaklar`'a yaz.
- Kira, malzeme, müşteri sayısı gibi kalemler varsayımdır: makul tut, `kaynaklar`'da "örnek varsayım" de, videoda "diyelim/örnek" de.
- Hesap tutarlı olmalı: `fis` satırlarının toplamı `total` ile aynı; söylenen sayılar ekrandakiyle aynı. Küçük betikle kontrol et.
- Yatırım/iş tavsiyesi verme; esnafı küçümseme; marka/işletme adı verme.
- Rakip hesapların (satisciyiz, bay.finans, mahalleceosu) videolarını, başlıklarını, hesaplarını kopyalama; aynı dükkânı onlar yeni yaptıysa erteleme.

## Fiş zamanlaması
Satırların `f` değeri = o kalemin adının `say` içindeki kelime sırası / toplam kelime (biraz önce). Elle tahmin etme; bir satırın kalemi
cümlede hangi kelimeyle geçiyorsa onun yerine göre hesapla (örnek: tools/bolum_uret.py ile üretip küçük bir betikle `f`'leri düzelt).
`total.f` ≈ (kelime sayısı − 1) / kelime sayısı ("Kalan?" kelimesine denk gelsin).

## Haftalık trend raporu (last30days)
Her pazartesi blackwolf0133/cop-adamla-tarih deposundaki "Trend araştırma" iş akışı `dukkan.md` raporunu üretir. Yazmadan önce oku:
```bash
TAG=$(gh api "repos/blackwolf0133/cop-adamla-tarih/releases?per_page=20" --jq '[.[]|select(.tag_name|startswith("trend-"))][0].tag_name')
ID=$(gh api "repos/blackwolf0133/cop-adamla-tarih/releases/tags/$TAG" --jq '.assets[]|select(.name=="dukkan.md").id')
gh api -H "Accept: application/octet-stream" "repos/blackwolf0133/cop-adamla-tarih/releases/assets/$ID" > /tmp/trend.md
```
(İlk rapor 16 Kasım'dan sonra çıkar; yoksa bu adımı atla.)
