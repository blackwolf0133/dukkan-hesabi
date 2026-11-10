"""001 şablonundan yeni bölüm JSON'u üretir (8 sahne, aynı yapı). Kullanım: tools/bolum_uret.py içindeki BOLUMLER listesine ekle, çalıştır."""
import copy
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def ep(b):
    d = copy.deepcopy(json.load(open(os.path.join(ROOT, "episodes", "001_berber.json"), encoding="utf-8")))
    d.update(id=b["id"], title=b["title"], country={"name": b["tag"]}, kaynaklar=b["src"], instagram_caption=b["caption"])
    S = d["scenes"]
    S[0]["say"] = S[0]["text"] = b["kanca"]
    S[0]["props"][0]["text"] = b["tag"].upper() + "!"
    S[1]["say"], S[1]["text"] = b["fiyat"]
    S[1]["props"][0]["text"] = b["tabela"]
    S[1]["props"][1].update(b["r_fiyat"])
    S[2]["say"], S[2]["text"] = b["ciro"]
    S[2]["props"][0].update(b["r_ciro"])
    S[3]["say"], S[3]["text"] = b["gider"]
    S[3]["props"][0]["rows"] = b["rows"]
    S[3]["props"][0]["total"] = b["total"]
    S[4]["say"], S[4]["text"] = b["sok"]
    S[4]["props"][0]["text"] = b["tabela"]
    S[4]["props"][1].update(b["r_sok"])
    S[5]["say"], S[5]["text"] = b["ters"]
    S[5]["props"][0].update(b["r_ters"][0])
    S[5]["props"][1].update(b["r_ters"][1])
    S[6]["say"], S[6]["text"] = b["ders"]
    S[6]["props"][0]["text"] = b["tabela"]
    S[6]["props"][1]["text"] = b["pop_ders"]
    S[7]["say"], S[7]["text"] = b["kapanis"]
    S[7]["props"][0]["text"] = b["pop_yarin"]
    tot = sum(r["tutar"] for r in b["rows"])
    assert tot == b["total"]["tutar"], (b["id"], tot, b["total"]["tutar"])
    out = os.path.join(ROOT, "episodes", f"{b['id']}_{b['slug']}.json")
    json.dump(d, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(b["id"], len(S), "sahne,", sum(len(s["say"].split()) for s in S), "kelime, toplam tutarlı:", tot)


if __name__ == "__main__":
    for b in json.load(open(sys.argv[1], encoding="utf-8")):
        ep(b)
