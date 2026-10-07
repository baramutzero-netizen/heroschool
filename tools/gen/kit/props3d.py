"""책상 소품 — 하나하나 따로 그린 1배 도트(그림자 포함 RGBA). 3D 로 만들 수 있는 것은 px3d 로, 납작한 것은 2D 로.
각 함수는 (그림, 바닥점) 을 돌려준다 — 바닥점 = 물체가 책상에 닿는 가운데(그림 안 픽셀 좌표). 배치 도구는 그림 왼쪽 위로 놓는다."""
import numpy as np, random
from PIL import Image, ImageDraw
from px3d import *

# ── 재질 (어두움 → 밝음, 색상을 조금씩 틀어 그늘은 붉게 · 밝은 쪽은 노랗게) ──
mat('brass',  ['4a2c10', '74481a', 'a26e2a', 'cf9c44', 'eec66c'], spec=(40, .55, 'fff1c4'))
mat('gold',   ['5e3c0e', '8c5e18', 'c08c2c', 'e6b84a', 'f8dc7a'], spec=(40, .55, 'fffbe0'))
mat('goldd',  ['4a2e0a', '6e4812', '9a6e22', 'c09032', 'd8aa48'])
mat('wax',    ['a88f68', 'c8b48c', 'e2d4b2', 'f2e8d0', 'fcf7ea'])
mat('flame',  ['e0602a', 'ff9a3c', 'ffcf62', 'fff0b8', 'ffffff'], emit=True)
mat('glasslit', ['e89838', 'ffc254', 'ffdc84', 'fff0c0', 'ffffff'], emit=True)
mat('wood',   ['2e1a10', '4a2a18', '6a3e22', '8a5630', 'a8703e'])
mat('porc',   ['8a8690', 'b2adb0', 'd6d0ca', 'eee8de', 'fbf8f2'], spec=(18, .5, 'ffffff'))
mat('porcblue', ['24365a', '34507e', '4a6c9c', '6a8cba', '92b0d4'], spec=(18, .5, 'e8f0fa'))
mat('tea',    ['3a180a', '5a2a12', '7a3e1a', '9a5626', 'b87034'], spec=(30, .5, 'e8b070'))
mat('inkglass', ['0a1020', '142038', '203256', '304a78', '4e6c9c'], spec=(18, .45, 'c8daf0'))
mat('ink',    ['040508', '080a10', '0c1018', '121822', '1a2230'], spec=(40, .6, '8090b0'))
mat('ocean',  ['1a4256', '245e78', '327c98', '4c9cb4', '78bccc'], spec=(22, .5, 'd8f0f4'))
mat('land',   ['30501e', '426a2a', '5a8638', '76a44a', '98c062'])
mat('leather', ['36101a', '561a28', '782636', '983a46', 'b45656'])
mat('velvet2', ['2a0c14', '44141f', '5e1e2a', '7a2a38', '943e4a'])
mat('cord',   ['7a5a32', '9a7a46', 'bc9c62', 'd8bc82', 'ecd6a4'])
mat('paper',  ['a08862', 'c4ac84', 'dec8a0', 'efdfba', 'faf0d8'])
mat('paperln', ['8a7250', 'a8906a', 'c4ac84', 'd6c09a', 'e6d4b0'])
mat('redcov', ['2e0c0c', '4e1616', '722624', '963a34', 'b45446'])
mat('navycov', ['0e1228', '182040', '26325a', '364876', '4c6294'])
mat('browncov', ['26160c', '402614', '5c3820', '784c2c', '94623a'])
mat('greencov', ['0e221a', '183626', '244c36', '346448', '4a805c'])
mat('gem_g',  ['0c3a2a', '146048', '208a66', '40b48a', '90e0c0'], spec=(40, .7, 'ffffff'))
mat('gem_r',  ['3a0a0a', '6a1414', '9c2420', 'cc4034', 'f08a78'], spec=(40, .7, 'ffffff'))
mat('petal',  ['b2aa9c', 'd4cec0', 'eae6dc', 'f6f4ee', 'ffffff'])
mat('fcenter', ['9a6410', 'c4861c', 'e2a82c', 'f2c648', 'fbe07a'])
mat('leaf',   ['1a3418', '2a4c22', '3c682e', '54863c', '72a44e'])
mat('sand',   ['94703c', 'b28a4e', 'cca464', 'e0bc7c', 'eed096'])
mat('redwax', ['3a0a0a', '5c1210', '801c18', 'a42a22', 'c03c30'], spec=(40, .6, 'f09080'))
mat('redwax_d', ['2a0606', '420c0a', '5c1210', '701816', '801c18'])
mat('parch',  ['8a6c44', 'b09062', 'd0b280', 'e4cea0', 'f2e4c2'])
mat('ribbon', ['440c0c', '6a1816', '922824', 'b43a30', 'd05646'], spec=(12, .55, 'f0a090'))
mat('dial',   ['d8d0c0', 'e6dfd0', 'f0eadc', 'f8f3e8', 'fdfaf2'], flat=True)
mat('dialink', ['2a2420', '2a2420', '2a2420', '2a2420', '2a2420'], flat=True)
mat('steel',  ['3a3e48', '5a606c', '828a96', 'aab2bc', 'd2d8de'], spec=(20, .5, 'ffffff'))
mat('glass',  ['5e7c88', '7c9aa4', 'a2bcc4', 'c8dce0', 'eef6f8'], alpha=70, spec=(20, .35, 'ffffff'))
mat('glasswarm', ['c8843a', 'e2a250', 'f0be6c', 'f8d898', 'fff0cc'], alpha=90, spec=(60, .75, 'ffffff'))
mat('leather2', ['2e160e', '4a2416', '683620', '864c2c', 'a4663c'])
mat('lens', ['8aa8b4', 'a6c2cc', 'c4dce2', 'dcecf0', 'f2fafc'], alpha=60, spec=(30, .6, 'ffffff'))

SCALE = 1.4                     # 소품 전체 크기 (모델 단위 → 1배 픽셀)
YAW = 0.0                       # 책상 위에서 돌린 각(도, 위에서 보아 반시계 +) — 프레임 뽑을 때 쓴다
YAW_MODE = False                # 켜면 모든 각도에서 같은 틀(원기둥 경계)로 그린다 → 바닥점이 프레임마다 같은 자리
def yaw_parts(parts, deg):
    if deg % 360 == 0: return parts
    M = rotm('z', deg)
    out = []
    for p in parts:
        f = (lambda g: (lambda P: g(P @ M)))(p.sdf)
        m = (lambda g: (lambda P, N: g(P @ M, N @ M)))(p.m) if callable(p.m) else p.m
        out.append(Part(f, m, p.name))
    return out
def _bounds(bmin, bmax):
    bmin = np.array(bmin, float); bmax = np.array(bmax, float)
    if not YAW_MODE: return bmin, bmax
    R = max(np.hypot(x, y) for x in (bmin[0], bmax[0]) for y in (bmin[1], bmax[1]))
    return np.array([-R, -R, bmin[2]]), np.array([R, R, bmax[2]])
def sprite(parts, bmin, bmax, **kw):
    s = SCALE; bmin, bmax = _bounds(bmin, bmax)
    img, (ox, oy) = render(scale_parts(yaw_parts(parts, YAW), s), bmin * s, bmax * s, **kw)
    return img, (ox, oy)
def glass_sprite(inner, glass, bmin, bmax, **kw):
    s = SCALE; bmin, bmax = _bounds(bmin, bmax)
    return render_glass(scale_parts(yaw_parts(inner, YAW), s), scale_parts(yaw_parts(glass, YAW), s), bmin * s, bmax * s, **kw)

def overlay(base, top):
    out = base.copy(); out.alpha_composite(top); return out

# ───────────────────────── 등잔 ─────────────────────────
def lamp():
    foot = [(0, 0), (12.5, 0), (13.6, 1.0), (13.4, 2.4), (11.4, 3.2), (8, 3.6), (0, 3.6)]
    font = [(0, 3.2), (8.4, 3.6), (10.4, 6.0), (10.2, 9.0), (7.6, 11.2), (0, 11.4)]
    collar = [(0, 11), (5.8, 11), (6.2, 12.2), (5.8, 13.6), (0, 13.6)]
    chim = [(0, 13.4), (5.4, 13.4), (8.2, 17.5), (8.8, 21.5), (7.2, 26), (4.8, 30), (5.2, 31.4), (0, 31.4)]
    inner = [
        Part(lambda P: sd_lathe(P, [0, 0, 0], foot), 'brass'),
        Part(lambda P: sd_lathe(P, [0, 0, 0], font), 'brass'),
        Part(lambda P: sd_lathe(P, [0, 0, 0], collar), 'brass'),
        Part(lambda P: sd_cyl(P, [0, 0, 14.4], 2.2, 1.0, 0.3), 'brass'),
        Part(lambda P: sd_ellipsoid(P, [0, 0, 20.4], [3.0, 3.0, 5.8]), 'flame'),
        Part(lambda P: sd_torus(local(P, [12.4, -2.4, 6.0], rotm('x', 90)), [0, 0, 0], 3.6, 1.1), 'brass'),
    ]
    glass = [Part(lambda P: sd_lathe(P, [0, 0, 0], chim), 'glasswarm')]
    return glass_sprite(inner, glass, np.array([-17, -15, 0.0]), np.array([18, 15, 32.0]), glass_alpha=0.42, over_ground=150)

# ───────────────────────── 촛대 ─────────────────────────
def candle():
    dish = [(0, 0), (12, 0), (13.6, 1.2), (13.6, 2.8), (12, 3.3), (6, 2.3), (0, 2.3)]
    cup = [(0, 2), (5.6, 2), (5.8, 5.2), (5.0, 5.6), (0, 5.6)]
    P_ = [
        Part(lambda P: sd_lathe(P, [0, 0, 0], dish), 'brass'),
        Part(lambda P: sd_lathe(P, [0, 0, 0], cup), 'brass'),
        Part(lambda P: sd_cyl(P, [0, 0, 5 + 6.5], 4.2, 6.5, 0.9), 'wax'),
        Part(lambda P: sd_capsule(P, [3.6, -2.4, 15], [4.4, -3.0, 9.5], 0.9), 'wax'),
        Part(lambda P: sd_ellipsoid(P, [0, 0, 22.4], [2.3, 2.3, 4.6]), 'flame'),
        Part(lambda P: sd_torus(local(P, [14.8, -2.5, 2.2], rotm('x', 90)), [0, 0, 0], 3.3, 1.0), 'brass'),
    ]
    return sprite(P_, [-16, -15, 0], [20, 15, 27])

# ───────────────────────── 모래시계 ─────────────────────────
def hourglass():
    """옆으로 누운 모래시계 — 두 유리 방울 · 나무 마개 · 기둥 셋. 모래는 아래로 고였다"""
    M = rotm('z', 14) @ rotm('y', 90)
    T = np.array([-15.1 * np.cos(np.radians(14)), -15.1 * np.sin(np.radians(14)), 9.6])
    bulb = [(0, 2.6), (5.6, 3.4), (6.6, 6.5), (5.4, 10.6), (2.2, 13.6), (1.1, 15), (2.2, 16.4), (5.4, 19.4), (6.6, 23.5), (5.6, 26.6), (0, 27.4)]
    bulb_in = [(0, 3.2), (5.0, 3.9), (5.9, 6.6), (4.8, 10.4), (1.8, 13.4), (0.7, 15), (1.8, 16.6), (4.8, 19.6), (5.9, 23.4), (5.0, 26.1), (0, 26.8)]
    posts = [(7.6 * np.cos(a), 7.6 * np.sin(a)) for a in np.radians([30, 150, 270])]
    def L_(P): return local(P, T, M)
    def sand(P):
        q = L_(P)
        a = sd_lathe(q, [0, 0, 0], bulb_in)
        right = np.maximum(a, np.maximum(P[:, 2] - 7.4, 15.6 - q[:, 2]))
        left = np.maximum(a, np.maximum(P[:, 2] - 4.6, q[:, 2] - 14.4))
        return np.minimum(right, left)
    inner = [
        Part(lambda P: sd_cyl(L_(P), [0, 0, 1.4], 9.4, 1.4, 0.6), 'wood'),
        Part(lambda P: sd_cyl(L_(P), [0, 0, 28.8], 9.4, 1.4, 0.6), 'wood'),
        Part(sand, 'sand'),
    ] + [Part((lambda x, y: (lambda P: sd_capsule(L_(P), [x, y, 2.6], [x, y, 27.6], 1.15)))(x, y), 'wood') for x, y in posts]
    glass = [Part(lambda P: sd_lathe(L_(P), [0, 0, 0], bulb), 'glass')]
    return glass_sprite(inner, glass, np.array([-19, -13, 0.0]), np.array([19, 13, 19.5]), glass_alpha=0.45, over_ground=95)

# ───────────────────────── 지구의 ─────────────────────────
def _globe_mat(P, N):
    q = local(P, [0, 0, 27], rotm('y', -18))
    q = q / (np.linalg.norm(q, axis=1, keepdims=True) + 1e-9)
    lat = np.arcsin(np.clip(q[:, 2], -1, 1)); lon = np.arctan2(q[:, 1], q[:, 0])
    f = (np.sin(lon * 2.0 + 0.6) * np.cos(lat * 2.4) + 0.55 * np.sin(lon * 3.6 - lat * 4.2 + 1.3) + 0.35 * np.cos(lon * 6.1 + lat * 5.0))
    land = f > 0.42
    return np.where(land, mid('land'), mid('ocean'))
def globe():
    foot = [(0, 0), (8.6, 0), (9.6, 1.0), (9.2, 2.6), (6.4, 3.2), (2.6, 4.4), (1.8, 6), (1.8, 11), (0, 11)]
    tilt = rotm('y', -20)
    def meridian(P):
        q = local(P, [0, 0, 27], tilt @ rotm('x', 90))
        ring = sd_torus(q, [0, 0, 0], 15.2, 0.95)
        return np.maximum(ring, q[:, 0] - 4.0)                   # 왼쪽 반만 (C 자) — 받침에서 꼭대기까지
    P_ = [
        Part(lambda P: sd_lathe(P, [0, 0, 0], foot), 'wood'),
        Part(lambda P: sd_torus(P, [0, 0, 1.2], 8.9, 0.7), 'gold'),
        Part(lambda P: sd_sphere(P, [0, 0, 27], 13.2), _globe_mat),
        Part(meridian, 'gold'),
        Part(lambda P: sd_capsule(P, [0, 0, 10], [0, 0, 13.6], 1.3), 'gold'),
        Part(lambda P: sd_sphere(local(P, [0, 0, 27], tilt), [0, 0, 15.6], 1.2), 'gold'),
    ]
    return sprite(P_, [-18, -18, 0], [18, 18, 44])

# ───────────────────────── 찻잔 ─────────────────────────
def teacup():
    saucer = [(0, 0), (9, 0), (15.5, 1.4), (17.5, 3.0), (17, 3.6), (14, 2.8), (9, 2.0), (0, 2.0)]
    cup_o = [(0, 1.8), (6.4, 1.8), (7.4, 2.6), (9.8, 6), (10.8, 9.6), (10.9, 10.6), (0, 10.6)]
    cup_i = [(0, 3.4), (6.2, 3.4), (9.0, 7), (9.8, 11.2), (0, 11.2)]
    tea = [(0, 7.6), (9.2, 7.6), (9.25, 8.0), (0, 8.0)]
    def cup(P): return np.maximum(sd_lathe(P, [0, 0, 0], cup_o), -sd_lathe(P, [0, 0, 0], cup_i))
    P_ = [
        Part(lambda P: sd_lathe(P, [0, 0, 0], saucer), 'porc'),
        Part(cup, lambda P, N: np.where((P[:, 2] > 8.4) & (P[:, 2] < 9.4) & (np.hypot(P[:, 0], P[:, 1]) > 10.0), mid('gold'), mid('porc'))),
        Part(lambda P: sd_lathe(P, [0, 0, 0], tea), 'tea'),
        Part(lambda P: sd_torus(local(P, [12.6, -1.5, 7.0], rotm('x', 90) @ rotm('z', 0)), [0, 0, 0], 3.0, 1.05), 'porc'),
    ]
    return sprite(P_, [-19, -19, 0], [19, 19, 12])

# ───────────────────────── 잉크병 ─────────────────────────
def inkwell():
    P_ = [
        Part(lambda P: sd_rbox(P, [0, 0, 6.5], [11, 11, 6.5], 2.4), 'inkglass'),
        Part(lambda P: np.maximum(sd_cyl(P, [0, 0, 14.2], 6.4, 1.6, 0.6), -sd_cyl(P, [0, 0, 16.0], 4.4, 1.6, 0.2)), 'brass'),
        Part(lambda P: sd_cyl(P, [0, 0, 14.0], 4.6, 0.5, 0.1), 'ink'),
    ]
    return sprite(P_, [-13, -13, 0], [13, 13, 16.2])

# ───────────────────────── 책 ─────────────────────────
def _book_mat(cov, c, ang, w, d, hh, gem):
    M = rotm('z', ang)
    def f(P, N):
        q = local(P, c, M); nl = N @ M
        out = np.full(len(P), mid(cov))
        top = nl[:, 2] > 0.7
        bx, by = w - 4.0, d - 4.0
        border = top & (((np.abs(np.abs(q[:, 0]) - bx) < 0.8) & (np.abs(q[:, 1]) < by + 0.8)) | ((np.abs(np.abs(q[:, 1]) - by) < 0.8) & (np.abs(q[:, 0]) < bx + 0.8)))
        out[border] = mid('gold')
        if gem:
            g = top & (np.hypot(q[:, 0] + 1.0, q[:, 1]) < 4.2)
            out[g] = mid('gold')
            out[top & (np.hypot(q[:, 0] + 1.0, q[:, 1]) < 2.7)] = mid(gem)
        side = ~top & (np.abs(q[:, 2]) < hh - 0.9)
        spine = side & (q[:, 0] < -w + 1.6)
        pages = side & ~spine
        out[pages] = np.where((np.floor((q[pages, 2] + hh) * 1.6) % 2) == 0, mid('paper'), mid('paperln'))
        return out
    return f
def book_parts(c, w, d, hh, ang, cov, gem=None):
    """(c: 가운데) 반폭 w · 반깊이 d · 반두께 hh · z축 회전 ang. 왼쪽(−x)이 책등"""
    M = rotm('z', ang)
    cov_box = Part(lambda P: sd_rbox(local(P, c, M), [0, 0, 0], [w, d, hh], 0.9), _book_mat(cov, c, ang, w, d, hh, gem))
    return [cov_box]
def book_stack():
    P_ = []
    P_ += book_parts([0, 0, 3.6], 30, 21, 3.6, 4, 'navycov')
    P_ += book_parts([-1, 1, 10.6], 28, 20, 3.4, -5, 'browncov')
    P_ += book_parts([1, 0, 17.2], 26, 18.5, 3.2, 2, 'redcov', gem='gem_g')
    return sprite(P_, [-34, -26, 0], [34, 26, 20.5])
def book_pair():
    P_ = []
    P_ += book_parts([0, 0, 3.4], 28, 19, 3.4, -3, 'greencov')
    P_ += book_parts([2, 1, 10.0], 25, 17.5, 3.2, 5, 'navycov', gem='gem_r')
    return sprite(P_, [-32, -24, 0], [32, 24, 13.4])

# ───────────────────────── 동전 · 주머니 ─────────────────────────
def _coin_face(c):
    def f(P, N):
        q = P - c; r = np.hypot(q[:, 0], q[:, 1])
        out = np.full(len(P), mid('gold'))
        top = N[:, 2] > 0.8
        out[top & (np.abs(r - 2.7) < 0.42)] = mid('goldd')
        out[top & (r < 0.9)] = mid('goldd')
        return out
    return f
def coin(tilt=0):
    c = np.array([0, 0, 0.9])
    P_ = [Part(lambda P: sd_cyl(P, c, 4.3, 0.75, 0.35), _coin_face(c))]
    return sprite(P_, [-6, -6, 0], [6, 6, 2.6])
def coin_stack(n=6, seed=2):
    rr = random.Random(seed); P_ = []
    for i in range(n):
        dx, dy = rr.uniform(-0.9, 0.9), rr.uniform(-0.9, 0.9)
        P_.append(Part((lambda dx, dy, i: (lambda P: sd_cyl(P, [dx, dy, 0.8 + i * 1.55], 4.3, 0.72, 0.3)))(dx, dy, i), 'gold'))
    top = 0.8 + (n - 1) * 1.55
    P_[-1] = Part(P_[-1].sdf, _coin_face(np.array([0, 0, top])))
    return sprite(P_, [-6, -6, 0], [6, 6, top + 1.5])
def _leather(P, N):
    n = np.sin(P[:, 0] * 0.9 + P[:, 2] * 0.7) + np.sin(P[:, 1] * 1.3 - P[:, 2] * 0.5) * 0.8
    return np.where(n > 1.15, mid('velvet2'), mid('leather'))
def pouch():
    """세워 둔 가죽 돈주머니 — 둥근 몸통 · 묶은 목 · 물결 주둥이 · 끈"""
    def body(P):
        a = sd_ellipsoid(P, [0, 0, 8.8], [11.6, 10.6, 9.0])
        b = sd_cyl(P, [0, 0, 17.0], 4.6, 2.6, 1.0)
        return smin(a, b, 3.2)
    ruff = [(0, 18.2), (4.6, 18.2), (7.6, 21.2), (9.2, 23.8), (8.0, 24.4), (6.0, 22.4), (3.4, 20.8), (0, 20.8)]
    def ruffle(P):
        r = np.hypot(P[:, 0], P[:, 1]); th = np.arctan2(P[:, 1], P[:, 0])
        k = 1 + 0.13 * np.sin(7 * th) * np.clip((P[:, 2] - 19.5) / 4, 0, 1)
        return sd_poly2(np.stack([r / k, P[:, 2]], 1), ruff) * 0.85
    P_ = [
        Part(body, _leather),
        Part(ruffle, 'leather'),
        Part(lambda P: sd_torus(P, [0, 0, 18.2], 4.9, 0.95), 'cord'),
        Part(lambda P: sd_capsule(P, [-1.5, -4.6, 17.6], [-3.4, -9.6, 9.0], 0.8), 'cord'),
        Part(lambda P: sd_capsule(P, [0.8, -4.7, 17.6], [2.2, -10.2, 10.4], 0.8), 'cord'),
        Part(lambda P: sd_sphere(P, [-3.5, -9.8, 8.6], 1.3), 'cord'),
        Part(lambda P: sd_sphere(P, [2.3, -10.4, 10.0], 1.3), 'cord'),
    ]
    return sprite(P_, [-14, -14, 0], [14, 14, 25])

# ───────────────────────── 회중시계 ─────────────────────────
def _dial(P, N):
    r = np.hypot(P[:, 0], P[:, 1]); ang = np.arctan2(P[:, 1], P[:, 0])
    out = np.full(len(P), mid('dial'))
    tick = (r > 5.6) & (r < 7.0) & (np.abs(((ang / (2 * np.pi) * 12) + 0.5) % 1 - 0.5) < 0.09)
    hand1 = (np.abs(P[:, 0]) < 0.45) & (P[:, 1] > -0.3) & (P[:, 1] < 5.0)
    hand2 = np.abs(P[:, 1] + 0.42 * P[:, 0]) < 0.45
    hand2 &= (P[:, 0] > -0.3) & (P[:, 0] < 3.6)
    out[tick | hand1 | hand2] = mid('dialink')
    return out
def pocket_watch():
    P_ = [
        Part(lambda P: sd_cyl(P, [0, 0, 1.6], 9.6, 1.6, 0.9), 'gold'),
        Part(lambda P: sd_cyl(P, [0, 0, 3.2], 7.6, 0.25, 0.1), _dial),
        Part(lambda P: sd_torus(P, [0, 0, 3.3], 8.3, 0.75), 'gold'),
        Part(lambda P: sd_cyl(local(P, [0, 10.6, 1.6], rotm('x', 90)), [0, 0, 0], 1.6, 1.4, 0.4), 'gold'),
        Part(lambda P: sd_torus(P, [0, 14.2, 1.0], 2.6, 0.75), 'gold'),
    ]
    beads = []
    for i in range(26):                                                  # 구슬 줄 — 고리에서 왼쪽 위로 휘어 나간다
        t = i / 25
        beads.append(np.array([-2 - t * 30 + np.sin(t * 3.4) * 6, 16 + t * 10 + np.sin(t * 5.0) * 5, 0.9]))
    def chain(P):
        d = np.full(len(P), 1e9)
        for b in beads: d = np.minimum(d, sd_sphere(P, b, 0.95))
        return d
    P_.append(Part(chain, 'gold'))
    return sprite(P_, [-36, -12, 0], [12, 32, 4])

# ───────────────────────── 안경 ─────────────────────────
def spectacles():
    """다리를 접어 뒤로 눕힌 안경 — 알이 위(카메라)를 본다"""
    M = rotm('z', -6) @ rotm('x', 30)
    R, r = 6.4, 0.8
    cz = 0.5 * R + r + 0.2
    cs = [np.array([-8.2, 0, cz]), np.array([8.2, 0, cz])]
    def rim(c): return lambda P: sd_torus(local(P, c, M), [0, 0, 0], R, r)
    def lens(c): return lambda P: sd_cyl(local(P, c, M), [0, 0, 0], R - 0.2, 0.25, 0.1)
    up = M @ np.array([0, 1, 0]); rt = M @ np.array([1, 0, 0])
    br0 = cs[0] + rt * (R * 0.8) + up * (R * 0.45); br1 = cs[1] - rt * (R * 0.8) + up * (R * 0.45)
    brm = (br0 + br1) / 2 + up * 1.2
    hinge = [cs[0] - rt * (R + 0.3) + up * 1.5, cs[1] + rt * (R + 0.3) + up * 1.5]
    inner = [Part(rim(cs[0]), 'gold'), Part(rim(cs[1]), 'gold'),
             Part(lambda P: np.minimum(sd_capsule(P, br0, brm, 0.7), sd_capsule(P, brm, br1, 0.7)), 'gold'),
             Part(lambda P: np.minimum(sd_capsule(P, hinge[0], [-12.5, 12, 0.9], 0.6), sd_capsule(P, [-12.5, 12, 0.9], [3, 15, 0.9], 0.6)), 'gold'),
             Part(lambda P: np.minimum(sd_capsule(P, hinge[1], [12.5, 11, 1.7], 0.6), sd_capsule(P, [12.5, 11, 1.7], [-2.5, 14.5, 1.9], 0.6)), 'gold')]
    glass = [Part(lens(cs[0]), 'lens'), Part(lens(cs[1]), 'lens')]
    return glass_sprite(inner, glass, np.array([-17, -6, 0.0]), np.array([17, 17, 12.0]), glass_alpha=0.5, over_ground=80)

# ───────────────────────── 꽃병 ─────────────────────────
def _daisy(c, nrm, rad, seed):
    """데이지 한 송이 — 꽃잎 원반(가장자리 물결) · 가운데 노란 공"""
    nrm = unit(nrm); a = unit(np.cross([0, 0, 1], nrm)) if abs(nrm[2]) < 0.999 else np.array([1.0, 0, 0])
    b = np.cross(nrm, a); M = np.stack([a, b, nrm], 1)
    prof = [(0, -0.45), (rad, -0.25), (rad, 0.15), (0, 0.45)]
    def petals(P):
        q = local(P, c, M); rr = np.hypot(q[:, 0], q[:, 1]); th = np.arctan2(q[:, 1], q[:, 0]) + seed
        k = 0.78 + 0.22 * np.abs(np.cos(th * 5))
        return sd_poly2(np.stack([rr / k, q[:, 2]], 1), prof) * 0.75
    return [Part(petals, 'petal'), Part(lambda P: sd_sphere(local(P, c, M), [0, 0, 0.5], rad * 0.36), 'fcenter')]
def vase_flowers():
    vase = [(0, 0), (4.8, 0), (7.4, 3), (8.6, 7.5), (7.6, 12), (4.2, 15.6), (3.6, 17.2), (4.8, 18.6), (4.6, 19.4), (0, 19.4)]
    P_ = [Part(lambda P: sd_lathe(P, [0, 0, 0], vase), 'porcblue')]
    rr = random.Random(4)
    mouth = np.array([0, 0, 19.0])
    for i in range(16):                                                   # 잎
        ang = rr.uniform(0, 2 * np.pi); ln = rr.uniform(8, 13); dip = rr.uniform(-0.15, 0.45)
        d = unit([np.cos(ang), np.sin(ang), dip])
        c = mouth + d * (ln * 0.55) + [0, 0, 2.5]
        a = unit(np.cross(d, [0, 0, 1])); n_ = np.cross(a, d)
        M = np.stack([d, a, n_], 1)
        P_.append(Part((lambda c, M, ln: (lambda P: sd_ellipsoid(local(P, c, M), [0, 0, 0], [ln * 0.5, 2.1, 0.55])))(c, M, ln), 'leaf'))
    spots = []
    for _ in range(300):
        ang = rr.uniform(0, 2 * np.pi); rad = np.sqrt(rr.random()) * 11.5
        pos = np.array([np.cos(ang) * rad, np.sin(ang) * rad * 0.95, 0])
        pos[2] = 31 - (rad / 11.5) ** 2 * 7.5 + rr.uniform(-0.8, 0.8)
        if all(np.linalg.norm(pos[:2] - s[:2]) > 5.3 for s in spots): spots.append(pos)
    for k, s in enumerate(spots):
        n_ = unit([s[0] * 0.05, s[1] * 0.05 - 0.15, 1])
        P_.append(Part((lambda s: (lambda P: sd_capsule(P, mouth, s, 0.45)))(s), 'leaf'))
        P_ += _daisy(s, n_, rr.uniform(3.0, 3.6), rr.uniform(0, 3))
    return sprite(P_, [-17, -17, 0], [17, 17, 35])

# ───────────────────────── 말린 지도 ─────────────────────────
def rolled_map():
    M = rotm('z', 8) @ rotm('y', 90)
    c = np.array([0, 0, 5.6])
    def roll(P): return sd_cyl(local(P, c, M), [0, 0, 0], 5.6, 30, 1.0)
    def mf(P, N):
        q = local(P, c, M); nl = N @ M
        out = np.full(len(P), mid('parch'))
        end = np.abs(nl[:, 2]) > 0.6
        rr = np.hypot(q[:, 0], q[:, 1]); th = np.arctan2(q[:, 1], q[:, 0])
        spiral = ((rr - th / (2 * np.pi) * 1.4) % 1.4) < 0.45
        out[end & spiral] = mid('paperln')
        return out
    def ribbon(P):
        q = local(P, c, M)
        return sd_torus(np.stack([q[:, 0], q[:, 1], q[:, 2] - 2.0], 1), [0, 0, 0], 5.9, 0.9) * 1.0
    bow_c = c + M @ np.array([0, 5.8, 2.0])
    P_ = [Part(roll, mf), Part(ribbon, 'ribbon'),
          Part(lambda P: sd_ellipsoid(P, bow_c + [-2.6, -1.0, 0.8], [2.6, 1.5, 1.2]), 'ribbon'),
          Part(lambda P: sd_ellipsoid(P, bow_c + [2.6, -0.4, 0.8], [2.6, 1.5, 1.2]), 'ribbon'),
          Part(lambda P: sd_capsule(P, bow_c + [-0.6, -1.2, 0], [-3.6, -11, 0.6], 0.9), 'ribbon'),
          Part(lambda P: sd_capsule(P, bow_c + [0.6, -1.2, 0], [4.4, -10, 0.6], 0.9), 'ribbon')]
    return sprite(P_, [-34, -14, 0], [34, 10, 12.5])

# ───────────────────────── 편지 · 봉랍 ─────────────────────────
def _env_mat(c, M, w, d):
    def f(P, N):
        q = local(P, c, M); nl = N @ M
        out = np.full(len(P), mid('paper'))
        top = nl[:, 2] > 0.6
        x, y = q[:, 0], q[:, 1]
        flap = top & (y > -d + 2) & (np.abs(x) / w * d * 0.95 < (y + d * 0.1))
        edge = top & (np.abs(np.abs(x) / w * d * 0.95 - (y + d * 0.1)) < 0.7) & (y > -d * 0.1)
        out[flap] = mid('parch'); out[edge] = mid('paperln')
        low = top & (np.abs(np.abs(x) / w * (d * 0.9) - (-y + d * 0.55)) < 0.6) & (y < -d * 0.05)
        out[low] = mid('paperln')
        return out
    return f
def _seal_parts(c, rad, seed=1, emblem=True):
    rr = random.Random(seed); ph = [rr.uniform(0, 6) for _ in range(3)]
    def blob(P):
        q = P - c; r = np.hypot(q[:, 0], q[:, 1]); th = np.arctan2(q[:, 1], q[:, 0])
        k = 1 + 0.07 * np.sin(th * 5 + ph[0]) + 0.05 * np.sin(th * 9 + ph[1])
        prof = [(0, 0), (rad, 0), (rad * 1.02, 0.7), (rad * 0.92, 1.6), (0, 1.9)]
        return sd_poly2(np.stack([r / k, q[:, 2]], 1), prof) * 0.85
    def wm(P, N):
        q = P - c; out = np.full(len(P), mid('redwax'))
        top = N[:, 2] > 0.75
        if emblem:
            cross = top & (((np.abs(q[:, 0]) < 0.7) & (np.abs(q[:, 1] - 0.3) < rad * 0.48)) | ((np.abs(q[:, 1] - 1.4) < 0.7) & (np.abs(q[:, 0]) < rad * 0.36)))
            out[cross] = mid('redwax_d')
        rim = top & (np.abs(np.hypot(q[:, 0], q[:, 1]) - rad * 0.7) < 0.5)
        out[rim] = mid('redwax_d')
        return out
    P_ = [Part(blob, wm)]
    return P_
def envelope():
    M = rotm('z', -8); c = np.array([0, 0, 0.7]); w, d = 22, 14
    P_ = [Part(lambda P: sd_rbox(local(P, c, M), [0, 0, 0], [w, d, 0.7], 0.3), _env_mat(c, M, w, d))]
    P_ += _seal_parts(c + M @ np.array([0, -1.2, 0.6]), 4.6, seed=3)
    return sprite(P_, [-25, -18, 0], [25, 18, 4])
def wax_seal():
    """두루마리에 찍는 붉은 봉랍 — 남색 리본 꼬리 둘"""
    c = np.array([0, 0, 0.0])
    P_ = _seal_parts(c + [0, 0, 0.4], 7.4, seed=7)
    for sx in (-1, 1):
        P_.append(Part((lambda sx: (lambda P: sd_rbox(local(P, [sx * 3.2, -10.5, 0.45], rotm('z', sx * 14)), [0, 0, 0], [2.4, 7.5, 0.4], 0.2)))(sx), 'navycov'))
    return sprite(P_, [-11, -19, 0], [11, 10, 3.5])

# ───────────────────────── 펼친 책 ─────────────────────────
def open_book():
    M = rotm('z', 4)
    def pages(sx):
        T = rotm('y', -sx * 5)
        cc = np.array([sx * 11.6, 0, 2.6])
        def f(P):
            q = local(local(P, [0, 0, 0], M), cc, T)
            u = np.clip(q[:, 0] * sx + 11.6, 0, 30)                     # 가운데(책등)에서 바깥으로
            bend = 1.6 * np.exp(-u / 3.0) - 0.006 * (u - 8) ** 2 * (u > 8)
            q2 = np.stack([q[:, 0], q[:, 1], q[:, 2] + bend - 0.4], 1)
            return sd_rbox(q2, [0, 0, 0], [12.0, 17, 1.6], 0.5) * 0.85
        def m(P, N):
            q = local(local(P, [0, 0, 0], M), cc, T); nl = (N @ M) @ T
            out = np.full(len(P), mid('paper'))
            top = nl[:, 2] > 0.5
            u = q[:, 0] * sx + 11.6
            ln = top & (u > 3.5) & (u < 20.5) & (q[:, 1] > -13.5) & (q[:, 1] < 13.5) & (((q[:, 1] + 13.5) % 2.4) < 0.8)
            out[ln] = mid('paperln')
            out[top & (u < 1.6)] = mid('paperln')                          # 가운데 골
            side = ~top
            out[side] = np.where((np.floor(q[side, 2] * 2.2) % 2) == 0, mid('paper'), mid('paperln'))
            return out
        return Part(f, m)
    cover = Part(lambda P: sd_rbox(local(P, [0, 0, 0.6], M), [0, 0, 0], [26.5, 18.6, 0.6], 0.4), 'browncov')
    rib = Part(lambda P: sd_rbox(local(P, [0, 0, 0], M), [1.2, -21, 0.5], [1.1, 4.2, 0.35], 0.2), 'ribbon')
    return sprite([cover, pages(-1), pages(1), rib], [-29, -27, 0], [29, 22, 7])

if __name__ == "__main__":
    import time
    out = []
    for f in (lamp, candle, hourglass, globe, teacup, inkwell, book_stack, book_pair, coin, coin_stack, pouch, pocket_watch):
        t0 = time.time(); img, org = f(); out.append((f.__name__, img)); print(f.__name__, img.size, '%.1fs' % (time.time() - t0))
    W_ = sum(i.width for _, i in out) + 10 * len(out) + 10; H_ = max(i.height for _, i in out) + 20
    sheet = Image.new('RGBA', (W_, H_), (150, 96, 56, 255)); x = 10
    for _, i in out: sheet.alpha_composite(i, (x, 10)); x += i.width + 10
    sheet.resize((W_ * 3, H_ * 3), Image.NEAREST).save('sheet.png')
