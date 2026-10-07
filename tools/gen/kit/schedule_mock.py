"""스케줄 창 목업 — 책상 위 일정 두루마리를 가까이 당겨 본 모습. 마을 그림 · 책상과 같은 1배 607x466 (2배로 본다) + 마을 액자.
두루마리 종이에 제목 · 버튼(종이 꼬리표) · 월~금 띠와 칸 · 일과 카드 9장 · 컨디션 · 결재 봉랍을 그린다. 글자는 갈무리 도트 글꼴(1배)."""
import sys, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import desk_top as DT
import scene2d as S
from px3d import *
import props3d as PR

HERE = os.path.dirname(os.path.abspath(__file__)) + "/"
FD = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fonts") + "/"
F7 = ImageFont.truetype(FD + "Galmuri7.woff", 8); F9 = ImageFont.truetype(FD + "Galmuri9.woff", 10)
F11 = ImageFont.truetype(FD + "Galmuri11.woff", 12); F11B = ImageFont.truetype(FD + "Galmuri11-Bold.woff", 12); F14 = ImageFont.truetype(FD + "Galmuri14.woff", 15)
DW, DH = 607, 466
C = S.C
INK, INK2, FADE = C('3a2a20'), C('5c4733'), C('a48d6c')
RED, GRN, BRASS = C('a3302a'), C('3b6b33'), C('8a5e1c')
PARCH = S.PARCH
CARD = DT.CARD
new = S.new
def rect(L, x0, y0, x1, y1, c, a=255): ImageDraw.Draw(L).rectangle([x0, y0, x1, y1], fill=tuple(c[:3]) + (a,))
def text(L, xy, s, font, c, a=255):
    d = ImageDraw.Draw(L); d.fontmode = "1"; d.text(xy, s, font=font, fill=tuple(c[:3]) + (a,))
def tw(s, f): return int(f.getlength(s))
def P(L, x, y, c, a=255):
    if 0 <= x < L.width and 0 <= y < L.height: L.putpixel((int(x), int(y)), tuple(c[:3]) + (a,))

# ───────────────────────── 책상 (가까이 — 판자 · 천이 크게) ─────────────────────────
def desk_zoom(seed=4):
    rng = random.Random(seed)
    W = S.WOOD
    L = Image.new('RGB', (DW, DH)); D = ImageDraw.Draw(L)
    y = -12; k = 0
    while y < DH:
        h = 35; tone = [2, 3][k % 2]
        D.rectangle([0, y, DW - 1, y + h - 1], fill=W[tone])
        for _ in range(60):
            x0 = rng.randrange(-30, DW); ln = rng.randrange(20, 110); yy = y + 3 + rng.randrange(h - 6)
            c = W[max(tone - 1, 0)] if rng.random() < .6 else W[min(tone + 1, 5)]
            amp = rng.uniform(0, 1.6); ph = rng.uniform(0, 6)
            pts = [(x0 + i, yy + round(amp * np.sin(ph + i / 14))) for i in range(0, ln, 3)]
            if len(pts) > 1: D.line(pts, fill=c)
        D.line([(0, y), (DW, y)], fill=C('2e1a10')); D.line([(0, y + 1), (DW, y + 1)], fill=W[min(tone + 2, 5)])
        y += h; k += 1
    L = L.convert('RGBA')
    rn = S.runner(w=156, h=DH)
    L.alpha_composite(rn, (DW // 2 - 78, 0))
    return L

# ───────────────────────── 종이 · 축 ─────────────────────────
PX0, PX1, PY0, PY1 = 30, 576, 14, 451            # 종이 (포함)
def paper_zoom(w, h, seed=8):
    rng = random.Random(seed); nr = np.random.RandomState(seed)
    A = np.zeros((h, w, 4), np.uint8); A[...] = list(PARCH[3]) + [255]
    noise = nr.rand(h, w)
    yy, xx = np.mgrid[0:h, 0:w]
    blot = np.zeros((h, w))
    for _ in range(16):
        cx, cy, r = rng.uniform(0, w), rng.uniform(0, h), rng.uniform(26, 70)
        blot += np.exp(-((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * r * r)) * rng.uniform(.5, 1)
    A[(blot > 0.62) & (noise < 0.5)] = list(PARCH[2]) + [255]
    A[(blot < 0.15) & (noise > 0.93)] = list(PARCH[4]) + [255]
    A[(noise < 0.035)] = list(PARCH[2]) + [255]; A[(noise > 0.982)] = list(PARCH[4]) + [255]
    for _ in range(140):                                                   # 섬유 결
        x0, y0 = rng.randrange(w), rng.randrange(h); ln = rng.randrange(4, 14)
        c = PARCH[2] if rng.random() < .7 else PARCH[4]
        for i in range(ln):
            if 0 <= x0 + i < w: A[y0, x0 + i] = list(c) + [255]
    for x in range(w):                                                     # 양 끝 — 축으로 말려 들어가는 그늘(넓게)
        d = min(x, w - 1 - x)
        if d < 12:
            t = [0, 0, 0, 1, 1, 1, 2, 2, 2, 2, 3, 3][d]
            col = [PARCH[0], PARCH[1], PARCH[2], PARCH[2]][t]
            sel = noise[:, x] < [1, 1, 1, .9, .8, .7, .55, .45, .35, .25, .15, .08][d]
            A[sel, x] = list(col) + [255]
    for yv, cl in ((0, PARCH[1]), (h - 1, PARCH[0])):
        A[yv, :] = list(cl) + [255]
    A[1, :][noise[1] < .55] = list(PARCH[2]) + [255]; A[h - 2, :][noise[h - 2] < .55] = list(PARCH[1]) + [255]
    for x in range(0, w, 4):
        if rng.random() < .45: A[0, x:x + rng.randrange(1, 4), 3] = 0
        if rng.random() < .45: A[h - 1, x:x + rng.randrange(1, 4), 3] = 0
    return Image.fromarray(A)

def rollers_zoom():
    """가까이 본 두 축 — 종이 양쪽(세계 x = PX0, PX1 언저리), 위아래 금 마개"""
    r = 11.0; M = rotm('x', 90)
    Hs = (PY1 - PY0) + 22
    Ly2 = (Hs / 2) / np.sin(TH)
    cxs = (PX0 - 2 - DW / 2, PX1 + 2 - DW / 2)
    parts = []
    for cx in cxs:
        c = np.array([cx, 0, r])
        parts.append(Part((lambda c: (lambda P: sd_cyl(local(P, c, M), [0, 0, 0], r, Ly2, 1.4)))(c), 'paper'))
        for sy in (-1, 1):
            k = c + [0, sy * (Ly2 + 2.6), 0]
            parts.append(Part((lambda k: (lambda P: sd_cyl(local(P, k, M), [0, 0, 0], r + 2.0, 2.6, 1.0)))(k), 'gold'))
            parts.append(Part((lambda k, sy: (lambda P: sd_sphere(P, k + [0, sy * 6.0, 0], 5.0)))(k, sy), 'gold'))
    b0 = np.array([cxs[0] - r - 6, -Ly2 - 16, 0]); b1 = np.array([cxs[1] + r + 6, Ly2 + 16, 2 * r + 4])
    img, (ox, oy) = render(parts, b0, b1)
    return img, (ox, oy)

# ───────────────────────── 꾸밈 조각 ─────────────────────────
def ink_rule(L, x0, x1, y, seed=1, col=INK2):
    rng = random.Random(seed)
    yy = y
    for x in range(x0, x1):
        if rng.random() < .04: yy = y + rng.choice([-1, 0, 0, 1]) if abs(yy - y) < 1 else y
        P(L, x, yy, col, 210 if rng.random() < .9 else 120)

def tag_button(L, x, y, label, ico=None, state='normal'):
    """종이 꼬리표 버튼 — 잉크 테두리 · 위 밝은 줄 · 아래 그림자. ico: 16x14 아이콘 그림(선택)"""
    pad = 6; iw = (ico.width + 3) if ico else 0
    w = tw(label, F9) + pad * 2 + iw; h = 17
    sh = new(w + 2, h + 2); rect(sh, 2, 2, w + 1, h + 1, (60, 36, 20), 70); L.alpha_composite(sh, (x, y))
    base = C('e9d7ad') if state == 'normal' else C('e2d3b4')
    rect(L, x, y, x + w - 1, y + h - 1, INK2)
    rect(L, x + 1, y + 1, x + w - 2, y + h - 2, base)
    rect(L, x + 1, y + 1, x + w - 2, y + 1, C('f7ecd0')); rect(L, x + 1, y + h - 2, x + w - 2, y + h - 2, C('c9b083'))
    for (px, py) in ((x, y), (x + w - 1, y), (x, y + h - 1), (x + w - 1, y + h - 1)): P(L, px, py, (0, 0, 0), 0)
    if ico: L.alpha_composite(ico, (x + pad - 1, y + (h - ico.height) // 2))
    text(L, (x + pad + iw, y + 3), label, F9, INK if state == 'normal' else FADE)
    return w

def day_ribbon(L, cx, y, label, pal, w=84):
    x0, x1 = cx - w // 2, cx + w // 2
    D = ImageDraw.Draw(L)
    D.polygon([(x0 - 7, y + 2), (x0 + 2, y + 2), (x0 + 2, y + 15), (x0 - 7, y + 15), (x0 - 3, y + 8)], fill=pal[1] + (255,))
    D.polygon([(x1 + 7, y + 2), (x1 - 2, y + 2), (x1 - 2, y + 15), (x1 + 7, y + 15), (x1 + 3, y + 8)], fill=pal[1] + (255,))
    D.polygon([(x0, y + 14), (x0 + 3, y + 17), (x0 + 3, y + 14)], fill=pal[0] + (255,)); D.polygon([(x1, y + 14), (x1 - 3, y + 17), (x1 - 3, y + 14)], fill=pal[0] + (255,))
    rect(L, x0, y, x1, y + 14, pal[2]); rect(L, x0, y, x1, y + 1, pal[3]); rect(L, x0, y + 14, x1, y + 14, pal[1])
    t = tw(label, F9)
    text(L, (cx - t // 2 + 1, y + 3), label, F9, pal[0]); text(L, (cx - t // 2, y + 2), label, F9, C('fffaf0'))

def dashed_box(L, x0, y0, x1, y1, col, a=255, dash=(4, 3)):
    on, off = dash; period = on + off
    for x in range(x0, x1 + 1):
        if (x - x0) % period < on: P(L, x, y0, col, a); P(L, x, y1, col, a)
    for y in range(y0, y1 + 1):
        if (y - y0) % period < on: P(L, x0, y, col, a); P(L, x1, y, col, a)

def mini_icon(kind):
    im = new(13, 12); D = ImageDraw.Draw(im)
    if kind == 'wand':
        D.line([(1, 11), (8, 4)], fill=C('6a4a2e') + (255,), width=2)
        for (x, y) in ((9, 0), (9, 1), (9, 2), (8, 2), (10, 2), (7, 2), (11, 2), (9, 3), (9, 4)): im.putpixel((x, y), C('f2c84a') + (255,))
        im.putpixel((9, 2), C('fff3b8') + (255,)); im.putpixel((3, 3), C('f2c84a') + (255,)); im.putpixel((11, 7), C('f2c84a') + (255,))
    elif kind == 'bowl':
        D.pieslice([1, 2, 11, 12], 0, 180, fill=C('b8794a') + (255,)); D.line([(1, 7), (11, 7)], fill=C('e8d8b8') + (255,))
        D.line([(3, 8), (9, 8)], fill=C('d69a62') + (255,))
        for (x, y) in ((4, 1), (4, 3), (5, 2), (7, 0), (7, 2), (8, 1)): im.putpixel((x, y), C('cfc6b4') + (255,))
    elif kind == 'eraser':
        D.polygon([(1, 8), (6, 3), (11, 3), (11, 6), (6, 11), (1, 11)], fill=C('e88a8a') + (255,))
        D.polygon([(1, 8), (4, 5), (7, 8), (4, 11), (1, 11)], fill=C('f2f0ea') + (255,))
        D.line([(0, 11), (12, 11)], fill=C('8a7350') + (255,))
    return DT.outline(im, C('3a2a20'))
ICON = {}
def icon(kind):
    if kind not in ICON: ICON[kind] = DT.icon(kind)
    return ICON[kind]

# ───────────────────────── 카드 (가까이 본 모습) ─────────────────────────
CW, CH = 56, 106
def life_tab(L, x, y, label, tone):
    t = tw(label, F7); w = t + 12
    col = {'3': C('3b6b33'), '2': C('8a5e1c'), '1': C('a3302a')}[tone]
    rect(L, x, y, x + w - 1, y + 10, INK2); rect(L, x + 1, y + 1, x + w - 2, y + 10, C('f3e6c4'))
    rect(L, x + 1, y + 1, x + w - 2, y + 1, C('fbf4de'))
    rect(L, x + 3, y + 4, x + 5, y + 6, col)
    text(L, (x + 8, y + 2), label, F7, INK2)

def card_big(L, x, y, c):
    """c = dict(col, name, kind(아이콘), cost, fx=[(이름, 개수, 나쁨)], cond, life('3'|'2'|'1'))"""
    name, pal = CARD[c['col']]
    sh = new(CW + 3, CH + 3); rect(sh, 2, 2, CW + 1, CH + 1, (50, 30, 16), 80); L.alpha_composite(sh, (x, y))
    rect(L, x, y, x + CW - 1, y + CH - 1, pal[0])                                  # 테두리 · 두께
    rect(L, x + 1, y + 1, x + CW - 2, y + 37, pal[2])                              # 색 머리
    rect(L, x + 1, y + 1, x + CW - 2, y + 1, pal[3]); rect(L, x + 1, y + 1, x + 1, y + 37, pal[3])
    rect(L, x + CW - 2, y + 2, x + CW - 2, y + 37, pal[1])
    px0, py0, px1, py1 = x + 13, y + 6, x + CW - 14, y + 25                        # 그림 칸
    rect(L, px0, py0, px1, py1, pal[4]); rect(L, px0, py0, px1, py0, pal[1]); rect(L, px0, py0, px0, py1, pal[1])
    rect(L, px0 + 1, py1, px1, py1, pal[3]); rect(L, px1, py0 + 1, px1, py1, pal[3])
    ic = icon(c['kind']); L.alpha_composite(ic, (x + CW // 2 - 8, py0 + 3))
    t = tw(c['name'], F9)
    text(L, (x + CW // 2 - t // 2 + 1, y + 27), c['name'], F9, pal[0]); text(L, (x + CW // 2 - t // 2, y + 26), c['name'], F9, C('fffaf0'))
    rect(L, x + 1, y + 38, x + CW - 2, y + CH - 3, C('f6ecd3'))                     # 종이 쪽
    rect(L, x + 1, y + 38, x + CW - 2, y + 38, pal[1])
    rect(L, x + 1, y + CH - 2, x + CW - 2, y + CH - 2, pal[1])
    yy = y + 41
    cn = name + (' · ' + c['cost'] if c.get('cost') else '')
    rect(L, x + 4, yy + 2, x + 6, yy + 4, pal[2]); text(L, (x + 9, yy), cn, F7, INK2)
    yy += 11
    for (fname, n, bad) in c.get('fx', []):
        text(L, (x + 4, yy), fname, F7, RED if bad else INK)
        pl = '+' * n; text(L, (x + CW - 4 - tw(pl, F7), yy), pl, F7, RED if bad else GRN)
        yy += 9
    ink_rule(L, x + 4, x + CW - 4, y + CH - 15, seed=len(c['name']), col=C('cbb48a'))
    cond = c['cond']; good = cond.startswith('+')
    text(L, (x + 4, y + CH - 13), '컨디션', F7, INK2)
    text(L, (x + CW - 4 - tw(cond, F7), y + CH - 13), cond, F7, GRN if good else RED)
    lt = {'3': '3주', '2': '2주', '1': '이번 주까지'}[c['life']]
    life_tab(L, x - 2, y - 7, lt, c['life'])

def slot_empty(L, x, y):
    dashed_box(L, x, y, x + CW - 1, y + CH - 1, C('8a7350'), 230)
    rect(L, x + 2, y + 2, x + CW - 3, y + CH - 3, C('d8c296'), 70)
    for i, s in enumerate(('일과', '배치')):
        t = tw(s, F9); text(L, (x + CW // 2 - t // 2, y + CH // 2 - 11 + i * 12), s, F9, C('8f7856'))

def chain_link(L, x0, x1, y, pct):
    """앞날 카드와 오늘 카드를 잇는 금 사슬 (고리를 엇갈려) + 그 아래 능률 표"""
    D = ImageDraw.Draw(L)
    x = x0
    k = 0
    while x + 6 <= x1:
        if k % 2 == 0:
            D.ellipse([x, y - 3, x + 7, y + 3], outline=C('5e3c0e') + (255,)); D.ellipse([x + 1, y - 2, x + 6, y + 2], outline=C('e6b84a') + (255,))
            P(L, x + 2, y - 2, C('f8dc7a')); P(L, x + 3, y - 2, C('fff1c4'))
        else:
            rect(L, x - 1, y - 1, x + 7, y + 1, C('5e3c0e')); rect(L, x, y, x + 6, y, C('c08c2c')); P(L, x + 2, y, C('f8dc7a'))
        x += 5; k += 1
    s_ = f'+{pct}%'; t = tw(s_, F7); cx = (x0 + x1) // 2
    rect(L, cx - t // 2 - 3, y + 6, cx + t // 2 + 3, y + 16, BRASS); rect(L, cx - t // 2 - 2, y + 7, cx + t // 2 + 2, y + 15, C('f4e3b4'))
    text(L, (cx - t // 2, y + 7), s_, F7, BRASS)

# ───────────────────────── 컨디션 · 결재 ─────────────────────────
def condition_list(L, x, y, rows, w=250):
    text(L, (x, y), '컨디션', F9, INK2)
    ink_rule(L, x, x + w, y + 13, seed=3)
    for i, (nm, v, eff) in enumerate(rows):
        yy = y + 18 + i * 14
        text(L, (x, yy), nm, F9, INK)
        bx0, bx1 = x + 64, x + w - 74
        rect(L, bx0, yy + 2, bx1, yy + 9, INK2); rect(L, bx0 + 1, yy + 3, bx1 - 1, yy + 8, C('e9dab5'))
        fill = bx0 + 1 + int((bx1 - bx0 - 2) * v / 100)
        rect(L, bx0 + 1, yy + 3, fill, yy + 8, C('4f8a42')); rect(L, bx0 + 1, yy + 3, fill, yy + 3, C('7fb867'))
        text(L, (bx1 + 6, yy + 1), f'{v}', F9, INK)
        text(L, (bx1 + 30, yy + 2), f'효율 {eff}%', F7, INK2)

def seal_sprite(rad=15.0):
    PR.SCALE = 1.0
    parts = PR._seal_parts(np.array([0, 0, 0.4]), rad, seed=7)
    img, org = render(parts, np.array([-rad - 4, -rad - 4, 0.0]), np.array([rad + 4, rad + 4, 4.0]))
    return img, org

def approval(L, x, y, enabled, label, sub, w=230, h=86):
    """결재란 — 겹 잉크 테두리 안에 서명 줄 · 봉랍 자리. 아래 줄이 진행 단추 글자"""
    rect(L, x + 2, y + 2, x + w + 1, y + h + 1, (60, 36, 20), 60)
    rect(L, x, y, x + w - 1, y + h - 1, INK2); rect(L, x + 1, y + 1, x + w - 2, y + h - 2, C('efe0bc') if enabled else C('eadbb7'))
    rect(L, x + 3, y + 3, x + w - 4, y + h - 4, C('b89c72')); rect(L, x + 4, y + 4, x + w - 5, y + h - 5, C('f3e6c6') if enabled else C('ece0c0'))
    text(L, (x + 9, y + 8), '결재', F9, INK2)
    S.signature(L, x + 14, y + 31)
    text(L, (x + 16, y + 42), '학원장', F7, FADE)
    cx, cy = x + w - 34, y + 30
    if enabled:
        D = ImageDraw.Draw(L)
        for sx in (-1, 1):
            D.polygon([(cx + sx * 4, cy + 10), (cx + sx * 13, cy + 30), (cx + sx * 8, cy + 27), (cx + sx * 5, cy + 31), (cx + sx * 1, cy + 12)], fill=S.NAVY[2 if sx < 0 else 1] + (255,))
        img, (ox, oy) = seal_sprite(15)
        L.alpha_composite(img, (cx - ox, cy - oy))
    else:
        D = ImageDraw.Draw(L)
        for a in range(0, 360, 14):
            D.arc([cx - 17, cy - 17, cx + 17, cy + 17], a, a + 8, fill=C('a0523f') + (210,))
        t = '봉랍'; text(L, (cx - tw(t, F9) // 2, cy - 5), t, F9, C('b07a66'))
    ink_rule(L, x + 8, x + w - 9, y + 54, seed=11, col=C('c9b083'))
    text(L, (x + 10, y + 58), label, F11B, INK if enabled else FADE)
    text(L, (x + 10, y + 73), sub, F7, INK2 if enabled else FADE)

# ───────────────────────── 장면 ─────────────────────────
HAND = [
    dict(col='gold', name='휴식', kind='cup', cost='', fx=[], cond='+4', life='2'),
    dict(col='red', name='대련', kind='swords', cost='10 G/명', fx=[('적극성', 2, False), ('팀워크', 1, False), ('침착성', 1, False)], cond='-1', life='2'),
    dict(col='sky', name='휴식', kind='cup', cost='', fx=[], cond='+4', life='2'),
    dict(col='none', name='원정 파견', kind='map', cost='20 G/명', fx=[('자금', 1, False), ('유물', 1, False), ('진로 평가', 1, False), ('업보', 1, True)], cond='-1~', life='2'),
    dict(col='sky', name='명상', kind='leaf', cost='10 G/명', fx=[('정신력', 3, False), ('침착성', 1, False)], cond='-1', life='3'),
    dict(col='green', name='휴식', kind='cup', cost='', fx=[], cond='+4', life='3'),
    dict(col='blue', name='전술 연구', kind='book', cost='10 G/명', fx=[('침착성', 3, False), ('천재성', 1, False)], cond='-1', life='3'),
    dict(col='green', name='기초 체력', kind='dumbbell', cost='10 G/명', fx=[('지구력', 3, False), ('정신력', 1, False)], cond='-1', life='3'),
    dict(col='gold', name='자율 훈련', kind='target', cost='', fx=[('멘탈리티', 1, False)], cond='-2', life='3'),
]
DAYS = ['월요일', '화요일', '수요일', '목요일', '금요일']
EMPTY_PAL = [C('4a3b2c'), C('6a5644'), C('8c7660'), C('a8927a'), C('c8b49a')]

def build(state='plan'):
    base = desk_zoom()
    pw, ph = PX1 - PX0 + 1, PY1 - PY0 + 1
    sh = new(DW, DH); rect(sh, PX0 + 4, PY0 + 5, PX1 + 4, PY1 + 5, (24, 12, 8), 80); base.alpha_composite(sh)
    base.alpha_composite(paper_zoom(pw, ph), (PX0, PY0))
    L = new(DW, DH)
    # 머리
    title = '왕국력 231년 봄 2주 스케줄'
    text(L, (44, 24), title, F14, INK)
    text(L, (45, 44), '11주 후 차감 예정 자금:', F9, INK2); text(L, (45 + tw('11주 후 차감 예정 자금: ', F9), 44), '2,500 G', F9, RED)
    # 버튼 꼬리표 (오른쪽 위)
    labels = [('자동 배치', 'wand'), ('식단: 평범 (학생 당 20 G)', 'bowl'), ('전부 비우기', 'eraser')]
    icons = [mini_icon(k) for _, k in labels]
    widths = [tw(l, F9) + 12 + ic.width + 3 for (l, _), ic in zip(labels, icons)]
    x = 562 - sum(widths) - 6 * (len(labels) - 1)
    for (l, _), ic, w in zip(labels, icons, widths):
        tag_button(L, x, 26, l, ic); x += w + 6
    ink_rule(L, 42, 565, 62, seed=5)
    # 요일 — 띠 · 칸
    if state == 'plan': placed = {0: 7, 1: 5}
    elif state == 'empty': placed = {}
    else: placed = {0: 7, 1: 5, 2: 4, 3: 2, 4: 1}
    slots = [HAND[placed[i]] if i in placed else None for i in range(5)]
    colw = (565 - 42) / 5
    cxs = [int(42 + colw * (i + .5)) for i in range(5)]
    for i in range(1, 5):                                                  # 칸 사이 잉크 점선
        xx = int(42 + colw * i)
        for yy in range(70, 190):
            if (yy // 3) % 4 != 3: P(L, xx, yy, C('b89c72'), 200)
    for i, cx in enumerate(cxs):
        c = slots[i]
        day_ribbon(L, cx, 70, DAYS[i], CARD[c['col']][1] if c else EMPTY_PAL)
        x0, y0 = cx - CW // 2, 92
        if c: card_big(L, x0, y0, c)
        else: slot_empty(L, x0, y0)
    # 체인 — 전날과 같은 색이 이어진 날: 두 카드를 금 사슬로 잇는다
    run = 0
    for i in range(5):
        c = slots[i]
        prev = slots[i - 1] if i else None
        if c and prev and c['col'] == prev['col'] and c['col'] != 'none':
            run += 1
            chain_link(L, cxs[i - 1] + CW // 2 + 1, cxs[i] - CW // 2 - 1, 92 + 46, 25 * min(run, 4))
        else: run = 0
    # 일과
    hand = [h for j, h in enumerate(HAND) if j not in placed.values()]
    text(L, (44, 210), f'일과 {len(hand)}장', F11, INK2)
    text(L, (44 + tw(f'일과 {len(hand)}장', F11) + 8, 213), '카드를 끌어 요일 칸에 놓는다 · 전날과 같은 색이면 능률이 오른다', F7, FADE)
    gap = 2
    x = 43
    for j, c in enumerate(hand):
        card_big(L, x, 234 + (j % 2), c); x += CW + gap
    ink_rule(L, 42, 565, 352, seed=9)
    # 아래 — 컨디션 · 결재
    condition_list(L, 44, 360, [('카르밀라', 100, 100), ('비리디스', 100, 100), ('브랜던', 100, 100)], w=262)
    left = sum(1 for s_ in slots if not s_)
    if left: approval(L, 334, 358, False, f'일과 {left}일치 세팅 필요', '다섯 칸을 채우면 봉랍을 찍는다')
    else: approval(L, 334, 358, True, '진행 (150 G 소모)', '훈련 30 G/명 · 식단 20 G/명 · 3명')
    base.alpha_composite(L)
    # 깃펜 — 결재란 오른쪽 아래에 막 서명하고 내려놓은 듯
    q, (nx, ny) = S.quill(length=74, ang=-13)
    base.alpha_composite(q, (452 - nx, 452 - ny))
    # 축
    rimg, (rx, ry) = rollers_zoom()
    cy = (PY0 + PY1) / 2
    base.alpha_composite(rimg, (int(round(DW / 2 - rx)), int(round(cy - ry + 11 * np.cos(TH)))))
    v = np.array(S.vignette()); v[..., 3] = (v[..., 3] * 0.45).astype(np.uint8); base.alpha_composite(Image.fromarray(v))
    fr = S.town_frame()
    out = Image.new('RGBA', fr.size, (0, 0, 0, 255)); out.alpha_composite(base, (13, 13)); out.alpha_composite(fr)
    return out, base

if __name__ == "__main__":
    st = sys.argv[1] if len(sys.argv) > 1 else 'plan'
    out, base = build(st)
    out.convert('RGB').resize((out.width * 2, out.height * 2), Image.NEAREST).save(HERE + f"sched_{st}_2x.png")
    out.convert('RGB').save(HERE + f"sched_{st}_1x.png")
    print("ok")
