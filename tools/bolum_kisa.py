"""KISA (13 Kasım) bölüm üretici: 5 sahne, 65-80 kelime, KAZANÇ + AMA kancası, kanca_yazi.

Kullanım: python tools/bolum_kisa.py tools/kisa_bolumler.json
Spec alanları: id, slug, (yeni bölümse) title, tag, caption, kaynaklar; her zaman: tabela, kanca_yazi, kalan,
kanca [say, text], fiyat [say, text, [label, value, kw], [label, value, kw]], gider [say, text],
rows [[ad, tutar, kw|null], ...], ters [say, text, [label, value, color, kw], [label, value, color, kw]],
kapanis [say, text], yarin.
Fiş/rakam `f` değerleri, `kw` kelimesinin `say` içindeki sırasından hesaplanır (docs: Fiş zamanlaması).
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _norm(w):
    return w.strip(".,!?;:…\"'").lower()


def kf(say, kw, onc=0.02):
    """kw ile başlayan ilk kelimenin oranı (biraz önce)."""
    ws = say.split()
    k = kw.lower()
    for i, w in enumerate(ws):
        if _norm(w).startswith(k):
            return round(max(0.0, i / len(ws) - onc), 3)
    raise ValueError(f"'{kw}' bulunamadı: {say}")


def build(b):
    path = os.path.join(ROOT, "episodes", f"{b['id']}_{b['slug']}.json")
    if os.path.exists(path):
        d = json.load(open(path, encoding="utf-8"))
    else:
        d = {"id": b["id"], "series": "DÜKKÂN HESABI", "title": b["title"], "country": {"name": b["tag"]}}
    for k_src, k_dst in (("title", "title"), ("caption", "instagram_caption"), ("kaynaklar", "kaynaklar")):
        if k_src in b:
            d[k_dst] = b[k_src]
    if "tag" in b:
        d["country"] = {"name": b["tag"]}

    ks, kt = b["kanca"]
    fa = kf(ks, "ama", 0.03)
    s1 = {"say": ks, "text": kt, "voice_delay": 0.0, "emotion": "şaşkın", "bg": "dukkan",
          "narrator": {"x": 0.32, "y": 0.97, "scale": 1.05, "pose": "point", "face": "happy",
                       "beats": [{"f": fa, "pose": "think", "face": "think"}]},
          "props": [{"type": "tabela", "text": b["tabela"], "delay": 0.0},
                    {"type": "rakam", "label": "AYDA KALAN", "value": b["kalan"], "color": "green",
                     "x": 0.58, "y": 0.12, "scale": 0.9, "f": 0.0},
                    {"type": "pop", "text": "AMA…", "x": 0.72, "y": 0.45, "size": 120, "f": fa, "rot": -6}]}
    if b.get("kalan_label"):
        s1["props"][1]["label"] = b["kalan_label"]

    fs, ft, r1, r2 = b["fiyat"]
    s2 = {"say": fs, "text": ft, "bg": "kasa",
          "actors": [{"id": "k", "x": 0.18, "pose": "open", "face": "happy", "scale": 1.0}],
          "props": [{"type": "rakam", "label": r1[0], "value": r1[1], "color": "gold",
                     "x": 0.56, "y": 0.18, "scale": 0.8, "f": kf(fs, r1[2])},
                    {"type": "rakam", "label": r2[0], "value": r2[1], "color": "green",
                     "x": 0.56, "y": 0.43, "scale": 0.85, "f": kf(fs, r2[2])}]}

    gs, gt = b["gider"]
    rows = []
    for ad, tutar, kw in b["rows"]:
        rows.append({"ad": ad, "tutar": tutar, "f": 0.0 if kw is None else kf(gs, kw)})
    n = len(gs.split())
    tot = sum(r["tutar"] for r in rows)
    assert tot == b["kalan"], (b["id"], tot, b["kalan"])
    assert len(rows) <= 7 and all(len(r["ad"]) <= 10 for r in rows), b["id"]
    s3 = {"say": gs, "text": gt, "bg": "kasa",
          "actors": [{"id": "k", "x": 0.14, "pose": "think", "face": "think", "scale": 0.9}],
          "props": [{"type": "fis", "title": b.get("fis_baslik", "AYLIK HESAP"), "x": 0.6, "y": 0.47, "scale": 0.9,
                     "rows": rows, "total": {"ad": "KALAN", "tutar": tot, "f": round((n - 1) / n, 3)}}]}

    ts, tt, c1, c2 = b["ters"]
    s4 = {"say": ts, "text": tt, "bg": "kasa", "actors": [],
          "props": [{"type": "rakam", "label": c1[0], "value": c1[1], "color": c1[2],
                     "x": 0.42, "y": 0.2, "scale": 0.85, "f": kf(ts, c1[3])},
                    {"type": "rakam", "label": c2[0], "value": c2[1], "color": c2[2],
                     "x": 0.42, "y": 0.5, "scale": 0.85, "f": kf(ts, c2[3])}]}

    cs, ct = b["kapanis"]
    s5 = {"say": cs, "text": ct, "emotion": "mutlu",
          "narrator": {"x": 0.5, "y": 0.97, "scale": 1.6, "pose": "point", "face": "happy",
                       "beats": [{"f": kf(cs, "yarın", 0.0), "pose": "wave", "face": "wink"}]},
          "props": [{"type": "pop", "text": "YARIN: " + b["yarin"], "x": 0.5, "y": 0.13, "size": 92,
                     "f": kf(cs, "yarın", 0.0), "rot": -4}]}

    d["scenes"] = [s1, s2, s3, s4, s5]
    d["kanca_v2"] = True
    d["kanca_yazi"] = b["kanca_yazi"]
    assert len(b["kanca_yazi"].split()) <= 8, b["kanca_yazi"]
    json.dump(d, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    w = sum(len(s["say"].split()) for s in d["scenes"])
    print(b["id"], b["slug"], "5 sahne,", w, "kelime", "" if 65 <= w <= 80 else "  <-- ARALIK DIŞI", "| kalan", tot)


if __name__ == "__main__":
    for b in json.load(open(sys.argv[1], encoding="utf-8")):
        build(b)
