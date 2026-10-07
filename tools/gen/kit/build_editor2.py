"""배치판 2판 HTML — kit.json · 시트 그림을 data URI 로 넣어 파일 하나로. 내 컴퓨터용(문서 전체)과 아티팩트용(본문만)."""
import json, base64, io, re, os
from PIL import Image
from fontTools import subset
from fontTools.ttLib import TTFont
HERE = os.path.dirname(os.path.abspath(__file__)) + "/"
OUT2 = HERE + "out2/"; OUT1 = HERE + "out/"
GAL = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fonts", "Galmuri11.woff")
def png_uri(path):
    buf = io.BytesIO(); Image.open(path).save(buf, "PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()
kit = json.load(open(OUT2 + "props.json", encoding="utf-8"))
for k, o in kit["objects"].items(): o["src"] = png_uri(OUT2 + o["file"])
kit["desk"].update(bg=png_uri(OUT1 + "desk_bg.png"), vignette=png_uri(OUT1 + "vignette.png"))
kit["frame"] = png_uri(OUT1 + "frame_1x.png")
kit["menuimg"] = png_uri(HERE + "out3/menu_ref.png")                 # 마을 화면에서 오린 메뉴판 (참고 그림)
kit["layout"] = json.load(open(OUT2 + "layout.json", encoding="utf-8"))
kit["note"] = kit["layout"]["note"]
v1 = json.load(open(OUT1 + "props.json", encoding="utf-8"))
kit["v1"] = {k: [v["ax"], v["ay"]] for k, v in v1.items()}
tpl = open(HERE + "editor2_template.html", encoding="utf-8").read()
heads = re.findall(r"<h1>(.*?)</h1>|<h2[^>]*>([^<]*)", tpl)
text = "".join(a + b for a, b in heads) + "JSON 불러오기0123456789"
f = TTFont(GAL); o = subset.Options(); o.flavor = "woff2"; o.layout_features = []
s = subset.Subsetter(o); s.populate(text="".join(sorted(set(text)))); s.subset(f); f.flavor = "woff2"
buf = io.BytesIO(); f.save(buf)
gal = "data:font/woff2;base64," + base64.b64encode(buf.getvalue()).decode()
body = tpl.replace("__GALMURI__", gal).replace("/*__KIT__*/null", json.dumps(kit, ensure_ascii=False, separators=(",", ":")))
open(OUT2 + "desk_editor_artifact.html", "w", encoding="utf-8").write(body)
head_end = body.index("</style>") + len("</style>")
full = ("<!doctype html>\n<html lang=\"ko\">\n<head>\n<meta charset=\"utf-8\">\n<meta name=\"viewport\" content=\"width=device-width, initial-scale=1, viewport-fit=cover\">\n"
        + body[:head_end] + "\n</head>\n<body>\n" + body[head_end:] + "\n</body>\n</html>\n")
open(OUT2 + "desk_editor.html", "w", encoding="utf-8").write(full)
print("artifact", len(body) // 1024, "KB")
