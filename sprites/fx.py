# -*- coding: utf-8 -*-
"""전투 이펙트 시트 생성기 — 128x128 셀 · 가로 8프레임 · 1행.

형태만 찍고 색은 게임에서 입힌다. 그래서 기준 색상(hue)을 하나로 고정하고
명암·채도 단계만 쓴다 — 머리색 치환과 같은 방식으로 원소별 색이 나온다.
"""
import os, colorsys
from collections import Counter
from PIL import Image, ImageDraw

N     = 128          # 셀 크기
FR    = 8            # 프레임 수
SS    = 4            # 슈퍼샘플 배율
W     = N * SS
BASE_H = 0.55        # 기준 색상 — 런타임에서 이 값을 돌려 원소를 만든다
OUT   = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")

# 명암 5단 — t=1 이 흰 심, t=0 이 바깥 테두리
TONES = [(1.00, 0.06, 1.00), (0.75, 0.30, 1.00), (0.50, 0.58, 0.96),
         (0.25, 0.86, 0.78), (0.00, 1.00, 0.52)]
def tone(t, a=255):
    """t 0~1 → RGBA. 5단으로 끊어 도트 느낌을 살린다."""
    best = min(TONES, key=lambda x: abs(x[0] - t))
    r, g, b = colorsys.hsv_to_rgb(BASE_H, best[1], best[2])
    return (int(r * 255), int(g * 255), int(b * 255), a)

def canvas():
    im = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    return im, ImageDraw.Draw(im)

def down(im):
    """4x4 블록 최빈색으로 줄인다 — 가장자리가 흐려지지 않는다."""
    src = im.load()
    out = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    dst = out.load()
    for y in range(N):
        for x in range(N):
            c = Counter()
            for dy in range(SS):
                for dx in range(SS):
                    p = src[x * SS + dx, y * SS + dy]
                    c[p if p[3] > 110 else (0, 0, 0, 0)] += 1
            dst[x, y] = c.most_common(1)[0][0]
    return out

def dot(d, x, y, r, c):
    d.ellipse([ (x - r) * SS, (y - r) * SS, (x + r) * SS, (y + r) * SS ], fill=c)

def ring(d, x, y, r, w, c, a0=0, a1=360):
    d.arc([ (x - r) * SS, (y - r) * SS, (x + r) * SS, (y + r) * SS ],
          a0, a1, fill=c, width=max(1, int(w * SS)))

def line(d, x0, y0, x1, y1, w, c):
    d.line([x0 * SS, y0 * SS, x1 * SS, y1 * SS], fill=c, width=max(1, int(w * SS)))

def poly(d, pts, c):
    d.polygon([(x * SS, y * SS) for x, y in pts], fill=c)

import math, random
C = 64

def band(d, ax, ay, bx, by, bow, wmax, c, t0=0.0, t1=1.0, steps=140):
    """A→B 를 잇되 수직으로 bow 만큼 휜 띠. 양끝이 가늘어진다."""
    dx, dy = bx - ax, by - ay
    L = math.hypot(dx, dy) or 1
    nx, ny = -dy / L, dx / L
    for i in range(steps + 1):
        t = t0 + (t1 - t0) * i / steps
        s = math.sin(math.pi * t)
        px = ax + dx * t + nx * bow * s
        py = ay + dy * t + ny * bow * s
        w = wmax * (s ** 0.55)
        if w < .6: continue
        dot(d, px, py, w / 2, c)

def rough_ring(d, cx, cy, r, w, c, seed=0, gap=None, jit=2.2):
    """도트로 찍는 거친 고리 — 매끈한 원보다 타격감이 산다."""
    rnd = random.Random(seed)
    step = max(6, int(260 / max(r, 6)))
    for a in range(0, 360, step):
        if gap and gap[0] <= a <= gap[1]: continue
        rr = r + rnd.uniform(-jit, jit)
        ax, ay = math.cos(math.radians(a)), -math.sin(math.radians(a))
        dot(d, cx + ax * rr, cy + ay * rr, w / 2, c)

def spark(d, x, y, r, c):
    poly(d, [(x, y - r), (x + r * .3, y - r * .3), (x + r, y), (x + r * .3, y + r * .3),
             (x, y + r), (x - r * .3, y + r * .3), (x - r, y), (x - r * .3, y - r * .3)], c)

# ── 참격 — 몸통을 가로지르는 초승달 ──────────────────────
SL_A, SL_B, SL_BOW = (112, 28), (26, 108), 15
def fx_slash(f):
    im, d = canvas()
    if f >= 7: return im
    ax, ay = SL_A; bx, by = SL_B
    if f <= 4:
        t1 = [.30, .58, .84, 1.0, 1.0][f]
        t0 = [0, 0, 0, 0, .22][f]
        wm = [11, 16, 20, 22, 15][f]
        band(d, ax, ay, bx, by, SL_BOW, wm + 9, tone(.12), t0, t1)
        band(d, ax, ay, bx, by, SL_BOW, wm,     tone(.45), t0, t1)
        band(d, ax, ay, bx, by, SL_BOW, wm * .5, tone(.85), t0, t1)
        if f >= 2:
            band(d, ax, ay, bx, by, SL_BOW, wm * .22, tone(1.0), t0 + .06, t1 - .06)
    else:
        k = f - 5
        for t0, t1 in [(.06, .28), (.40, .60), (.72, .92)][:3 - k]:
            wm = 12 - k * 5
            band(d, ax, ay, bx, by, SL_BOW, wm, tone(.5 - k * .15), t0, t1)
            band(d, ax, ay, bx, by, SL_BOW, wm * .4, tone(.95), t0 + .03, t1 - .03)
    if 2 <= f <= 4:
        for k, (sx, sy) in enumerate([(-30, 34), (-6, 52), (30, -26), (14, 8)]):
            spark(d, C + sx, C + sy, 7 - (f - 2) * 2, tone(.95))
    return im

# ── 관통 — 꽂히고 터진다 ────────────────────────────────
PX, PY = 54, 62
def fx_pierce(f):
    im, d = canvas()
    if f >= 7: return im
    if f <= 2:
        head = [110, 84, 62][f]
        tail = min(136, head + [30, 62, 90][f])
        poly(d, [(head, PY), (tail, PY - 13), (tail, PY + 13)], tone(.2))
        poly(d, [(head, PY), (tail, PY - 7),  (tail, PY + 7)],  tone(.55))
        poly(d, [(head, PY), (tail, PY - 2),  (tail, PY + 2)],  tone(1.0))
    if f >= 2:
        k = f - 2                                   # 0~4
        r0 = [9, 17, 24, 29, 32][k]
        w  = [14, 11, 7, 4, 2.5][k]
        tv = [1.0, .8, .55, .35, .2][k]
        rays = (18, 74, 130, 195, 250, 310)
        for j, a in enumerate(rays):
            if k >= 3 and j % 2: continue          # 늦은 프레임은 살을 절반만
            ax, ay = math.cos(math.radians(a)), -math.sin(math.radians(a))
            band(d, PX + ax * (r0 * .25), PY + ay * (r0 * .25),
                 PX + ax * r0 * 1.15, PY + ay * r0 * 1.15, 0, w, tone(tv))
        if k <= 2:
            dot(d, PX, PY, 15 - k * 4, tone(.5))
            dot(d, PX, PY, 9 - k * 3,  tone(1.0))
    return im

# ── 타격 — 거친 충격파 ──────────────────────────────────
def fx_blunt(f):
    im, d = canvas()
    if f >= 7: return im
    r  = [9, 19, 29, 39, 47, 54, 58][f]
    w  = [16, 15, 13, 10, 7, 5, 4][f]
    tv = [1.0, .95, .8, .62, .48, .34, .22][f]
    if f <= 4:
        rough_ring(d, C, C, r + 2, w + 6, tone(max(0, tv - .35)), seed=1)
        rough_ring(d, C, C, r, w, tone(tv), seed=2)
        rough_ring(d, C, C, r, w * .42, tone(min(1, tv + .3)), seed=3, jit=1.2)
    else:
        for a0, a1 in ((14, 96), (150, 214), (262, 322)):
            for a in range(a0, a1, 11):
                ax, ay = math.cos(math.radians(a)), -math.sin(math.radians(a))
                dot(d, C + ax * r, C + ay * r, w / 2, tone(tv))
    if f <= 2:
        dot(d, C, C, 15 - f * 5, tone(.55))
        dot(d, C, C, 10 - f * 3, tone(1.0))
    if 1 <= f <= 3:
        r2 = r - 15
        if r2 > 5: rough_ring(d, C, C, r2, 7, tone(.95), seed=5)
    if 2 <= f <= 5:
        for a in range(10, 360, 51):
            ax, ay = math.cos(math.radians(a)), -math.sin(math.radians(a))
            spark(d, C + ax * (r + 9), C + ay * (r + 9), max(2, 8 - (f - 2) * 2), tone(.9))
    return im

# ── 폭발 ───────────────────────────────────────────────
def _chunks(seed, n, r0, r1):
    rnd = random.Random(seed)
    return [(rnd.uniform(0, 360), rnd.uniform(r0, r1), rnd.uniform(.65, 1.45)) for _ in range(n)]

def fx_burst(f):
    im, d = canvas()
    if f >= 7: return im
    if f == 0:
        dot(d, C, C, 10, tone(.45)); dot(d, C, C, 6, tone(1.0))
    elif f == 1:
        dot(d, C, C, 18, tone(.3)); dot(d, C, C, 12, tone(.7)); dot(d, C, C, 7, tone(1.0))
    elif f == 2:
        dot(d, C, C, 33, tone(.4)); dot(d, C, C, 24, tone(.78)); dot(d, C, C, 14, tone(1.0))
        for a in range(0, 360, 30):
            ax, ay = math.cos(math.radians(a)), -math.sin(math.radians(a))
            band(d, C + ax * 24, C + ay * 24, C + ax * 52, C + ay * 52, 0, 8, tone(.65))
    else:
        k = f - 3
        R  = [40, 49, 56, 60][k]
        tv = [.6, .45, .32, .2][k]
        for a, rr, sc in _chunks(11, 13 - k * 2, R * .5, R):
            ax, ay = math.cos(math.radians(a)), -math.sin(math.radians(a))
            rad = max(2, (13 - k * 2.5) * sc)
            dot(d, C + ax * rr, C + ay * rr, rad, tone(tv))
            if k <= 1: dot(d, C + ax * rr, C + ay * rr, rad * .48, tone(min(1, tv + .38)))
        if k == 0:
            dot(d, C, C, 22, tone(.8)); dot(d, C, C, 12, tone(1.0))
    return im

# ── 오라 — 발밑에서 올라오는 고리 ────────────────────────
def fx_aura(f):
    im, d = canvas()
    if f >= 7: return im
    y  = [104, 94, 82, 68, 54, 40, 28][f]
    rx = [28, 33, 37, 38, 35, 30, 24][f]
    ry = [8, 9, 10, 10, 9, 8, 6][f]
    tv = [.5, .75, 1.0, .95, .75, .55, .38][f]
    # 타원 고리를 도트로 — 두툼하게
    for a in range(0, 360, 3):
        ax, ay = math.cos(math.radians(a)), math.sin(math.radians(a))
        dot(d, C + ax * rx, y + ay * ry, 3.4, tone(max(0, tv - .35)))
    for a in range(0, 360, 3):
        ax, ay = math.cos(math.radians(a)), math.sin(math.radians(a))
        dot(d, C + ax * rx, y + ay * ry, 1.6, tone(min(1, tv + .2)))
    for i, (dx, off) in enumerate([(-34, 4), (-15, 18), (9, 10), (30, 0), (-24, 28), (22, 26), (0, 36)]):
        py = y - off - f * 4
        if py < 4 or f < 1: continue
        r = max(1.5, 4.6 - f * .35 - (i % 3) * .4)
        dot(d, C + dx, py, r + 1.2, tone(max(0, tv - .45)))
        dot(d, C + dx, py, r, tone(.95 if i % 2 else .65))
    return im

# ── 회복 — 떠오르는 빛과 십자 ───────────────────────────
def fx_heal(f):
    im, d = canvas()
    if f >= 7: return im
    ps  = [0, 11, 19, 24, 20, 13, 7][f]
    tv  = [0, .55, .85, 1.0, .8, .55, .35][f]
    arm = [0, 3, 4, 5, 4, 3, 2][f]
    if ps > 3:
        d.rectangle([(C - arm - 2) * SS, (C - ps - 2) * SS, (C + arm + 2) * SS, (C + ps + 2) * SS],
                    fill=tone(max(0, tv - .45)))
        d.rectangle([(C - ps - 2) * SS, (C - arm - 2) * SS, (C + ps + 2) * SS, (C + arm + 2) * SS],
                    fill=tone(max(0, tv - .45)))
        d.rectangle([(C - arm) * SS, (C - ps) * SS, (C + arm) * SS, (C + ps) * SS], fill=tone(tv))
        d.rectangle([(C - ps) * SS, (C - arm) * SS, (C + ps) * SS, (C + arm) * SS], fill=tone(tv))
        if 2 <= f <= 4:
            h = max(1, arm - 3)
            d.rectangle([(C - h) * SS, (C - ps + 5) * SS, (C + h) * SS, (C + ps - 5) * SS], fill=tone(1.0))
            d.rectangle([(C - ps + 5) * SS, (C - h) * SS, (C + ps - 5) * SS, (C + h) * SS], fill=tone(1.0))
    MOTE = [(-36, 0), (-20, 12), (-7, -8), (12, 4), (28, -12), (37, 14), (-29, 22), (5, 20), (20, 32)]
    for i, (dx, off) in enumerate(MOTE):
        py = 110 - off - f * 13 - i * 2
        if py < 4 or py > 124: continue
        r = max(1.5, 5.0 - abs(f - 3) * .5 - (i % 3) * .6)
        dot(d, C + dx, py, r + 1.2, tone(.2))
        dot(d, C + dx, py, r, tone(.95 if i % 2 else .6))
    return im

FX = [("slash", fx_slash), ("pierce", fx_pierce), ("blunt", fx_blunt),
      ("burst", fx_burst), ("aura", fx_aura), ("heal", fx_heal)]

def build():
    os.makedirs(OUT, exist_ok=True)
    for name, fn in FX:
        sheet = Image.new("RGBA", (N * FR, N), (0, 0, 0, 0))
        for f in range(FR):
            sheet.alpha_composite(down(fn(f)), (f * N, 0))
        sheet.save(os.path.join(OUT, f"fx_{name}.png"))
        print(f"fx_{name}.png  {N*FR}x{N}  {FR}프레임")

if __name__ == "__main__":
    build()
