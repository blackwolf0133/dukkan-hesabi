# Dükkân Hesabı

Her akşam **19:30**'da (Türkiye) "Bu dükkânı açsak ayda ne kazanırız?" sorusunu çöp adam çizimli, rakamlı bir Reels
videosuyla cevaplayan otomatik kanal. Anlatıcı: kasketli, bıyıklı, önlüklü esnaf maskot. Ses: Gemini (`assets/voice/gemini_ses`).
Altyapı Para Atlası motorunun kopyasıdır (cairo çizim + Gemini ses + resmi Instagram API).

- `episodes/NNN_konu.json` — bölümler (biçim: `docs/senaryo_formati.md`)
- `engine/` — çizim ve video motoru (`props_dukkan.py`: dükkân/sokak/kasa zemini, `fis`, `rakam`, `tabela`)
- `daily.py` + `.github/workflows/gunluk-paylasim.yml` — günlük üretim ve paylaşım (`assets/yayinda` yoksa paylaşmaz)
- `publisher.py` — Instagram Reels yükleme; yanlış hesaba paylaşımı engelleyen hesap kilidi var
- `istatistik.yml`, `baglanti-testi.yml`, `ses-dene.yml` — istatistik, bağlantı testi, ses denemesi

Yerel önizleme (ses yok): `TTS_ENGINE=sessiz python -c "from engine import render; render.render_episode('episodes/001_berber.json','/tmp/t.mp4','none',workdir='/tmp/b')"`
