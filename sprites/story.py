# -*- coding: utf-8 -*-
"""프롤로그 · 튜토리얼 그림과 튜토리얼 아이콘을 굽는다.
   실행:  python story.py        (sprites/ 안에서)
"""
import io, os, json, base64, re
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SRC  = os.path.join(HERE, "src")
OUTJS= os.path.join(HERE, "story.js")
GAME = os.path.join(os.path.dirname(HERE), "game.html")

PROL_W, PROL_Q = 820,  74    # 프롤로그 — 장면 그림
TUT_W,  TUT_Q  = 1100, 78    # 튜토리얼 — 글씨가 많아 크게 굽는다
ICON_W, ICON_Q = 200,  92    # 튜토리얼 아이콘
FB_W,   FB_Q   = 260,  90    # 피드백 아이콘

def bake(path, w, q):
    im = Image.open(path).convert("RGB")
    h = int(w*im.size[1]/im.size[0])
    im = im.resize((w,h), Image.LANCZOS)
    buf = io.BytesIO(); im.save(buf,"WEBP",quality=q,method=6)
    b64 = base64.b64encode(buf.getvalue()).decode()
    return "data:image/webp;base64,"+b64, (w,h), len(b64)

def main():
    prol={}; tut={}; icon=None; tot=0
    for i in (1,2,3):
        p = os.path.join(SRC, f"prologue{i}.png")
        if os.path.exists(p):
            prol[str(i)], sz, n = bake(p, PROL_W, PROL_Q); tot += n
            print(f"프롤로그 {i} {sz[0]}x{sz[1]} · {n/1024:.0f}KB")
        p = os.path.join(SRC, f"tutorial{i}.png")
        if os.path.exists(p):
            tut[str(i)], sz, n = bake(p, TUT_W, TUT_Q); tot += n
            print(f"튜토리얼 {i} {sz[0]}x{sz[1]} · {n/1024:.0f}KB")
    p = os.path.join(SRC, "icon_tutorial.png")
    if os.path.exists(p):
        icon, sz, n = bake(p, ICON_W, ICON_Q); tot += n
        print(f"아이콘    {sz[0]}x{sz[1]} · {n/1024:.0f}KB")
    fb = None
    p = os.path.join(SRC, "feedback.png")
    if os.path.exists(p):
        fb, sz, n = bake(p, FB_W, FB_Q); tot += n
        print(f"피드백    {sz[0]}x{sz[1]} · {n/1024:.0f}KB")
    js = ("const PROL_IMG=%s;\nconst TUT_IMG=%s;\nconst TUT_ICON=%s;\nconst FB_ICON=%s;\n" % (
        json.dumps(prol, separators=(",",":")),
        json.dumps(tut, separators=(",",":")),
        json.dumps(icon), json.dumps(fb)))
    io.open(OUTJS,"w",encoding="utf-8").write(js)
    src = io.open(GAME,encoding="utf-8").read()
    for line in js.strip().split("\n"):
        key = line.split("=")[0]                       # const PROL_IMG
        pat = r'^' + re.escape(key) + r'=.*$'
        if re.search(pat, src, re.M): src = re.sub(pat, line, src, count=1, flags=re.M)
        else:
            i = src.index("const FIELD_IMG="); j = src.index("\n", i)+1
            src = src[:j] + line + "\n" + src[j:]
    io.open(GAME,"w",encoding="utf-8").write(src)
    print(f"→ {OUTJS} · game.html 반영 · 합계 {tot/1024:.0f}KB")

main()
