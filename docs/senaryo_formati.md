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


## 12 Kasım güncellemesi: KAZANÇ + AMA kancası (ZORUNLU)
İlk 2 bölümde izleyici ortalama 7-12 sn'de kaydırdı (rakam 50. saniyedeydi). Yeni yapı (6 sahne, ~45 sn):
1. **Kanca (0. sn):** `say` = "<Dükkân> ayda <KALAN> bin lira bırakıyor. Ama <ters köşeyi ele vermeden ima eden yarım cümle>."
   Görsel: bg "dukkan" + tabela + `rakam` (label "AYDA KALAN", value=KALAN, color green, x 0.58, y 0.12, scale 0.9, f 0.0) +
   `pop` "AMA…" (x 0.72, y 0.45, size 120, f ≈ "Ama" kelimesinin konumu) + narrator (x 0.32, scale 1.05, pose point → think).
2. Fiyat (eski sahne 1) · 3. Ciro (eski 2) · 4. Fiş (eski 3) · 5. Ters köşe (eski 5) · 6. Kapanış + "Yarın akşam: X" (eski 7).
Eski "KALAN açıklama" ve "ders" sahneleri yok. Bölüm JSON'una `"kanca_v2": true` yaz.

---

## 13 Kasım: İLK 3 SANİYE kuralları (ZORUNLU, diğer kurallarla çelişirse bu geçerli)

Veri: 8 kanalda izleyici ortalama 5-13 sn'de kaydırıyor. Instagram videoyu önce küçük bir test grubuna gösteriyor; izlenme süresi, sona kadar izlenme ve DM ile gönderilme iyi değilse yaymıyor. Reels izleyicisi ~1,4 sn'de karar veriyor ve izlemelerin yarısından fazlası ses kapalı başlıyor.

**Motor ne yapıyor (otomatik):** 0. saniyede ekranda büyük kanca yazısı (~3 sn) + ilk 0,8 sn hızlı zoom. Yazı bölümdeki `"kanca_yazi"` alanından gelir; yoksa açıklamanın (caption / instagram_caption) ilk satırından, o da uzunsa ilk cümlesinden. Bu yüzden:
- Her bölüme `"kanca_yazi"` ekle: en fazla 8 kelime, sessizken tek başına merak uyandıran cümle (cevabı vermeden). Seslendirilen ilk cümleyle aynı olmak zorunda değil ama aynı merakı açsın. (Son Mola'da bu alan sahne içindedir ve 2-3 kelimedir; orada mevcut kural geçerli.)
- Açıklamanın ilk satırı da kısa ve merak uyandıran olsun (yedek kanca yazısı olarak kullanılıyor).

**Kanca puanlama (yazdıktan sonra her bölüm için):** İlk seslendirilen cümleyi ve kanca_yazi'yi şu 5 türe göre 1-5 puanla, kendine sor: "Akışta kaydırırken 1,5 sn'de durur muydum?"
1. Ortak dert: izleyicinin yaşadığı ama dile getirmediği bir sıkıntı (Reels'te en güçlüsü)
2. Merak boşluğu: kapanması için izlemek gereken bir soru/boşluk
3. İddialı/ters köşe cümle: doğru ama şaşırtıcı, karşı çıkılası bir iddia
4. Kalıp kırma: beklenmedik bir giriş
5. Görsel şok: ilk karede açıklama isteyen bir görüntü
En yüksek puan 4'ün altındaysa ilk cümleyi yeniden yaz. Selamlama, giriş, "bugün size … anlatacağım", tarih/yer ile başlamak YASAK; en çarpıcı an ilk cümlede. Doğruluk kuralları aynen geçerli (abartı/uydurma yok).

**Gönderilme (DM) sebebi:** Instagram'da yeni kişilere ulaştıran en güçlü sinyal videonun DM ile birine gönderilmesi. Her bölümün SON seslendirilen cümlesi (ya da kapanış kartı alt yazısı), izleyicinin videoyu belirli birine göndermesi için doğal bir sebep versin; TEK cümle, dilenmeden: "Bunu her ay sonu batan arkadaşına gönder.", "Bunu gece yolculuğu seven birine gönder." Açıklamadaki tek çağrı kuralı aynen kalır (bu cümle videonun içinde).
