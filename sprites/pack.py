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
    "spellblade":"spellsword",
}
# 시트 한 장당 쓸 색 수 — 도트 느낌을 유지하면서 아틀라스를 가볍게 만든다.
# 26 을 넘기면 WebP 가 팔레트 모드를 포기해 용량이 세 배로 뛴다.
QUANT = 26

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
    # 색 줄이기 — 아틀라스에 실제로 박히는 색과 머리색 목록을 여기서 일치시킨다
    if QUANT:
        a = im.split()[3]
        flat = Image.new("RGB", im.size, (0,0,0)); flat.paste(im.convert("RGB"), mask=a)
        q = flat.quantize(colors=QUANT, method=Image.MEDIANCUT, dither=Image.NONE).convert("RGB")
        im = q.convert("RGBA"); im.putalpha(a)
    return im, cell, cols, counts

def skin_colors(im, cell):
    """얼굴 살덩이에서 살색 램프를 직접 읽는다.
       idle 1프레임 위쪽 45% 안에서 가장 큰 살구빛 덩어리를 찾고,
       그 덩어리에 쓰인 색을 전부 '살색'으로 본다 (손·목도 같은 램프를 쓴다)."""
    import numpy as np
    from scipy import ndimage
    reg = im.crop((0, 0, cell, cell))
    bb = reg.split()[-1].getbbox()
    if not bb: return set()
    x0, y0, x1, y1 = bb; H = y1 - y0
    a = np.asarray(reg, dtype=np.int16)
    r, g, b, al = a[...,0], a[...,1], a[...,2], a[...,3]
    mx = np.maximum(np.maximum(r,g),b); mn = np.minimum(np.minimum(r,g),b)
    sat = np.where(mx>0, (mx-mn)/np.maximum(mx,1), 0)
    hue = np.zeros_like(sat, dtype=float); d = np.maximum(mx-mn,1)
    isR=(mx==r); isG=(mx==g)&~isR; isB=(~isR)&(~isG)
    hue[isR]=(((g-b)[isR]/d[isR])%6)*60
    hue[isG]=(((b-r)[isG]/d[isG])+2)*60
    hue[isB]=(((r-g)[isB]/d[isB])+4)*60
    skin = (al>80)&(mx>100)&(sat>0.10)&(sat<0.62)&(hue>=6)&(hue<=45)&(r>=g)&(g>=b)
    skin[y0+int(H*0.45):,:] = False; skin[:y0,:] = False
    lab, n = ndimage.label(skin)
    if n == 0: return set()
    sizes = ndimage.sum(skin, lab, range(1, n+1))
    keep = lab == int(np.argmax(sizes))+1
    ys, xs = np.where(keep)
    out = set()
    for y, x in zip(ys, xs):
        c = tuple(int(v) for v in a[y, x, :3])
        out.add("%02x%02x%02x" % c)
    # 26색으로 줄인 뒤라 손·목도 얼굴과 같은 팔레트 칸을 쓴다 — 얼굴 색만 막으면 충분하다.
    return out

def head_only(im, cell, thr=.70):
    """머리에만 쓰이는 색 — idle 칸에서 그 색 픽셀의 70% 이상이 머리 쪽에 있으면 머리로 본다.
       몸에도 함께 쓰이는 색(머리와 옷이 같은 색인 캐릭터)은 막지 않는다."""
    reg = im.crop((0, 0, cell, cell))
    bb = reg.getbbox()
    if not bb: return set()
    x0, y0, x1, y1 = bb
    band = y0 + (y1 - y0) * HAIR_BAND
    px = im.load()
    cnt, up = Counter(), Counter()
    for y in range(y0, y1):
        for x in range(x0, x1):
            c = px[x, y]
            if not c[3]: continue
            cnt[c[:3]] += 1
            if y < band: up[c[:3]] += 1
    return {"%02x%02x%02x" % c for c, n in cnt.items() if n >= 8 and up[c]/n >= thr}

HAIR_BAND = .42     # 캐릭터 bbox 위에서부터 이 비율까지가 "머리 쪽"
HAIR_DH   = .055    # 같은 머리색으로 볼 색상(hue) 차이 (0~.5)
HAIR_TOP  = .25     # 그 색의 픽셀 중 머리 쪽에 있어야 하는 최소 비율
HAIR_MIN  = 2       # 이보다 적으면 그 직업은 머리색 변형을 끈다
# 자동 검출이 빗나가는 직업은 여기서 직접 지정한다.
# 빈 배열이면 "변형 없음" — 머리와 피부가 같은 색을 쓰는 그림이 그렇다.
# 여러 시트가 공유하는 살색 램프 — 머리색으로 잘못 잡히면 얼굴·손까지 물든다.
# 검출 결과에서 무조건 빼낸다.
SKIN = {"ffd7b9", "eab89c", "d29c80", "b17a67", "6f4b43", "513e35", "815737",
        "ffdfc4", "eabda3", "c9a28d", "a47878", "594034"}

# 머리색 변형은 폐기했다 — hair_colors 는 이제 "바꾸면 안 되는 색"을 걸러내는 데만 쓴다.
HAIR_FIX = {}

def hair_colors(im, cell):
    """머리색 자동 검출.
       1) idle 행에서 캐릭터 bbox 를 잡고 위 42% 를 '머리 쪽'으로 본다
       2) 머리 쪽에 많이 깔린 채도 있는 색 하나를 기준으로 삼고
       3) 그 색상(hue) 가까이 있으면서 머리 쪽에 몰려 있는 색만 고른다
       피부·가죽·갑옷은 색상이 다르거나 아래쪽에 몰려 있어 걸러진다."""
    W, H = im.size
    reg = im.crop((0, 0, W, cell))
    bb = reg.getbbox()
    if not bb: return [], 0
    x0, y0, x1, y1 = bb
    band = y0 + (y1 - y0) * HAIR_BAND
    px = im.load()
    cnt, top = Counter(), Counter()
    for y in range(y0, y1):
        for x in range(x0, x1):
            c = px[x, y]
            if c[3] == 0: continue
            cnt[c[:3]] += 1
            if y < band: top[c[:3]] += 1
    if not cnt: return [], 0
    hsv = lambda c: colorsys.rgb_to_hsv(c[0]/255, c[1]/255, c[2]/255)
    ratio = lambda c: top[c] / cnt[c]
    seedable = [c for c in cnt if hsv(c)[1] >= .18 and ratio(c) >= .45]
    if not seedable: seedable = [c for c in cnt if hsv(c)[1] >= .18]
    if not seedable: return [], 0
    seed = max(seedable, key=lambda c: cnt[c] * ratio(c))
    base = hsv(seed)[0]
    def dh(h):
        d = abs(h - base); return min(d, 1 - d)
    allc = Counter()
    ap = im.load()
    for y in range(H):
        for x in range(W):
            c = ap[x, y]
            if c[3]: allc[c[:3]] += 1
    out = [c for c in allc
           if hsv(c)[1] >= .15 and dh(hsv(c)[0]) <= HAIR_DH
           and (c not in cnt or ratio(c) >= HAIR_TOP)]
    out.sort(key=lambda c: -allc[c])
    return ["%02x%02x%02x" % c for c in out], base

# ── 복장 색 검출 ──
# 머리색 변형을 못 쓰는 직업(머리와 피부가 같은 램프)은 대신 옷의 주된 색을 바꾼다.
CLOTH_DH   = .14    # 같은 옷감으로 볼 색상(hue) 차이 — 넓게 잡아 옷 전체를 함께 돌린다
CLOTH_LOW  = .35    # 그 색 픽셀 중 몸통 쪽(허리 아래 포함)에 있어야 하는 최소 비율
CLOTH_SAT  = .20    # 씨앗 색의 최소 채도 — 무채색 옷은 색을 돌려도 안 변한다
CLOTH_VAL  = .14    # 너무 어두우면 색을 돌려도 티가 안 난다
CLOTH_MIN  = 2
CLOTH_FIX  = {      # 자동 검출이 빗나가면 여기서 직접 지정 (빈 배열이면 변형 없음)
    # 프리스트의 금장식은 26색으로 줄이면서 살색 음영과 같은 칸을 쓰게 됐다.
    # 직접 지정하면 얼굴까지 물들어서 자동 검출에 맡긴다.
}

def cloth_colors(im, cell, ban=None):
    """복장 색 검출 — 살색·머리색을 뺀 나머지에서 '가장 옷다운 색상 무리'를 고른다.
       색 하나를 씨앗으로 잡지 않고, 색상(hue) 창을 훑으며
       그 창 안에 든 색들의 '눈에 띄는 양'(넓이 x 채도 x 밝기)이 가장 큰 곳을 쓴다.
       갈색 가죽처럼 넓지만 칙칙한 색보다, 좁아도 선명한 옷감이 이기도록 채도를 세제곱한다."""
    import colorsys
    ban = set(x.lower() for x in (ban or set()))
    W, H = im.size
    reg = im.crop((0, 0, W, cell))
    bb = reg.getbbox()
    if not bb: return [], 0
    x0, y0, x1, y1 = bb
    band = y0 + (y1 - y0) * HAIR_BAND
    px = im.load()
    cnt, low = Counter(), Counter()
    for y in range(y0, y1):
        for x in range(x0, x1):
            c = px[x, y]
            if c[3] == 0: continue
            cnt[c[:3]] += 1
            if y >= band: low[c[:3]] += 1
    if not cnt: return [], 0
    hsv  = lambda c: colorsys.rgb_to_hsv(c[0]/255, c[1]/255, c[2]/255)
    hexs = lambda c: "%02x%02x%02x" % c
    ratio = lambda c: low[c] / cnt[c]
    # 시트 전체 색 분포 (칸 하나가 아니라 장 전체에서 넓이를 센다)
    allc = Counter()
    ap = im.load()
    for y in range(H):
        for x in range(W):
            c = ap[x, y]
            if c[3]: allc[c[:3]] += 1
    cands = [c for c in allc if hexs(c) not in ban]
    if not cands: return [], 0
    def mass(c):
        h, sa, v = hsv(c)
        r = ratio(c) if c in cnt else 0.5      # idle 칸에 없으면 중립으로 본다
        return allc[c] * (sa ** 3) * v * (0.4 + 0.6 * r)
    def dh(a, b):
        d = abs(a - b); return min(d, 1 - d)
    best = (0, None)
    for seed in cands:
        hs, ss, vs = hsv(seed)
        if ss < CLOTH_SAT or vs < CLOTH_VAL: continue
        m = sum(mass(c) for c in cands if dh(hsv(c)[0], hs) <= CLOTH_DH)
        if m > best[0]: best = (m, hs)
    if best[1] is None: return [], 0
    base = best[1]
    out = [c for c in cands
           if hsv(c)[1] >= .10 and dh(hsv(c)[0], base) <= CLOTH_DH
           and (c not in cnt or ratio(c) >= .22)]
    out.sort(key=lambda c: -allc[c])
    return [hexs(c) for c in out], base

FX_ORDER = ["slash","pierce","blunt","burst","aura","heal"]
def pack_fx():
    """fx_*.png (1행 N프레임) 들을 세로로 쌓아 한 장으로 만든다."""
    sheets = []
    for name in FX_ORDER:
        f = os.path.join(SRC, "fx_%s.png" % name)
        if not os.path.exists(f): continue
        im = Image.open(f).convert("RGBA")
        W, H = im.size
        if W % H: raise SystemExit("%s: 가로 %d 가 세로 %d 로 안 나눠떨어진다" % (f, W, H))
        px = im.load()
        for y in range(H):
            for x in range(W):
                c = px[x, y]
                px[x, y] = (0,0,0,0) if c[3] < 128 else (c[0], c[1], c[2], 255)
        sheets.append((name, im, H, W // H))
    if not sheets:
        return "const FX_KEYS=[],FX_CELL=0,FX_N=0,FX_IMG=\"\";\n"
    CELL = sheets[0][2]
    FRN  = max(s[3] for s in sheets)
    atlas = Image.new("RGBA", (FRN*CELL, len(sheets)*CELL), (0,0,0,0))
    for i,(n,im,c,fr) in enumerate(sheets):
        atlas.alpha_composite(im, (0, i*CELL))
        print("fx_%-8s %d프레임" % (n, fr))
    flat = Image.new("RGB", atlas.size, (0,0,0)); flat.paste(atlas, mask=atlas.split()[3])
    q = flat.quantize(colors=255, method=Image.MEDIANCUT).convert("RGBA")
    q.putalpha(atlas.split()[3])
    buf = io.BytesIO(); q.save(buf, "PNG", optimize=True)
    raw = buf.getvalue(); b64 = base64.b64encode(raw).decode()
    atlas.save(os.path.join(os.path.dirname(SRC), "fx_atlas.png"))
    print("이펙트 아틀라스 %dx%d · PNG %.1fKB" % (atlas.size[0], atlas.size[1], len(raw)/1024))
    return ("const FX_KEYS=%s,FX_CELL=%d,FX_N=%d;\n"
            "const FX_IMG=\"data:image/png;base64,%s\";\n") % (
            json.dumps([s[0] for s in sheets], separators=(",",":")), CELL, FRN, b64)

def main():
    # fx_*.png 는 전투 이펙트 시트(1행 8프레임),
    # mon_*.png 는 원정지 주인의 정지 그림 한 장 — 둘 다 여기서 다루지 않는다
    # 직업 시트가 아닌 그림들 — 얼굴 원본·배경·팝업·튜토리얼·승리 포즈·아이콘 따위
    SKIP_PRE = ("fx_","mon_","original_","field_","popup_","prologue","tutorial","victory","icon_")
    SKIP_NAME = {"feedback"}
    files = [f for f in sorted(glob.glob(os.path.join(SRC,"*.png")))
             if not os.path.basename(f).startswith(SKIP_PRE)
             and os.path.splitext(os.path.basename(f))[0] not in SKIP_NAME]
    if not files: raise SystemExit("src/ 에 png 가 없다")
    sheets = []
    for f in files:
        raw_job = os.path.splitext(os.path.basename(f))[0]
        job = ALIAS.get(raw_job, raw_job)
        if job != raw_job: print(f"  ({raw_job}.png → 직업 id '{job}')")
        im, cell, cols, counts = read_sheet(f)
        # 살색과 머리색은 건드리지 않는다 — 바꾸는 것은 복장뿐
        skin = skin_colors(im, cell)
        hair0 = head_only(im, cell)          # 머리에만 쓰이는 색만 막는다
        ban = set(x.lower() for x in skin) | set(x.lower() for x in hair0)
        if job in CLOTH_FIX:
            hair = list(CLOTH_FIX[job])
            print("  (%s: 복장 색을 직접 지정 — %d색)" % (job, len(hair)))
        else:
            cl, cb = cloth_colors(im, cell, ban)
            cl = [c for c in cl if c.lower() not in ban]
            if len(cl) >= CLOTH_MIN:
                hair = cl
                print("  (%s: 복장 %d색 — 기준 %.0f° · 살색 %d개·머리 전용 %d개 제외)"
                      % (job, len(cl), cb*360, len(skin), len(hair0)))
            else:
                hair = []
                print("  (%s: 쓸 만한 복장 색을 못 찾아 변형 없음)" % job)
        dup = next((k for k,x in enumerate(sheets) if x["job"]==job), None)
        if dup is not None:
            # 같은 직업 id 로 두 장이 들어왔다 — 이름을 바꿔 넣은 쪽(별칭)을 남긴다
            if job != raw_job:
                print(f"  ({job}: 파일 두 장 — '{raw_job}.png' 를 쓰고 이전 파일은 버립니다)")
                sheets.pop(dup)
            else:
                print(f"  ({job}: 파일 두 장 — 이미 넣은 쪽을 유지하고 '{raw_job}.png' 는 건너뜁니다)")
                continue
        sheets.append(dict(job=job, im=im, cell=cell, cols=cols, counts=counts, hair=hair))
        print(f"{job:12s} cell={cell} cols={cols} frames={counts} 복장 {len(hair)}색")
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
    # 무손실로 굽는다 — 런타임 머리색 교체가 정확한 RGB 일치를 요구하므로
    # 전역 양자화(색이 밀린다)를 쓰지 않는다
    buf = io.BytesIO(); atlas.save(buf, "WEBP", lossless=True, method=6, exact=True)
    raw = buf.getvalue()
    b64 = base64.b64encode(raw).decode()
    meta = {s["job"]: s["counts"] for s in sheets}
    hair = {s["job"]: s["hair"] for s in sheets}
    js = ("const SPR_CELL=%d,SPR_COLS=%d;\n"
          "const SPR_JOB=%s;\n"
          "const SPR_HAIR=%s;\n"
          "const SPR_IMG=\"data:image/webp;base64,%s\";\n") % (
          CELL, MAXC, json.dumps(meta, separators=(",",":")),
          json.dumps(hair, separators=(",",":")), b64)
    js += pack_fx()
    out = os.path.join(os.path.dirname(SRC), "sprites.js")
    io.open(out,"w",encoding="utf-8").write(js)
    # game.html 안의 const 줄들을 갈아 끼운다
    import re
    GAME = os.path.join(os.path.dirname(os.path.dirname(SRC)), "game.html")
    if os.path.exists(GAME):
        g = io.open(GAME, encoding="utf-8").read(); n = 0
        for line in js.strip().split("\n"):
            m = re.match(r"const ([A-Za-z_]\w*)", line)
            if not m: continue
            pat = r"^const " + re.escape(m.group(1)) + r"[=,].*$"
            if re.search(pat, g, re.M):
                g = re.sub(pat, lambda _: line, g, count=1, flags=re.M); n += 1
        io.open(GAME, "w", encoding="utf-8").write(g)
        print("game.html 반영 — %d줄" % n)
    atlas.save(os.path.join(os.path.dirname(SRC),"atlas.png"))
    print("아틀라스 %dx%d · WebP %.1fKB · base64 %.1fKB → %s" %
          (atlas.size[0],atlas.size[1],len(raw)/1024,len(b64)/1024,out))

main()
