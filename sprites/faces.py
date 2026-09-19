# -*- coding: utf-8 -*-
"""original_<직업>.png 에서 얼굴만 잘라 FACE_IMG 로 굽는다.
   - 배경(초록 화면·바둑판 무늬)은 테두리부터 번져 들어가며 지운다
   - 얼굴 위치는 살구빛 덩어리로 찾고, 어긋나는 몇은 TUNE 으로 직접 잡는다
   실행:  python faces.py        (sprites/ 안에서)
"""
import io, os, json, base64
from collections import deque, Counter
from PIL import Image
import numpy as np
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
SRC  = os.path.join(HERE, "src")
FSRC = os.path.join(HERE, "face_src")   # 얼굴 전용 원본 — 있으면 original_*.png 보다 우선한다
OUTJS= os.path.join(HERE, "faces.js")
GAME = os.path.join(os.path.dirname(HERE), "game.html")
SIZE = 128            # 굽는 크기 (정사각)
# face_src/ 는 전투 시트에서 뽑은 128px 칸 — 확대하므로 도트가 뭉개지지 않게 NEAREST 로 키운다

JOBS = ["paladin","sword","monk","druid","archer","rogue","wizard","forcemage",
        "spellsword","gunner","ninja","priest","darkpriest","timemage","enchanter","bard"]

# 자동 검출이 빗나가는 그림만 직접 잡는다 — box:[왼쪽, 위, 한 변] (원본 좌표)
# 아래 좌표는 face_src/<job>.png (128px 칸) 기준이다.
TUNE = {
  "wizard":     {"box":[32,14,64]},   # 모자가 커서 살색 덩어리를 못 찾는다
  "darkpriest": {"box":[40, 8,60]},   # 머리카락에 얼굴이 묻힌다
  "timemage":   {"box":[34,14,64]},   # 눈만 잡혀 지나치게 확대된다
  "bard":       {"box":[56,18,62]},   # 모자 깃털을 얼굴로 착각한다
}

def _near(c,d,tol): return max(abs(c[0]-d[0]),abs(c[1]-d[1]),abs(c[2]-d[2]))<=tol
def _green(c): return c[1]>150 and c[1]>c[0]*1.6 and c[1]>c[2]*1.6

def declutter(im):
    """테두리에 배경이 칠해져 있으면 번져 들어가며 지운다"""
    w,h = im.size; px = im.load()
    samples=[]
    for x in range(0,w,5): samples += [px[x,0],px[x,h-1]]
    for y in range(0,h,5): samples += [px[0,y],px[w-1,y]]
    if sum(1 for s in samples if s[3]>10) < len(samples)*.5: return "투명"
    cnt = Counter(s[:3] for s in samples if s[3]>10)
    tot = sum(cnt.values())
    bgs = [c for c,n in cnt.most_common(6) if n >= tot*0.035]
    green = any(_green(c) for c in bgs)
    tol = 30
    seen = bytearray(w*h); q = deque()
    def ok(c): return c[3]>10 and (any(_near(c,b,tol) for b in bgs) or (green and _green(c)))
    def push(x,y):
        i=y*w+x
        if seen[i]: return
        if ok(px[x,y]): seen[i]=1; q.append((x,y))
    for x in range(w): push(x,0); push(x,h-1)
    for y in range(h): push(0,y); push(w-1,y)
    while q:
        x,y=q.popleft(); px[x,y]=(0,0,0,0)
        for nx,ny in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
            if 0<=nx<w and 0<=ny<h: push(nx,ny)
    if green:                      # 머리카락 사이에 갇힌 초록 자국
        for y in range(h):
            for x in range(w):
                c=px[x,y]
                if c[3]>10 and _green(c): px[x,y]=(0,0,0,0)
    elif len(bgs)>=2 and all(max(b)-min(b)<=5 for b in bgs):   # 바둑판 무늬
        for y in range(h):
            for x in range(w):
                c=px[x,y]; mx=max(c[:3]); mn=min(c[:3])
                if c[3]>10 and (mx-mn)<=5 and (198<=mx<=238 or mx>=246): px[x,y]=(0,0,0,0)
    return "초록" if green else "단색"

def faceBox(im, job):
    bb = im.split()[-1].getbbox(); x0,y0,x1,y1 = bb; H = y1-y0
    t = TUNE.get(job,{})
    if t.get("box"):
        L,T,SD = t["box"]; return (L,T,L+SD,T+SD)
    a = np.asarray(im, dtype=np.int16)
    r,g,b,al = a[...,0],a[...,1],a[...,2],a[...,3]
    mx = np.maximum(np.maximum(r,g),b); mn = np.minimum(np.minimum(r,g),b)
    sat = np.where(mx>0,(mx-mn)/np.maximum(mx,1),0)
    hue = np.zeros_like(sat, dtype=float); d = np.maximum(mx-mn,1)
    isR = (mx==r); isG = (mx==g)&~isR; isB = (~isR)&(~isG)
    hue[isR] = (((g-b)[isR]/d[isR])%6)*60
    hue[isG] = (((b-r)[isG]/d[isG])+2)*60
    hue[isB] = (((r-g)[isB]/d[isB])+4)*60
    skin = (al>80)&(mx>100)&(sat>0.14)&(sat<0.62)&(hue>=8)&(hue<=42)&(r>g)&(g>=b)
    skin[y0+int(H*0.45):,:] = False; skin[:y0,:] = False
    lab,n = ndimage.label(skin)
    if n==0:
        cx=(x0+x1)//2; cy=y0+int(H*.18); fw=H*0.2
    else:
        sizes = ndimage.sum(skin, lab, range(1,n+1))
        ys,xs = np.where(lab==int(np.argmax(sizes))+1)
        cx=int(xs.mean()); cy=int(ys.mean()); fw=xs.max()-xs.min()+1
    W = im.size[0]
    side = int(min(max(fw*t.get("k",2.6), H*0.45), H*0.60))
    cx += int(side*t.get("dx",0)); cy += int(side*t.get("dy",0))
    left = int(cx-side/2); top = int(cy-side*0.50)
    left = max(0, min(left, W-side)); top = max(0, min(top, im.size[1]-side))
    return (left, top, left+side, top+side)

def main():
    out={}; tot=0
    for job in JOBS:
        fp = os.path.join(FSRC, f"{job}.png")
        p  = fp if os.path.exists(fp) else os.path.join(SRC, f"original_{job}.png")
        if not os.path.exists(p): print(f"{job:11s} 원본 없음 — 건너뛴다"); continue
        im = Image.open(p).convert("RGBA")
        how = declutter(im)
        small = (p == fp)
        if small: how = "전용"
        face = im.crop(faceBox(im, job)).resize((SIZE,SIZE), Image.NEAREST if small else Image.LANCZOS)
        buf = io.BytesIO(); face.save(buf,"WEBP",lossless=True,method=6)
        b64 = base64.b64encode(buf.getvalue()).decode()
        out[job] = "data:image/webp;base64,"+b64
        tot += len(b64)
        print(f"{job:11s} {how:3s} 배경 · {len(b64)/1024:.0f}KB")
    js = "const FACE_IMG=%s;\n" % json.dumps(out, separators=(",",":"))
    io.open(OUTJS,"w",encoding="utf-8").write(js)
    # game.html 안의 FACE_IMG 줄을 갈아 끼운다 (없으면 FIELD_IMG 아래에 넣는다)
    src = io.open(GAME,encoding="utf-8").read()
    import re
    if re.search(r'^const FACE_IMG=.*$', src, re.M):
        src = re.sub(r'^const FACE_IMG=.*$', js.rstrip("\n"), src, count=1, flags=re.M)
    else:
        i = src.index("const FIELD_IMG=")
        j = src.index("\n", i)+1
        src = src[:j] + js + src[j:]
    io.open(GAME,"w",encoding="utf-8").write(src)
    print(f"→ {OUTJS} · game.html 반영 · 합계 {tot/1024:.0f}KB ({SIZE}px 무손실 WebP)")

main()
