"""Para Atlası çizimleri: bayraklar, söz kartı, pasaport damgası, sikke, banknot,
cüzdan, kumbara, külçe altın, dünya küresi. Hepsi kodla çizilir."""
import math

import cairo

from . import draw as D
from .draw import sx, sy, stroke_fill, line, set_font, text_width
from .theme_dukkan import GOLD, GOLD_DARK, CREAM, DARK, RED_STAMP, EMERALD, rounded_rect

RED = (0.80, 0.12, 0.18)
WHITE = (1, 1, 1)
BLUE = (0.10, 0.22, 0.55)
YELLOW = (1.0, 0.80, 0.0)
GREEN = (0.0, 0.55, 0.30)
BLACK = (0.08, 0.08, 0.08)
ORANGE = (1.0, 0.55, 0.1)

# Basit bayraklar: (yön, renkler)  h = yatay şeritler, v = dikey şeritler
SIMPLE = {
    "DE": ("h", [BLACK, (0.86, 0.0, 0.0), YELLOW]),
    "RU": ("h", [WHITE, BLUE, RED]),
    "NL": ("h", [(0.68, 0.11, 0.16), WHITE, (0.13, 0.27, 0.55)]),
    "FR": ("v", [BLUE, WHITE, RED]),
    "IT": ("v", [GREEN, WHITE, RED]),
    "IE": ("v", [GREEN, WHITE, ORANGE]),
    "MX": ("v", [GREEN, WHITE, RED]),
    "EG": ("h", [RED, WHITE, BLACK]),
    "IN": ("h", [ORANGE, WHITE, GREEN]),
    "AT": ("h", [RED, WHITE, RED]),
    "HU": ("h", [RED, WHITE, GREEN]),
    "PL": ("h", [WHITE, RED]),
    "UA": ("h", [(0.0, 0.36, 0.73), YELLOW]),
    "ID": ("h", [RED, WHITE]),
}


def _star(ctx, cx, cy, r, rot=-math.pi / 2):
    pts = []
    for i in range(10):
        rr = r if i % 2 == 0 else r * 0.4
        a = rot + i * math.pi / 5
        pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
    ctx.move_to(*pts[0])
    for p in pts[1:]:
        ctx.line_to(*p)
    ctx.close_path()


def draw_cflag(ctx, code, x, y, w, h, t=0.0, wave=True):
    """Ülke bayrağı (sadeleştirilmiş). Bilinmeyen kodlarda beyaz bayrak + kod yazısı."""
    ctx.save()
    if wave:  # hafif dalgalanma: dikey şeritlerle kaydırma yerine maskeli ofset
        ctx.translate(0, 3 * math.sin(t * 4))
    ctx.rectangle(x, y, w, h)
    ctx.clip()
    code = (code or "").upper()
    if code in SIMPLE:
        d, cols = SIMPLE[code]
        n = len(cols)
        for i, c in enumerate(cols):
            ctx.set_source_rgb(*c)
            if d == "h":
                ctx.rectangle(x, y + h * i / n, w, h / n + 1)
            else:
                ctx.rectangle(x + w * i / n, y, w / n + 1, h)
            ctx.fill()
        if code == "IN":
            ctx.arc(x + w / 2, y + h / 2, h * 0.13, 0, 2 * math.pi)
            ctx.set_source_rgb(*BLUE)
            ctx.set_line_width(max(1, h * 0.03))
            ctx.stroke()
    elif code == "JP":
        ctx.set_source_rgb(*WHITE); ctx.rectangle(x, y, w, h); ctx.fill()
        ctx.arc(x + w / 2, y + h / 2, h * 0.3, 0, 2 * math.pi)
        ctx.set_source_rgb(0.74, 0.0, 0.18); ctx.fill()
    elif code == "TR":
        ctx.set_source_rgb(0.89, 0.04, 0.09); ctx.rectangle(x, y, w, h); ctx.fill()
        # Türk bayrağı oranları (yaklaşık): hilal ve yıldız
        cx = x + h * 0.5 + w * 0.0
        cx = x + 0.5 * h
        ctx.arc(cx, y + h / 2, h / 4, 0, 2 * math.pi)
        ctx.set_source_rgb(*WHITE); ctx.fill()
        ctx.arc(cx + h * 0.0625, y + h / 2, h * 0.2, 0, 2 * math.pi)
        ctx.set_source_rgb(0.89, 0.04, 0.09); ctx.fill()
        _star(ctx, cx + h * 0.333, y + h / 2, h * 0.125, rot=math.pi)
        ctx.set_source_rgb(*WHITE); ctx.fill()
    elif code == "CN":
        ctx.set_source_rgb(0.87, 0.16, 0.06); ctx.rectangle(x, y, w, h); ctx.fill()
        ctx.set_source_rgb(1.0, 0.87, 0.0)
        _star(ctx, x + w * 0.17, y + h * 0.27, h * 0.15); ctx.fill()
        for dx, dy in ((0.33, 0.1), (0.4, 0.2), (0.4, 0.35), (0.33, 0.45)):
            _star(ctx, x + w * dx, y + h * dy, h * 0.05); ctx.fill()
    elif code == "KR":
        ctx.set_source_rgb(*WHITE); ctx.rectangle(x, y, w, h); ctx.fill()
        cx, cy, r = x + w / 2, y + h / 2, h * 0.25
        ctx.arc(cx, cy, r, math.pi, 2 * math.pi); ctx.set_source_rgb(0.80, 0.18, 0.20); ctx.fill()
        ctx.arc(cx, cy, r, 0, math.pi); ctx.set_source_rgb(0.0, 0.20, 0.53); ctx.fill()
        for (dx, dy, a) in ((-0.3, -0.28, 0.6), (0.3, 0.28, 0.6), (0.3, -0.28, -0.6), (-0.3, 0.28, -0.6)):
            ctx.save(); ctx.translate(x + w / 2 + dx * w, y + h / 2 + dy * h * 1.1); ctx.rotate(a)
            for k in range(3):
                ctx.rectangle(-h * 0.1, -h * 0.09 + k * h * 0.065, h * 0.2, h * 0.04)
            ctx.set_source_rgb(*BLACK); ctx.fill(); ctx.restore()
    elif code == "ES":
        for i, c in enumerate([(0.67, 0.08, 0.11), (0.98, 0.75, 0.0), (0.98, 0.75, 0.0), (0.67, 0.08, 0.11)]):
            ctx.set_source_rgb(*c); ctx.rectangle(x, y + h * i / 4, w, h / 4 + 1); ctx.fill()
    elif code == "US":
        for i in range(13):
            ctx.set_source_rgb(*((0.70, 0.13, 0.20) if i % 2 == 0 else WHITE))
            ctx.rectangle(x, y + h * i / 13, w, h / 13 + 1); ctx.fill()
        ctx.set_source_rgb(0.24, 0.23, 0.43); ctx.rectangle(x, y, w * 0.4, h * 7 / 13); ctx.fill()
        ctx.set_source_rgb(*WHITE)
        for r_ in range(4):
            for c_ in range(5):
                ctx.arc(x + w * 0.04 + c_ * w * 0.08, y + h * 0.07 + r_ * h * 0.13, max(1, h * 0.025), 0, 2 * math.pi)
                ctx.fill()
    elif code == "GB":
        ctx.set_source_rgb(0.0, 0.14, 0.49); ctx.rectangle(x, y, w, h); ctx.fill()
        for (a, b, c, d_) in ((x, y, x + w, y + h), (x + w, y, x, y + h)):
            line(ctx, (a, b), (c, d_), WHITE, h * 0.2)
            line(ctx, (a, b), (c, d_), (0.78, 0.06, 0.18), h * 0.07)
        line(ctx, (x + w / 2, y), (x + w / 2, y + h), WHITE, h * 0.33)
        line(ctx, (x, y + h / 2), (x + w, y + h / 2), WHITE, h * 0.33)
        line(ctx, (x + w / 2, y), (x + w / 2, y + h), (0.78, 0.06, 0.18), h * 0.2)
        line(ctx, (x, y + h / 2), (x + w, y + h / 2), (0.78, 0.06, 0.18), h * 0.2)
    elif code in ("SE", "FI", "DK", "NO"):
        bg, cr = {"SE": ((0.0, 0.42, 0.66), YELLOW), "FI": (WHITE, (0.0, 0.21, 0.5)),
                  "DK": ((0.78, 0.06, 0.18), WHITE), "NO": ((0.73, 0.05, 0.18), WHITE)}[code]
        ctx.set_source_rgb(*bg); ctx.rectangle(x, y, w, h); ctx.fill()
        if code == "NO":
            line(ctx, (x + w * 0.36, y), (x + w * 0.36, y + h), WHITE, h * 0.25)
            line(ctx, (x, y + h / 2), (x + w, y + h / 2), WHITE, h * 0.25)
            cr = (0.0, 0.13, 0.36)
        line(ctx, (x + w * 0.36, y), (x + w * 0.36, y + h), cr, h * 0.16)
        line(ctx, (x, y + h / 2), (x + w, y + h / 2), cr, h * 0.16)
    elif code == "GR":
        for i in range(9):
            ctx.set_source_rgb(*((0.05, 0.37, 0.69) if i % 2 == 0 else WHITE))
            ctx.rectangle(x, y + h * i / 9, w, h / 9 + 1); ctx.fill()
        ctx.set_source_rgb(0.05, 0.37, 0.69); ctx.rectangle(x, y, h * 5 / 9, h * 5 / 9); ctx.fill()
        line(ctx, (x + h * 2.5 / 9, y), (x + h * 2.5 / 9, y + h * 5 / 9), WHITE, h / 9)
        line(ctx, (x, y + h * 2.5 / 9), (x + h * 5 / 9, y + h * 2.5 / 9), WHITE, h / 9)
    elif code == "BR":
        ctx.set_source_rgb(0.0, 0.61, 0.23); ctx.rectangle(x, y, w, h); ctx.fill()
        ctx.move_to(x + w / 2, y + h * 0.08); ctx.line_to(x + w * 0.93, y + h / 2)
        ctx.line_to(x + w / 2, y + h * 0.92); ctx.line_to(x + w * 0.07, y + h / 2); ctx.close_path()
        ctx.set_source_rgb(1.0, 0.87, 0.0); ctx.fill()
        ctx.arc(x + w / 2, y + h / 2, h * 0.22, 0, 2 * math.pi); ctx.set_source_rgb(0.0, 0.15, 0.46); ctx.fill()
    else:
        ctx.set_source_rgb(*CREAM); ctx.rectangle(x, y, w, h); ctx.fill()
        set_font(ctx, D.CAPTION_FONT, h * 0.45, bold=True)
        tw = text_width(ctx, code)
        ctx.set_source_rgb(*DARK); ctx.move_to(x + w / 2 - tw / 2, y + h * 0.66); ctx.show_text(code)
    ctx.restore()
    ctx.rectangle(x, y + (3 * math.sin(t * 4) if wave else 0), w, h)
    ctx.set_source_rgba(0, 0, 0, 0.6)
    ctx.set_line_width(2)
    ctx.stroke()


def draw_flag_on_pole(ctx, code, x, y, s, t):
    """Direkte dalgalanan büyük bayrak. x,y direk dibi."""
    line(ctx, (x, y), (x, y - 420 * s), (0.75, 0.75, 0.78), 10 * s)
    ctx.arc(x, y - 425 * s, 12 * s, 0, 2 * math.pi)
    stroke_fill(ctx, GOLD, DARK, 3)
    draw_cflag(ctx, code, x + 6 * s, y - 410 * s, 300 * s, 200 * s, t, wave=True)


def _font_for(text):
    if any(0x3040 <= ord(c) <= 0x30FF or 0x4E00 <= ord(c) <= 0x9FFF for c in text):
        return "Noto Sans CJK JP"
    if any(0xAC00 <= ord(c) <= 0xD7AF for c in text):
        return "Noto Sans CJK KR"
    if any(0x0370 <= ord(c) <= 0x04FF for c in text):   # Kiril / Yunan
        return "DejaVu Sans"
    if any(0x0590 <= ord(c) <= 0x06FF for c in text):   # İbranice / Arapça
        return "DejaVu Sans"
    return D.CAPTION_FONT


def _wrap(ctx, text, max_w):
    words, lines, cur = text.split(), [], ""
    for wd in words:
        trial = (cur + " " + wd).strip()
        if text_width(ctx, trial) > max_w and cur:
            lines.append(cur)
            cur = wd
        else:
            cur = trial
    lines.append(cur)
    return lines


def draw_quote_card(ctx, p, k):
    """Sözün orijinali + okunuşu + Türkçesi. k: 0..1 giriş animasyonu."""
    if k <= 0:
        return
    e = D.elastic(min(1.0, k))
    cx, cy = sx(p.get("x", 0.5)), sy(p.get("y", 0.42))
    w = 860
    orig, roman, tr = p.get("original", ""), p.get("roman", ""), p.get("tr", "")
    # yükseklik hesabı
    set_font(ctx, D.CAPTION_FONT, 52, bold=True)
    tr_lines = _wrap(ctx, "“" + tr + "”", w - 100)
    of = _font_for(orig)
    osize = 78 if of.startswith("Noto") else 58
    ctx.select_font_face(of, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(osize)
    o_lines = _wrap(ctx, orig, w - 80) if " " in orig else [orig]
    h = 70 + len(o_lines) * (osize + 18) + (50 if roman else 0) + 40 + len(tr_lines) * 64 + 40
    ctx.save()
    ctx.translate(cx, cy)
    ctx.scale(e, e)
    ctx.translate(-cx, -cy)
    x, y = cx - w / 2, cy - h / 2
    # gölge + kart
    rounded_rect(ctx, x + 10, y + 14, w, h, 30)
    ctx.set_source_rgba(0, 0, 0, 0.35)
    ctx.fill()
    rounded_rect(ctx, x, y, w, h, 30)
    stroke_fill(ctx, (0.99, 0.96, 0.88), GOLD, 8)
    # tırnak süsü
    set_font(ctx, D.TITLE_FONT, 120)
    ctx.set_source_rgba(*GOLD, 0.35)
    ctx.move_to(x + 24, y + 110)
    ctx.show_text("“")
    yy = y + 60
    ctx.select_font_face(of, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(osize)
    ctx.set_source_rgb(*DARK)
    for ln in o_lines:
        yy += osize + 4
        tw = text_width(ctx, ln)
        ctx.move_to(cx - tw / 2, yy)
        ctx.show_text(ln)
        yy += 14
    if roman:
        ctx.select_font_face(D.CAPTION_FONT, cairo.FONT_SLANT_ITALIC, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(36)
        ctx.set_source_rgb(0.40, 0.40, 0.40)
        tw = text_width(ctx, roman)
        ctx.move_to(cx - tw / 2, yy + 40)
        ctx.show_text(roman)
        yy += 50
    line(ctx, (cx - 120, yy + 24), (cx + 120, yy + 24), GOLD, 4)
    yy += 40
    set_font(ctx, D.CAPTION_FONT, 52, bold=True)
    ctx.set_source_rgb(0.04, 0.33, 0.24)
    for ln in tr_lines:
        yy += 64
        tw = text_width(ctx, ln)
        ctx.move_to(cx - tw / 2, yy - 10)
        ctx.show_text(ln)
    ctx.restore()


def draw_stamp(ctx, p, k, t):
    """Pasaport damgası: büyükten küçülerek 'güm' diye iner."""
    if k <= 0:
        return
    s = 2.4 - 1.4 * D.ease_out(min(1.0, k / 0.25))
    alpha = min(1.0, k / 0.12)
    cx, cy = sx(p.get("x", 0.5)), sy(p.get("y", 0.5))
    col = tuple(p.get("color", RED_STAMP))
    ctx.save()
    ctx.translate(cx, cy)
    ctx.rotate(math.radians(p.get("rot", -12)))
    ctx.scale(s * p.get("scale", 1.0), s * p.get("scale", 1.0))
    ctx.set_source_rgba(*col, 0.88 * alpha)
    ctx.set_line_width(10)
    ctx.arc(0, 0, 150, 0, 2 * math.pi)
    ctx.stroke()
    ctx.set_line_width(4)
    ctx.arc(0, 0, 126, 0, 2 * math.pi)
    ctx.stroke()
    set_font(ctx, D.CAPTION_FONT, 50, bold=True)
    txt = D.tr_upper(p.get("text", ""))
    while text_width(ctx, txt) > 220:
        ctx.set_font_size(ctx.get_font_matrix().xx - 2)
    tw = text_width(ctx, txt)
    ctx.move_to(-tw / 2, 18)
    ctx.show_text(txt)
    set_font(ctx, D.CAPTION_FONT, 24, bold=True)
    sub = p.get("sub", "PARA ATLASI")
    tw = text_width(ctx, sub)
    ctx.move_to(-tw / 2, -50)
    ctx.show_text(sub)
    sub2 = p.get("sub2", "✓ ZİYARET EDİLDİ")
    tw = text_width(ctx, sub2)
    ctx.move_to(-tw / 2, 78)
    ctx.show_text(sub2)
    for i in range(2):
        _star(ctx, (-1 if i == 0 else 1) * 95, 8, 12)
        ctx.fill()
    ctx.restore()


def draw_coin(ctx, x, y, r, t, spin=True, symbol="₺"):
    """Altın sikke; spin ile kendi ekseninde döner gibi daralır."""
    sxk = abs(math.cos(t * 4)) * 0.85 + 0.15 if spin else 1.0
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(sxk, 1)
    ctx.arc(0, 0, r, 0, 2 * math.pi)
    stroke_fill(ctx, GOLD, GOLD_DARK, max(2, r * 0.12))
    ctx.arc(0, 0, r * 0.72, 0, 2 * math.pi)
    ctx.set_source_rgb(*GOLD_DARK)
    ctx.set_line_width(max(1.5, r * 0.06))
    ctx.stroke()
    if sxk > 0.45:
        ctx.select_font_face("DejaVu Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(r * 0.9)
        tw = text_width(ctx, symbol)
        ctx.set_source_rgb(*GOLD_DARK)
        ctx.move_to(-tw / 2, r * 0.32)
        ctx.show_text(symbol)
    ctx.arc(-r * 0.35, -r * 0.35, r * 0.15, 0, 2 * math.pi)
    ctx.set_source_rgba(1, 1, 1, 0.5)
    ctx.fill()
    ctx.restore()


def draw_coin_stack(ctx, x, y, n, r=46):
    for i in range(n):
        yy = y - i * r * 0.32
        ctx.save()
        ctx.translate(x, yy)
        ctx.scale(1, 0.35)
        ctx.arc(0, 0, r, 0, 2 * math.pi)
        ctx.restore()
        stroke_fill(ctx, GOLD, GOLD_DARK, 3)


def draw_banknote(ctx, x, y, s, rot=0.0, symbol="₺"):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    ctx.scale(s, s)
    rounded_rect(ctx, -110, -55, 220, 110, 10)
    stroke_fill(ctx, (0.55, 0.78, 0.55), (0.12, 0.35, 0.18), 4)
    rounded_rect(ctx, -96, -42, 192, 84, 8)
    ctx.set_source_rgb(0.12, 0.35, 0.18)
    ctx.set_line_width(2)
    ctx.stroke()
    ctx.arc(0, 0, 28, 0, 2 * math.pi)
    stroke_fill(ctx, (0.75, 0.90, 0.72), (0.12, 0.35, 0.18), 2)
    ctx.select_font_face("DejaVu Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(34)
    tw = text_width(ctx, symbol)
    ctx.set_source_rgb(0.12, 0.35, 0.18)
    ctx.move_to(-tw / 2, 12)
    ctx.show_text(symbol)
    ctx.restore()


def draw_wallet(ctx, x, y, s, t, empty=False):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    if not empty:
        for i in range(3):
            draw_banknote(ctx, -10 + i * 14, -70 - i * 6, 0.55, rot=-0.15 + i * 0.12)
    rounded_rect(ctx, -110, -80, 220, 140, 22)
    stroke_fill(ctx, (0.45, 0.28, 0.16), DARK, 5)
    rounded_rect(ctx, 30, -40, 90, 60, 14)
    stroke_fill(ctx, (0.55, 0.35, 0.20), DARK, 4)
    ctx.arc(70, -10, 9, 0, 2 * math.pi)
    stroke_fill(ctx, GOLD, DARK, 2)
    if empty:  # boş cüzdandan uçan güve (espri)
        mx, my = -20 + 40 * math.sin(t * 2), -150 - 25 * math.sin(t * 3)
        for side in (-1, 1):
            ctx.save()
            ctx.translate(mx, my)
            ctx.scale(side, 1)
            ctx.move_to(0, 0)
            ctx.curve_to(18, -26 * abs(math.sin(t * 12)) - 6, 40, -10, 30, 10)
            ctx.close_path()
            ctx.restore()
            stroke_fill(ctx, (0.85, 0.82, 0.75), DARK, 2)
        ctx.arc(mx, my, 5, 0, 2 * math.pi)
        stroke_fill(ctx, (0.4, 0.35, 0.3), DARK, 1.5)
    ctx.restore()


def draw_piggy(ctx, x, y, s, t):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    for lx in (-60, -25, 30, 60):
        ctx.rectangle(lx - 12, 40, 24, 45)
        stroke_fill(ctx, (0.95, 0.62, 0.70), DARK, 4)
    ctx.save()
    ctx.scale(1.25, 1)
    ctx.arc(0, 0, 95, 0, 2 * math.pi)
    ctx.restore()
    stroke_fill(ctx, (0.97, 0.70, 0.77), DARK, 5)
    ctx.save()
    ctx.translate(122, 5)
    ctx.scale(0.7, 1)
    ctx.arc(0, 0, 32, 0, 2 * math.pi)
    ctx.restore()
    stroke_fill(ctx, (0.95, 0.60, 0.68), DARK, 4)
    for nx in (114, 130):
        ctx.arc(nx, 5, 5, 0, 2 * math.pi)
        ctx.set_source_rgb(*DARK)
        ctx.fill()
    ctx.move_to(40, -80)
    ctx.line_to(70, -125)
    ctx.line_to(85, -72)
    ctx.close_path()
    stroke_fill(ctx, (0.97, 0.70, 0.77), DARK, 4)
    ctx.arc(70, -30, 8, 0, 2 * math.pi)
    ctx.set_source_rgb(*DARK)
    ctx.fill()
    ctx.rectangle(-30, -96, 60, 10)
    ctx.set_source_rgb(*DARK)
    ctx.fill()
    ctx.restore()


def draw_goldbars(ctx, x, y, s):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    rows = [(-130, 0), (-40, 0), (50, 0), (-85, -55), (5, -55), (-40, -110)]
    for bx, by in rows:
        ctx.move_to(bx, by)
        ctx.line_to(bx + 90, by)
        ctx.line_to(bx + 78, by - 50)
        ctx.line_to(bx + 12, by - 50)
        ctx.close_path()
        stroke_fill(ctx, GOLD, GOLD_DARK, 4)
        ctx.move_to(bx + 18, by - 44)
        ctx.line_to(bx + 40, by - 44)
        ctx.set_source_rgba(1, 1, 1, 0.6)
        ctx.set_line_width(4)
        ctx.stroke()
    ctx.restore()


def draw_globe(ctx, x, y, r, t, pin=None):
    """Dönen dünya küresi; pin=(enlem, boylam) verilirse iğne batar."""
    ctx.save()
    ctx.arc(x, y, r, 0, 2 * math.pi)
    ctx.clip_preserve()
    ctx.set_source_rgb(0.15, 0.45, 0.65)
    ctx.fill()
    rot = t * 0.4
    # basit kıta lekeleri (dekoratif)
    blobs = [(-0.3, 0.3, 0.35, 0.25), (0.4, 0.2, 0.3, 0.4), (0.1, -0.4, 0.25, 0.2), (-0.5, -0.2, 0.2, 0.3), (0.8, -0.3, 0.3, 0.2)]
    for bx, by, bw, bh in blobs:
        px = ((bx + rot) % 2.4) - 1.2
        ctx.save()
        ctx.translate(x + px * r, y + by * r)
        ctx.scale(bw * r, bh * r)
        ctx.arc(0, 0, 1, 0, 2 * math.pi)
        ctx.restore()
        ctx.set_source_rgb(0.30, 0.65, 0.35)
        ctx.fill()
    ctx.restore()
    for k in (-0.5, 0, 0.5):
        ctx.save()
        ctx.translate(x, y)
        ctx.scale(1, 1)
        ctx.move_to(-r * math.cos(math.asin(k)), k * r)
        ctx.line_to(r * math.cos(math.asin(k)), k * r)
        ctx.restore()
        ctx.set_source_rgba(1, 1, 1, 0.35)
        ctx.set_line_width(2)
        ctx.stroke()
    ctx.arc(x, y, r, 0, 2 * math.pi)
    ctx.set_source_rgb(*GOLD)
    ctx.set_line_width(5)
    ctx.stroke()
    if pin:
        px, py, k = pin
        e = D.ease_out(min(1.0, k / 0.3))
        top = y - r - 150
        ty = top + (py - top) * e
        line(ctx, (px, ty), (px, ty - 60), (0.85, 0.85, 0.88), 6)
        ctx.arc(px, ty - 70, 18, 0, 2 * math.pi)
        stroke_fill(ctx, RED_STAMP, DARK, 3)


# --------------------------------------------------------------------------

def draw_prop_para(ctx, p, st, ink, voice_delay=0.12, voice_dur=5.0):
    tp = p["type"]
    if "delay" in p:
        t0 = p["delay"]
    elif "f" in p:
        t0 = voice_delay + p["f"] * voice_dur
    else:
        t0 = 0.0
    k = st - t0
    if k < 0:
        return tp in ("quote", "stamp", "cflag", "coin", "coins", "banknote", "wallet", "piggy", "goldbars", "globe",
                      "fis", "rakam", "tabela")
    if tp in ("fis", "rakam", "tabela"):
        from . import props_dukkan as PD
        if tp == "fis":
            PD.draw_fis(ctx, p, st, t0, voice_delay, voice_dur)
        elif tp == "rakam":
            PD.draw_rakam(ctx, p, k)
        else:
            PD.draw_tabela(ctx, p.get("text", ""), k)
        return True
    x, y = p.get("x", 0.5), p.get("y", 0.9)
    if "to_x" in p or "to_y" in p:
        u = D.ease_in_out((st - p.get("move_start", t0)) / p.get("move_dur", 2.0))
        x = x + (p.get("to_x", x) - x) * u
        y = y + (p.get("to_y", y) - y) * u - p.get("arc", 0) * math.sin(math.pi * u)
    s = p.get("scale", 1.0)
    if tp == "quote":
        draw_quote_card(ctx, p, k / 0.45)
    elif tp == "stamp":
        draw_stamp(ctx, p, k, st)
    elif tp == "cflag":
        draw_flag_on_pole(ctx, p.get("code", ""), sx(x), sy(y), s, st)
    elif tp == "coin":
        draw_coin(ctx, sx(x), sy(y), 50 * s, st + p.get("phase", 0), p.get("spin", True), p.get("symbol", "₺"))
    elif tp == "coins":
        draw_coin_stack(ctx, sx(x), sy(y), p.get("n", 6), 46 * s)
    elif tp == "banknote":
        draw_banknote(ctx, sx(x), sy(y), s, p.get("rot", 0.0) + (0.3 * math.sin(st * 3) if p.get("flutter") else 0),
                      p.get("symbol", "₺"))
    elif tp == "wallet":
        draw_wallet(ctx, sx(x), sy(y), s, st, p.get("empty", False))
    elif tp == "piggy":
        draw_piggy(ctx, sx(x), sy(y), s, st)
    elif tp == "goldbars":
        draw_goldbars(ctx, sx(x), sy(y), s)
    elif tp == "globe":
        pin = None
        if "pin" in p:
            pin = (sx(p["pin"][0]), sy(p["pin"][1]), st - p.get("pin_delay", 0.5))
        draw_globe(ctx, sx(x), sy(y), 230 * s, st, pin)
    else:
        return False
    return True
