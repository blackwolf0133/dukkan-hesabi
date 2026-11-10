"""Dükkân Hesabı görsel kimliği: koyu lacivert + fiş sarısı; gelir yeşil, gider kırmızı.
Kağıt dokusu, başlık, sahne zemini, anlatıcı zemini, ülke etiketi ve altyazı renkleri."""
import math
import random

import cairo

from . import draw as D
from .draw import W, H, PX, PY, PW, PH, stroke_fill, line, set_font, text_width

# Not: değişken adları Para Atlası motoruyla uyum için korunuyor (EMERALD = ana zemin, GOLD = vurgu).
EMERALD = (0.07, 0.10, 0.18)
EMERALD_2 = (0.10, 0.14, 0.24)
EMERALD_3 = (0.14, 0.19, 0.31)
GOLD = (1.00, 0.80, 0.22)
GOLD_DARK = (0.80, 0.58, 0.08)
CREAM = (0.98, 0.96, 0.90)
DARK = (0.06, 0.07, 0.10)
RED_STAMP = (0.86, 0.20, 0.18)
GREEN = (0.22, 0.78, 0.42)
RED = (0.93, 0.27, 0.24)

SERIES = "DÜKKÂN HESABI"
HANDLE = "@nekazanir.tr"


def rounded_rect(ctx, x, y, w, h, r):
    ctx.new_sub_path()
    ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    ctx.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2)
    ctx.close_path()


def make_paper():
    """Banknot dokulu koyu yeşil zemin (guilloche çizgileri)."""
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    ctx = cairo.Context(surf)
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgb(0, 0.05, 0.07, 0.13)
    g.add_color_stop_rgb(0.5, *EMERALD)
    g.add_color_stop_rgb(1, 0.04, 0.05, 0.10)
    ctx.set_source(g)
    ctx.paint()
    # kareli hesap defteri çizgileri
    ctx.set_line_width(1.0)
    for x in range(0, W + 1, 45):
        ctx.set_source_rgba(1, 1, 1, 0.035)
        ctx.move_to(x, 0)
        ctx.line_to(x, H)
        ctx.stroke()
    for y in range(0, H + 1, 45):
        ctx.set_source_rgba(1, 1, 1, 0.035)
        ctx.move_to(0, y)
        ctx.line_to(W, y)
        ctx.stroke()
    rnd = random.Random(4)
    for _ in range(4000):
        ctx.set_source_rgba(1, 1, 1, rnd.uniform(0.01, 0.03))
        ctx.arc(rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(0.5, 1.6), 0, 2 * math.pi)
        ctx.fill()
    return surf


def draw_calc_icon(ctx, x, y, r, col):
    rounded_rect(ctx, x - r * 0.8, y - r, r * 1.6, r * 2, r * 0.25)
    ctx.set_source_rgb(*col)
    ctx.set_line_width(3.5)
    ctx.stroke()
    ctx.rectangle(x - r * 0.55, y - r * 0.75, r * 1.1, r * 0.45)
    ctx.fill()
    for i in range(3):
        for j in range(2):
            ctx.arc(x - r * 0.38 + i * r * 0.38, y + r * 0.12 + j * r * 0.45, r * 0.11, 0, 2 * math.pi)
            ctx.fill()


def draw_globe_icon(ctx, x, y, r, col):
    ctx.arc(x, y, r, 0, 2 * math.pi)
    ctx.set_source_rgb(*col)
    ctx.set_line_width(4)
    ctx.stroke()
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(0.45, 1)
    ctx.arc(0, 0, r, 0, 2 * math.pi)
    ctx.restore()
    ctx.stroke()
    line(ctx, (x - r, y), (x + r, y), col, 3)
    line(ctx, (x, y - r), (x, y + r), col, 3)


def make_header(ep, paper):
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    ctx = cairo.Context(surf)
    ctx.set_source_surface(paper)
    ctx.paint()
    # seri rozeti
    set_font(ctx, D.CAPTION_FONT, 40, bold=True)
    label = ep.get("series", SERIES)
    tw = text_width(ctx, label)
    bw, bh = tw + 110, 70
    bx, by = W / 2 - bw / 2, 66
    rounded_rect(ctx, bx, by, bw, bh, 35)
    stroke_fill(ctx, GOLD, GOLD_DARK, 4)
    draw_calc_icon(ctx, bx + 42, by + bh / 2, 20, DARK)
    ctx.set_source_rgb(*DARK)
    ctx.move_to(bx + 75, by + 49)
    ctx.show_text(label)
    # başlık
    size = 70
    set_font(ctx, D.CAPTION_FONT, size, bold=True)
    title = ep["title"]
    while text_width(ctx, title) > 980 and size > 44:
        size -= 3
        set_font(ctx, D.CAPTION_FONT, size, bold=True)
    tw = text_width(ctx, title)
    ctx.move_to(W / 2 - tw / 2, 232)
    ctx.text_path(title)
    ctx.set_source_rgb(*CREAM)
    ctx.fill()
    return surf


def draw_bg(ctx, bg, t):
    """Sahne zemini: koyu yeşil, ortada altın ışık, zeminde çizgi; isteğe göre şehir silueti."""
    ctx.rectangle(PX, PY, PW, PH)
    ctx.set_source_rgb(*EMERALD_2)
    ctx.fill()
    cx, cy = PX + PW / 2, PY + PH * 0.45
    rg = cairo.RadialGradient(cx, cy, 30, cx, cy, PW * 0.75)
    rg.add_color_stop_rgba(0, *GOLD, 0.22)
    rg.add_color_stop_rgba(1, *GOLD, 0.0)
    ctx.rectangle(PX, PY, PW, PH)
    ctx.set_source(rg)
    ctx.fill()
    g = D.sy(0.93)
    if bg in ("dukkan", "sokak", "kasa"):
        from .props_dukkan import draw_shop_bg
        draw_shop_bg(ctx, bg, t, g)
    if bg in ("city", "bank"):
        rnd = random.Random(9)
        x = PX
        while x < PX + PW:
            w = rnd.uniform(60, 130)
            h = rnd.uniform(120, 360)
            ctx.rectangle(x, g - h, w - 8, h)
            ctx.set_source_rgba(0.02, 0.10, 0.08, 0.55)
            ctx.fill()
            for wy in range(int(g - h + 20), int(g - 10), 34):
                for wx in range(int(x + 10), int(x + w - 20), 26):
                    if rnd.random() < 0.35:
                        ctx.rectangle(wx, wy, 10, 14)
                        ctx.set_source_rgba(*GOLD, 0.35)
                        ctx.fill()
            x += w
    ctx.rectangle(PX, g, PW, PY + PH - g)
    ctx.set_source_rgba(0, 0, 0, 0.25)
    ctx.fill()
    line(ctx, (PX, g), (PX + PW, g), GOLD, 3)
    # yüzen altın tozları
    rnd = random.Random(1)
    for _ in range(18):
        px = PX + rnd.random() * PW
        py = PY + ((rnd.random() * PH - t * 25 * (0.5 + rnd.random())) % (PH * 0.9))
        ctx.arc(px, py, rnd.uniform(1.5, 3.5), 0, 2 * math.pi)
        ctx.set_source_rgba(*GOLD, 0.5)
        ctx.fill()


def draw_burst(ctx, t):
    ctx.rectangle(PX, PY, PW, PH)
    ctx.set_source_rgb(*EMERALD_2)
    ctx.fill()
    cx, cy = PX + PW / 2, PY + PH * 0.45
    n = 20
    for i in range(n):
        a1 = t * 0.3 + i * 2 * math.pi / n
        a2 = a1 + math.pi / n
        ctx.move_to(cx, cy)
        ctx.line_to(cx + math.cos(a1) * 1500, cy + math.sin(a1) * 1500)
        ctx.line_to(cx + math.cos(a2) * 1500, cy + math.sin(a2) * 1500)
        ctx.close_path()
        ctx.set_source_rgb(*EMERALD_3)
        ctx.fill()
    rg = cairo.RadialGradient(cx, cy, 20, cx, cy, 520)
    rg.add_color_stop_rgba(0, *GOLD, 0.35)
    rg.add_color_stop_rgba(1, *GOLD, 0.0)
    ctx.rectangle(PX, PY, PW, PH)
    ctx.set_source(rg)
    ctx.fill()


def draw_frame(ctx):
    rounded_rect(ctx, PX, PY, PW, PH, 28)
    ctx.set_source_rgb(*GOLD)
    ctx.set_line_width(6)
    ctx.stroke()


def clip_panel(ctx):
    rounded_rect(ctx, PX, PY, PW, PH, 28)
    ctx.clip()


def draw_country_tag(ctx, country):
    """Panelin sol üstünde dükkân etiketi (bayrak kodu yoksa sadece yazı)."""
    if not country:
        return
    if not country.get("code"):
        set_font(ctx, D.CAPTION_FONT, 36, bold=True)
        name = D.tr_upper(country.get("name", ""))
        tw = text_width(ctx, name)
        x, y = PX + 24, PY + 24
        rounded_rect(ctx, x, y, tw + 44, 64, 16)
        stroke_fill(ctx, GOLD, DARK, 3)
        ctx.set_source_rgb(*DARK)
        ctx.move_to(x + 22, y + 45)
        ctx.show_text(name)
        return
    from .props_para import draw_cflag
    set_font(ctx, D.CAPTION_FONT, 36, bold=True)
    name = country.get("name", "")
    tw = text_width(ctx, name)
    x, y = PX + 24, PY + 24
    rounded_rect(ctx, x, y, tw + 120, 64, 16)
    stroke_fill(ctx, (0.03, 0.14, 0.10), GOLD, 3)
    draw_cflag(ctx, country.get("code", ""), x + 14, y + 12, 72, 40, t=0, wave=False)
    ctx.set_source_rgb(*CREAM)
    ctx.move_to(x + 100, y + 45)
    ctx.show_text(name)


CAPTION_TEXT = CREAM
CAPTION_HL_BG = GOLD
CAPTION_HL_TEXT = DARK
FIGURE_INK = CREAM
