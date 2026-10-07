"""책상 배경 · 남색 천 · 일정 두루마리(종이 2D + 3D 축) · 깃펜 · 불빛 · 가장자리 그늘 · 마을 액자 — 모두 1배.
책상 크기는 마을 그림과 같다: 1배 607x466 (2배 1214x931 — 마지막 줄은 반만)."""
import sys, numpy as np, random
from PIL import Image, ImageDraw
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import desk_top as DT
from px3d import *
import props3d as PR

DW, DH = 607, 466
TOWN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "assets", "town") + "/"   # 저장소 assets/town
def C(h): h = h.lstrip('#'); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
def new(w, h): return Image.new('RGBA', (w, h), (0, 0, 0, 0))
P_, rect, poly, ell, ring, line, text = DT.P, DT.rect, DT.poly, DT.ell, DT.ring, DT.line, DT.text
WOOD = [C('4a2816'), C('663a22'), C('84502e'), C('9e6438'), C('b87c48'), C('cc9058')]
NAVY = [C('141a36'), C('1c2246'), C('262e58'), C('323c6e'), C('445290')]
GOLD = [C('6a4618'), C('a8782e'), C('d1a24a'), C('ecc874'), C('fbe7a6')]
PARCH = [C('a0825a'), C('c4a77c'), C('dcc496'), C('ebd8ac'), C('f5e8c6'), C('faf1d8')]

# ───────────────────────── 책상 (판자) ─────────────────────────
def desk_bg(seed=11):
    rng = random.Random(seed); nr = np.random.RandomState(seed)
    A = np.zeros((DH, DW, 3), np.uint8)
    L = Image.new('RGB', (DW, DH)); D = ImageDraw.Draw(L)
    y = -7; k = 0
    while y < DH:
        h = 22
        tone = [2, 3, 2, 3][k % 4] + (1 if rng.random() < .25 else 0) * (1 if k % 2 else 0)
        base = WOOD[min(tone, 4)]
        D.rectangle([0, y, DW - 1, y + h - 1], fill=base)
        # 큰 결 — 판자마다 밝기 얼룩
        for _ in range(6):
            x0 = rng.randrange(-60, DW); ln = rng.randrange(60, 200); yy = y + rng.randrange(3, h - 3)
            D.rectangle([x0, yy - 1, x0 + ln, yy + 1], fill=WOOD[min(tone + 1, 5)] if rng.random() < .5 else WOOD[max(tone - 1, 1)])
        # 나뭇결 — 물결 선
        for _ in range(42):
            x0 = rng.randrange(-20, DW); ln = rng.randrange(14, 70); yy = y + 2 + rng.randrange(h - 4)
            c = WOOD[max(tone - 1, 0)] if rng.random() < .62 else WOOD[min(tone + 1, 5)]
            amp = rng.uniform(0, 1.2); ph = rng.uniform(0, 6)
            pts = [(x0 + i, yy + round(amp * np.sin(ph + i / 9))) for i in range(0, ln, 3)]
            if len(pts) > 1: D.line(pts, fill=c)
        # 옹이
        if rng.random() < .55:
            kx, ky = rng.randrange(20, DW - 20), y + 6 + rng.randrange(h - 12)
            D.ellipse([kx - 6, ky - 3, kx + 6, ky + 3], fill=WOOD[max(tone - 1, 0)])
            D.ellipse([kx - 4, ky - 2, kx + 4, ky + 2], fill=WOOD[max(tone - 2, 0)])
            D.ellipse([kx - 2, ky - 1, kx + 1, ky + 1], fill=WOOD[0])
            D.arc([kx - 10, ky - 5, kx + 10, ky + 5], 200, 340, fill=WOOD[max(tone - 1, 0)])
        # 판자 이음 · 못
        for x in range(rng.randrange(40, 160), DW, rng.randrange(170, 260)):
            D.line([(x, y), (x, y + h - 1)], fill=WOOD[0]); D.line([(x + 1, y), (x + 1, y + h - 1)], fill=WOOD[min(tone + 1, 5)])
            for ny in (y + 5, y + h - 6):
                for nx in (x - 4, x + 5):
                    D.point((nx, ny), fill=C('2e1a10')); D.point((nx - 1, ny - 1), fill=WOOD[5])
        # 판자 사이 틈 — 어두운 선 + 아래 판자 윗변 밝게
        D.line([(0, y), (DW, y)], fill=C('2e1a10')); D.line([(0, y + 1), (DW, y + 1)], fill=WOOD[min(tone + 2, 5)])
        D.line([(0, y + h - 1), (DW, y + h - 1)], fill=WOOD[max(tone - 1, 0)])
        y += h; k += 1
    return L.convert('RGBA')

def vignette():
    """가장자리 그늘 — 보통 섞기(알파)로 얹는다. 4단"""
    yy, xx = np.mgrid[0:DH, 0:DW]
    v = (((xx - DW * .42) / (DW * .62)) ** 2 + ((yy - DH * .48) / (DH * .62)) ** 2)
    a = np.clip((v - 0.55) / 1.1, 0, 1)
    bands = np.digitize(a, [.12, .3, .5, .72])
    alpha = np.array([0, 26, 52, 80, 110])[bands]
    # 단 경계를 체크무늬로 섞는다
    chk = ((xx + yy) % 2 == 0)
    edge = np.digitize(np.clip(a + 0.03, 0, 1), [.12, .3, .5, .72]) != bands
    alpha = np.where(edge & chk, np.array([0, 26, 52, 80, 110, 110])[np.minimum(bands + 1, 5)], alpha)
    img = np.zeros((DH, DW, 4), np.uint8); img[..., :3] = (24, 12, 8); img[..., 3] = alpha
    return Image.fromarray(img)

def glow(rad, col=(255, 196, 120), strength=(.34, .22, .13, .06)):
    """불빛 — 띠 넷의 둥근 빛 웅덩이 (화면 섞기로 얹는다). 가운데 = (rad, rad*0.87)"""
    w, h = rad * 2 + 1, int(rad * 2 * 0.87) + 1
    yy, xx = np.mgrid[0:h, 0:w]
    d = np.hypot((xx - rad) / rad, (yy - h / 2) / (h / 2))
    edges = [.28, .5, .74, 1.0]
    band = np.digitize(d, edges)
    chk = (xx + yy) % 2 == 0
    nb = np.digitize(d + 0.035, edges)
    band = np.where((nb != band) & chk, nb, band)
    al = np.array(list(strength) + [0])[np.minimum(band, 4)]
    img = np.zeros((h, w, 4), np.uint8); img[..., :3] = col; img[..., 3] = (al * 255).astype(np.uint8)
    return Image.fromarray(img)

# ───────────────────────── 남색 천 ─────────────────────────
def runner(w=98, h=DH):
    L = new(w, h)
    rect(L, 0, 0, w - 1, h - 1, NAVY[2])
    rr = random.Random(3)
    for y in range(h):                                                   # 촘촘한 직물 결 — 점을 성기게
        for x in range((y % 2), w, 2):
            if (x + y * 3) % 8 == 0: P_(L, x, y, NAVY[1])
            elif (x * 3 + y) % 11 == 0: P_(L, x, y, NAVY[3])
    for _ in range(40):                                                  # 실 뭉침
        x, y = rr.randrange(8, w - 8), rr.randrange(h)
        P_(L, x, y, NAVY[3]); P_(L, x + 1, y, NAVY[1])
    for x, s in ((5, 1), (w - 6, -1)):                                   # 금실 테두리 두 줄 + 마름모
        rect(L, x, 0, x, h - 1, GOLD[2]); rect(L, x + s, 0, x + s, h - 1, GOLD[1])
        rect(L, x + 4 * s, 0, x + 4 * s, h - 1, GOLD[1])
        for y in range(3, h, 8):
            cx = x + 2 * s
            P_(L, cx, y, GOLD[3]); P_(L, cx, y + 1, GOLD[2]); P_(L, cx, y - 1, GOLD[2])
    rect(L, 0, 0, 0, h - 1, NAVY[0]); rect(L, w - 1, 0, w - 1, h - 1, NAVY[0])
    rect(L, 1, 0, 1, h - 1, NAVY[3])
    for cy in (54, h - 58):
        emblem(L, w // 2, cy)
    return L
def emblem(L, cx, cy):
    for i in range(9):                                                    # 월계관
        a = 0.35 + i * 0.29
        x = int(round(cx - 17 * np.cos(a))); y = int(round(cy - 13 * np.sin(a) + 8))
        for (ox, oy, c) in ((0, 0, GOLD[3]), (-1, 0, GOLD[2]), (0, -1, GOLD[4]), (-1, 1, GOLD[1])):
            P_(L, x + ox, y + oy, c); P_(L, 2 * cx - x - ox, y + oy, c)
    rect(L, cx - 2, cy - 12, cx + 1, cy + 12, GOLD[2]); rect(L, cx - 8, cy - 6, cx + 7, cy - 3, GOLD[2])
    rect(L, cx - 2, cy - 12, cx - 2, cy + 12, GOLD[4]); rect(L, cx - 8, cy - 6, cx + 7, cy - 6, GOLD[4])
    rect(L, cx + 1, cy - 11, cx + 1, cy + 12, GOLD[0]); rect(L, cx - 7, cy - 3, cx + 7, cy - 3, GOLD[0])
    P_(L, cx - 1, cy - 5, GOLD[4])

# ───────────────────────── 일정 두루마리 ─────────────────────────
COLS = DT.COLS; DECK = DT.DECK; CARD = DT.CARD
CW, CH = 48, 38; PITCH = 54
def tab(L, cx, y, key):
    name, pal = CARD[key]
    x0, x1 = cx - 20, cx + 20
    for (a, b) in (((x0 - 6, y + 2), (x0, y + 2)), ((x1, y + 2), (x1 + 6, y + 2))):
        pass
    poly(L, [(x0 - 6, y + 2), (x0 + 2, y + 2), (x0 + 2, y + 14), (x0 - 6, y + 14), (x0 - 2, y + 8)], pal[1])   # 꼬리(접힌 끝)
    poly(L, [(x1 + 6, y + 2), (x1 - 2, y + 2), (x1 - 2, y + 14), (x1 + 6, y + 14), (x1 + 2, y + 8)], pal[1])
    poly(L, [(x0, y + 13), (x0 + 3, y + 16), (x0 + 3, y + 13)], pal[0]); poly(L, [(x1, y + 13), (x1 - 3, y + 16), (x1 - 3, y + 13)], pal[0])
    rect(L, x0, y, x1, y + 13, pal[2]); rect(L, x0, y, x1, y, pal[3]); rect(L, x0, y + 1, x1, y + 1, pal[3])
    rect(L, x0, y + 13, x1, y + 13, pal[1])
    tw = DT.F9.getlength(name)
    text(L, (cx - tw / 2 + 1, y + 3), name, DT.F9, pal[0])
    text(L, (cx - tw / 2, y + 2), name, DT.F9, C('fffaf0'))
def card(L, x, y, key, label, kind):
    name, pal = CARD[key]
    rect(L, x + 2, y + 2, x + CW + 1, y + CH + 2, PARCH[0], 120)                      # 종이 위 그림자
    rect(L, x, y + CH - 1, x + CW - 1, y + CH, pal[0])                                 # 두께
    rect(L, x, y, x + CW - 1, y + CH - 2, pal[2])
    rect(L, x, y, x + CW - 1, y, pal[3]); rect(L, x, y, x, y + CH - 2, pal[3])
    rect(L, x + CW - 1, y + 1, x + CW - 1, y + CH - 2, pal[1])
    px0, py0, px1, py1 = x + 3, y + 3, x + CW - 4, y + 22
    rect(L, px0, py0, px1, py1, pal[4]); rect(L, px0, py0, px1, py0, pal[1]); rect(L, px0, py0, px0, py1, pal[1])
    rect(L, px0 + 1, py1, px1, py1, pal[3]); rect(L, px1, py0 + 1, px1, py1, pal[3])
    ic = DT.icon(kind); L.alpha_composite(ic, (x + CW // 2 - 8, py0 + 3))
    tw = DT.F7.getlength(label)
    text(L, (x + CW / 2 - tw / 2 + 1, y + 26), label, DT.F7, pal[0])
    text(L, (x + CW / 2 - tw / 2, y + 25), label, DT.F7, C('fffaf0'))
def signature(L, x0, y0):
    INK = C('4a3430')
    line(L, [(x0 - 2, y0 + 8), (x0 + 96, y0 + 8)], PARCH[1])
    ctrl = [(0, 5), (4, -7), (8, -9), (9, -3), (5, 3), (2, 2), (9, -1), (13, 0), (15, -4), (14, 1), (18, 2), (21, -3), (22, 2), (26, 1), (28, -5), (30, -8), (30, 1),
            (33, 2), (36, -2), (38, 1), (41, 0), (44, -3), (46, 1), (50, 0), (54, -2), (58, 0), (64, -1)]
    line(L, DT.catmull([(x0 + x, y0 + y) for x, y in ctrl], 12), INK)
    line(L, DT.catmull([(x0 + 4, y0 + 6), (x0 + 30, y0 + 4), (x0 + 60, y0 + 5), (x0 + 74, y0 + 2)], 12), INK)

def paper(w, h, seed=5):
    """양피지 — 결 · 얼룩 · 가장자리 · 축 가까이 말리는 그늘"""
    rng = random.Random(seed)
    L = new(w, h)
    rect(L, 0, 0, w - 1, h - 1, PARCH[3])
    A = np.array(L)
    nr = np.random.RandomState(seed)
    noise = nr.rand(h, w)
    A[(noise < 0.05)] = list(PARCH[2]) + [255]; A[(noise > 0.975)] = list(PARCH[4]) + [255]
    yy, xx = np.mgrid[0:h, 0:w]
    blot = np.zeros((h, w))
    for _ in range(7):
        cx, cy, r = rng.uniform(0, w), rng.uniform(0, h), rng.uniform(14, 40)
        blot += np.exp(-((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * r * r))
    A[(blot > 0.55) & (noise < 0.35)] = list(PARCH[2]) + [255]
    for x in range(w):                                                     # 양 끝 — 축으로 말려 들어가는 그늘
        d = min(x, w - 1 - x)
        if d < 7:
            t = [0, 0, 1, 1, 2, 2, 3][d]
            col = [PARCH[0], PARCH[1], PARCH[2], PARCH[2]][t]
            sel = (noise[:, x] < [1, 1, .8, .5, .5, .3, .2][d])
            A[sel, x] = list(col) + [255]
    A[0, :] = list(PARCH[1]) + [255]; A[1, :][noise[1] < .5] = list(PARCH[2]) + [255]
    A[h - 1, :] = list(PARCH[0]) + [255]; A[h - 2, :][noise[h - 2] < .5] = list(PARCH[1]) + [255]
    for x in range(0, w, 5):                                               # 들쭉날쭉한 위아래 가장자리
        if rng.random() < .5: A[0, x:x + rng.randrange(1, 4), 3] = 0
        if rng.random() < .5: A[h - 1, x:x + rng.randrange(1, 4), 3] = 0
    return Image.fromarray(A)

def rollers_sprite(Wp, Hp):
    """두 축 — 종이 양쪽 끝(세계 x = ±(Wp/2+1)). 화면에서 종이 높이보다 위아래로 6px 더"""
    Ly2 = (Hp / 2 + 7) / np.sin(TH)
    r = 5.6; xs = Wp / 2 - 1.5
    M = rotm('x', 90)
    parts = []
    for sx in (-1, 1):
        c = np.array([sx * xs, 0, r])
        parts.append(Part((lambda c: (lambda P: sd_cyl(local(P, c, M), [0, 0, 0], r, Ly2, 0.8)))(c), 'paper'))
        for sy in (-1, 1):
            k = c + [0, sy * (Ly2 + 1.6), 0]
            parts.append(Part((lambda k: (lambda P: sd_cyl(local(P, k, M), [0, 0, 0], r + 1.0, 1.6, 0.6)))(k), 'gold'))
            parts.append(Part((lambda k, sy: (lambda P: sd_sphere(P, k + [0, sy * 3.4, 0], 2.8)))(k, sy), 'gold'))
    b0 = np.array([-xs - 9, -Ly2 - 8, 0]); b1 = np.array([xs + 9, Ly2 + 8, 2 * r + 1])
    return render(parts, b0, b1)

def scroll_sprite():
    ncol = len(COLS)
    Wp = ncol * PITCH + 24; Hp = 206
    pad = 26
    L = new(Wp + pad * 2, Hp + pad * 2)
    ox, oy = pad, pad
    sh = new(L.width, L.height); rect(sh, ox + 3, oy + 3, ox + Wp + 2, oy + Hp + 2, (24, 12, 8), 70)   # 종이가 책상에 지는 옅은 그림자
    L.alpha_composite(sh)
    L.alpha_composite(paper(Wp, Hp), (ox, oy))
    colx = [ox + 12 + PITCH // 2 + PITCH * i for i in range(ncol)]
    tab_y = oy + 12; card_y = [oy + 36, oy + 82, oy + 128]
    for i in range(1, ncol):                                               # 줄 사이 잉크 점선
        x = colx[i] - PITCH // 2
        for y in range(tab_y - 2, card_y[-1] + CH + 4):
            if (y // 3) % 4 != 3: P_(L, x, y, PARCH[1])
    for i, key in enumerate(COLS):
        tab(L, colx[i], tab_y, key)
        for j, (label, kind) in enumerate(DECK[key]):
            card(L, colx[i] - CW // 2, card_y[j], key, label, kind)
    signature(L, ox + 24, oy + Hp - 20)
    rimg, (rx, ry) = rollers_sprite(Wp, Hp)
    # 축 그림의 세계 원점 = 종이 가운데 (화면에서 축 가운데가 z 만큼 위로 올라가 보이는 것을 맞춘다)
    cx, cy = ox + Wp / 2, oy + Hp / 2
    L.alpha_composite(rimg, (int(round(cx - rx)), int(round(cy - ry + 5.6 * np.cos(TH)))))
    bb = L.getbbox(); L = L.crop(bb)
    return L, (int(cx - bb[0]), int(cy - bb[1]))

# ───────────────────────── 깃펜 (2D) ─────────────────────────
def quill(length=70, ang=-32):
    """흰 깃펜 — 펜촉은 왼쪽 아래, 깃은 오른쪽 위로. 깃 한쪽은 밝게 · 한쪽은 그늘 · 갈라진 결"""
    S = 4; Wd = int(length * 1.2) + 20; Hd = int(length * 0.9) + 20
    big = Image.new('RGBA', (Wd * S, Hd * S), (0, 0, 0, 0)); D = ImageDraw.Draw(big)
    a = np.radians(ang); u = np.array([np.cos(a), np.sin(a)]); n = np.array([-u[1], u[0]])
    p0 = np.array([10, Hd - 10], float)
    def pt(t, off): c = p0 + u * length * t + n * off; return (c[0] * S, c[1] * S)
    top, bot = [], []
    for t in np.linspace(.2, 1, 60):
        k = (t - .2) / .8; w = np.sin(np.pi * min(1, k * 1.05)) ** .7
        top.append(pt(t - 0.03 * w, -w * 8.5)); bot.append(pt(t - 0.02 * w, w * 5.2))
    D.polygon(top + bot[::-1], fill=C('f3efe6') + (255,))
    D.polygon([pt(.2, 0)] + bot + [pt(1, 0)], fill=C('d4cdbd') + (255,))
    mid_ = [pt(t, -np.sin(np.pi * (t - .2) / .8) ** .7 * 4.2) for t in np.linspace(.22, .98, 40)]
    D.line(mid_, fill=C('fbf9f4') + (255,), width=S)
    rr = random.Random(2)
    for t in np.linspace(.3, .95, 9):                                     # 갈라진 곳
        w = np.sin(np.pi * (t - .2) / .8) ** .7
        D.line([pt(t, -0.5), pt(t - .05, -w * 8.0)], fill=C('c4bcab') + (255,), width=S)
        if rr.random() < .6: D.line([pt(t + .02, 0.5), pt(t - .03, w * 5.0)], fill=C('b4ac9a') + (255,), width=S)
    D.line([pt(0.02, 0), pt(1.0, 0)], fill=C('a69e8c') + (255,), width=S)   # 깃대
    D.line([pt(0.02, 0), pt(.2, 0)], fill=C('ebe4d2') + (255,), width=int(S * 1.5))
    D.line([pt(0.0, 0), pt(0.05, 0)], fill=C('1a1416') + (255,), width=S)   # 펜촉(잉크)
    img = big.resize((Wd, Hd), Image.NEAREST)
    a_ = np.array(img); a_[..., 3] = np.where(a_[..., 3] > 127, 255, 0); img = Image.fromarray(a_)
    img = DT.outline(img, OUT)
    sh = DT.shadow_of(img, 3, 2, 100, (24, 12, 8)) if False else None
    m = np.array(img)[..., 3] > 0
    s = np.zeros_like(np.array(img)); sm = np.zeros_like(m); sm[2:, 3:] = m[:-2, :-3]
    s[sm & ~m] = [24, 12, 8, 95]
    out = Image.fromarray(s); out.alpha_composite(img)
    bb = out.getbbox(); out = out.crop(bb)
    return out, (int(p0[0] - bb[0]), int(p0[1] - bb[1]))

def town_frame():
    fr = Image.open(TOWN + "frame.png")
    return fr.resize((fr.width // 2, fr.height // 2), Image.NEAREST)        # 1배 633x492 — 안쪽 (13, 13) 부터 607x466
