"""스케줄 창 목업 v2 — 물마루 글꼴 · 학생 15명 · 시간이 지나며 자라는 개인 행동 자리.

그림(책상 · 종이 · 카드 · 띠 · 단추 몸통 · 막대)은 1배로 그려 2배로 키우고, 글자는 2배 화면 위에 물마루로 바로 쓴다.
게임의 도트 모드와 같다 — 본문 12px · 제목 24px (24px 은 글꼴 한 칸 = 그림 한 칸이라 짝수 좌표에 놓는다).

아래 띠(개인 행동 · 컨디션 · 의뢰 · 결재)가 자라는 자리다.
  · 왼쪽 — 개인 행동 머리(전원 단추) → 부상 알림 → 컨디션 명부(학생 6명부터 두 단, 15명이면 8+7줄)
  · 오른쪽 — 의뢰 공고 쪽지(의뢰가 열리면) → 결재
"""
import sys, math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont

import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import desk_top as DT
import scene2d as S
from px3d import TH
import schedule_mock as SM

HERE = os.path.dirname(os.path.abspath(__file__)) + "/"
MD = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fonts") + "/"
M12 = ImageFont.truetype(MD + "mulmaru.woff2", 12)
M24 = ImageFont.truetype(MD + "mulmaru.woff2", 24)
N12 = ImageFont.truetype(MD + "mulmaru_mono.woff2", 12)

DW, DH = 607, 466
C = S.C; new = S.new
INK, INK2, FADE = C('3a2a20'), C('5c4733'), C('a48d6c')
RED, GRN, BRASS, AMBER = C('a3302a'), C('3b6b33'), C('8a5e1c'), C('9a6410')
WHITE = C('fffaf0')
CARD = DT.CARD

def w(s, f=M12): return int(round(f.getlength(s)))
def ev(v): return int(v) // 2 * 2
def rect(L, x0, y0, x1, y1, c, a=255):
    if x1 < x0 or y1 < y0: return
    ImageDraw.Draw(L).rectangle([x0, y0, x1, y1], fill=tuple(c[:3]) + (a,))
def P(L, x, y, c, a=255):
    if 0 <= x < L.width and 0 <= y < L.height: L.putpixel((int(x), int(y)), tuple(c[:3]) + (a,))

class Sc:
    """L — 1배 그림 (종이 위) · T — 2배 화면에 쓸 글자"""
    def __init__(s):
        s.L = new(DW, DH); s.T = []
    def t(s, x, y, txt, f=M12, c=INK, sh=None, so=None):
        if so is None: so = 2 if f is M24 else 1
        s.T.append((int(x), int(y), txt, f, c, sh, so))
        return w(txt, f)
    def runs(s, x, y, parts, f=M12):
        for txt, c in parts: x += s.t(x, y, txt, f, c)
        return x

def draw_texts(img2, T):
    d = ImageDraw.Draw(img2); d.fontmode = "1"
    for (x, y, s, f, c, sh, so) in T:
        if sh is not None: d.text((x + so, y + so), s, font=f, fill=tuple(sh[:3]) + (255,))
        d.text((x, y), s, font=f, fill=tuple(c[:3]) + (255,))

# ───────────────────────── 작은 그림 ─────────────────────────
def mini(kind):
    """8x8 단추 아이콘"""
    im = new(8, 8)
    def p(x, y, c): im.putpixel((x, y), C(c) + (255,))
    if kind == 'wand':
        for i in range(6): p(i, 7 - i, '6a4a2e')
        for (x, y) in ((6, 0), (5, 1), (7, 1), (6, 2)): p(x, y, 'd99a1e')
        p(6, 1, 'fff3b8'); p(2, 1, 'd99a1e'); p(7, 5, 'd99a1e')
    elif kind == 'bowl':
        for (x, y) in ((2, 0), (3, 1), (2, 2), (5, 0), (6, 1), (5, 2)): p(x, y, 'a89c84')
        for x in range(8): p(x, 4, 'f2e6c8')
        for x in range(1, 7): p(x, 5, 'b8794a')
        for x in range(2, 6): p(x, 6, '9a5f36')
        for x in range(3, 5): p(x, 7, '6e4126')
    elif kind == 'eraser':
        rows = ['....ppp.', '...pppPd', '..wpppd.', '.wwwPd..', 'wwwwd...', 'wwwd....', '.dd.....', '........']
        pal = {'p': 'e88a8a', 'P': 'c96a6a', 'w': 'f4f0e6', 'd': '8a6a50'}
        for y, r in enumerate(rows):
            for x, ch in enumerate(r):
                if ch in pal: p(x, y, pal[ch])
    elif kind == 'book':
        rows = ['.bbbbbb.', 'bwwwwwwb', 'bwbbbbwb', 'bwwwwwwb', 'bwbbbwwb', 'bwwwwwwb', 'bggggggb', '.bbbbbb.']
        pal = {'b': '3c4f8a', 'w': 'f1ead6', 'g': 'c9a24a'}
        for y, r in enumerate(rows):
            for x, ch in enumerate(r):
                if ch in pal: p(x, y, pal[ch])
    elif kind == 'water':
        rows = ['...cc...', '...dd...', '..dLLd..', '.dLLLLd.', 'dLLwLLLd', 'dLLLLLLd', '.dLLLLd.', '..dddd..']
        pal = {'c': '8a5e1c', 'd': '2f6f86', 'L': '7fd0e0', 'w': 'f2fbff'}
        for y, r in enumerate(rows):
            for x, ch in enumerate(r):
                if ch in pal: p(x, y, pal[ch])
    return im

def cross(L, x, y, c=RED):
    """6x6 붉은 십자 — 부상"""
    for (a, b) in ((2, 0), (3, 0), (2, 1), (3, 1), (2, 4), (3, 4), (2, 5), (3, 5)): P(L, x + a, y + b, c)
    for a in range(6):
        P(L, x + a, y + 2, c); P(L, x + a, y + 3, c)
    P(L, x + 2, y + 2, C('d9665a')); P(L, x + 2, y + 0, C('d9665a'))

ICON = {}
def icon(kind):
    if kind not in ICON: ICON[kind] = DT.icon(kind)
    return ICON[kind]

# ───────────────────────── 종이 꼬리표 단추 ─────────────────────────
BTN_EDGE = {'n': INK2, 'bad': RED, 'off': C('ad987a'), 'brass': BRASS, 'ok': GRN}
BTN_TXT = {'n': INK, 'bad': RED, 'off': FADE, 'brass': BRASS, 'ok': GRN}
def btn_w(label, ico=None):
    off = (8 + ico.width * 2 + 5) if ico else 12
    return (off + w(label) + 12 + 1) // 2
def btn(sc, x, y, label, ico=None, tone='n', right=False):
    """높이 12 (그림 칸). right=True 면 x 가 오른쪽 끝 칸. 돌려주는 값: (왼쪽 x, 너비)"""
    off = (8 + ico.width * 2 + 5) if ico else 12
    wa = btn_w(label, ico); h = 12
    if right: x = x - wa + 1
    L = sc.L
    sh = new(wa + 2, h + 2); rect(sh, 2, 2, wa + 1, h + 1, (60, 36, 20), 70); L.alpha_composite(sh, (x, y))
    base = C('e4d6b6') if tone == 'off' else C('ecdcb4')
    rect(L, x, y, x + wa - 1, y + h - 1, BTN_EDGE[tone])
    rect(L, x + 1, y + 1, x + wa - 2, y + h - 2, base)
    rect(L, x + 1, y + 1, x + wa - 2, y + 1, C('f8eed4')); rect(L, x + 1, y + h - 2, x + wa - 2, y + h - 2, C('cdb488'))
    for (px, py) in ((x, y), (x + wa - 1, y), (x, y + h - 1), (x + wa - 1, y + h - 1)): P(L, px, py, (0, 0, 0), 0)
    if ico: L.alpha_composite(ico, (x + 4, y + (h - ico.height) // 2))
    sc.t(2 * x + off, 2 * y + 6, label, M12, BTN_TXT[tone])
    return x, wa

def btn_row_right(sc, xr, y, items, gap=4):
    """오른쪽 끝(xr)에서 왼쪽으로 단추를 늘어놓는다. items = [(label, ico, tone)] (왼→오 순서)"""
    x = xr
    for label, ico, tone in reversed(items):
        x0, wa = btn(sc, x, y, label, ico, tone, right=True)
        x = x0 - gap

# ───────────────────────── 요일 띠 ─────────────────────────
def ribbon(sc, cx, y, label, pal, wdt=84):
    L = sc.L; D = ImageDraw.Draw(L)
    x0, x1 = cx - wdt // 2, cx + wdt // 2
    D.polygon([(x0 - 7, y + 2), (x0 + 2, y + 2), (x0 + 2, y + 15), (x0 - 7, y + 15), (x0 - 3, y + 8)], fill=pal[1] + (255,))
    D.polygon([(x1 + 7, y + 2), (x1 - 2, y + 2), (x1 - 2, y + 15), (x1 + 7, y + 15), (x1 + 3, y + 8)], fill=pal[1] + (255,))
    D.polygon([(x0, y + 14), (x0 + 3, y + 17), (x0 + 3, y + 14)], fill=pal[0] + (255,))
    D.polygon([(x1, y + 14), (x1 - 3, y + 17), (x1 - 3, y + 14)], fill=pal[0] + (255,))
    rect(L, x0, y, x1, y + 14, pal[2]); rect(L, x0, y, x1, y + 1, pal[3]); rect(L, x0, y + 14, x1, y + 14, pal[1])
    sc.t(ev(2 * cx - w(label, M24) / 2), 2 * y + 4, label, M24, WHITE, sh=pal[0], so=2)

# ───────────────────────── 카드 ─────────────────────────
CW, CH = 56, 80
HB = 27          # 색 머리 마지막 줄
def life_tab(sc, x, y, label, tone):
    col = {'3': GRN, '2': BRASS, '1': RED}[tone]
    wa = (14 + w(label) + 6 + 1) // 2
    L = sc.L
    rect(L, x, y, x + wa - 1, y + 7, INK2); rect(L, x + 1, y + 1, x + wa - 2, y + 7, C('f3e6c4'))
    rect(L, x + 1, y + 1, x + wa - 2, y + 1, C('fbf4de'))
    rect(L, x + 2, y + 3, x + 4, y + 5, col)
    sc.t(2 * x + 13, 2 * y + 3, label, M12, INK2)

def mark_badge(sc, x, y, mk):
    """카드 표식 (×2 두 배 등) — 카드 오른쪽 위 금 딱지"""
    L = sc.L
    lab = mk
    wa = (w(lab) + 9) // 2
    rect(L, x - wa + 1, y, x, y + 8, BRASS); rect(L, x - wa + 2, y + 1, x - 1, y + 7, C('f6e3a8'))
    rect(L, x - wa + 2, y + 1, x - 1, y + 1, C('fff4cc'))
    sc.t(2 * (x - wa + 1) + 5, 2 * y + 4, lab, M12, BRASS)

def card(sc, x, y, c):
    name, pal = CARD[c['col']]
    L = sc.L
    sh = new(CW + 3, CH + 3); rect(sh, 2, 2, CW + 1, CH + 1, (50, 30, 16), 80); L.alpha_composite(sh, (x, y))
    rect(L, x, y, x + CW - 1, y + CH - 1, pal[0])
    rect(L, x + 1, y + 1, x + CW - 2, y + HB, pal[2])
    rect(L, x + 1, y + 1, x + CW - 2, y + 1, pal[3]); rect(L, x + 1, y + 1, x + 1, y + HB, pal[3])
    rect(L, x + CW - 2, y + 2, x + CW - 2, y + HB, pal[1])
    px0, py0, px1, py1 = x + 17, y + 3, x + 38, y + 19
    rect(L, px0, py0, px1, py1, pal[4]); rect(L, px0, py0, px1, py0, pal[1]); rect(L, px0, py0, px0, py1, pal[1])
    rect(L, px0 + 1, py1, px1, py1, pal[3]); rect(L, px1, py0 + 1, px1, py1, pal[3])
    L.alpha_composite(icon(c['kind']), (x + 20, y + 5))
    sc.t(2 * x + CW - w(c['name']) // 2, 2 * y + 42, c['name'], M12, WHITE, sh=pal[0])
    rect(L, x + 1, y + HB + 1, x + CW - 2, y + CH - 3, C('f6ecd3'))
    rect(L, x + 1, y + HB + 1, x + CW - 2, y + HB + 1, pal[1])
    rect(L, x + 1, y + CH - 2, x + CW - 2, y + CH - 2, pal[1])
    rect(L, x + 4, y + 32, x + 5, y + 33, pal[2])
    cn = name + (' · ' + c['cost'] if c.get('cost') else '')
    sc.t(2 * x + 15, 2 * y + 60, cn, M12, INK2)
    yy = 2 * y + 76
    for (fname, n, bad) in c.get('fx', []):
        sc.t(2 * x + 8, yy, fname, M12, RED if bad else INK)
        pl = '+' * n
        sc.t(2 * x + 2 * CW - 8 - w(pl), yy, pl, M12, RED if bad else GRN)
        yy += 14
    SM.ink_rule(L, x + 4, x + CW - 4, y + CH - 11, seed=len(c['name']) + 3, col=C('cbb48a'))
    cond = c['cond']
    sc.t(2 * x + 8, 2 * y + 142, '컨디션', M12, INK2)
    sc.t(2 * x + 2 * CW - 8 - w(cond), 2 * y + 142, cond, M12, GRN if cond.startswith('+') else RED)
    lt = {'3': '3주', '2': '2주', '1': '이번 주까지'}[c['life']]
    life_tab(sc, x - 2, y - 7, lt, c['life'])
    if c.get('mark'): mark_badge(sc, x + CW + 1, y - 4, c['mark'])

def slot_empty(sc, x, y):
    SM.dashed_box(sc.L, x, y, x + CW - 1, y + CH - 1, C('8a7350'), 230)
    rect(sc.L, x + 2, y + 2, x + CW - 3, y + CH - 3, C('d8c296'), 70)
    for i, s in enumerate(('일과', '배치')):
        sc.t(2 * x + CW - w(s) // 2, 2 * y + CH - 14 + i * 16, s, M12, C('8f7856'))

def chain(sc, x0, x1, y, pct):
    L = sc.L; D = ImageDraw.Draw(L)
    x = x0; k = 0
    while x + 6 <= x1:
        if k % 2 == 0:
            D.ellipse([x, y - 3, x + 7, y + 3], outline=C('5e3c0e') + (255,)); D.ellipse([x + 1, y - 2, x + 6, y + 2], outline=C('e6b84a') + (255,))
            P(L, x + 2, y - 2, C('f8dc7a')); P(L, x + 3, y - 2, C('fff1c4'))
        else:
            rect(L, x - 1, y - 1, x + 7, y + 1, C('5e3c0e')); rect(L, x, y, x + 6, y, C('c08c2c')); P(L, x + 2, y, C('f8dc7a'))
        x += 5; k += 1
    s_ = f'+{pct}%'; tw_ = w(s_)
    wa = (tw_ + 10 + 1) // 2
    bx = (x0 + x1) // 2 - wa // 2
    rect(L, bx, y + 6, bx + wa - 1, y + 16, BRASS); rect(L, bx + 1, y + 7, bx + wa - 2, y + 15, C('f4e3b4'))
    sc.t(2 * bx + (2 * wa - tw_) // 2, 2 * (y + 6) + 6, s_, M12, BRASS)

# ───────────────────────── 명부 (개인 행동 · 컨디션) ─────────────────────────
CHIP = {'auto': ('임의', C('84704f'), None, C('a89070')), 'train': ('훈련', INK, C('e6d2a4'), INK2),
        'rest': ('휴식', GRN, C('d3e3bb'), GRN), 'job': ('의뢰', BRASS, C('f2dc9c'), BRASS)}
def chip(sc, x, y, act):
    lab, tc, fill, edge = CHIP[act]
    L = sc.L; wa = 15
    if fill is None:
        for i in range(wa):
            if i % 2 == 0: P(L, x + i, y, edge); P(L, x + i, y + 7, edge)
        for j in range(8):
            if j % 2 == 0: P(L, x, y + j, edge); P(L, x + wa - 1, y + j, edge)
    else:
        rect(L, x, y, x + wa - 1, y + 7, edge); rect(L, x + 1, y + 1, x + wa - 2, y + 6, fill)
        rect(L, x + 1, y + 1, x + wa - 2, y + 1, tuple(min(255, v + 18) for v in fill))
    sc.t(2 * x + 4, 2 * y + 3, lab, M12, tc)

def tone(v):
    if v >= 70: return GRN, C('4f8a42'), C('86bd6c'), 100
    if v >= 40: return AMBER, C('c3922c'), C('e6c262'), 60
    return RED, C('b0473a'), C('d97a62'), 20

ROW_H = 9
def roster_row(sc, x, y, s, chips, eff_mul, colw):
    L = sc.L
    if s.get('act') == 'rest': rect(L, x - 2, y, x + colw - 4, y + ROW_H - 1, C('cfe2b0'), 80)
    sc.t(2 * x, 2 * y + 3, s['n'], M12, INK)
    if chips:
        chip(sc, x + 31, y, s['act'])
        if s.get('inj'):
            cross(L, x + 48, y + 1)
            sc.t(2 * (x + 48) + 15, 2 * y + 3, f"{s['inj']}주", M12, RED)
        bx = x + 66
    else:
        bx = x + 33
    bw = 80
    v = s['c']; tc, fc, hc, pct = tone(v)
    rect(L, bx, y + 2, bx + bw - 1, y + 6, C('8c7353'))
    rect(L, bx + 1, y + 3, bx + bw - 2, y + 5, C('e8d8b2'))
    if v > 0:
        fx1 = bx + 1 + max(0, round((bw - 3) * v / 100))
        rect(L, bx + 1, y + 3, fx1, y + 5, fc); rect(L, bx + 1, y + 3, fx1, y + 3, hc)
    vs = str(v)
    sc.t(2 * (bx + bw) + 4 + (18 - w(vs, N12)), 2 * y + 3, vs, N12, tc)
    sc.t(2 * (bx + bw) + 28, 2 * y + 3, f'{round(pct * eff_mul)}%', M12, tc)

MAX_ST = 15
def roster(sc, x0, y0, studs, chips, eff_mul, colw=192, gap=6):
    """명부 — 처음부터 15줄(8 + 7) 자리가 그어져 있고, 컨디션 낮은 순으로 위에서부터 채운다 (왼쪽 단 → 오른쪽 단)"""
    studs = sorted(studs, key=lambda s: s['c'])
    per = math.ceil(MAX_ST / 2)
    L = sc.L
    for i in range(MAX_ST):
        col, row = divmod(i, per)
        x, y = x0 + col * (colw + gap), y0 + row * ROW_H
        for xx in range(x - 1, x + colw - 6):                             # 명부 줄 (빈 줄도 긋는다)
            if xx % 2 == 0: P(L, xx, y + ROW_H - 1, C('b39668'), 170 if i < len(studs) else 150)
        if i < len(studs): roster_row(sc, x, y, studs[i], chips, eff_mul, colw)
    xx = x0 + colw + gap // 2 - 1                                          # 두 단 사이 점선
    for yy in range(y0, y0 + per * ROW_H - 1):
        if (yy // 2) % 2 == 0: P(L, xx, yy, C('a08660'), 200)
    return y0 + per * ROW_H

# ───────────────────────── 알림 · 의뢰 쪽지 · 결재 ─────────────────────────
def injury_box(sc, x0, x1, y, hurt):
    """부상 알림 — 붉은 테 두 줄 + 휴식 전환 단추"""
    L = sc.L
    rect(L, x0, y, x1, y + 19, RED); rect(L, x0 + 1, y + 1, x1 - 1, y + 18, C('f3dfc8'))
    rect(L, x0 + 1, y + 1, x1 - 1, y + 1, C('fbeedd'))
    cross(L, x0 + 5, y + 4)
    bad = [h for h in hurt if h['act'] != 'rest']
    parts = [(f'부상 {len(hurt)}명  ', RED)]
    for i, h in enumerate(hurt):
        parts.append((('' if i == 0 else ' · ') + f"{h['n']} ", INK))
        parts.append((f"{h['inj']}주", RED))
        if h['act'] == 'rest': parts.append((' 휴식 중', GRN))
    sc.runs(2 * x0 + 24, 2 * y + 7, parts)
    sc.runs(2 * x0 + 24, 2 * y + 22, [('멘탈리티 50% · 휴식 외 훈련은 실패', FADE)] +
            ([(f" — {', '.join(h['n'] for h in bad)} 훈련 중", RED)] if bad else []))
    if bad: btn(sc, x1 - 4, y + 4, f'휴식 전환 ({len(bad)}명)', tone='bad', right=True)

def job_slip(sc, x0, x1, y0, J):
    """의뢰 공고 쪽지 — 의뢰가 열린 뒤 (여름 제외)"""
    L = sc.L
    y1 = y0 + 60
    sh = new(DW, DH); rect(sh, x0 + 2, y0 + 3, x1 + 2, y1 + 3, (40, 22, 10), 60); L.alpha_composite(sh)
    rect(L, x0, y0, x1, y1, C('c2a274')); rect(L, x0 + 1, y0 + 1, x1 - 1, y1 - 1, C('f9f0da'))
    rect(L, x0 + 1, y0 + 1, x1 - 1, y0 + 1, C('fffaea'))
    rng = random.Random(3)                                                 # 아래 가장자리 — 찢긴 결
    for x in range(x0, x1 + 1):
        r = rng.random()
        if r < .28: P(L, x, y1, (0, 0, 0), 0)
        elif r < .4: P(L, x, y1, C('d9c39a'))
    cx, py = x1 - 12, y0 + 4                                               # 놋쇠 압정 (오른쪽 위)
    for (dx, dy, a) in ((1, 2, 90), (2, 2, 70), (2, 1, 70), (3, 2, 40), (2, 3, 40)): P(L, cx + dx, py + dy, (60, 36, 20), a)
    pin = ['.ddd.', 'dhLLd', 'dLLMd', 'dLMMd', '.ddd.']
    pc = {'d': '6a4618', 'L': 'ecc874', 'M': 'c99a3e', 'h': 'fff2c0'}
    for j, r in enumerate(pin):
        for i, ch in enumerate(r):
            if ch in pc: P(L, cx - 2 + i, py - 2 + j, C(pc[ch]))
    X = 2 * x0 + 12
    sc.t(ev(X), 2 * y0 + 12, '의뢰', M24, BRASS)
    gx = x0 + 6 + (w('의뢰', M24) + 1) // 2 + 3
    lab = f"{J['grade']}등급"; wa = (w(lab) + 9) // 2
    rect(L, gx, y0 + 9, gx + wa - 1, y0 + 17, BRASS); rect(L, gx + 1, y0 + 10, gx + wa - 2, y0 + 16, C('f6e3a8'))
    sc.t(2 * gx + 5, 2 * y0 + 22, lab, M12, BRASS)
    sc.runs(X, 2 * y0 + 42, [('보수 ', INK2), (f"{J['pay']} G/일", BRASS), (' · 컨디션 ', INK2), ('-2/일', RED)])
    sc.runs(X, 2 * y0 + 56, [('멘탈리티 하나 ', INK2), ('▲', GRN), (' · 하나 ', INK2), ('▼', RED)])
    xx = sc.runs(X, 2 * y0 + 70, [('누적 ', INK2), (f"{J['cnt']} / {J['nxt']}회", INK)])
    bx0 = (xx + 8) // 2; bx1 = x1 - 6
    rect(L, bx0, y0 + 36, bx1, y0 + 39, C('8c7353')); rect(L, bx0 + 1, y0 + 37, bx1 - 1, y0 + 38, C('e8d8b2'))
    fx1 = bx0 + 1 + round((bx1 - bx0 - 2) * J['cnt'] / J['nxt'])
    rect(L, bx0 + 1, y0 + 37, fx1, y0 + 38, C('c3922c')); rect(L, bx0 + 1, y0 + 37, fx1, y0 + 37, C('e6c262'))
    sc.runs(X, 2 * y0 + 84, [('이번 주 ', INK2), (f"의뢰 {J['n']}명", BRASS), (' · 최대 ', INK2), (f"+{J['max']} G", BRASS)])
    sc.t(X, 2 * y0 + 100, '의뢰처는 첫 의뢰 때 정해진다', M12, FADE)

def sig_small(L, x0, y0):
    ink = C('4a3430')
    S.line(L, [(x0 - 2, y0 + 6), (x0 + 66, y0 + 6)], S.PARCH[1])
    ctrl = [(0, 5), (4, -7), (8, -9), (9, -3), (5, 3), (2, 2), (9, -1), (13, 0), (15, -4), (14, 1), (18, 2), (21, -3), (22, 2), (26, 1), (28, -5), (30, -8), (30, 1),
            (33, 2), (36, -2), (38, 1), (41, 0), (44, -3), (46, 1), (50, 0), (54, -2), (58, 0), (64, -1)]
    k = .78
    S.line(L, DT.catmull([(x0 + x * k, y0 + y * .8) for x, y in ctrl], 12), ink)
    S.line(L, DT.catmull([(x0 + 3, y0 + 5), (x0 + 22, y0 + 3), (x0 + 44, y0 + 4), (x0 + 56, y0 + 1)], 12), ink)

def approval(sc, x, y, wdt, hgt, enabled, label, subs):
    L = sc.L
    rect(L, x + 2, y + 2, x + wdt + 1, y + hgt + 1, (60, 36, 20), 60)
    rect(L, x, y, x + wdt - 1, y + hgt - 1, INK2); rect(L, x + 1, y + 1, x + wdt - 2, y + hgt - 2, C('efe0bc') if enabled else C('eadbb7'))
    rect(L, x + 3, y + 3, x + wdt - 4, y + hgt - 4, C('b89c72')); rect(L, x + 4, y + 4, x + wdt - 5, y + hgt - 5, C('f3e6c6') if enabled else C('ece0c0'))
    sc.t(2 * x + 14, 2 * y + 12, '결재', M12, INK2)
    sig_small(L, x + 14, y + 21)
    sc.t(2 * x + 24, 2 * y + 58, '학원장', M12, FADE)
    cx, cy = x + wdt - 27, y + 19
    D = ImageDraw.Draw(L)
    if enabled:
        for sx in (-1, 1):
            D.polygon([(cx + sx * 4, cy + 8), (cx + sx * 11, cy + 18), (cx + sx * 7, cy + 17), (cx + sx * 4, cy + 19), (cx + sx * 1, cy + 10)],
                      fill=S.NAVY[2 if sx < 0 else 1] + (255,))
        img, (ox, oy) = SM.seal_sprite(13)
        L.alpha_composite(img, (cx - ox, cy - oy))
    else:
        for a in range(0, 360, 14):
            D.arc([cx - 14, cy - 14, cx + 14, cy + 14], a, a + 8, fill=C('a0523f') + (210,))
        sc.t(2 * cx - w('봉랍') // 2, 2 * cy - 5, '봉랍', M12, C('b07a66'))
    SM.ink_rule(L, x + 8, x + wdt - 9, y + 37, seed=11, col=C('c9b083'))
    sc.t(ev(2 * x + 14), ev(2 * y + 82), label, M24, INK if enabled else FADE)
    yy = 2 * y + 110
    for parts in subs:
        sc.runs(2 * x + 16, yy, parts); yy += 14

# ───────────────────────── 카드 묶음 ─────────────────────────
def K(col, name, kind, cost='', fx=(), cond='-1', life='3', mark=None):
    return dict(col=col, name=name, kind=kind, cost=cost, fx=list(fx), cond=cond, life=life, mark=mark)
G10, G20 = '10 G/명', '20 G/명'
def basic(c='green', life='3'): return K(c, '기초 체력', 'dumbbell', G10, [('지구력', 3, 0), ('정신력', 1, 0)], '-1', life)
def heavy(life='2'): return K('green', '고강도 단련', 'barbell', G20, [('지구력', 4, 0), ('정신력', 2, 0)], '-2', life)
def rest(c, life='3'): return K(c, '휴식', 'cup', '', [], '+4', life)
def spar(life='2'): return K('red', '대련', 'swords', G10, [('적극성', 2, 0), ('팀워크', 1, 0), ('침착성', 1, 0)], '-1', life)
def mock(life='3'): return K('red', '모의전', 'shield', G20, [('팀워크', 3, 0), ('침착성', 3, 0), ('천재성', 2, 0)], '-3', life)
def tact(life='3'): return K('blue', '전술 연구', 'book', G10, [('침착성', 3, 0), ('천재성', 1, 0)], '-1', life)
def form(life='3'): return K('blue', '진형 훈련', 'flag', G20, [('팀워크', 3, 0), ('천재성', 2, 0)], '-2', life)
def medit(life='3'): return K('sky', '명상', 'leaf', G10, [('정신력', 3, 0), ('침착성', 1, 0)], '-1', life)
def deep(life='3', mark=None): return K('sky', '심층 명상', 'lotus', G20, [('정신력', 4, 0), ('천재성', 2, 0)], '-2', life, mark)
def free(life='3'): return K('gold', '자율 훈련', 'target', '', [('멘탈리티', 1, 0)], '-2', life)
def strike(life='1'): return K('gold', '실전 타격', 'arrow', G20, [('적극성', 4, 0), ('침착성', 2, 0)], '-2', life)
def exped(life='2'): return K('none', '원정 파견', 'map', G20, [('자금', 1, 0), ('유물', 1, 0), ('진로 평가', 1, 0), ('업보', 1, 1)], '-1~', life)

def St(n, c, act='auto', inj=0): return dict(n=n, c=c, act=act, inj=inj)

STATES = {
    # 1년차 봄 2주 — 개인 행동이 열리기 전. 학생 3명, 컨디션만
    'early': dict(
        title='왕국력 231년 봄 2주 스케줄', due=('11주 후', '2,500 G'), diet='식단: 평범 (학생 당 20 G)',
        days=[basic(), rest('green'), None, None, None],
        hand=[rest('gold', '2'), spar(), rest('sky', '2'), exped(), medit(), tact(), free()],
        studs=[St('카르밀라', 100), St('비리디스', 100), St('브랜던', 100)],
        act=False, job=None, church=False, undo=0, eff=1.0,
        ok=False, label='일과 3일치 세팅 필요', subs=[[('다섯 칸을 채우면 봉랍을 찍는다', FADE)]]),
    # 1년차 봄 5주 — 개인 행동이 열린 뒤. 학생 6명 · 다섯 칸을 채워 봉랍이 찍힌 상태
    'mid': dict(
        title='왕국력 231년 봄 5주 스케줄', due=('8주 후', '3,150 G'), diet='식단: 평범 (학생 당 20 G)',
        days=[basic(), rest('green'), medit(), spar(), rest('gold', '2')],
        hand=[tact(), exped(), free(), rest('sky')],
        studs=[St('로빈', 35, 'rest'), St('카르밀라', 58, 'train'), St('비리디스', 64), St('브랜던', 72),
               St('가웨인', 81, 'train'), St('세라핀', 90)],
        act=True, job=None, church=False, undo=1, eff=1.0,
        ok=True, label='진행 (240 G 소모)',
        subs=[[('일과 30 G × 4명 · 식단 20 G × 6명', INK2)], [('쉬는 2명은 일과 비용이 없다', FADE)]]),
    # 3년차 가을 5주 — 학생 15명 · 의뢰 2등급 · 부상 2명 · 교회 2단계(성수 · 예지의 서)
    'late': dict(
        title='왕국력 233년 가을 5주 스케줄', due=('8주 후', '21,350 G'), diet='식단: 균형 잡힘 (학생 당 40 G)',
        days=[heavy(), rest('green'), deep('3', '×2'), None, None],
        hand=[mock(), spar('1'), form(), rest('gold', '2'), exped('3'), strike()],
        studs=[St('비리디스', 18, 'train', 3), St('가웨인', 31, 'rest', 1), St('토르핀', 44, 'rest'), St('아리아', 52),
               St('녹스', 57, 'job'), St('카르밀라', 63, 'train'), St('헤이즐', 68), St('이졸데', 71, 'job'),
               St('브랜던', 74, 'train'), St('레온하르트', 79), St('세라핀', 83, 'job'), St('로빈', 88, 'train'),
               St('유페미아', 92), St('바스티안', 96), St('실비아', 100, 'train')],
        act=True, job=dict(grade=2, pay=200, cnt=137, nxt=500, n=3, max='3,000'), church=True, undo=2, eff=1.1,
        ok=False, label='일과 2일치 세팅 필요', subs=[[('다섯 칸을 채우면 봉랍을 찍는다', FADE)]]),
}
DAYS = ['월요일', '화요일', '수요일', '목요일', '금요일']
EMPTY_PAL = SM.EMPTY_PAL

# 자리 (그림 칸)
X0, X1 = 42, 565
Y_RIB, Y_DAY, Y_HANDL, Y_HAND, Y_RULE2, Y_BAND = 54, 78, 164, 186, 272, 280
XL1 = 432                    # 왼쪽(개인 행동) 끝
XR0 = 440                    # 오른쪽(의뢰 · 결재) 시작

def content(sc, st):
    """종이 위 내용 — 머리 · 요일 · 손패 · 아래 띠 (1배 그림은 sc.L, 글자는 sc.T)"""
    L = sc.L
    # ── 머리 ──
    sc.t(88, 44, st['title'], M24, INK)
    sc.runs(90, 74, [(f"{st['due'][0]} 차감 예정 자금: ", INK2), (st['due'][1], RED)])
    btn_row_right(sc, X1 - 2, 24, [('자동 배치', mini('wand'), 'n'), (st['diet'], mini('bowl'), 'n'), ('전부 비우기', mini('eraser'), 'n')])
    SM.ink_rule(L, X0, X1, 48, seed=5)
    # ── 요일 ──
    colw = (X1 - X0) / 5
    cxs = [int(X0 + colw * (i + .5)) for i in range(5)]
    for i in range(1, 5):
        xx = int(X0 + colw * i)
        for yy in range(Y_RIB + 2, Y_DAY + CH + 2):
            if (yy // 3) % 4 != 3: P(L, xx, yy, C('b89c72'), 200)
    slots = st['days']
    for i, cx in enumerate(cxs):
        c = slots[i]
        ribbon(sc, cx, Y_RIB, DAYS[i], CARD[c['col']][1] if c else EMPTY_PAL)
        if c: card(sc, cx - CW // 2, Y_DAY, c)
        else: slot_empty(sc, cx - CW // 2, Y_DAY)
    run = 0
    for i in range(5):
        c, prev = slots[i], (slots[i - 1] if i else None)
        if c and prev and c['col'] == prev['col'] and c['col'] != 'none':
            run += 1; chain(sc, cxs[i - 1] + CW // 2 + 1, cxs[i] - CW // 2 - 1, Y_DAY + CH // 2, 25 * min(run, 4))
        else: run = 0
    # ── 일과 (손패) ──
    hand = st['hand']
    lab = f'일과 {len(hand)}장'
    sc.t(88, 2 * Y_HANDL, lab, M24, INK2)
    sc.t(88 + w(lab, M24) + 12, 2 * Y_HANDL + 10, '카드를 끌어 요일 칸에 놓는다 · 전날과 같은 색이면 능률이 오른다', M12, FADE)
    if st['church']:
        btn_row_right(sc, X1 - 2, Y_HANDL, [('예지의 서 (일과 교체) ×1', mini('book'), 'n'), ('예지의 서 구매 · 800 G', None, 'brass')])
    for j, c in enumerate(hand):
        card(sc, 43 + j * (CW + 2), Y_HAND + (j % 2), c)
    SM.ink_rule(L, X0, X1, Y_RULE2, seed=9)
    # ── 아래 띠 — 왼쪽: 개인 행동 · 컨디션 ──
    studs = st['studs']
    y = Y_BAND
    if st['act']:
        hl = '개인 행동'
        sc.t(88, 2 * y, hl, M24, INK2)
        bx = 44 + (w(hl, M24) + 1) // 2 + 6
        items = ['전원 임의', '전원 훈련', '전원 휴식'] + (['전원 의뢰'] if st['job'] else [])
        for it in items:
            _, wa = btn(sc, bx, y, it); bx += wa + 3
        if st['undo']: btn(sc, bx + 3, y, f"변경 취소 ({st['undo']}명)")
        y += 17
        hurt = [s for s in studs if s['inj']]
        if hurt:
            injury_box(sc, X0, XL1, y, hurt); y += 25
        xx = sc.runs(88, 2 * y + 6, [('컨디션', INK2), (' · 낮은 순 · ', FADE), (f'{len(studs)}명', INK2)])
        sc.t(xx + 12, 2 * y + 6, '행동 칸을 누르면 임의 → 훈련 → 휴식' + (' → 의뢰' if st['job'] else ''), M12, FADE)
        if st['church']: btn(sc, XL1, y, '신비한 성수 (전원 +15) · 1,500 G', mini('water'), 'n', right=True)
        y += 16
        roster(sc, X0 + 2, y, studs, True, st['eff'])
    else:
        xx = sc.t(88, 2 * y, '컨디션', M24, INK2)
        sc.runs(88 + xx + 10, 2 * y + 10, [('낮은 순 · ', FADE), (f'{len(studs)}명', INK2)])
        y += 18
        roster(sc, X0 + 2, y, studs, False, st['eff'])
    # ── 아래 띠 — 오른쪽: 의뢰 쪽지 · 결재 ──
    approval(sc, XR0, Y_BAND, X1 - XR0 + 1, 72, st['ok'], st['label'], st['subs'])
    if st['job']: job_slip(sc, XR0 + 1, X1 - 1, Y_BAND + 82, st['job'])

# ───────────────────────── 종이 · 축 ─────────────────────────
# 처음 목업(schedule_mock)보다 종이를 양옆으로 EXT 칸씩 넓힌다 — 왼쪽 축이 오른쪽으로 드리운 그늘(6칸)이 글자 첫 칸(x 44)에 닿지 않게.
# 내용 자리(X0 · X1 …)는 그대로라 종이 가운데도 그대로다.
EXT = 6
PX0, PX1, PY0, PY1 = SM.PX0 - EXT, SM.PX1 + EXT, SM.PY0, SM.PY1
ROLL_R = 11.0

def rollers():
    """가까이 본 두 축 — schedule_mock.rollers_zoom 과 같은 모양 · 같은 빛, 종이 폭만 이 판 값.
    돌려주는 값: (그림, 세계 원점의 그림 속 자리, 두 축 가운데의 세계 x). 한 번 그린 것은 종이 범위별로 저장해 다시 쓴다 (한 장 30초 남짓)"""
    import os, json
    cache = HERE + f"cache/rollers_{PX0}_{PX1}_{PY0}_{PY1}.png"
    if os.path.exists(cache) and os.path.exists(cache + ".json"):
        m = json.load(open(cache + ".json"))
        return Image.open(cache).convert('RGBA'), tuple(m['org']), tuple(m['cxs'])
    from px3d import rotm, Part, sd_cyl, sd_sphere, local, render
    r = ROLL_R; M = rotm('x', 90)
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
    img, org = render(parts, b0, b1)
    os.makedirs(os.path.dirname(cache), exist_ok=True)
    img.save(cache); json.dump(dict(org=[int(org[0]), int(org[1])], cxs=list(cxs)), open(cache + ".json", "w"))
    return img, (int(org[0]), int(org[1])), cxs

def roller_place():
    """축 그림의 왼쪽 위 — 두루마리 1배 캔버스(DW×DH) 좌표. 위 · 아래로 캔버스를 넘친다 (금 마개가 잘리는 자리)"""
    rimg, (rx, ry), _ = ROLLERS
    cy = (PY0 + PY1) / 2
    return int(round(DW / 2 - rx)), int(round(cy - ry + ROLL_R * np.cos(TH)))

def roller_cols():
    """두 축 가운데 칸 (캔버스 x)"""
    rimg, (rx, ry), cxs = ROLLERS
    rX, _ = roller_place()
    return [int(np.floor(rX + rx + c)) for c in cxs]

def paper_center():
    return (PX0 + PX1 + 1) // 2, (PY0 + PY1 + 1) // 2

def build(key):
    st = STATES[key]
    base = SM.desk_zoom()
    base.alpha_composite(paper_base())
    sc = Sc(); L = sc.L
    content(sc, st)
    base.alpha_composite(L)
    # ── 2배로 키워 글자를 쓴다 ──
    B2 = base.resize((DW * 2, DH * 2), Image.NEAREST)
    draw_texts(B2, sc.T)
    # 깃펜 · 축 · 가장자리 그늘 (글자 위)
    q, (nx, ny) = S.quill(length=70, ang=-13)
    qx, qy = 478 - nx, 455 - ny
    B2.alpha_composite(q.resize((q.width * 2, q.height * 2), Image.NEAREST), (2 * qx, 2 * qy))
    rimg = ROLLERS[0]; rX, rY = roller_place()
    B2.alpha_composite(rimg.resize((rimg.width * 2, rimg.height * 2), Image.NEAREST), (2 * rX, 2 * rY))
    v = np.array(S.vignette()); v[..., 3] = (v[..., 3] * 0.45).astype(np.uint8)
    B2.alpha_composite(Image.fromarray(v).resize((DW * 2, DH * 2), Image.NEAREST))
    fr = S.town_frame(); fr2 = fr.resize((fr.width * 2, fr.height * 2), Image.NEAREST)
    out = Image.new('RGBA', fr2.size, (0, 0, 0, 255)); out.alpha_composite(B2, (26, 26)); out.alpha_composite(fr2)
    return out

def paper_base():
    """투명 바탕에 종이 그림자 · 종이 (책상 1배 좌표 그대로)"""
    base = new(DW, DH)
    pw, ph = PX1 - PX0 + 1, PY1 - PY0 + 1
    sh = new(DW, DH); rect(sh, PX0 + 4, PY0 + 5, PX1 + 4, PY1 + 5, (24, 12, 8), 80); base.alpha_composite(sh)
    base.alpha_composite(SM.paper_zoom(pw, ph), (PX0, PY0))
    return base

MX = 24                              # 배치판 그림 캔버스 양옆 여유 (넓힌 축 · 축 그림자가 잘리지 않게)
def scroll_sprite(key):
    """배치판용 두루마리 — 그림자 · 종이 · 내용 · 축(구운 그림자)을 투명 바탕에 2배로.
    위 · 아래는 처음처럼 캔버스(DH)에서 자른다 — 잘려 나간 금 마개는 end_pieces() 가 따로 만든다.
    돌려주는 값: (2배 그림, 기준점 1배) — 기준점 = 종이 가운데"""
    global ROLLERS
    if ROLLERS is None: ROLLERS = rollers()
    st = STATES[key]
    base = paper_base()
    sc = Sc(); content(sc, st); base.alpha_composite(sc.L)
    B2 = base.resize((DW * 2, DH * 2), Image.NEAREST)
    draw_texts(B2, sc.T)
    W2 = Image.new('RGBA', ((DW + MX * 2) * 2, DH * 2), (0, 0, 0, 0)); W2.alpha_composite(B2, (MX * 2, 0))
    rimg = ROLLERS[0]; rX, rY = roller_place()
    W2.alpha_composite(rimg.resize((rimg.width * 2, rimg.height * 2), Image.NEAREST), (2 * (rX + MX), 2 * rY))
    x0, y0, x1, y1 = W2.getbbox()
    x0, y0 = x0 // 2 * 2, y0 // 2 * 2; x1, y1 = (x1 + 1) // 2 * 2, (y1 + 1) // 2 * 2
    pcx, pcy = paper_center()
    return W2.crop((x0, y0, x1, y1)), (pcx + MX - x0 // 2, pcy - y0 // 2)

def end_pieces():
    """축 끝 — 두루마리 그림 밖(캔버스 위 · 아래)으로 잘려 나간 금 마개 · 꼭지 · 그 그림자 (1배).
    축 그림 하나를 잘라 나눈 것이라 붙이면 이음매 없이 처음 그림이 된다.
    돌려주는 값: pieces = {'bottom': [(그림, 기준점) 왼쪽 축, 오른쪽 축], 'top': [...]},
                 ends = {'bottom': [(dx, dy) 왼쪽, 오른쪽], 'top': [...]} — 종이 가운데(두루마리 기준점)에서 붙일 자리까지.
    기준점 = 잘린 줄 바로 바깥 한 줄(아래는 캔버스 y = DH, 위는 y = -1)의 축 가운데 칸"""
    global ROLLERS
    if ROLLERS is None: ROLLERS = rollers()
    A = np.array(ROLLERS[0]); H, W = A.shape[:2]
    rX, rY = roller_place(); cols = roller_cols(); pcx, pcy = paper_center()
    split = (cols[0] + cols[1]) // 2 - rX                                   # 두 축을 가르는 세로줄 (축 그림 x)
    pieces, ends = {}, {}
    for side, (r0, r1), prow in (('bottom', (DH - rY, H), DH), ('top', (0, -rY), -1)):
        pieces[side], ends[side] = [], []
        for i, col in enumerate(cols):
            c0, c1 = (0, split) if i == 0 else (split, W)
            sub = A[r0:r1, c0:c1]
            ys, xs = np.nonzero(sub[..., 3])
            by0, by1, bx0, bx1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
            img = Image.fromarray(sub[by0:by1, bx0:bx1].copy())
            ox, oy = rX + c0 + bx0, rY + r0 + by0                             # 조각 왼쪽 위 (캔버스)
            pieces[side].append((img, (col - ox, prow - oy)))
            ends[side].append((col - pcx, prow - pcy))
    return pieces, ends

ROLLERS = None
if __name__ == "__main__":
    import os
    OUTD = HERE + "sched2/"; os.makedirs(OUTD, exist_ok=True)
    ROLLERS = rollers()
    keys = sys.argv[1:] or ['early', 'mid', 'late']
    for k in keys:
        out = build(k)
        out.convert('RGB').save(OUTD + f"sched_{k}_2x.png")
        print(k, out.size)
