# -*- coding: utf-8 -*-
"""victory.png(여러 명이 든 시트) + victory_<직업>.png(단독) 을 승리 포즈로 굽는다.
   시트는 덩어리로 잘라 왼쪽 위부터 SHEET_ORDER 순서로 직업을 붙인다.
   실행:  python victory.py        (sprites/ 안에서)
"""
import io, os, json, base64, re
from PIL import Image
import numpy as np
from scipy import ndimage

HERE  = os.path.dirname(os.path.abspath(__file__))
SRC   = os.path.join(HERE, "src")
OUTJS = os.path.join(HERE, "victory.js")
GAME  = os.path.join(os.path.dirname(HERE), "game.html")
H     = 210     # 굽는 높이 (가로는 비율대로)
QUAL  = 86      # WebP 품질 · 0 이면 무손실
PAD   = 6       # 잘라낼 때 남길 여백
MIN_A = 3000    # 이보다 작은 덩어리는 사람이 아니다

# victory.png 안에서 왼쪽 위부터 읽어 나가는 순서
SHEET_ORDER = ["paladin","rogue","forcemage","ninja","spellsword","druid","sword","gunner",
               "darkpriest","priest","monk","wizard","archer","bard","enchanter"]

def bake(im):
    b = im.split()[-1].getbbox()
    if b: im = im.crop(b)
    w = max(1, round(im.width*H/im.height))
    im = im.resize((w, H), Image.LANCZOS)
    buf = io.BytesIO()
    if QUAL: im.save(buf,"WEBP",quality=QUAL,method=6)
    else:    im.save(buf,"WEBP",lossless=True,method=6)
    return base64.b64encode(buf.getvalue()).decode(), im.size

def cutSheet(path):
    im = Image.open(path).convert("RGBA")
    a = np.asarray(im)[...,3] > 16
    lab,n = ndimage.label(a)
    boxes = [s for s in ndimage.find_objects(lab)
             if s and (s[0].stop-s[0].start)*(s[1].stop-s[1].start) > MIN_A]
    if not boxes: return []
    # 줄 나누기 — 세로로 겹치지 않는 덩어리끼리 한 줄
    boxes.sort(key=lambda s: s[0].start)
    rows=[]; 
    for s in boxes:
        for r in rows:
            if s[0].start < r[0][0].stop: r.append(s); break
        else: rows.append([s])
    out=[]
    for r in rows:
        r.sort(key=lambda s: s[1].start)
        for s in r:
            out.append(im.crop((max(0,s[1].start-PAD), max(0,s[0].start-PAD),
                                min(im.width, s[1].stop+PAD), min(im.height, s[0].stop+PAD))))
    return out

def main():
    out={}; tot=0
    sheet = os.path.join(SRC, "victory.png")
    if os.path.exists(sheet):
        cuts = cutSheet(sheet)
        if len(cuts) != len(SHEET_ORDER):
            print(f"※ 시트에서 {len(cuts)}명을 찾았는데 SHEET_ORDER 는 {len(SHEET_ORDER)}명이다 — 순서를 확인해라")
        for job, c in zip(SHEET_ORDER, cuts):
            b64, sz = bake(c); out[job] = "data:image/webp;base64,"+b64; tot += len(b64)
            print(f"{job:11s} 시트 {sz[0]}x{sz[1]} · {len(b64)/1024:.0f}KB")
    # 단독 파일이 있으면 그쪽이 우선
    for f in sorted(os.listdir(SRC)):
        m = re.match(r'^victory_([a-z]+)\.png$', f)
        if not m: continue
        job = m.group(1)
        b64, sz = bake(Image.open(os.path.join(SRC,f)).convert("RGBA"))
        if job in out: tot -= len(out[job])
        out[job] = "data:image/webp;base64,"+b64; tot += len(b64)
        print(f"{job:11s} 단독 {sz[0]}x{sz[1]} · {len(b64)/1024:.0f}KB")
    js = "const VICT_IMG=%s;\n" % json.dumps(out, separators=(",",":"))
    io.open(OUTJS,"w",encoding="utf-8").write(js)
    src = io.open(GAME,encoding="utf-8").read()
    if re.search(r'^const VICT_IMG=.*$', src, re.M):
        src = re.sub(r'^const VICT_IMG=.*$', js.rstrip("\n"), src, count=1, flags=re.M)
    else:
        i = src.index("const FIELD_IMG="); j = src.index("\n", i)+1
        src = src[:j] + js + src[j:]
    io.open(GAME,"w",encoding="utf-8").write(src)
    print(f"→ {OUTJS} · game.html 반영 · {len(out)}명 · 합계 {tot/1024:.0f}KB")

main()
