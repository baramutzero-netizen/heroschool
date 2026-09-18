# -*- coding: utf-8 -*-
"""popup_<계절>.png 을 팝업 머리 그림으로 굽는다.
   실행:  python popups.py        (sprites/ 안에서)
"""
import io, os, json, base64, re
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SRC  = os.path.join(HERE, "src")
OUTJS= os.path.join(HERE, "popups.js")
GAME = os.path.join(os.path.dirname(HERE), "game.html")
WIDTH = 760      # 굽는 가로 크기
QUAL  = 72       # WebP 품질
KEYS  = ["spring","summer","fall","winter","winter3"]

def main():
    out={}; tot=0
    for k in KEYS:
        p = os.path.join(SRC, f"popup_{k}.png")
        if not os.path.exists(p): print(f"{k:8s} 원본 없음 — 건너뛴다"); continue
        im = Image.open(p).convert("RGB")
        h = int(WIDTH*im.size[1]/im.size[0])
        im = im.resize((WIDTH,h), Image.LANCZOS)
        buf = io.BytesIO(); im.save(buf,"WEBP",quality=QUAL,method=6)
        b64 = base64.b64encode(buf.getvalue()).decode()
        out[k] = "data:image/webp;base64,"+b64
        tot += len(b64)
        print(f"{k:8s} {WIDTH}x{h} · {len(b64)/1024:.0f}KB")
    js = "const POPUP_IMG=%s;\n" % json.dumps(out, separators=(",",":"))
    io.open(OUTJS,"w",encoding="utf-8").write(js)
    src = io.open(GAME,encoding="utf-8").read()
    if re.search(r'^const POPUP_IMG=.*$', src, re.M):
        src = re.sub(r'^const POPUP_IMG=.*$', js.rstrip("\n"), src, count=1, flags=re.M)
    else:
        i = src.index("const FIELD_IMG="); j = src.index("\n", i)+1
        src = src[:j] + js + src[j:]
    io.open(GAME,"w",encoding="utf-8").write(src)
    print(f"→ {OUTJS} · game.html 반영 · 합계 {tot/1024:.0f}KB")

main()
