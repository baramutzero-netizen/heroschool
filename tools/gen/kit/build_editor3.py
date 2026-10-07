"""스케줄 배치판(3판) HTML — props.json · 그림을 data URI 로 넣어 파일 하나로. 내 컴퓨터용(문서 전체)과 아티팩트용(본문만)."""
import json, base64, io, re, os
from PIL import Image
from fontTools import subset
from fontTools.ttLib import TTFont
HERE = os.path.dirname(os.path.abspath(__file__)) + "/"
OUT3 = HERE + "out3/"
MUL = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fonts", "mulmaru.woff2")
def png_uri(path):
    buf = io.BytesIO(); Image.open(path).save(buf, "PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()
kit = json.load(open(OUT3 + "props.json", encoding="utf-8"))
for k, o in kit["objects"].items(): o["src"] = png_uri(OUT3 + o["file"])
kit["deskbg"] = png_uri(OUT3 + "desk_bg.png")
kit["frame"] = png_uri(OUT3 + "frame_1x.png")
kit["menuimg"] = png_uri(OUT3 + "menu_ref.png")
kit["layout"] = json.load(open(OUT3 + "layout.json", encoding="utf-8"))
kit["note"] = kit["layout"]["note"]
tpl = open(HERE + "editor3_template.html", encoding="utf-8").read()
heads = re.findall(r"<h1>(.*?)</h1>|<h2[^>]*>(?:<b>)?([^<]*)", tpl)
text = "".join(a + b for a, b in heads) + "JSON 불러오기0123456789"
f = TTFont(MUL); o = subset.Options(); o.flavor = "woff2"; o.layout_features = []
s = subset.Subsetter(o); s.populate(text="".join(sorted(set(text)))); s.subset(f); f.flavor = "woff2"
buf = io.BytesIO(); f.save(buf)
mul = "data:font/woff2;base64," + base64.b64encode(buf.getvalue()).decode()
body = tpl.replace("__MULMARU__", mul).replace("/*__KIT__*/null", json.dumps(kit, ensure_ascii=False, separators=(",", ":")))
open(OUT3 + "schedule_editor_artifact.html", "w", encoding="utf-8").write(body)
head_end = body.index("</style>") + len("</style>")
full = ("<!doctype html>\n<html lang=\"ko\">\n<head>\n<meta charset=\"utf-8\">\n<meta name=\"viewport\" content=\"width=device-width, initial-scale=1, viewport-fit=cover\">\n"
        + body[:head_end] + "\n</head>\n<body>\n" + body[head_end:] + "\n</body>\n</html>\n")
open(OUT3 + "schedule_editor.html", "w", encoding="utf-8").write(full)
print("artifact", len(body) // 1024, "KB", "· font chars", len(set(text)))
