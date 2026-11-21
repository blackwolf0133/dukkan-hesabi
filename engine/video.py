"""KAÇ SANİYEN VAR? video motoru (21 Kasım: Son Mola motorundan uyarlandı; hayatta kalma kararları, A/B + doğru cevap).
21 Kasım (2): tam ekran çizim, elde kamera sarsıntısı, sahne girişlerinde zoom vuruşu, zıplayan alt yazı, nabız gibi atan
geri sayım + üstte eriyen süre çubuğu, son kartta kayarak gelen A/B kutuları; açılış/kapanış efekt sesleri yok.
Sahne = yapay zekâ çizimi (hareketli: parallax + parçacık) + karanlık renk + film greni + sis + kelime kelime alt yazı
+ isteğe bağlı TELEFON ekranı (grup mesajları / bildirim) + sonda A/B SEÇİM kartı.
Kullanım: python -m engine.video <bölüm.json> <resim_klasörü> <çıktı.mp4>"""
import json
import re
import math
import os
import subprocess
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from . import ses as S

W, H, FPS = 1080, 1920, 30
IMG_Y, IMG_H = 0, 1920          # 21 Kasım: tam ekran çizim (üst/alt siyah bant yok)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT = os.path.join(ROOT, "fonts", "Poppins-Bold.ttf")
HANDLE = os.environ.get("KANAL_HANDLE", "@kacsaniyenvar.tr")
RED = (226, 58, 52)
BLUE = (70, 120, 225)
GREEN = (90, 210, 125)
WHITE = (240, 240, 244)
LEAD, GAP, FADE, END = 0.25, 0.3, 0.16, 3.4   # 21 Kasım: daha hızlı tempo, sert geçişler
CAP_Y = 1180
PUNCH = 0.38                     # her sahne girişinde zoom vuruşu (sn)


def font(size):
    return ImageFont.truetype(FONT, size)


def tr_upper(s):
    return s.replace("i", "İ").replace("ı", "I").upper()


# --------------------------------------------------------------------------
# Sabit katmanlar
# --------------------------------------------------------------------------
def bolum_etiketi(ep):
    """Üst başlık: "MAHALLE GRUBU · 2. GECE" gibi (dizi_adi + gece); yoksa başlık."""
    if ep.get("dizi_adi"):
        g = (" · KARAR" if ep.get("gece") == 1 else " · SONUÇ") if ep.get("gece") else ""
        return tr_upper(f"{ep['dizi_adi']}{g}")
    return tr_upper(ep["title"])


def header(ep):
    """Tam ekran çizimin üstüne binen katman: üstte koyu geçiş + kanal adı + bölüm etiketi, altta alt yazı için koyu geçiş."""
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    a = np.zeros((H,), np.float32)
    a[:430] = 0.82 * (1 - np.linspace(0, 1, 430)) ** 1.6
    a[1050:] = np.maximum(a[1050:], 0.78 * np.linspace(0, 1, H - 1050) ** 1.4)
    grad = np.zeros((H, W, 4), np.uint8)
    grad[..., 3] = (a * 255).astype(np.uint8)[:, None]
    im = Image.alpha_composite(im, Image.fromarray(grad, "RGBA"))
    d = ImageDraw.Draw(im)
    f1 = font(30)
    t1 = "K A Ç   S A N İ Y E N   V A R ?"
    d.text(((W - d.textlength(t1, font=f1)) / 2, 62), t1, font=f1, fill=RED + (255,))
    size = 54
    t2 = bolum_etiketi(ep)
    while d.textlength(t2, font=font(size)) > W - 80 and size > 34:
        size -= 2
    d.text(((W - d.textlength(t2, font=font(size))) / 2, 108), t2, font=font(size), fill=WHITE + (255,),
           stroke_width=3, stroke_fill=(0, 0, 0, 200))
    fh = font(30)
    d.text(((W - d.textlength(HANDLE, font=fh)) / 2, 182), HANDLE, font=fh, fill=(200, 202, 210, 220))
    return np.asarray(im, np.float32)


def edge_mask():
    m = np.ones((IMG_H, W), np.float32)
    yy, xx = np.mgrid[0:IMG_H, 0:W].astype(np.float32)
    dist = np.sqrt(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - IMG_H / 2) / (IMG_H * 0.62)) ** 2)
    vig = np.clip(1.12 - dist ** 2 * 0.42, 0.45, 1.0)
    return m[..., None], vig[..., None]


def kenar_kirmizi():
    """Son saniyelerde nabız gibi atan kırmızı kenar (geri sayım gerilimi)."""
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    dx = np.minimum(xx, W - 1 - xx) / 170
    dy = np.minimum(yy, H - 1 - yy) / 170
    return (np.clip(1 - np.minimum(dx, dy), 0, 1) ** 2)[..., None]


def grains(n=6, seed=9):
    rng = np.random.default_rng(seed)
    return [rng.normal(0, 4, (IMG_H // 2, W // 2)).astype(np.float32).repeat(2, 0).repeat(2, 1)[..., None]
            for _ in range(n)]


class Fog:
    """Dikişsiz (periyodik) yavaş akan sis dokusu."""

    def __init__(self, h=IMG_H, w=W, seed=3):
        rng = np.random.default_rng(seed)
        fy = np.fft.fftfreq(h)[:, None]
        fx = np.fft.fftfreq(w)[None, :]
        acc = np.zeros((h, w), np.float32)
        for sigma, wgt in ((16, 0.45), (45, 0.35), (110, 0.2)):
            n = rng.random((h, w)).astype(np.float32)
            b = np.real(np.fft.ifft2(np.fft.fft2(n) * np.exp(-2 * (np.pi * sigma) ** 2 * (fx ** 2 + fy ** 2))))
            acc += ((b - b.mean()) / (b.std() + 1e-6)).astype(np.float32) * wgt
        acc = np.clip((np.clip(0.5 + acc * 0.32, 0, 1) - 0.35) * 2.0, 0, 1)
        self.tex = np.concatenate([acc, acc], axis=1)
        self.w = w
        yy = np.linspace(0, 1, h, dtype=np.float32)[:, None]
        self.band = np.clip((yy - 0.25) / 0.6, 0.2, 1.0)

    def alpha(self, t, k):
        o1 = int((t * 22) % self.w)
        o2 = int((t * 9 + self.w / 2) % self.w)
        a = 0.6 * self.tex[:, o1:o1 + self.w] + 0.4 * self.tex[::-1, o2:o2 + self.w]
        return (a * self.band * k)[..., None]


def grade(img, sicak=False):
    """Parlak 3D çizim: renkleri bastırma, hafif kontrast."""
    tint = np.array([1.04, 1.0, 0.95] if sicak else [1.0, 1.0, 1.0], np.float32)
    return (img * tint - 128) * 1.06 + 130


# --------------------------------------------------------------------------
# Alt yazı
# --------------------------------------------------------------------------
def word_times(text, start, dur):
    words = text.split()
    w = [len(x) + 2 for x in words]
    tot = sum(w)
    out, t = [], start
    for x, k in zip(words, w):
        d = dur * k / tot
        out.append((x, t, t + d))
        t += d
    return out


def chunks(timed, maxw=W - 160, size=74):
    d = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    f = font(size)
    res, cur = [], []
    for item in timed:
        trial = " ".join(x for x, _, _ in cur + [item])
        if cur and (d.textlength(trial, font=f) > maxw or len(cur) >= 4 or cur[-1][0][-1] in ".!?:"):
            res.append(cur)
            cur = []
        cur.append(item)
    if cur:
        res.append(cur)
    return res


_CAP = {}


def caption_layer(ch, hi, size=74):
    key = (id(ch), hi)
    if key in _CAP:
        return _CAP[key]
    f = font(size)
    lay = Image.new("RGBA", (W, 150), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    words = [x for x, _, _ in ch]
    sp = d.textlength(" ", font=f)
    widths = [d.textlength(x, font=f) for x in words]
    x = (W - (sum(widths) + sp * (len(words) - 1))) / 2
    for i, (wd, wtxt) in enumerate(zip(widths, words)):
        if i == hi:
            d.rounded_rectangle([x - 12, 22, x + wd + 12, 128], 16, fill=RED + (240,))
        d.text((x, 26), wtxt, font=f, fill=(255, 255, 255, 255), stroke_width=6, stroke_fill=(0, 0, 0, 255))
        x += wd + sp
    arr = np.asarray(lay, np.float32)
    _CAP[key] = arr
    return arr


def paste(frame, lay, y, alpha=1.0, scale=1.0):
    """Tam genişlikte katmanı y'ye yapıştırır; scale != 1 ise merkezden büyütüp/küçültür (pop animasyonu)."""
    if abs(scale - 1.0) > 0.005:
        h0, w0 = lay.shape[:2]
        nh, nw = max(2, int(h0 * scale)), max(2, int(w0 * scale))
        lay = cv2.resize(lay, (nw, nh), interpolation=cv2.INTER_LINEAR)
        y = int(y + (h0 - nh) / 2)
        x = int((W - nw) / 2)
        if x < 0:
            lay = lay[:, -x:-x + W]
            x = 0
        overlay(frame, lay, x, y, alpha)
        return
    h = lay.shape[0]
    a = lay[..., 3:4] / 255 * alpha
    frame[y:y + h] = frame[y:y + h] * (1 - a) + lay[..., :3] * a


def overlay(frame, lay, x, y, alpha=1.0):
    """RGBA katmanı (x, y) konumuna, ekran dışına taşan kısmı kırparak bindirir."""
    h, w = lay.shape[:2]
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(W, x + w), min(H, y + h)
    if x1 <= x0 or y1 <= y0 or alpha <= 0:
        return
    sub = lay[y0 - y:y1 - y, x0 - x:x1 - x]
    a = sub[..., 3:4] / 255 * alpha
    frame[y0:y1, x0:x1] = frame[y0:y1, x0:x1] * (1 - a) + sub[..., :3] * a


def pop(e, d=0.16, start=0.8):
    """0..d sn arasında start'tan 1'e hafif taşarak (overshoot) büyüme."""
    if e >= d:
        return 1.0
    k = max(0.0, e / d)
    return start + (1 - start) * (1 + 2.2 * (k - 1) ** 3 + 1.2 * (k - 1) ** 2)


def tag_layer(text):
    f = font(30)
    d = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    tw = int(d.textlength(text, font=f))
    lay = Image.new("RGBA", (tw + 40, 56), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.rectangle([0, 0, tw + 39, 55], fill=(8, 8, 10, 200), outline=RED + (255,), width=3)
    d.text((20, 9), text, font=f, fill=WHITE + (255,))
    return np.asarray(lay, np.float32)


# --------------------------------------------------------------------------
# 0. saniye kanca yazısı (13 Kasım): sessiz izleyen de ilk karede ne olduğunu anlasın
# --------------------------------------------------------------------------
KANCA_SURE, ZOOM_SURE = 3.0, 0.8


def kanca_metni(ep):
    """Bölümde "kanca_yazi" varsa o; yoksa açıklamanın ilk satırı (zaten kanca olarak yazılıyor)."""
    t = (ep.get("kanca_yazi") or "").strip()
    if not t:
        t = ((ep.get("caption") or ep.get("instagram_caption") or "").strip().split("\n") or [""])[0]
    t = "".join(ch for ch in t if ord(ch) < 0x2190 or ch in "…’‘“”–—").strip()
    t = " ".join(t.split())
    if len(t) > 60:                      # uzunsa sadece ilk cümle
        m = re.match(r"(.+?[.?!…])(\s|$)", t)
        if m and len(m.group(1)) >= 15:
            t = m.group(1)
    w = t.split()
    if len(w) > 18:
        t = " ".join(w[:17]) + "…"
    return t


def _kanca_sar(d, metin, f, maxw):
    satirlar, cur = [], ""
    for w in metin.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) > maxw and cur:
            satirlar.append(cur)
            cur = w
        else:
            cur = t
    if cur:
        satirlar.append(cur)
    return satirlar


def kanca_layer(text, size=78):
    if not text:
        return None
    d = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    while size > 54:
        lines = _kanca_sar(d, text, font(size), W - 170)
        if len(lines) <= 3:
            break
        size -= 4
    f = font(size)
    lh = int(size * 1.25)
    h = lh * len(lines) + 70
    lay = Image.new("RGBA", (W, h), (0, 0, 0, 0))
    dd = ImageDraw.Draw(lay)
    bw = max(dd.textlength(ln, font=f) for ln in lines) + 90
    dd.rounded_rectangle([(W - bw) / 2, 0, (W + bw) / 2, h - 1], 34, fill=(8, 8, 10, 175))
    y = 35
    for ln in lines:
        dd.text(((W - dd.textlength(ln, font=f)) / 2, y), ln, font=f, fill=(255, 255, 255, 255),
                stroke_width=6, stroke_fill=(10, 8, 6, 255))
        y += lh
    return np.asarray(lay, np.float32)


def zoom_region(region, t):
    """İlk 0,8 sn: %18 yakından başlayıp normale inen hızlı zoom (kalıp kırma)."""
    if t >= ZOOM_SURE:
        return region
    k = 1 - (1 - t / ZOOM_SURE) ** 3
    return zoom_by(region, 1.18 - 0.18 * k)


def zoom_by(region, z):
    if z <= 1.002:
        return region
    h, w = region.shape[:2]
    ch, cw = int(h / z), int(w / z)
    y0, x0 = (h - ch) // 2, (w - cw) // 2
    return cv2.resize(region[y0:y0 + ch, x0:x0 + cw], (w, h), interpolation=cv2.INTER_LINEAR)


def _sar(d, metin, f, maxw):
    return _kanca_sar(d, metin, f, maxw)


def _kutu(metin, harf, renk, cerceve, f2=None, w=W - 160):
    f2 = f2 or font(54)
    d0 = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    lines = _sar(d0, metin, f2, w - 230)[:4]
    bh = 74 * len(lines) + 76
    im = Image.new("RGBA", (w, bh), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, bh - 1], 34, outline=cerceve + (255,), width=7, fill=(12, 12, 16, 235))
    d.text((44, bh / 2 - 64), harf, font=font(100), fill=renk + (255,))
    yy = 38
    for ln in lines:
        d.text((170, yy), ln, font=f2, fill=WHITE + (255,))
        yy += 74
    return np.asarray(im, np.float32)


def _yazi(t, size, renk, stroke=0):
    f = font(size)
    d0 = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    while d0.textlength(t, font=f) > W - 80 and size > 30:
        size -= 3
        f = font(size)
    tw = int(d0.textlength(t, font=f)) + 20
    im = Image.new("RGBA", (tw, int(size * 1.45)), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((10, 4), t, font=f, fill=renk + (255,), stroke_width=stroke, stroke_fill=(0, 0, 0, 255))
    return np.asarray(im, np.float32)


_SON = {}


def end_parts(ep):
    """Son kartın parçaları: (katman, y, gecikme, animasyon). Animasyon: pop / sol / sag / alt."""
    if ep.get("id") in _SON:
        return _SON[ep.get("id")]
    P = []
    secim, dg = ep.get("secim"), ep.get("dogru")
    if secim:
        P.append((_yazi("SEN OLSAN NE YAPARDIN?", 72, WHITE, 4), 470, 0.0, "pop"))
        y = 640
        for i, harf in enumerate(("A", "B")):
            renk = RED if harf == "A" else BLUE
            k = _kutu(secim[harf], harf, renk, renk)
            P.append((k, y, 0.18 + 0.14 * i, "sol" if harf == "A" else "sag"))
            y += k.shape[0] + 46
        P.append((_yazi("Yorumlara A ya da B yaz", 50, WHITE, 3), y + 30, 0.55, "nabiz"))
        P.append((_yazi("Sonuç ve doğru cevap bu akşam", 38, (190, 192, 205), 2), y + 110, 0.7, "alt"))
    elif dg:
        P.append((_yazi("DOĞRU CEVAP", 80, GREEN, 4), 440, 0.0, "pop"))
        renk = RED if dg.get("harf") == "A" else BLUE
        k = _kutu(dg["metin"], dg.get("harf", ""), renk, GREEN)
        P.append((k, 580, 0.2, "pop"))
        y = 580 + k.shape[0] + 44
        if dg.get("kaynak"):
            P.append((_yazi("Kaynak: " + dg["kaynak"], 38, (190, 192, 205), 2), y, 0.45, "alt"))
            y += 76
        P.append((_yazi("Bunu sevdiğin birine gönder", 48, WHITE, 3), y + 30, 0.65, "nabiz"))
    else:
        P.append((_yazi(ep.get("son_kart", "KAÇ SANİYEN VAR?"), 84, RED, 4), 760, 0.0, "pop"))
        P.append((_yazi(ep.get("son_alt", "Yeni hikâye yarın akşam"), 46, WHITE, 2), 890, 0.3, "alt"))
    _SON[ep.get("id")] = P
    return P


def end_card(ep, te, bg):
    """Son kart: son karenin bulanık/karartılmış hâli üstünde kayarak gelen A/B (ya da DOĞRU CEVAP) kutuları."""
    frame = bg.copy()
    for lay, y, gec, anim in end_parts(ep):
        e = te - gec
        if e <= 0:
            continue
        k = min(1.0, e / 0.32)
        ease = 1 - (1 - k) ** 3
        h, w = lay.shape[:2]
        x = (W - w) // 2
        if anim == "sol":
            overlay(frame, lay, int(x - (1 - ease) * (W + 40)), y)
        elif anim == "sag":
            overlay(frame, lay, int(x + (1 - ease) * (W + 40)), y)
        elif anim == "alt":
            overlay(frame, lay, x, int(y + (1 - ease) * 60), ease)
        elif anim == "nabiz":
            sc = pop(e, 0.25, 0.6) * (1 + 0.045 * max(0.0, math.sin((e - 0.25) * 2 * math.pi * 1.1)) * (e > 0.25))
            _ortala(frame, lay, y, sc, ease)
        else:
            _ortala(frame, lay, y, pop(e, 0.26, 0.55), ease)
    return frame


def _ortala(frame, lay, y, sc, alpha=1.0):
    h0, w0 = lay.shape[:2]
    if abs(sc - 1) > 0.005:
        lay = cv2.resize(lay, (max(2, int(w0 * sc)), max(2, int(h0 * sc))), interpolation=cv2.INTER_LINEAR)
    h, w = lay.shape[:2]
    overlay(frame, lay, (W - w) // 2, int(y + (h0 - h) / 2), alpha)


def end_bg(last):
    """Son kare -> bulanık, karartılmış arka plan."""
    im = Image.fromarray(last.clip(0, 255).astype(np.uint8)).resize((W // 4, H // 4), Image.BILINEAR)
    im = im.filter(ImageFilter.GaussianBlur(6)).resize((W, H), Image.BILINEAR)
    return np.asarray(im, np.float32) * 0.32


_SAYAC = {}


def sayac_layer(kalan):
    """Sağ üstte kırmızı geri sayım rozeti: ⏱ 00:12 (karar bölümlerinde "sure_sn" alanı varsa)."""
    if kalan in _SAYAC:
        return _SAYAC[kalan]
    f = font(62)
    t = f"00:{kalan:02d}"
    d0 = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    w = int(d0.textlength(t, font=f)) + 60
    im = Image.new("RGBA", (w, 104), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    renk = (205, 30, 36, 240) if kalan > 3 else (255, 40, 40, 255)
    d.rounded_rectangle([0, 0, w - 1, 103], 28, fill=renk, outline=(255, 255, 255, 200), width=3)
    d.text((30, 12), t, font=f, fill=(255, 255, 255, 255))
    _SAYAC[kalan] = np.asarray(im, np.float32)
    return _SAYAC[kalan]


# --------------------------------------------------------------------------
# Telefon ekranı (19 Kasım): sahnede "telefon" alanı varsa çizimin üstüne telefon gelir.
#   "telefon": {"baslik": "Apartman Sakinleri", "alt": "24 kişi",
#               "mesajlar": [{"kim": "Kapıcı", "metin": "Kimse kapısını açmasın."}, {"ben": true, "metin": "Ne oldu?"}],
#               "bildirim": "Bilinmeyen numara: Arkana bakma."}   (bildirim tek başına da olabilir)
# Mesajlar sahne süresine yayılarak tek tek belirir. Telefon sahne başında aşağıdan kayarak gelir.
# --------------------------------------------------------------------------
PH_W, PH_H = 700, 940


def _metin_sar(d, metin, f, maxw):
    satir, cur = [], ""
    for w in metin.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) > maxw and cur:
            satir.append(cur)
            cur = w
        else:
            cur = t
    if cur:
        satir.append(cur)
    return satir


class Telefon:
    def __init__(self, spec):
        self.spec = spec
        self.msgs = spec.get("mesajlar", [])
        self.cache = {}

    def layer(self, n, bildirim_a):
        key = (n, round(bildirim_a, 1))
        if key in self.cache:
            return self.cache[key]
        im = Image.new("RGBA", (PH_W + 40, PH_H + 40), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle([20, 20, PH_W + 20, PH_H + 20], 70, fill=(8, 8, 10, 255), outline=(60, 62, 70, 255), width=6)
        x0, y0, x1, y1 = 44, 44, PH_W - 4, PH_H - 4
        d.rounded_rectangle([x0, y0, x1, y1], 52, fill=(17, 27, 33, 255))
        d.rounded_rectangle([x0, y0, x1, y0 + 120], 52, fill=(31, 44, 52, 255))
        d.rectangle([x0, y0 + 70, x1, y0 + 120], fill=(31, 44, 52, 255))
        d.text((x0 + 40, y0 + 20), "03:12", font=font(26), fill=(220, 220, 225, 255))
        if self.spec.get("baslik"):
            d.ellipse([x0 + 30, y0 + 58, x0 + 82, y0 + 110], fill=(90, 96, 110, 255))
            d.text((x0 + 100, y0 + 54), self.spec["baslik"][:26], font=font(32), fill=(240, 240, 244, 255))
            if self.spec.get("alt"):
                d.text((x0 + 100, y0 + 90), self.spec["alt"][:40], font=font(20), fill=(150, 160, 170, 255))
        y = y0 + 150
        fm, fk = font(30), font(22)
        bloklar = []
        for m in self.msgs[:n]:
            ben = m.get("ben")
            lines = _metin_sar(d, m["metin"], fm, PH_W - 230)
            h = 40 * len(lines) + (70 if not ben and m.get("kim") else 40)
            bloklar.append((m, lines, h))
        toplam = sum(h + 18 for _, _, h in bloklar)
        alan = (y1 - 40) - y
        if toplam > alan:          # eski mesajlar yukarı kayar
            y -= toplam - alan
        for m, lines, h in bloklar:
            ben = m.get("ben")
            bw = max(d.textlength(ln, font=fm) for ln in lines) + 50
            if not ben and m.get("kim"):
                bw = max(bw, d.textlength(m["kim"], font=fk) + 50)
            bx = x1 - 30 - bw if ben else x0 + 30
            if y + h > y0 + 130:
                d.rounded_rectangle([bx, y, bx + bw, y + h], 22,
                                    fill=(0, 92, 75, 255) if ben else (32, 44, 51, 255))
                yy = y + 14
                if not ben and m.get("kim"):
                    d.text((bx + 24, yy), m["kim"], font=fk, fill=m.get("renk_rgba", (233, 113, 90, 255)))
                    yy += 32
                for ln in lines:
                    d.text((bx + 24, yy), ln, font=fm, fill=(236, 238, 240, 255))
                    yy += 40
            y += h + 18
        d.rectangle([0, 0, PH_W + 40, 20], fill=(0, 0, 0, 0))
        if self.spec.get("bildirim") and bildirim_a > 0:
            a = int(255 * bildirim_a)
            fb = font(30)
            lines = _metin_sar(d, self.spec["bildirim"], fb, PH_W - 120)[:3]
            bh = 44 * len(lines) + 40
            d.rounded_rectangle([x0 + 16, y0 + 130, x1 - 16, y0 + 130 + bh], 26, fill=(235, 235, 240, a))
            yy = y0 + 150
            for ln in lines:
                d.text((x0 + 44, yy), ln, font=fb, fill=(20, 20, 24, a))
                yy += 44
        arr = np.asarray(im, np.float32)
        self.cache[key] = arr
        return arr

    def ciz(self, frame, t0, dur, t):
        """Sahne başlangıcı t0, süresi dur; t anındaki telefonu kareye bindirir."""
        e = t - t0
        if e < 0:
            return
        gir = min(1.0, e / 0.45)
        gir = 1 - (1 - gir) ** 3
        n = len(self.msgs)
        if n:
            adim = max(0.6, (dur - 0.6) / n)
            goster = min(n, 1 + int(max(0.0, e - 0.35) / adim))
        else:
            goster = 0
        b_a = 0.0
        if self.spec.get("bildirim"):
            bt = 0.5 if not n else max(0.5, dur * 0.6)
            b_a = max(0.0, min(1.0, (e - bt) / 0.3))
        lay = self.layer(goster, b_a)
        h, w = lay.shape[:2]
        x = (W - w) // 2
        y = int(IMG_Y + 150 + (1 - gir) * 900)
        y2 = min(H, y + h)
        if y2 <= y:
            return
        sub = lay[: y2 - y]
        al = sub[..., 3:4] / 255
        frame[y:y2, x:x + w] = frame[y:y2, x:x + w] * (1 - al) + sub[..., :3] * al


# --------------------------------------------------------------------------
# Ana akış
# --------------------------------------------------------------------------
def plan(durs):
    starts, t = [], LEAD
    for d in durs:
        starts.append(t)
        t += d + GAP
    return starts, round(t + 0.6, 2)


def render_episode(ep_path, img_dir, out):
    from .motion import SceneMotion
    ep = json.load(open(ep_path, encoding="utf-8"))
    work = os.path.join(os.path.dirname(os.path.abspath(out)), "work_" + ep["id"])
    os.makedirs(work, exist_ok=True)
    sc = ep["scenes"]
    parts = S.seslendir([s.get("say", s["text"]) for s in sc], work)
    starts, speech_end = plan([d for _, d in parts])
    total = speech_end + END
    audio = os.path.join(work, "audio.wav")
    # 21 Kasım (kullanıcı isteği): baştaki ürperti sesi ve sondaki vuruş sesi kaldırıldı; müzik son kartta susar.
    S.birlestir(parts, starts, total, audio, work, sting_at=None, seed=int(ep.get("seed", 7)) % 100000 + 7,
                muzik_bitis=speech_end)
    print(f"Süre: {total:.1f} sn", flush=True)

    hdr = header(ep)
    hdr_a = hdr[..., 3:4] / 255
    hdr_c = hdr[..., :3]
    klay = kanca_layer(kanca_metni(ep))
    kbit = max(2.2, min(KANCA_SURE, starts[0] + parts[0][1]))
    _, vig = edge_mask()
    kirmizi = kenar_kirmizi() if ep.get("sure_sn") else None
    gr = grains()
    fog = Fog()
    karar = bool(ep.get("secim"))
    prepared = []
    for i, (s, st, (_, d)) in enumerate(zip(sc, starts, parts)):
        img = os.path.join(img_dir, f"sahne{i + 1}.png")
        # ilk sahne ve karar videoları daha "elde kamera" hissi versin
        shake = 1.6 if i == 0 else (1.15 if karar else 0.9)
        mot = SceneMotion(img, s.get("prompt", ""), W, IMG_H, seed=i + 1, shake=shake)
        p = (s.get("prompt", "") or "").lower()
        sis = s.get("sis", 0.3 if any(k in p for k in ("fog", "mist", "haze")) else 0.0)
        prepared.append({"t": 0.0 if i == 0 else st - 0.12, "mot": mot, "sis": sis, "sicak": s.get("sicak", False),
                         "caps": chunks(word_times(s["text"], st, d)),
                         "tag": tag_layer(s["yer"]) if s.get("yer") else None,
                         "tel": Telefon(s["telefon"]) if s.get("telefon") else None, "st": st, "dur": d})
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-i", audio, "-c:v", "libx264", "-preset", "veryfast",
                           "-crf", "23", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest",
                           "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    n = int(total * FPS)
    son, bg = None, None
    for fi in range(n):
        t = fi / FPS
        if t >= speech_end:
            if bg is None:
                bg = end_bg(son if son is not None else np.zeros((H, W, 3), np.float32))
            ff.stdin.write(end_card(ep, t - speech_end, bg).clip(0, 255).astype(np.uint8).tobytes())
            continue
        idx = max(i for i, p in enumerate(prepared) if p["t"] <= t)
        region = np.zeros((IMG_H, W, 3), np.float32)
        layers = []
        if idx > 0 and t - prepared[idx]["t"] < FADE:
            layers.append((idx - 1, 1.0))
            layers.append((idx, (t - prepared[idx]["t"]) / FADE))
        else:
            layers.append((idx, 1.0))
        for j, a in layers:
            p = prepared[j]
            nxt = prepared[j + 1]["t"] if j + 1 < len(prepared) else speech_end
            img = grade(p["mot"].frame(t - p["t"], (t - p["t"]) / max(0.5, nxt - p["t"] + FADE)), p["sicak"])
            if p["sis"] > 0:
                fa = fog.alpha(t, p["sis"])
                img = img * (1 - fa) + np.array([150, 156, 168], np.float32) * fa
            region = region * (1 - a) + img * a
        region = region * vig + gr[fi % len(gr)]
        e = t - prepared[idx]["t"]
        if idx == 0:
            region = zoom_region(region, t)
        elif e < PUNCH:                                   # sahne girişi: zoom vuruşu + kısa parlama
            k = 1 - e / PUNCH
            region = zoom_by(region, 1 + 0.10 * k ** 2)
            if e < 0.12:
                region = region + 70 * (1 - e / 0.12)
        frame = region * (1 - hdr_a) + hdr_c * hdr_a
        cur = prepared[idx]
        if cur["tag"] is not None:
            ta = min(1.0, max(0.0, (t - cur["t"] - 0.2) / 0.4))
            overlay(frame, cur["tag"], 40, 260, ta)
        if cur.get("tel") is not None:
            cur["tel"].ciz(frame, cur["t"] + 0.1, cur["dur"] + (cur["st"] - cur["t"]), t)
        for ch in ([] if (klay is not None and t < kbit - 0.3) else cur["caps"]):
            if ch[0][1] - 0.05 <= t <= ch[-1][2] + 0.2:
                hi = max([i for i, (_, s0, _) in enumerate(ch) if s0 <= t] or [0])
                paste(frame, caption_layer(ch, hi), CAP_Y, scale=pop(t - ch[0][1] + 0.05, 0.16, 0.78))
                break
        if klay is not None and t < kbit:
            paste(frame, klay, int(IMG_H * 0.40), min(1.0, (kbit - t) / 0.3), scale=pop(t, 0.28, 1.45))
        if ep.get("sure_sn"):
            kalan_f = ep["sure_sn"] * (1 - t / max(1.0, speech_end))
            kalan = max(0, int(math.ceil(kalan_f)))
            faz = kalan_f - math.floor(kalan_f)                 # tik anında ~1, sonra 0'a iner
            nabiz = max(0.0, (faz - 0.7) / 0.3) if kalan_f > 0 else 0.0
            lay = sayac_layer(kalan)
            sc_ = 1 + (0.16 if kalan <= 3 else 0.08) * nabiz
            if sc_ > 1.005:
                lay = cv2.resize(lay, (int(lay.shape[1] * sc_), int(lay.shape[0] * sc_)), interpolation=cv2.INTER_LINEAR)
            h, w = lay.shape[:2]
            overlay(frame, lay, W - w - 44 + int((sc_ - 1) * w / 2), 250 - int((sc_ - 1) * h / 2))
            # üstte eriyen süre çubuğu
            bw = int(W * max(0.0, kalan_f) / ep["sure_sn"])
            frame[0:12, :bw] = frame[0:12, :bw] * 0.1 + np.array(RED, np.float32) * 0.9
            if kalan <= 3 and kirmizi is not None:              # son saniyeler: kırmızı kenar nabzı
                ka = kirmizi * (0.25 + 0.45 * nabiz)
                frame = frame * (1 - ka) + np.array([230, 20, 30], np.float32) * ka
        son = frame
        ff.stdin.write(frame.clip(0, 255).astype(np.uint8).tobytes())
        if fi % 300 == 0:
            print(f"  kare {fi}/{n}", flush=True)
    ff.stdin.close()
    ff.wait()
    print(f"Hazır: {out} ({total:.1f} sn)")


if __name__ == "__main__":
    render_episode(sys.argv[1], sys.argv[2], sys.argv[3])
