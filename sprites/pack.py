# -*- coding: utf-8 -*-
"""src/<jobid>.png 들을 하나의 아틀라스로 묶고 game.html 에 박을 JS 조각을 만든다.
   시트 규격: 가로 = 프레임, 세로 = 모션 5행 (idle/attack/hit/down/win)
   셀 크기는 세로/5 로 자동 판정한다 (64 든 128 이든 상관없음)."""
import os, io, glob, base64, json, colorsys
from collections import Counter
from PIL import Image

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
ROWS = 5
MOT  = ["idle","attack","hit","down","win"]
# 파일 이름이 게임의 직업 id 와 다를 때 여기서 연결한다
ALIAS = {
    "magician":"wizard", "mage":"wizard", "witch":"wizard",
    "swordman":"sword", "swordsman":"sword", "knight":"paladin",
    "thief":"rogue", "assassin":"rogue", "cleric":"priest",
    "hunter":"archer", "ranger":"archer", "warlock":"darkpriest",
}

def read_sheet(path):
    im = Image.open(path).convert("RGBA")
    W,H = im.size
    if H % ROWS: raise SystemExit(f"{path}: 세로 {H} 가 5행으로 안 나눠떨어진다")
    cell = H // ROWS
    if W % cell: raise SystemExit(f"{path}: 가로 {W} 가 셀 {cell} 로 안 나눠떨어진다")
    cols = W // cell
    px = im.load()
    counts = []
    for r in range(ROWS):
        n = 0
        for c in range(cols):
            hit = False
            for y in range(r*cell, (r+1)*cell):
                for x in range(c*cell, (c+1)*cell):
                    if px[x,y][3] >= 128: hit = True; break
                if hit: break
            if hit: n = c+1          # 왼쪽부터 채운다는 전제 — 마지막 채워진 칸까지
        counts.append(n)
    if counts[0] == 0: raise SystemExit(f"{path}: idle 행이 비어 있다")
    for r in range(1,ROWS):
        if counts[r] == 0: counts[r] = 0   # 비면 idle 로 대체 (런타임에서 처리)
    # 알파 정리 — 반투명은 버린다
    for y in range(H):
        for x in range(W):
            c = px[x,y]
            px[x,y] = (0,0,0,0) if c[3] < 128 else (c[0],c[1],c[2],255)
    return im, cell, cols, counts

HAIR_BAND = .42     # 캐릭터 bbox 위에서부터 이 비율까지가 "머리 쪽"
HAIR_DH   = .055    # 같은 머리색으로 볼 색상(hue) 차이 (0~.5)
HAIR_TOP  = .25     # 그 색의 픽셀 중 머리 쪽에 있어야 하는 최소 비율
def hair_colors(im, cell):
    """머리색 자동 검출.
       1) idle 행에서 캐릭터 bbox 를 잡고 위 42% 를 '머리 쪽'으로 본다
       2) 머리 쪽에 많이 깔린 채도 있는 색 하나를 기준으로 삼고
       3) 그 색상(hue) 가까이 있으면서 머리 쪽에 몰려 있는 색만 고른다
       피부·가죽·갑옷은 색상이 다르거나 아래쪽에 몰려 있어 걸러진다."""
    W,H = im.size
    reg = im.crop((0,0,W,cell))
    bb = reg.getbbox()
    if not bb: return [], 0
    x0,y0,x1,y1 = bb
    band = y0 + (y1-y0)*HAIR_BAND
    px = im.load()
    cnt, top = Counter(), Counter()
    for y in range(y0,y1):
        for x in range(x0,x1):
            c = px[x,y]
            if c[3] == 0: continue
            cnt[c[:3]] += 1
            if y < band: top[c[:3]] += 1
    if not cnt: return [], 0
    hsv = lambda c: colorsys.rgb_to_hsv(c[0]/255, c[1]/255, c[2]/255)
    ratio = lambda c: top[c]/cnt[c]
    seedable = [c for c in cnt if hsv(c)[1] >= .18 and ratio(c) >= .45]
    if not seedable: seedable = [c for c in cnt if hsv(c)[1] >= .18]
    if not seedable: return [], 0
    seed = max(seedable, key=lambda c: cnt[c]*ratio(c))
    base = hsv(seed)[0]
    def dh(h):
        d = abs(h-base); return min(d, 1-d)
    # 시트 전체에서 같은 색을 모은다 (검출은 idle 기준, 적용은 전 프레임)
    allc = Counter()
    ap = im.load()
    for y in range(H):
        for x in range(W):
            c = ap[x,y]
            if c[3]: allc[c[:3]] += 1
    out = [c for c in allc
           if hsv(c)[1] >= .15 and dh(hsv(c)[0]) <= HAIR_DH
           and (c not in cnt or ratio(c) >= HAIR_TOP)]
    out.sort(key=lambda c: -allc[c])
    return ["%02x%02x%02x" % c for c in out], base

def main():
    files = sorted(glob.glob(os.path.join(SRC,"*.png")))
    if not files: raise SystemExit("src/ 에 png 가 없다")
    sheets = []
    for f in files:
        raw_job = os.path.splitext(os.path.basename(f))[0]
        job = ALIAS.get(raw_job, raw_job)
        if job != raw_job: print(f"  ({raw_job}.png → 직업 id '{job}')")
        im, cell, cols, counts = read_sheet(f)
        hair, base = hair_colors(im, cell)
        sheets.append(dict(job=job, im=im, cell=cell, cols=cols, counts=counts, hair=hair))
        print(f"{job:12s} cell={cell} cols={cols} frames={counts} 머리 {len(hair)}색 (기준 {base*360:.0f}°)")
    CELL = max(s["cell"] for s in sheets)
    MAXC = max(s["cols"] for s in sheets)
    atlas = Image.new("RGBA",(MAXC*CELL, len(sheets)*ROWS*CELL),(0,0,0,0))
    for i,s in enumerate(sheets):
        im = s["im"]
        if s["cell"] != CELL:                       # 정수배로만 맞춘다
            k = CELL // s["cell"]
            if CELL % s["cell"]: raise SystemExit(f"{s['job']}: 셀 {s['cell']} 가 {CELL} 의 약수가 아니다")
            im = im.resize((im.size[0]*k, im.size[1]*k), Image.NEAREST)
        atlas.alpha_composite(im, (0, i*ROWS*CELL))
    # 팔레트로 줄인다
    flat = Image.new("RGB", atlas.size, (0,0,0)); flat.paste(atlas, mask=atlas.split()[3])
    q = flat.quantize(colors=255, method=Image.MEDIANCUT)
    q = q.convert("RGBA"); q.putalpha(atlas.split()[3])
    buf = io.BytesIO(); q.save(buf,"PNG",optimize=True)
    raw = buf.getvalue()
    b64 = base64.b64encode(raw).decode()
    meta = {s["job"]: s["counts"] for s in sheets}
    hair = {s["job"]: s["hair"] for s in sheets}
    js = ("const SPR_CELL=%d,SPR_COLS=%d;\n"
          "const SPR_JOB=%s;\n"
          "const SPR_HAIR=%s;\n"
          "const SPR_IMG=\"data:image/png;base64,%s\";\n") % (
          CELL, MAXC, json.dumps(meta, separators=(",",":")),
          json.dumps(hair, separators=(",",":")), b64)
    out = os.path.join(os.path.dirname(SRC), "sprites.js")
    io.open(out,"w",encoding="utf-8").write(js)
    atlas.save(os.path.join(os.path.dirname(SRC),"atlas.png"))
    print("아틀라스 %dx%d · PNG %.1fKB · base64 %.1fKB → %s" %
          (atlas.size[0],atlas.size[1],len(raw)/1024,len(b64)/1024,out))

main()
