"""Bir bölümün her sahnesinden önizleme karesi çıkarır (kontrol için)."""
import json, sys, os, cairo
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from engine import render as R, draw as D, theme_para as T
from PIL import Image
ep = json.load(open(sys.argv[1])); out = sys.argv[2]
paper = T.make_paper(); header = T.make_header(ep, paper)
surf = cairo.ImageSurface(cairo.FORMAT_RGB24, D.W, D.H); ctx = cairo.Context(surf)
ims = []
for sc in ep["scenes"]:
    vd = 5.5; t = float(sys.argv[3]) if len(sys.argv) > 3 else 4.0
    ctx.set_source_surface(header); ctx.paint()
    R.draw_scene(ctx, sc, t, vd + 1, vd)
    T.draw_country_tag(ctx, ep.get("country"))
    R.draw_caption(ctx, R.chunk_words(R.word_timings(sc["text"], vd), ctx), t - sc.get("voice_delay", 0.12))
    surf.write_to_png("/tmp/_c.png")
    ims.append(Image.open("/tmp/_c.png").crop((0, 120, 1080, 1560)).resize((300, 400)))
n = len(ims); cols = 5; rows = (n + cols - 1) // cols
sheet = Image.new("RGB", (300 * cols, 400 * rows), "white")
for i, im in enumerate(ims): sheet.paste(im, ((i % cols) * 300, (i // cols) * 400))
sheet.save(out)
