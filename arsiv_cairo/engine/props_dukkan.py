"""Dükkân Hesabı sahne öğeleri: dükkân/sokak/kasa zeminleri, satır satır dolan fiş, sayan rakam kartı, tabela."""
import math
import random

from . import draw as D
from .draw import PX, PY, PW, PH, sx, sy, stroke_fill, line, set_font, text_width
from .theme_dukkan import GOLD, CREAM, DARK, GREEN, RED, rounded_rect

PAPER = (0.99, 0.98, 0.94)
INK = (0.10, 0.11, 0.14)
AWNINGS = [((0.86, 0.22, 0.20), (0.98, 0.96, 0.92)), ((0.16, 0.50, 0.32), (0.98, 0.96, 0.92)),
           ((0.20, 0.38, 0.72), (0.98, 0.96, 0.92)), ((0.95, 0.62, 0.12), (0.98, 0.96, 0.92))]


def tl(n, sign=False):
    """75000 -> '75.000 ₺' ; sign=True -> '+75.000 ₺' / '−75.000 ₺'."""
    s = f"{abs(int(round(n))):,}".replace(",", ".")
    pre = ("+" if n >= 0 else "−") if sign else ("−" if n < 0 else "")
    return f"{pre}{s} ₺"


def _awning(ctx, x, w, top, h, cols, t, n=6):
    sw = w / n
    for i in range(n):
        ctx.move_to(x + i * sw, top)
        ctx.line_to(x + (i + 1) * sw, top)
        ctx.line_to(x + (i + 1) * sw, top + h)
        ctx.line_to(x + i * sw, top + h)
        ctx.close_path()
        ctx.set_source_rgb(*cols[i % 2])
        ctx.fill()
    # sallanan saçak
    for i in range(n):
        cx = x + (i + 0.5) * sw
        ctx.arc(cx, top + h, sw / 2, 0, math.pi)
        ctx.set_source_rgb(*cols[i % 2])
        ctx.fill()
    line(ctx, (x, top), (x + w, top), INK, 4)


def _shop(ctx, x, w, g, h, cols, t, door=True, seed=0):
    top = g - h
    ctx.rectangle(x, top, w, h)
    stroke_fill(ctx, (0.80, 0.74, 0.64), INK, 4)
    # tabela alanı
    ctx.rectangle(x + w * 0.08, top + 14, w * 0.84, h * 0.13)
    stroke_fill(ctx, (0.15, 0.17, 0.24), INK, 3)
    aw_top = top + 22 + h * 0.13
    _awning(ctx, x - 6, w + 12, aw_top, h * 0.09, cols, t)
    win_top = aw_top + h * 0.09 + w / 12 + 14
    ww = w * (0.52 if door else 0.84)
    ctx.rectangle(x + w * 0.08, win_top, ww, g - win_top - 30)
    stroke_fill(ctx, (0.62, 0.80, 0.90), INK, 4)
    rnd = random.Random(seed)
    # vitrinde raflar ve ürünler
    for r in range(3):
        ry = win_top + (r + 1) * (g - win_top - 30) / 4
        line(ctx, (x + w * 0.08, ry), (x + w * 0.08 + ww, ry), INK, 2)
        bx = x + w * 0.1
        while bx < x + w * 0.08 + ww - 26:
            bh = rnd.uniform(16, 34)
            ctx.rectangle(bx, ry - bh, 18, bh)
            stroke_fill(ctx, rnd.choice([(0.95, 0.4, 0.3), (0.98, 0.8, 0.25), (0.3, 0.7, 0.45), (0.4, 0.55, 0.9)]),
                        INK, 1.5)
            bx += rnd.uniform(24, 34)
    # cam parlaması
    ctx.move_to(x + w * 0.12, win_top + 20)
    ctx.line_to(x + w * 0.22, win_top + 20)
    ctx.line_to(x + w * 0.12, win_top + 90)
    ctx.close_path()
    ctx.set_source_rgba(1, 1, 1, 0.35)
    ctx.fill()
    if door:
        dx = x + w * 0.66
        ctx.rectangle(dx, win_top, w * 0.26, g - win_top)
        stroke_fill(ctx, (0.45, 0.30, 0.20), INK, 4)
        ctx.arc(dx + w * 0.22, win_top + (g - win_top) * 0.55, 5, 0, 2 * math.pi)
        ctx.set_source_rgb(*GOLD)
        ctx.fill()
    return top


def draw_shop_bg(ctx, bg, t, g):
    if bg == "dukkan":  # tek büyük dükkân cephesi
        _shop(ctx, PX + PW * 0.06, PW * 0.88, g, PH * 0.62, AWNINGS[0], t, seed=3)
    elif bg == "sokak":  # yan yana dükkânlar
        n = 3
        w = PW / n
        for i in range(n):
            _shop(ctx, PX + i * w + 10, w - 20, g, PH * (0.42 + 0.06 * (i % 2)), AWNINGS[(i + 1) % 4], t,
                  door=(i != 1), seed=i)
    elif bg == "kasa":  # tezgâh + yazar kasa
        ty = g - PH * 0.16
        ctx.rectangle(PX, ty, PW, g - ty)
        stroke_fill(ctx, (0.55, 0.38, 0.24), INK, 4)
        line(ctx, (PX, ty + 14), (PX + PW, ty + 14), INK, 2)
        kx, ky = PX + PW * 0.72, ty
        ctx.move_to(kx - 110, ky)
        ctx.line_to(kx + 110, ky)
        ctx.line_to(kx + 90, ky - 110)
        ctx.line_to(kx - 90, ky - 110)
        ctx.close_path()
        stroke_fill(ctx, (0.30, 0.33, 0.40), INK, 4)
        ctx.rectangle(kx - 70, ky - 190, 140, 70)
        stroke_fill(ctx, (0.15, 0.17, 0.22), INK, 4)
        set_font(ctx, D.CAPTION_FONT, 34, bold=True)
        ctx.set_source_rgb(*GREEN)
        s = f"{int(t * 37) % 1000:03d},00"
        ctx.move_to(kx - text_width(ctx, s) / 2, ky - 142)
        ctx.show_text(s)
        for i in range(4):
            for j in range(2):
                ctx.rectangle(kx - 70 + i * 36, ky - 95 + j * 34, 28, 24)
                stroke_fill(ctx, CREAM, INK, 2)


def draw_tabela(ctx, text, k):
    """Dükkân tabelası (bg 'dukkan' üstüne), k: görünme zamanı."""
    a = max(0.0, min(1.0, k / 0.35))
    h = PH * 0.62
    top = sy(0.93) - h
    x, w = PX + PW * 0.06 + PW * 0.88 * 0.08, PW * 0.88 * 0.84
    size = 64
    set_font(ctx, D.CAPTION_FONT, size, bold=True)
    txt = D.tr_upper(text)
    while text_width(ctx, txt) > w - 40 and size > 30:
        size -= 3
        set_font(ctx, D.CAPTION_FONT, size, bold=True)
    ctx.set_source_rgba(*GOLD, a)
    ctx.move_to(x + w / 2 - text_width(ctx, txt) / 2, top + 14 + h * 0.065 + size * 0.36)
    ctx.show_text(txt)


def draw_fis(ctx, p, st, t0, voice_delay, voice_dur):
    """Satır satır dolan fiş. rows: [{"ad":"Kira","tutar":-45000,"f":0.2}], total: {"ad":"KALAN","tutar":...,"f":..}."""
    s = p.get("scale", 1.0)
    rows = p.get("rows", [])
    total = p.get("total")
    w = 640 * s
    rh = 70 * s
    n = len(rows) + (1 if total else 0)
    h = 120 * s + rh * n + (30 * s if total else 0)
    cx, cy = sx(p.get("x", 0.5)), sy(p.get("y", 0.45))
    x, y = cx - w / 2, cy - h / 2
    k0 = st - t0
    a = min(1.0, max(0.0, k0 / 0.3))
    ctx.save()
    ctx.translate(0, (1 - a) * 60)
    # zikzak kenarlı fiş kâğıdı
    ctx.new_path()
    ctx.move_to(x, y)
    zz = 14 * s
    i = 0
    while x + i * zz < x + w:
        ctx.line_to(x + i * zz + zz / 2, y - (8 * s if i % 2 == 0 else 0))
        i += 1
    ctx.line_to(x + w, y)
    ctx.line_to(x + w, y + h)
    i = 0
    while x + w - i * zz > x:
        ctx.line_to(x + w - i * zz - zz / 2, y + h + (8 * s if i % 2 == 0 else 0))
        i += 1
    ctx.line_to(x, y + h)
    ctx.close_path()
    ctx.set_source_rgba(0, 0, 0, 0.35 * a)
    ctx.save()
    ctx.translate(10, 12)
    ctx.fill_preserve()
    ctx.restore()
    ctx.new_path()
    ctx.move_to(x, y)
    i = 0
    while x + i * zz < x + w:
        ctx.line_to(x + i * zz + zz / 2, y - (8 * s if i % 2 == 0 else 0))
        i += 1
    ctx.line_to(x + w, y)
    ctx.line_to(x + w, y + h)
    i = 0
    while x + w - i * zz > x:
        ctx.line_to(x + w - i * zz - zz / 2, y + h + (8 * s if i % 2 == 0 else 0))
        i += 1
    ctx.line_to(x, y + h)
    ctx.close_path()
    ctx.set_source_rgba(*PAPER, a)
    ctx.fill()
    # başlık
    set_font(ctx, "DejaVu Sans Mono", 42 * s, bold=True)
    title = D.tr_upper(p.get("title", "HESAP"))
    ctx.set_source_rgba(*INK, a)
    ctx.move_to(cx - text_width(ctx, title) / 2, y + 58 * s)
    ctx.show_text(title)
    ctx.set_dash([8 * s, 6 * s])
    line(ctx, (x + 24 * s, y + 84 * s), (x + w - 24 * s, y + 84 * s), INK, 2)
    ctx.set_dash([])

    def row_time(r, idx):
        if "delay" in r:
            return r["delay"]
        if "f" in r:
            return voice_delay + r["f"] * voice_dur
        return t0 + 0.4 + idx * 0.5

    yy = y + 84 * s + rh * 0.78
    for i, r in enumerate(rows):
        kr = st - row_time(r, i)
        if kr < 0:
            break
        ar = min(1.0, kr / 0.25)
        set_font(ctx, "DejaVu Sans Mono", 40 * s, bold=True)
        ctx.set_source_rgba(*INK, ar)
        ctx.move_to(x + 30 * s + (1 - ar) * -30, yy)
        ctx.show_text(r["ad"])
        tut = r.get("tutar", 0)
        val = r.get("yazi") or tl(tut, sign=True)
        set_font(ctx, "DejaVu Sans Mono", 42 * s, bold=True)
        col = GREEN if tut >= 0 else RED
        ctx.set_source_rgba(col[0] * 0.8, col[1] * 0.8, col[2] * 0.8, ar)
        ctx.move_to(x + w - 30 * s - text_width(ctx, val), yy)
        ctx.show_text(val)
        yy += rh
    if total:
        kt = st - row_time(total, len(rows))
        if kt >= 0:
            line(ctx, (x + 24 * s, yy - rh * 0.6), (x + w - 24 * s, yy - rh * 0.6), INK, 3)
            u = min(1.0, kt / 0.9)
            u = 1 - (1 - u) ** 3
            tut = total.get("tutar", 0)
            pop = 1 + 0.15 * math.sin(min(1.0, kt / 0.35) * math.pi)
            yy += 14 * s
            rounded_rect(ctx, x + 16 * s, yy - 50 * s, w - 32 * s, 72 * s, 12 * s)
            col = GREEN if tut >= 0 else RED
            ctx.set_source_rgba(*col, 0.22)
            ctx.fill()
            set_font(ctx, "DejaVu Sans Mono", 46 * s * pop, bold=True)
            ctx.set_source_rgb(*INK)
            ctx.move_to(x + 30 * s, yy)
            ctx.show_text(D.tr_upper(total.get("ad", "KALAN")))
            val = total.get("yazi") or tl(tut * u)
            ctx.set_source_rgb(col[0] * 0.75, col[1] * 0.75, col[2] * 0.75)
            ctx.move_to(x + w - 30 * s - text_width(ctx, val), yy)
            ctx.show_text(val)
    ctx.restore()


def draw_rakam(ctx, p, k):
    """Sayarak büyüyen büyük rakam kartı: {"label":"AYLIK CİRO","value":750000,"color":"green"}."""
    s = p.get("scale", 1.0)
    cx, cy = sx(p.get("x", 0.5)), sy(p.get("y", 0.3))
    a = min(1.0, max(0.0, k / 0.25))
    u = min(1.0, max(0.0, k / p.get("count", 0.9)))
    u = 1 - (1 - u) ** 3
    col = {"green": GREEN, "red": RED, "gold": GOLD}.get(p.get("color", "gold"), GOLD)
    val = p.get("yazi") or tl(p.get("value", 0) * u)
    pop = 1 + 0.12 * math.sin(min(1.0, k / 0.3) * math.pi)
    set_font(ctx, D.CAPTION_FONT, 96 * s * pop, bold=True)
    vw = text_width(ctx, val)
    set_font(ctx, D.CAPTION_FONT, 34 * s, bold=True)
    label = D.tr_upper(p.get("label", ""))
    lw_ = text_width(ctx, label)
    bw = max(vw, lw_) + 80 * s
    bh = 190 * s
    ctx.save()
    ctx.translate(cx, cy)
    ctx.rotate(math.radians(p.get("rot", 0)))
    rounded_rect(ctx, -bw / 2, -bh / 2, bw, bh, 26 * s)
    ctx.set_source_rgba(*DARK, 0.88 * a)
    ctx.fill_preserve()
    ctx.set_source_rgba(*col, a)
    ctx.set_line_width(6 * s)
    ctx.stroke()
    ctx.set_source_rgba(*CREAM, a)
    ctx.move_to(-lw_ / 2, -bh / 2 + 52 * s)
    ctx.show_text(label)
    set_font(ctx, D.CAPTION_FONT, 96 * s * pop, bold=True)
    ctx.set_source_rgba(*col, a)
    ctx.move_to(-vw / 2, bh / 2 - 34 * s)
    ctx.show_text(val)
    ctx.restore()
