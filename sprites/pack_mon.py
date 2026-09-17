# -*- coding: utf-8 -*-
"""src/mon_*.png (한 장짜리 정지 그림) 를 모아 game.html 에 박을 MON_IMG 를 만든다.
   애니메이션 프레임은 없다. 캔버스를 그대로 쓰고 정수배로만 확대한다 —
   잘라내지 않으므로 캔버스 안에서의 위치가 그대로 화면 배치가 된다.
   가로가 긴 그림(256x128)과 정사각(128x128)이 섞여도 같은 배율이 걸려
   원화에서 의도한 크기 차이가 그대로 유지된다."""
import os, io, glob, base64, json
from PIL import Image

SRC   = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
OUT   = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mon.js")
MON_K = 2            # 확대 배율 — 128 높이 캔버스가 화면에서 256px 이 된다

def main():
    files = sorted(glob.glob(os.path.join(SRC, "mon_*.png")))
    if not files:
        print("src/ 에 mon_*.png 가 없다 — 건너뛴다")
        io.open(OUT, "w", encoding="utf-8").write("const MON_IMG={};\n")
        return
    out, tot = {}, 0
    for f in files:
        job = os.path.splitext(os.path.basename(f))[0]
        im = Image.open(f).convert("RGBA")
        px = im.load()                                   # 반투명 정리 — 도트는 0/255 만
        for y in range(im.size[1]):
            for x in range(im.size[0]):
                c = px[x,y]
                px[x,y] = (0,0,0,0) if c[3] < 128 else (c[0],c[1],c[2],255)
        w,h = im.size
        buf = io.BytesIO(); im.save(buf, "PNG", optimize=True)
        b64 = base64.b64encode(buf.getvalue()).decode()
        tot += len(b64)
        out[job] = {"w":w, "h":h, "k":MON_K, "src":"data:image/png;base64,"+b64}
        print(f"{job:14s} {w}x{h} ×{MON_K} → 화면 {w*MON_K}x{h*MON_K} · {len(b64)/1024:.1f}KB")
    js = "const MON_IMG=%s;\n" % json.dumps(out, separators=(",",":"), ensure_ascii=False)
    io.open(OUT, "w", encoding="utf-8").write(js)
    print(f"→ {OUT} · 합계 {tot/1024:.1f}KB")

main()
