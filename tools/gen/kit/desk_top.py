"""스케줄 책상 — 거의 바로 위에서 내려다본 도트(1배 640x360 · 마을 그림과 같은 2배로 보면 1280x720).
학생 · 마스터의 손 없이 책상만. 두루마리에는 게임의 카드 색 여섯 가지(적 · 녹 · 청 · 하늘 · 황 · 무)를 한 줄씩 늘어놓는다.
각 줄의 카드는 그 색의 실제 훈련(CARD_COL)과 휴식 — 무색은 원정 파견뿐."""
from PIL import Image, ImageDraw, ImageFont
import numpy as np, random
import os
HERE = os.path.dirname(os.path.abspath(__file__)) + "/"
FONT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fonts") + "/"
W, H = 640, 360
rng = random.Random(5)

def C(h): h = h.lstrip('#'); return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
OUT = (40, 26, 20)

WOOD   = [C('4e2a18'), C('6e3e25'), C('8c5330'), C('a5683a'), C('bf834c')]
PARCH  = [C('a98b5f'), C('cdb184'), C('e2cb9c'), C('efdcb2'), C('f7ecca')]
NAVY   = [C('1c2140'), C('262d55'), C('323b6c'), C('43508a')]
GOLD   = [C('7a5420'), C('a8782e'), C('d1a24a'), C('ecc874'), C('fbe7a6')]
# 게임의 카드 색 (CARD_COLOR) — 어두움 → 밝음 다섯 단
CARD = {
    'red'  : ('적',   [C('7a2a33'), C('a83a46'), C('e0616a'), C('f08f92'), C('f9cfc9')]),
    'green': ('녹',   [C('24603c'), C('368552'), C('54ae70'), C('82c98d'), C('c9eac5')]),
    'blue' : ('청',   [C('2a447f'), C('3d62ad'), C('5b87dd'), C('88aaee'), C('cddcf8')]),
    'sky'  : ('하늘', [C('1a6f80'), C('2a98ad'), C('48c3d8'), C('80d9e6'), C('c8f0f5')]),
    'gold' : ('황',   [C('7c5512'), C('a97c22'), C('d9a63c'), C('ecc56a'), C('f9e7b2')]),
    'none' : ('무',   [C('484c55'), C('666b74'), C('8a8f98'), C('b1b5bc'), C('dcdee2')]),
}
COLS = ['red', 'green', 'blue', 'sky', 'gold', 'none']
DECK = {   # 색마다 실제 카드 (CARD_COL) — 휴식은 다섯 색 중 하나를 달고 온다, 무색은 원정 파견뿐
    'red'  : [('대련', 'swords'), ('모의전', 'shield'), ('휴식', 'cup')],
    'green': [('기초 체력', 'dumbbell'), ('고강도 단련', 'barbell'), ('휴식', 'cup')],
    'blue' : [('전술 연구', 'book'), ('진형 훈련', 'flag'), ('휴식', 'cup')],
    'sky'  : [('명상', 'leaf'), ('심층 명상', 'lotus'), ('휴식', 'cup')],
    'gold' : [('자율 훈련', 'target'), ('실전 타격', 'arrow'), ('휴식', 'cup')],
    'none' : [('원정 파견', 'map')],
}
F7 = ImageFont.truetype(FONT + "Galmuri7.woff", 8)
F9 = ImageFont.truetype(FONT + "Galmuri9.woff", 10)

def new(w=W, h=H): return Image.new('RGBA', (w, h), (0, 0, 0, 0))
def P(im, x, y, c, a=255):
    if 0 <= x < im.width and 0 <= y < im.height: im.putpixel((int(x), int(y)), tuple(c[:3]) + (a,))
def rect(im, x0, y0, x1, y1, c, a=255): ImageDraw.Draw(im).rectangle([x0, y0, x1, y1], fill=tuple(c[:3]) + (a,))
def poly(im, pts, c, a=255): ImageDraw.Draw(im).polygon([tuple(p) for p in pts], fill=tuple(c[:3]) + (a,))
def ell(im, x0, y0, x1, y1, c, a=255): ImageDraw.Draw(im).ellipse([x0, y0, x1, y1], fill=tuple(c[:3]) + (a,))
def ring(im, x0, y0, x1, y1, c, a=255, w=1): ImageDraw.Draw(im).ellipse([x0, y0, x1, y1], outline=tuple(c[:3]) + (a,), width=w)
def line(im, pts, c, w=1, a=255): ImageDraw.Draw(im).line([tuple(p) for p in pts], fill=tuple(c[:3]) + (a,), width=w)
def text(im, xy, s, font, c): d = ImageDraw.Draw(im); d.fontmode = "1"; d.text(xy, s, font=font, fill=tuple(c[:3]) + (255,))

def outline(im, col=OUT, diag=False):
    arr = np.array(im); a = arr[..., 3] > 0
    d = a.copy()
    d[1:, :] |= a[:-1, :]; d[:-1, :] |= a[1:, :]; d[:, 1:] |= a[:, :-1]; d[:, :-1] |= a[:, 1:]
    if diag:
        d[1:, 1:] |= a[:-1, :-1]; d[1:, :-1] |= a[:-1, 1:]; d[:-1, 1:] |= a[1:, :-1]; d[:-1, :-1] |= a[1:, 1:]
    ring_ = d & ~a
    arr[ring_] = list(col[:3]) + [255]
    return Image.fromarray(arr)
def shadow_of(im, dx=3, dy=3, a=90, col=(30, 16, 10)):
    m = np.array(im)[..., 3] > 0
    s = np.zeros(m.shape + (4,), np.uint8)
    sh = np.zeros_like(m)
    sh[dy:, dx:] = m[:m.shape[0] - dy, :m.shape[1] - dx]
    s[sh] = list(col) + [a]
    return Image.fromarray(s)
def place(base, L, sh=(3, 3, 90), ol=OUT):
    """그림자 → 테두리 → 본체"""
    if sh: base.alpha_composite(shadow_of(L, *sh))
    base.alpha_composite(outline(L, ol) if ol else L)

# ───────────────────────── 책상 ─────────────────────────
def desk():
    L = new()
    y = 0; k = 0
    while y < H:
        h = 22
        base = WOOD[2] if k % 2 == 0 else WOOD[3]
        rect(L, 0, y, W - 1, min(H - 1, y + h - 1), base)
        rect(L, 0, y, W - 1, y, WOOD[1])
        rect(L, 0, y + 1, W - 1, y + 1, WOOD[3] if base == WOOD[2] else WOOD[4])
        for x in range(rng.randrange(80), W, 190):
            rect(L, x, y, x, min(H - 1, y + h - 1), WOOD[1])
        for _ in range(95):
            x0 = rng.randrange(W); ln = rng.randrange(5, 26); yy = y + 2 + rng.randrange(h - 3)
            if yy < H: rect(L, x0, yy, min(W - 1, x0 + ln), yy, WOOD[1] if rng.random() < .55 else (WOOD[4] if base == WOOD[3] else WOOD[3]))
        for _ in range(rng.randrange(0, 2) + 1):
            kx, ky = rng.randrange(W), y + 5 + rng.randrange(h - 10)
            ell(L, kx - 4, ky - 2, kx + 4, ky + 2, WOOD[1]); ell(L, kx - 2, ky - 1, kx + 2, ky + 1, WOOD[0])
        y += h; k += 1
    return L

# ───────────────────────── 남색 천 ─────────────────────────
RX0, RX1 = 272, 368
def emblem(L, cx, cy):
    for i in range(8):
        a = 0.45 + i * 0.3
        x = int(round(cx - 15 * np.cos(a))); y = int(round(cy - 12 * np.sin(a) + 7))
        P(L, x, y, GOLD[3]); P(L, x - 1, y, GOLD[2]); P(L, 2 * cx - x, y, GOLD[3]); P(L, 2 * cx - x + 1, y, GOLD[2])
    rect(L, cx - 1, cy - 10, cx + 1, cy + 10, GOLD[3]); rect(L, cx - 7, cy - 5, cx + 7, cy - 3, GOLD[3])
    rect(L, cx, cy - 10, cx, cy + 10, GOLD[4]); rect(L, cx - 7, cy - 5, cx + 7, cy - 5, GOLD[4])
    rect(L, cx + 1, cy - 9, cx + 1, cy + 10, GOLD[1]); rect(L, cx - 6, cy - 3, cx + 7, cy - 3, GOLD[1])
def runner():
    L = new()
    rect(L, RX0, 0, RX1, H - 1, NAVY[1])
    for y in range(0, H, 4):
        for x in range(RX0 + (y // 4) % 2 * 2, RX1, 4): P(L, x, y, NAVY[2])
    for x, s in ((RX0 + 4, 1), (RX1 - 4, -1)):
        rect(L, x, 0, x, H - 1, GOLD[2]); rect(L, x + s, 0, x + s, H - 1, GOLD[1])
    for y in range(2, H, 6):
        P(L, RX0 + 8, y, GOLD[1]); P(L, RX1 - 8, y, GOLD[1])
    rect(L, RX0, 0, RX0, H - 1, NAVY[0]); rect(L, RX1, 0, RX1, H - 1, NAVY[0])
    emblem(L, 320, 316); emblem(L, 320, 30)
    return L

# ───────────────────────── 카드 그림 (16x14 · 1배) ─────────────────────────
IC = {'o': C('2a1a14'), 'S': C('eef2f6'), 's': C('aab4c0'), 'd': C('6c7684'), 'g': C('f0c050'), 'G': C('b08028'),
      'w': C('8a5a34'), 'W': C('5b3a22'), 'p': C('fbf3dc'), 'P': C('d9c49a'), 'r': C('d24a40'), 'R': C('8c2e28'),
      'n': C('62a64a'), 'N': C('3c6e2e'), 'L': C('a6d27a'), 'b': C('4f78c8'), 'B': C('2f4c8c'), 'c': C('fbf8f0'),
      'C': C('d6cdbb'), 't': C('a8642e'), 'T': C('d89a54'), 'y': C('f6d65c'), 'm': C('ead2a0'), 'M': C('c9aa70'),
      'i': C('4a4e58'), 'I': C('8a909c'), 'q': C('f6c6d2'), 'Q': C('de8aa6'), 'v': C('ffffff')}
def icon(kind):
    im = new(16, 14); D = ImageDraw.Draw(im)
    def L_(pts, k): D.line(pts, fill=IC[k] + (255,))
    def R_(b, k): D.rectangle(b, fill=IC[k] + (255,))
    def E_(b, k): D.ellipse(b, fill=IC[k] + (255,))
    def G_(pts, k): D.polygon(pts, fill=IC[k] + (255,))
    def p_(x, y, k, a=255): im.putpixel((x, y), IC[k] + (a,))
    if kind == 'swords':
        for m in (1, 0):                                   # 뒤 칼 먼저
            f = (lambda x: 15 - x) if m else (lambda x: x)
            L_([(f(2), 1), (f(9), 8)], 'S'); L_([(f(3), 1), (f(10), 8)], 's')
            for (x, y) in ((12, 7), (11, 8), (10, 9), (9, 10)): p_(f(x), y, 'g')
            p_(f(11), 10, 'w'); p_(f(12), 11, 'W'); p_(f(13), 12, 'g')
    elif kind == 'shield':
        G_([(2, 1), (13, 1), (13, 7), (8, 12), (7, 12), (2, 7)], 'g')
        G_([(3, 2), (12, 2), (12, 7), (8, 11), (7, 11), (3, 7)], 's')
        G_([(3, 2), (7, 2), (7, 11), (3, 7)], 'S')
        R_([7, 3, 8, 10], 'r'); R_([4, 5, 11, 6], 'r')
    elif kind == 'dumbbell':
        R_([4, 6, 11, 7], 'I'); R_([4, 7, 11, 7], 'i')
        for x0 in (1, 11):
            R_([x0, 2, x0 + 3, 11], 'i'); R_([x0, 2, x0, 11], 'I'); R_([x0, 2, x0 + 3, 2], 'I')
    elif kind == 'barbell':
        R_([1, 6, 14, 7], 'I'); R_([1, 7, 14, 7], 'i')
        for (a, b) in ((2, 4), (11, 13)):
            R_([a, 1, b, 12], 'R'); R_([a, 1, a, 12], 'r'); R_([a, 1, b, 1], 'r')
        R_([5, 3, 5, 10], 'i'); R_([10, 3, 10, 10], 'i')
    elif kind == 'book':
        R_([1, 3, 14, 12], 'B'); R_([1, 12, 14, 12], 'b')
        R_([1, 2, 7, 11], 'p'); R_([8, 2, 14, 11], 'p'); R_([7, 2, 8, 11], 'P')
        for y in (4, 6, 8): R_([2, y, 5, y], 'P'); R_([10, y, 13, y], 'P')
    elif kind == 'flag':
        R_([3, 1, 3, 12], 'w'); R_([4, 1, 4, 12], 'W'); p_(3, 0, 'g'); p_(4, 0, 'g')
        G_([(5, 2), (14, 2), (11, 5), (14, 8), (5, 8)], 'r'); R_([5, 2, 13, 2], 'q'); p_(8, 5, 'g'); p_(9, 5, 'g')
    elif kind == 'leaf':
        G_([(2, 12), (3, 7), (6, 3), (10, 1), (14, 1), (13, 5), (10, 9), (6, 11)], 'n')
        G_([(3, 7), (6, 3), (10, 1), (13, 1), (8, 5), (4, 9)], 'L')
        L_([(3, 11), (12, 2)], 'N'); p_(1, 13, 'N'); p_(2, 12, 'N')
    elif kind == 'lotus':
        E_([1, 9, 14, 13], 'n'); R_([2, 11, 13, 11], 'N')
        G_([(7, 1), (8, 1), (10, 5), (9, 10), (6, 10), (5, 5)], 'q')
        G_([(1, 5), (5, 6), (7, 10), (3, 10)], 'q'); G_([(14, 5), (10, 6), (8, 10), (12, 10)], 'Q')
        p_(7, 2, 'c'); p_(7, 3, 'c'); p_(2, 6, 'c'); L_([(8, 3), (8, 8)], 'Q')
    elif kind == 'target':
        E_([1, 0, 14, 13], 'r'); E_([3, 2, 12, 11], 'c'); E_([5, 4, 10, 9], 'r'); R_([7, 6, 8, 7], 'y')
    elif kind == 'arrow':
        E_([1, 3, 11, 13], 'r'); E_([3, 5, 9, 11], 'c'); E_([5, 7, 7, 9], 'r')
        L_([(6, 8), (12, 2)], 'W'); p_(13, 1, 'c'); p_(14, 2, 'c'); p_(12, 1, 'c'); p_(14, 1, 'R'); p_(13, 2, 'R')
    elif kind == 'map':
        R_([1, 2, 4, 11], 'm'); R_([5, 3, 9, 12], 'M'); R_([10, 2, 14, 11], 'm')
        for (x, y) in ((3, 9), (5, 8), (7, 8), (8, 6), (10, 6)): p_(x, y, 'R')
        for (x, y) in ((11, 3), (13, 3), (12, 4), (11, 5), (13, 5)): p_(x, y, 'r')
    elif kind == 'cup':                                     # 옆에서 본 찻잔 — 김이 오른다
        E_([0, 10, 15, 13], 'C'); E_([1, 10, 14, 12], 'c')
        G_([(1, 5), (12, 5), (11, 11), (2, 11)], 'c'); G_([(9, 5), (12, 5), (11, 11), (9, 11)], 'C')
        R_([1, 7, 12, 7], 'q'); R_([9, 7, 11, 7], 'Q')
        E_([1, 3, 12, 6], 'c'); E_([2, 4, 11, 5], 't')
        for (x, y) in ((13, 5), (14, 6), (14, 7), (14, 8), (13, 9)): p_(x, y, 'c')
        p_(12, 6, 'c'); p_(12, 9, 'C')
        out = outline(im, IC['o'])
        for (x, y) in ((5, 2), (6, 1), (5, 0), (9, 2), (10, 1), (9, 0)): out.putpixel((x, y), IC['v'] + (235,))   # 김 — 테두리 없이
        return out
    return outline(im, IC['o'])

# ───────────────────────── 두루마리 · 색 띠 · 카드 ─────────────────────────
PX0, PY0, PX1, PY1 = 134, 66, 506, 266
COLW = 60
COLX = [PX0 + 36 + COLW * i for i in range(6)]          # 줄 가운데
TAB_Y = 78; CARD_Y = [98, 144, 190]; CW, CH = 50, 38

def tab(L, cx, y, key):
    name, pal = CARD[key]
    x0, x1 = cx - 21, cx + 21
    poly(L, [(x0 - 4, y), (x1 + 4, y), (x1, y + 6), (x1 + 4, y + 12), (x0 - 4, y + 12), (x0, y + 6)], pal[1])   # 꼬리
    rect(L, x0, y - 1, x1, y + 13, pal[2]); rect(L, x0, y - 1, x1, y - 1, pal[3]); rect(L, x0, y + 13, x1, y + 13, pal[1])
    rect(L, x0, y - 1, x0, y + 13, pal[1]); rect(L, x1, y - 1, x1, y + 13, pal[1])
    tw = F9.getlength(name)
    text(L, (cx - tw / 2 + 1, y + 2), name, F9, pal[0])
    text(L, (cx - tw / 2, y + 1), name, F9, C('fffaf0'))

def card(L, x, y, key, label, kind):
    name, pal = CARD[key]
    rect(L, x, y, x + CW - 1, y + CH - 1, pal[2])
    rect(L, x, y, x + CW - 1, y, pal[3]); rect(L, x, y, x, y + CH - 1, pal[3])
    rect(L, x + CW - 1, y + 1, x + CW - 1, y + CH - 1, pal[1]); rect(L, x + 1, y + CH - 1, x + CW - 1, y + CH - 1, pal[1])
    px0, py0, px1, py1 = x + 3, y + 3, x + CW - 4, y + 22                  # 그림 칸
    rect(L, px0, py0, px1, py1, pal[4]); rect(L, px0, py0, px1, py0, pal[1]); rect(L, px0, py0, px0, py1, pal[1])
    ic = icon(kind); L.alpha_composite(ic, (x + CW // 2 - 8, py0 + 3))
    tw = F7.getlength(label)
    text(L, (x + CW / 2 - tw / 2 + 1, y + 27), label, F7, pal[0])
    text(L, (x + CW / 2 - tw / 2, y + 26), label, F7, C('fffaf0'))

def scroll():
    L = new()
    rect(L, PX0, PY0, PX1, PY1, PARCH[3])
    for y in range(PY0, PY1 + 1):
        for x in range(PX0, PX1 + 1):
            r = rng.random()
            if r < .04: P(L, x, y, PARCH[2])
            elif r < .055: P(L, x, y, PARCH[4])
    for y in (PY0, PY0 + 1, PY1 - 1, PY1): rect(L, PX0, y, PX1, y, PARCH[1] if y in (PY0, PY1) else PARCH[2])
    for x in range(PX0, PX1, 7): P(L, x + rng.randrange(5), PY0, PARCH[2]); P(L, x + rng.randrange(5), PY1, PARCH[0])
    for i in range(1, 6):                                                   # 줄 사이 잉크 선
        x = COLX[i] - COLW // 2
        for y in range(TAB_Y - 4, CARD_Y[-1] + CH + 4):
            if (y // 3) % 4 != 3: P(L, x, y, PARCH[1])
    for i, key in enumerate(COLS):
        tab(L, COLX[i], TAB_Y, key)
        for j, (label, kind) in enumerate(DECK[key]):
            card(L, COLX[i] - CW // 2, CARD_Y[j], key, label, kind)
    return L

def rollers():
    L = new()
    for (x0, x1) in ((PX0 - 18, PX0 + 1), (PX1 - 1, PX1 + 18)):
        y0, y1 = PY0 - 6, PY1 + 6
        rect(L, x0, y0, x1, y1, PARCH[2])
        rect(L, x0 + 2, y0, x0 + 5, y1, PARCH[4]); rect(L, x0 + 6, y0, x0 + 8, y1, PARCH[3])
        rect(L, x1 - 4, y0, x1, y1, PARCH[1]); rect(L, x1, y0, x1, y1, PARCH[0])
        for yy in range(y0 + 3, y1 - 2, 9): rect(L, x0 + 1, yy, x1 - 1, yy, PARCH[1]) if False else None
        cx = (x0 + x1) // 2
        for yy, s in ((y0 - 5, 1), (y1 + 1, -1)):                          # 금 마개
            rect(L, cx - 4, yy, cx + 4, yy + 4, GOLD[2]); rect(L, cx - 4, yy, cx - 3, yy + 4, GOLD[3]); rect(L, cx + 3, yy, cx + 4, yy + 4, GOLD[1])
            ell(L, cx - 3, yy + (4 if s < 0 else -2), cx + 3, yy + (6 if s < 0 else 0), GOLD[2])
    return L


# ───────────────────────── 소품 (위에서 본 모습 · 앞면이 조금 보인다) ─────────────────────────
IRON = [C('241f1d'), C('3a322d'), C('54473d'), C('76634f'), C('9a8468')]
def rot(cx, cy, pts, ang):
    a = np.radians(ang); ca, sa = np.cos(a), np.sin(a)
    return [(cx + x * ca - y * sa, cy + x * sa + y * ca) for (x, y) in pts]

def book_top(L, cx, cy, w, h, ang, t, cov, gem=None, band=True):
    """위에서 본 책 — 표지(회전) + 화면 아래쪽으로 보이는 책장 두께 t"""
    c0, c1, c2 = cov
    q = rot(cx, cy, [(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)], ang)
    lo = sorted(q, key=lambda p: p[1])[2:]                      # 아래쪽 두 꼭짓점
    lo = sorted(lo, key=lambda p: p[0])
    poly(L, [lo[0], lo[1], (lo[1][0], lo[1][1] + t), (lo[0][0], lo[0][1] + t)], PARCH[3])
    for k in range(1, t, 2):
        line(L, [(lo[0][0] + 2, lo[0][1] + k), (lo[1][0] - 1, lo[1][1] + k)], PARCH[1])
    line(L, [(lo[0][0], lo[0][1] + t), (lo[1][0], lo[1][1] + t)], c0)
    poly(L, q, c1)
    edge = rot(cx, cy, [(-w / 2, -h / 2), (w / 2, -h / 2)], ang); line(L, edge, c2)
    edge = rot(cx, cy, [(-w / 2, -h / 2), (-w / 2, h / 2)], ang); line(L, edge, c2)
    sp = rot(cx, cy, [(-w / 2 + 1, -h / 2 + 1), (-w / 2 + 5, -h / 2 + 1), (-w / 2 + 5, h / 2 - 1), (-w / 2 + 1, h / 2 - 1)], ang)
    poly(L, sp, c0)                                              # 책등 쪽 띠
    if band:
        fr = rot(cx, cy, [(-w / 2 + 9, -h / 2 + 4), (w / 2 - 4, -h / 2 + 4), (w / 2 - 4, h / 2 - 4), (-w / 2 + 9, h / 2 - 4)], ang)
        line(L, fr + [fr[0]], GOLD[2])
        for p in fr: P(L, round(p[0]), round(p[1]), GOLD[4])
    if gem:
        gx, gy = rot(cx, cy, [(2.5, 0)], ang)[0]
        ell(L, gx - 5, gy - 5, gx + 5, gy + 5, GOLD[2]); ell(L, gx - 3, gy - 3, gx + 3, gy + 3, gem[0]); P(L, gx - 1, gy - 1, gem[1]); P(L, gx - 2, gy - 1, gem[1])

def coin(L, x, y, face=True):
    ell(L, x - 4, y - 3, x + 4, y + 4, GOLD[0]); ell(L, x - 4, y - 4, x + 4, y + 3, GOLD[2])
    ell(L, x - 3, y - 3, x + 3, y + 2, GOLD[3]); ring(L, x - 3, y - 3, x + 3, y + 2, GOLD[2])
    P(L, x - 2, y - 2, GOLD[4]); P(L, x - 1, y - 3, GOLD[4]); P(L, x, y, GOLD[2]); P(L, x + 1, y - 1, GOLD[2])

def lantern(L, lx, ly, E=None):
    """위에서 본 유리 등잔 — 놋쇠 받침 · 빛나는 유리 갓 · 가운데 굴뚝 속 불꽃 · 옆 손잡이"""
    ring(L, lx + 13, ly - 5, lx + 26, ly + 8, GOLD[0], w=3); ring(L, lx + 13, ly - 6, lx + 26, ly + 7, GOLD[2])
    ell(L, lx - 19, ly - 16, lx + 19, ly + 22, GOLD[0]); ell(L, lx - 19, ly - 18, lx + 19, ly + 19, GOLD[1])
    ell(L, lx - 17, ly - 17, lx + 16, ly + 15, GOLD[2]); ell(L, lx - 16, ly - 17, lx + 8, ly + 6, GOLD[3])
    for T in ([L] + ([E] if E is not None else [])):
        ell(T, lx - 14, ly - 14, lx + 14, ly + 14, C('f6c768'))              # 유리 갓
        ell(T, lx - 12, ly - 12, lx + 12, ly + 12, C('ffe29a')); ell(T, lx - 11, ly - 11, lx + 8, ly + 8, C('fff0c4'))
        ring(T, lx - 6, ly - 6, lx + 6, ly + 6, GOLD[2], w=2)                  # 굴뚝 테
        ell(T, lx - 4, ly - 4, lx + 4, ly + 4, C('ffb347')); ell(T, lx - 3, ly - 3, lx + 2, ly + 2, C('ffe08a'))
        ell(T, lx - 2, ly - 2, lx + 1, ly + 1, C('ffffff'))
        for (x, y) in ((lx - 9, ly - 8), (lx - 8, ly - 9), (lx - 10, ly - 6)): P(T, x, y, C('ffffff'))

def candle(L, cx, cy, E=None):
    ell(L, cx - 14, cy - 8, cx + 14, cy + 12, GOLD[1]); ell(L, cx - 14, cy - 9, cx + 14, cy + 10, GOLD[2]); ell(L, cx - 10, cy - 6, cx + 10, cy + 7, GOLD[3])
    ring(L, cx + 12, cy - 2, cx + 20, cy + 6, GOLD[1], w=2)
    rect(L, cx - 5, cy - 6, cx + 5, cy + 3, C('e9dcc0')); rect(L, cx + 2, cy - 6, cx + 5, cy + 3, C('cfbf9e'))   # 초 몸통 앞면
    ell(L, cx - 5, cy - 9, cx + 5, cy - 3, C('fbf3dc')); ell(L, cx - 2, cy - 7, cx + 2, cy - 5, C('efe2c2'))
    P(L, cx - 3, cy - 2, C('fbf3dc')); P(L, cx - 3, cy - 1, C('fbf3dc'))
    for (x, y, c) in ((cx, cy - 16, 'ffb54a'), (cx, cy - 15, 'ffd36a'), (cx - 1, cy - 14, 'ffb54a'), (cx, cy - 14, 'fff2c0'), (cx + 1, cy - 14, 'ffd36a'),
                      (cx - 1, cy - 13, 'ffd36a'), (cx, cy - 13, 'ffffff'), (cx + 1, cy - 13, 'fff2c0'), (cx - 1, cy - 12, 'ffb54a'), (cx, cy - 12, 'fff2c0'), (cx + 1, cy - 12, 'ffb54a'), (cx, cy - 11, 'e0703a'), (cx, cy - 10, '3a2a20')):
        P(L, x, y, C(c))
        if E is not None and c != '3a2a20': P(E, x, y, C(c))

def envelope(L):
    q = rot(52, 110, [(-38, -22), (38, -22), (38, 22), (-38, 22)], -7)
    poly(L, q, C('eedcb0'))
    m = rot(52, 110, [(0, 4)], -7)[0]
    poly(L, [q[0], q[1], m], C('e2cd9c'))
    line(L, [q[0], m, q[1]], C('b89c68'))
    line(L, [q[3], (m[0], m[1] + 6), q[2]], C('d8c290'))
    ell(L, m[0] - 7, m[1] - 6, m[0] + 7, m[1] + 7, C('1f3570')); ell(L, m[0] - 6, m[1] - 6, m[0] + 6, m[1] + 5, C('2f4f98'))
    ell(L, m[0] - 3, m[1] - 3, m[0] + 3, m[1] + 2, C('25407e')); P(L, m[0] - 3, m[1] - 4, C('8fb0e8')); P(L, m[0] - 4, m[1] - 3, C('8fb0e8'))

def pouch(L, x, y):
    """가죽 동전 주머니 — 옆으로 누워 오른쪽으로 입이 벌어지고 동전이 쏟아진다"""
    LEA = [C('3a1f14'), C('5c3220'), C('7c4630'), C('9a5e3e'), C('b87a52')]
    ell(L, x - 20, y - 14, x + 8, y + 15, LEA[1])                                         # 몸통
    ell(L, x - 19, y - 14, x + 5, y + 10, LEA[2]); ell(L, x - 16, y - 12, x - 2, y + 1, LEA[3]); ell(L, x - 13, y - 10, x - 7, y - 5, LEA[4])
    poly(L, [(x + 2, y - 9), (x + 13, y - 4), (x + 13, y + 3), (x + 2, y + 10)], LEA[1])        # 모인 목
    poly(L, [(x + 2, y - 9), (x + 13, y - 4), (x + 13, y - 1), (x + 3, y - 3)], LEA[2])
    for (a, b) in (((x + 12, y - 2), (x - 4, y - 9)), ((x + 12, y), (x - 6, y + 1)), ((x + 12, y + 2), (x - 3, y + 9))):  # 주름
        line(L, [a, ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2 + 1), b], LEA[0])
    pts = []
    for i in range(14):                                                                   # 물결 주둥이
        a = -np.pi / 2 + i / 13 * np.pi; r = 11 + (1.6 if i % 2 else -0.4)
        pts.append((x + 17 + np.cos(a) * r * .75, y + np.sin(a) * r))
    poly(L, [(x + 13, y - 6)] + pts + [(x + 13, y + 5)], LEA[3])
    ell(L, x + 16, y - 7, x + 25, y + 7, LEA[0])
    for (cx_, cy_) in ((x + 20, y - 2), (x + 22, y + 3), (x + 19, y + 3)): ell(L, cx_ - 2, cy_ - 1, cx_ + 2, cy_ + 1, GOLD[3]); P(L, cx_ - 1, cy_ - 1, GOLD[4])
    rect(L, x + 11, y - 6, x + 13, y + 5, C('d8b47a')); rect(L, x + 11, y - 6, x + 11, y + 5, C('f0d29a'))   # 끈
    line(L, [(x + 12, y + 5), (x + 7, y + 16)], C('c8a46a')); line(L, [(x + 13, y + 5), (x + 18, y + 15)], C('c8a46a'))
    ell(L, x + 5, y + 15, x + 9, y + 19, C('c8a46a')); ell(L, x + 16, y + 14, x + 20, y + 18, C('c8a46a'))

def spectacles(L, cx, cy):
    for sx in (-14, 14):
        ell(L, cx + sx - 10, cy - 8, cx + sx + 10, cy + 8, C('cfe3ec'), 120)
        ring(L, cx + sx - 10, cy - 8, cx + sx + 10, cy + 8, GOLD[2], w=2); ring(L, cx + sx - 10, cy - 8, cx + sx + 10, cy + 8, GOLD[3])
        P(L, cx + sx - 5, cy - 4, C('ffffff')); P(L, cx + sx - 4, cy - 5, C('ffffff')); P(L, cx + sx - 6, cy - 3, C('ffffff'))
    line(L, [(cx - 4, cy - 3), (cx - 1, cy - 5), (cx + 1, cy - 5), (cx + 4, cy - 3)], GOLD[2], 2)
    line(L, [(cx - 24, cy - 3), (cx - 30, cy - 12), (cx - 10, cy - 15)], GOLD[2], 1)               # 접힌 다리
    line(L, [(cx + 24, cy - 3), (cx + 30, cy - 12), (cx + 10, cy - 15)], GOLD[2], 1)

def teacup(L, cx, cy):
    ell(L, cx - 26, cy - 15, cx + 26, cy + 19, C('cdc3ae')); ell(L, cx - 26, cy - 17, cx + 26, cy + 16, C('f4efe2'))
    ring(L, cx - 21, cy - 13, cx + 21, cy + 12, C('d9cfb8'))
    ell(L, cx - 15, cy - 11, cx + 15, cy + 14, C('d6ccb6'))                               # 잔 앞면
    ell(L, cx - 15, cy - 13, cx + 15, cy + 11, C('fbf8f0'))
    ring(L, cx - 15, cy - 13, cx + 15, cy + 11, GOLD[2])
    ell(L, cx - 12, cy - 10, cx + 12, cy + 8, C('8a4a22')); ell(L, cx - 11, cy - 9, cx + 10, cy + 6, C('a8642e'))
    ell(L, cx - 8, cy - 7, cx - 2, cy - 4, C('d89a54')); P(L, cx - 7, cy - 6, C('f2c890'))
    ring(L, cx + 13, cy - 5, cx + 24, cy + 5, C('f4efe2'), w=3); ring(L, cx + 13, cy - 5, cx + 24, cy + 5, C('d6ccb6'))

def watch(L, cx, cy):
    pts = []
    for i in range(16):                                                                  # 줄
        t = i / 15; x = cx - 4 - t * 40 + np.sin(t * 3.2) * 10; y = cy - 15 - t * 6 + np.cos(t * 2.4) * 8 - 8
        pts.append((x, y))
    for i, (x, y) in enumerate(pts):
        ell(L, x - 1.5, y - 1.5, x + 1.5, y + 1.5, GOLD[2] if i % 2 else GOLD[3])
    ring(L, cx - 4, cy - 19, cx + 4, cy - 11, GOLD[2], w=2)
    rect(L, cx - 2, cy - 14, cx + 2, cy - 11, GOLD[2])
    ell(L, cx - 13, cy - 11, cx + 13, cy + 15, GOLD[1]); ell(L, cx - 13, cy - 12, cx + 13, cy + 13, GOLD[2])
    ell(L, cx - 13, cy - 12, cx + 9, cy + 9, GOLD[3])
    ell(L, cx - 10, cy - 9, cx + 10, cy + 10, C('fbf6e8'))
    for i in range(12):
        a = i / 12 * 2 * np.pi; P(L, round(cx + np.sin(a) * 8), round(cy + .5 - np.cos(a) * 8), C('6a5a48'))
    line(L, [(cx, cy), (cx, cy - 6)], C('2a2420')); line(L, [(cx, cy), (cx + 4, cy + 2)], C('2a2420')); P(L, cx, cy, GOLD[1])

def inkwell(L, x, y):
    """유리 잉크병 — 위에서. 앞면이 조금 보이고, 가운데 놋쇠 목 안에 잉크"""
    G = [C('0e1424'), C('1a2540'), C('263759'), C('3b5480'), C('7d98c4')]
    rect(L, x + 1, y + 21, x + 23, y + 26, G[0]); rect(L, x + 2, y + 21, x + 6, y + 25, G[1])          # 앞면
    rect(L, x, y, x + 24, y + 21, G[2]); rect(L, x + 1, y + 1, x + 23, y + 20, G[1])
    rect(L, x + 1, y + 1, x + 23, y + 2, G[3]); rect(L, x + 1, y + 1, x + 2, y + 20, G[3])
    rect(L, x + 3, y + 4, x + 4, y + 17, G[4]); P(L, x + 5, y + 4, G[4])
    ell(L, x + 5, y + 4, x + 19, y + 18, GOLD[0]); ell(L, x + 5, y + 4, x + 19, y + 17, GOLD[2]); ell(L, x + 5, y + 4, x + 16, y + 14, GOLD[3])
    ell(L, x + 8, y + 7, x + 16, y + 15, C('07090e')); P(L, x + 10, y + 9, C('5a6a90')); P(L, x + 11, y + 9, C('3a4a70'))

def quill(L, x0, y0, x1, y1):
    """흰 깃펜 — 펜촉은 잉크병 입에, 깃은 책상 위로 눕는다"""
    p0 = np.array([x0, y0], float); v = np.array([x1 - x0, y1 - y0], float); u = v / np.linalg.norm(v); n = np.array([-u[1], u[0]])
    left, right = [], []
    for t in np.linspace(.22, 1, 40):
        c = p0 + v * t; k = (t - .22) / .78
        w = np.sin(np.pi * k) ** .75
        left.append(tuple(c + n * w * 7.5 - u * w * 1.5)); right.append(tuple(c - n * w * 4.5 - u * w * 1.0))
    poly(L, left + right[::-1], C('f6f3ec'))
    poly(L, [tuple(p0 + v * .22)] + right + [tuple(p0 + v)], C('d6d0c3'))
    for t in (.42, .58, .74):                                                             # 깃 갈라진 곳
        c = p0 + v * t; w = np.sin(np.pi * (t - .22) / .78) ** .75
        line(L, [tuple(c + n * 1), tuple(c + n * w * 7.2 - u * 3)], C('cbc4b5'))
    line(L, [tuple(p0 + v * .12), tuple(p0 + v)], C('a9a293'))
    line(L, [tuple(p0), tuple(p0 + v * .22)], C('e9e2d2'))
    P(L, x0, y0, C('1a1416')); P(L, round(x0 + u[0]), round(y0 + u[1]), C('3a3030'))

def globe(L, cx, cy):
    ell(L, cx - 22, cy + 8, cx + 22, cy + 30, C('4e2e1a')); ell(L, cx - 22, cy + 6, cx + 22, cy + 27, C('6e4428'))   # 받침
    ell(L, cx - 20, cy - 20, cx + 20, cy + 20, C('2f6c80'))
    ell(L, cx - 19, cy - 20, cx + 17, cy + 16, C('3f86a0')); ell(L, cx - 16, cy - 17, cx + 6, cy + 2, C('5aa2b8'))
    for blob in ([(cx - 12, cy - 10), (cx - 3, cy - 14), (cx + 2, cy - 7), (cx - 4, cy - 1), (cx - 11, cy - 2)],
                 [(cx + 4, cy + 3), (cx + 13, cy + 1), (cx + 14, cy + 9), (cx + 7, cy + 14), (cx + 2, cy + 9)],
                 [(cx - 15, cy + 5), (cx - 9, cy + 6), (cx - 8, cy + 12), (cx - 14, cy + 11)]):
        poly(L, blob, C('6f9a52')); P(L, blob[0][0] + 2, blob[0][1] + 1, C('9cc070'))
    P(L, cx - 9, cy - 13, C('cfe6ec')); P(L, cx - 10, cy - 12, C('cfe6ec')); P(L, cx - 8, cy - 14, C('cfe6ec'))
    ring(L, cx - 26, cy - 24, cx + 26, cy + 24, GOLD[1], w=3); ring(L, cx - 26, cy - 25, cx + 26, cy + 23, GOLD[3])   # 지평 고리
    ring(L, cx - 5, cy - 22, cx + 5, cy + 22, GOLD[2])                                    # 자오 고리
    ell(L, cx - 2, cy - 25, cx + 2, cy - 21, GOLD[3])

def bouquet(L, cx, cy):
    rr = random.Random(3)
    LEAF = [C('2f4a26'), C('4a6c35'), C('6a8f4c'), C('93b56b')]
    for _ in range(46):
        a = rr.uniform(0, 2 * np.pi); r = 12 + rr.random() * 26
        lx, ly = cx + np.cos(a) * r, cy + np.sin(a) * r
        ca, sa = np.cos(a), np.sin(a)
        pts = [(lx + ca * 8, ly + sa * 8), (lx - sa * 3, ly + ca * 3), (lx - ca * 5, ly - sa * 5), (lx + sa * 3, ly - ca * 3)]
        poly(L, pts, LEAF[2]); poly(L, [pts[0], pts[1], pts[2]], LEAF[1]); P(L, lx - sa, ly + ca, LEAF[3])
    ell(L, cx - 10, cy - 10, cx + 10, cy + 10, LEAF[0])
    PET = [C('cdc3ae'), C('e2dacb'), C('f2eee4'), C('fefcf6')]
    bl = []
    for _ in range(600):
        a = rr.uniform(0, 2 * np.pi); r = np.sqrt(rr.random()) * 30
        x, y = cx + np.cos(a) * r, cy + np.sin(a) * r
        if all((x - bx) ** 2 + (y - by) ** 2 > 64 for bx, by in bl): bl.append((x, y))
    for bx, by in sorted(bl, key=lambda b: b[1]):
        x, y = int(round(bx)), int(round(by))
        for (ox, oy, k) in ((-1, -3, 3), (0, -3, 3), (1, -3, 2), (-3, -1, 3), (3, -1, 2), (-3, 0, 2), (3, 0, 1), (-3, 1, 2), (3, 1, 1), (-1, 3, 1), (0, 3, 0), (1, 3, 0),
                            (-2, -2, 3), (2, -2, 2), (-2, 2, 1), (2, 2, 0)):
            P(L, x + ox, y + oy, PET[k])
        for oy in (-2, -1, 0, 1, 2):
            for ox in (-2, -1, 0, 1, 2):
                if abs(ox) + abs(oy) <= 3: P(L, x + ox, y + oy, PET[3] if ox + oy < 0 else PET[2])
        ell(L, x - 1, y - 1, x + 1, y + 1, C('e8b94a')); P(L, x + 1, y + 1, C('c48f2c')); P(L, x - 1, y - 1, C('f6d97a'))

def rolled_map(L, x0, y0, x1):
    rect(L, x0, y0, x1, y0 + 13, PARCH[3]); rect(L, x0, y0, x1, y0 + 2, PARCH[4]); rect(L, x0, y0 + 9, x1, y0 + 13, PARCH[1])
    rect(L, x0, y0 + 12, x1, y0 + 13, PARCH[0])
    for x in (x0, x1 - 6):
        ell(L, x, y0, x + 6, y0 + 13, PARCH[2]); ring(L, x + 1, y0 + 3, x + 5, y0 + 10, PARCH[0]); P(L, x + 3, y0 + 6, PARCH[0])
    m = (x0 + x1) // 2
    rect(L, m - 2, y0 - 1, m + 2, y0 + 14, C('b8352c')); rect(L, m - 2, y0 - 1, m - 1, y0 + 14, C('d6584a'))
    poly(L, [(m, y0 + 6), (m - 9, y0 + 1), (m - 9, y0 + 11)], C('9c2c24')); poly(L, [(m, y0 + 6), (m + 9, y0 + 1), (m + 9, y0 + 11)], C('9c2c24'))
    line(L, [(m - 1, y0 + 13), (m - 6, y0 + 24)], C('b8352c'), 2); line(L, [(m + 1, y0 + 13), (m + 5, y0 + 23)], C('9c2c24'), 2)

def wax_seal(L, cx, cy):
    rr = random.Random(9)
    poly(L, [(cx - 4, cy + 6), (cx - 10, cy + 26), (cx - 6, cy + 23), (cx - 3, cy + 27), (cx, cy + 8)], NAVY[2])   # 리본 꼬리
    poly(L, [(cx + 4, cy + 6), (cx + 11, cy + 25), (cx + 7, cy + 22), (cx + 3, cy + 26), (cx, cy + 8)], NAVY[1])
    pts = []
    for i in range(20):
        a = i / 20 * 2 * np.pi; r = 12 + rr.uniform(-1.2, 1.4)
        pts.append((cx + np.cos(a) * r, cy + np.sin(a) * r))
    poly(L, pts, C('8c2a24'))
    ell(L, cx - 11, cy - 11, cx + 10, cy + 10, C('b8352c')); ell(L, cx - 8, cy - 8, cx + 8, cy + 8, C('9c2c24'))
    ell(L, cx - 7, cy - 8, cx + 7, cy + 6, C('c7453a'))
    rect(L, cx - 1, cy - 6, cx + 1, cy + 5, C('8c2a24')); rect(L, cx - 4, cy - 3, cx + 4, cy - 1, C('8c2a24'))
    rect(L, cx - 1, cy - 6, cx - 1, cy + 5, C('e07a6a')); rect(L, cx - 4, cy - 3, cx + 4, cy - 3, C('e07a6a'))
    P(L, cx - 8, cy - 7, C('f0a090')); P(L, cx - 7, cy - 8, C('f0a090'))

def catmull(pts, n=10):
    out = []
    P_ = [pts[0]] + pts + [pts[-1]]
    for i in range(1, len(P_) - 2):
        p0, p1, p2, p3 = map(np.array, (P_[i - 1], P_[i], P_[i + 1], P_[i + 2]))
        for t in np.linspace(0, 1, n, endpoint=False):
            out.append(tuple(.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3)))
    out.append(tuple(pts[-1]))
    return out
def signature(L, x0, y0):
    INK = C('4a3430')
    line(L, [(x0 - 2, y0 + 8), (x0 + 96, y0 + 8)], PARCH[1])
    ctrl = [(0, 5), (4, -7), (8, -9), (9, -3), (5, 3), (2, 2), (9, -1), (13, 0), (15, -4), (14, 1), (18, 2), (21, -3), (22, 2), (26, 1), (28, -5), (30, -8), (30, 1),
            (33, 2), (36, -2), (38, 1), (41, 0), (44, -3), (46, 1), (50, 0), (54, -2), (58, 0), (64, -1)]
    line(L, catmull([(x0 + x, y0 + y) for x, y in ctrl], 12), INK)
    line(L, catmull([(x0 + 4, y0 + 6), (x0 + 30, y0 + 4), (x0 + 60, y0 + 5), (x0 + 74, y0 + 2)], 12), INK)
    P(L, x0 + 78, y0 - 1, INK); P(L, x0 + 79, y0 - 1, INK)

def glow(base, lights):
    arr = np.array(base).astype(float)
    yy, xx = np.mgrid[0:H, 0:W]
    acc = np.zeros((H, W))
    for (lx, ly, rx, ry, s) in lights:
        acc += np.exp(-(((xx - lx) / rx) ** 2 + ((yy - ly) / ry) ** 2)) * s
    vig = np.clip(1 - .30 * (((xx - W / 2) / (W / 2)) ** 2 * .75 + ((yy - H / 2) / (H / 2)) ** 2 * .75), .62, 1)
    tint = np.array([1.0, .74, .42])
    for k in range(3): arr[..., k] *= vig + acc * tint[k]
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))

EMIT = None
def props_layers():
    out = []
    Lb = new(); rolled_map(Lb, 150, 20, 250); out.append(('map', Lb))
    Lc = new(); candle(Lc, 432, 32, EMIT); out.append(('candle', Lc))
    Ll = new(); lantern(Ll, 50, 44, EMIT); out.append(('lantern', Ll))
    Le = new(); envelope(Le); out.append(('envelope', Le))
    Lk = new()
    book_top(Lk, 56, 206, 84, 58, 4, 5, (C('161c38'), NAVY[1], NAVY[3]))
    book_top(Lk, 52, 198, 78, 54, -4, 5, (C('3a2214'), C('6a4026'), C('8c5a36')))
    book_top(Lk, 54, 190, 72, 50, 2, 5, (C('4a1818'), C('7a2c2a'), C('9a4440')), gem=(C('2f8a6a'), C('9fe0c0')))
    out.append(('books_l', Lk))
    Lp = new(); pouch(Lp, 40, 306)
    for (x, y) in ((74, 300), (84, 296), (80, 308), (93, 302), (90, 314), (104, 296), (101, 310), (112, 304), (70, 318)): coin(Lp, x, y)
    out.append(('pouch', Lp))
    Ls = new(); spectacles(Ls, 214, 316); out.append(('glasses', Ls))
    Lt = new(); teacup(Lt, 432, 314); out.append(('tea', Lt))
    Lg = new(); globe(Lg, 572, 98); out.append(('globe', Lg))
    Li = new(); inkwell(Li, 540, 160); quill(Li, 552, 171, 626, 128); out.append(('ink', Li))
    Lr = new()
    book_top(Lr, 584, 238, 80, 50, -3, 5, (C('2a1a12'), C('5b3a24'), C('7a5234')))
    book_top(Lr, 580, 232, 70, 44, 5, 5, (C('161c38'), NAVY[1], NAVY[3]), gem=(C('a8302a'), C('f0a090')))
    out.append(('books_r', Lr))
    Lw = new(); watch(Lw, 580, 312); out.append(('watch', Lw))
    Lf = new(); bouquet(Lf, 622, 18); out.append(('flowers', Lf))
    return out

def build(out_name="desk_top"):
    global EMIT
    EMIT = new()
    base = Image.new('RGBA', (W, H), (0, 0, 0, 255))
    base.alpha_composite(desk())
    base.alpha_composite(runner())
    for name, L in props_layers():
        place(base, L, (3, 3, 95))
    sc = scroll(); place(base, sc, (4, 4, 95))
    Lw = new(); wax_seal(Lw, COLX[5], 206); signature(Lw, 160, 246); place(base, Lw, (2, 2, 80))
    place(base, rollers(), (3, 3, 80))
    out = glow(base, [(50, 44, 70, 62, .55), (432, 22, 48, 40, .35), (320, 180, 360, 220, .06)])
    out.alpha_composite(EMIT)
    out = out.convert('RGB')
    out.save(HERE + out_name + "_1x.png")
    out.resize((W * 2, H * 2), Image.NEAREST).save(HERE + out_name + "_2x.png")
    return out

if __name__ == "__main__":
    build(); print("ok")
