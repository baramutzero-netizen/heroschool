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
HAIR_MIN  = 2       # 이보다 적으면 그 직업은 머리색 변형을 끈다
# 자동 검출이 빗나가는 직업은 여기서 직접 지정한다.
# 빈 배열이면 "변형 없음" — 머리와 피부가 같은 색을 쓰는 그림이 그렇다.
# 여러 시트가 공유하는 살색 램프 — 머리색으로 잘못 잡히면 얼굴·손까지 물든다.
# 검출 결과에서 무조건 빼낸다.
SKIN = {"ffd7b9", "eab89c", "d29c80", "b17a67", "6f4b43", "513e35", "815737",
        "ffdfc4", "eabda3", "c9a28d", "a47878", "594034"}

HAIR_FIX = {
    # 머리색이 옷·피부와 같은 색을 공유해서 자동 검출이 옷까지 물들이는 직업들 —
    # 빈 목록이면 색 변화를 끈다 (모두 원본 색 그대로).
    "paladin":   [],
    "priest":    [],
    "sword":     [],   # 머리의 중간·어두운 톤이 살색 램프와 같아, 일부만 칠해져 얼룩진다
    "druid":     [],
    "ninja":     [],
    "forcemage": [],
    "rogue":     [],   # 새 원화 — 금발이 살색 램프와 같은 색을 써서 일부만 칠해진다
    "monk":      ["442d36", "352832", "503838", "725045"],    # 짙은 갈색 머리
}

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
CLOTH_DH   = .07    # 같은 옷감으로 볼 색상(hue) 차이
CLOTH_LOW  = .45    # 그 색 픽셀 중 몸통 쪽(허리 아래 포함)에 있어야 하는 최소 비율
CLOTH_SAT  = .22    # 씨앗 색의 최소 채도 — 무채색 옷은 색을 돌려도 안 변한다
CLOTH_VAL  = .14    # 너무 어두우면 색을 돌려도 티가 안 난다
CLOTH_MIN  = 2
CLOTH_FIX  = {      # 자동 검출이 빗나가면 여기서 직접 지정 (빈 배열이면 변형 없음)
    # 프리스트 — 흰 로브는 그대로 두고 지팡이만 바꾼다
    "priest": ["e2ad42", "967751", "f5d2b1"],
}

def cloth_colors(im, cell):
    """옷 주요 색 자동 검출 — 머리 검출의 거울상.
       idle bbox 의 위 42% 를 '머리 쪽'으로 보고, 그 아래에 몰려 있으면서
       채도가 있는 색 하나를 씨앗으로 잡아 같은 색상 계열을 모은다.
       피부 램프는 무조건 제외한다."""
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
    hsv = lambda c: colorsys.rgb_to_hsv(c[0]/255, c[1]/255, c[2]/255)
    hexs = lambda c: "%02x%02x%02x" % c
    ratio = lambda c: low[c] / cnt[c]
    seedable = [c for c in cnt
                if hexs(c) not in SKIN and hsv(c)[1] >= CLOTH_SAT
                and hsv(c)[2] >= CLOTH_VAL and ratio(c) >= CLOTH_LOW]
    if not seedable: return [], 0
    # 넓이뿐 아니라 '색을 돌렸을 때 눈에 띄는 정도'(채도x밝기)도 같이 본다 —
    # 어두운 그림자색이 가장 넓다고 씨앗이 되면 색을 돌려도 티가 안 난다
    def seedScore(c):
        s, v = hsv(c)[1], hsv(c)[2]
        return cnt[c] * ratio(c) * s * v
    seed = max(seedable, key=seedScore)
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
           if hexs(c) not in SKIN and hsv(c)[1] >= .14 and dh(hsv(c)[0]) <= CLOTH_DH
           and (c not in cnt or ratio(c) >= .30)]
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
    files = [f for f in sorted(glob.glob(os.path.join(SRC,"*.png")))
             if not os.path.basename(f).startswith(("fx_","mon_"))]
    if not files: raise SystemExit("src/ 에 png 가 없다")
    sheets = []
    for f in files:
        raw_job = os.path.splitext(os.path.basename(f))[0]
        job = ALIAS.get(raw_job, raw_job)
        if job != raw_job: print(f"  ({raw_job}.png → 직업 id '{job}')")
        im, cell, cols, counts = read_sheet(f)
        hair, base = hair_colors(im, cell)
        cut = [h for h in hair if h.lower() in SKIN]
        if cut:
            hair = [h for h in hair if h.lower() not in SKIN]
            print("  (%s: 살색 %d개를 머리색에서 제외)" % (job, len(cut)))
        if job in HAIR_FIX:
            hair = list(HAIR_FIX[job])
            print("  (%s: 머리색을 직접 지정 — %d색)" % (job, len(hair)))
        elif len(hair) < HAIR_MIN:
            print("  (%s: 쓸 만한 머리색을 못 찾아 변형을 끕니다)" % job)
            hair = []
        if len(hair) < HAIR_MIN:                      # 머리를 못 쓰면 옷으로
            if job in CLOTH_FIX:
                hair = list(CLOTH_FIX[job])
                print("  (%s: 복장 색을 직접 지정 — %d색)" % (job, len(hair)))
            else:
                cl, cb = cloth_colors(im, cell)
                if len(cl) >= CLOTH_MIN:
                    hair = cl
                    print("  (%s: 머리 대신 복장 %d색을 바꿉니다 — 기준 %.0f°)" % (job, len(cl), cb*360))
                else:
                    print("  (%s: 복장 색도 못 찾아 변형 없음)" % job)
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
    js += pack_fx()
    out = os.path.join(os.path.dirname(SRC), "sprites.js")
    io.open(out,"w",encoding="utf-8").write(js)
    atlas.save(os.path.join(os.path.dirname(SRC),"atlas.png"))
    print("아틀라스 %dx%d · PNG %.1fKB · base64 %.1fKB → %s" %
          (atlas.size[0],atlas.size[1],len(raw)/1024,len(b64)/1024,out))

main()
