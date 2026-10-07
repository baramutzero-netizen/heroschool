"""작은 3D 도트 렌더러 — 소품을 거리장(SDF)으로 만들고, 위에서 비스듬히(정사영) 내려다본 그림을 1배 도트로 뽑는다.
빛은 왼쪽 위 뒤에서. 톤은 재질마다 5단으로 나누고(툰), 반짝임 · 그늘(AO) · 자기 그림자 · 책상 위 그림자를 계산한다.
픽셀마다 4x4 표본을 뽑아 가장 많이 나온 색 하나로 정한다(섞지 않음 — 도트가 뭉개지지 않게)."""
import numpy as np
from PIL import Image

# ── 카메라 · 빛 (세계: x 오른쪽 · y 앞쪽(화면 위) · z 책상에서 위로, 1 = 1배 픽셀) ──
TH = np.radians(60)
FWD = np.array([0.0, np.cos(TH), -np.sin(TH)])
UPV = np.array([0.0, np.sin(TH), np.cos(TH)])
RGT = np.array([1.0, 0.0, 0.0])
def unit(v): v = np.asarray(v, float); return v / np.linalg.norm(v)
LIGHT = unit([-0.5, 0.38, 1.0])
HALF = unit(LIGHT - FWD)
T0 = 400.0
OUT = (40, 26, 20)

def C(h): h = h.lstrip('#'); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

# ── 재질 — 어두움 → 밝음 5단 · 반짝임(빛나는 정도, 문턱, 색) · 테두리 ──
MAT = {}
def mat(name, pal, spec=None, emit=False, alpha=255, rim=None, bands=(.12, .32, .55, .78), flat=False):
    MAT[name] = dict(id=len(MAT) + 1, pal=[C(c) if isinstance(c, str) else c for c in pal], spec=spec, emit=emit, alpha=alpha, bands=bands, flat=flat)
    return name
def mid(name): return MAT[name]['id']
MID2 = {}
def _rebuild():
    MID2.clear()
    for k, v in MAT.items(): MID2[v['id']] = k

# ── 거리장 기본 도형 (P: N x 3) ──
def sd_sphere(P, c, r): return np.linalg.norm(P - c, axis=1) - r
def sd_ellipsoid(P, c, r):
    r = np.asarray(r, float); q = (P - c) / r
    k0 = np.linalg.norm(q, axis=1); k1 = np.linalg.norm(q / r, axis=1)
    return k0 * (k0 - 1) / np.maximum(k1, 1e-9)
def sd_rbox(P, c, b, rr=0.0):
    q = np.abs(P - c) - (np.asarray(b, float) - rr)
    return np.linalg.norm(np.maximum(q, 0), axis=1) + np.minimum(q.max(1), 0) - rr
def sd_cyl(P, c, r, h, rr=0.0):
    """세로(z) 원기둥 — 반높이 h · 모서리 둥글게 rr"""
    d = P - c
    a = np.hypot(d[:, 0], d[:, 1]) - (r - rr); b = np.abs(d[:, 2]) - (h - rr)
    return np.minimum(np.maximum(a, b), 0) + np.hypot(np.maximum(a, 0), np.maximum(b, 0)) - rr
def sd_torus(P, c, R, r):
    d = P - c; q = np.hypot(d[:, 0], d[:, 1]) - R
    return np.hypot(q, d[:, 2]) - r
def sd_capsule(P, a, b, r):
    a = np.asarray(a, float); b = np.asarray(b, float)
    pa = P - a; ba = b - a
    h = np.clip(pa @ ba / (ba @ ba), 0, 1)
    return np.linalg.norm(pa - np.outer(h, ba), axis=1) - r
def sd_poly2(q, V):
    """2D 다각형 거리 (q: N x 2) — 안쪽 음수"""
    V = np.asarray(V, float); n = len(V)
    d = np.sum((q - V[0]) ** 2, axis=1); s = np.ones(len(q))
    j = n - 1
    for i in range(n):
        e = V[j] - V[i]; w = q - V[i]
        b = w - np.outer(np.clip((w @ e) / (e @ e), 0, 1), e)
        d = np.minimum(d, np.sum(b * b, axis=1))
        c1 = q[:, 1] >= V[i][1]; c2 = q[:, 1] < V[j][1]; c3 = e[0] * w[:, 1] > e[1] * w[:, 0]
        flip = (c1 & c2 & c3) | (~c1 & ~c2 & ~c3)
        s = np.where(flip, -s, s)
        j = i
    return s * np.sqrt(d)
def sd_lathe(P, c, prof):
    """세로축 회전체 — prof: (반지름, 높이) 닫힌 다각형"""
    d = P - c
    q = np.stack([np.hypot(d[:, 0], d[:, 1]), d[:, 2]], 1)
    return sd_poly2(q, prof)
def smin(a, b, k):
    h = np.clip(0.5 + 0.5 * (b - a) / k, 0, 1)
    return b + (a - b) * h - k * h * (1 - h)

def rotm(ax, deg):
    a = np.radians(deg); c, s = np.cos(a), np.sin(a)
    if ax == 'x': return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
    if ax == 'y': return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])
def local(P, t, M):
    """세계 → 부품 좌표 (M: 부품 축을 세계에 놓는 회전)"""
    return (P - np.asarray(t, float)) @ M

class Part:
    def __init__(self, sdf, m, name=''):
        self.sdf = sdf; self.m = m; self.name = name   # m: 재질 이름, 또는 f(P, N) -> 재질 id 배열

def scene_sdf(parts, P):
    D = np.stack([p.sdf(P) for p in parts], 0)
    return D.min(0), D.argmin(0)

def hard_shadow(parts, P, L, mint=0.6, maxt=90.0, steps=64):
    """빛 쪽으로 가다가 막히면 0 — 거리장이 조금 틀려도(얇은 타원체) 거짓 그림자가 생기지 않는다"""
    res = np.ones(len(P)); t = np.full(len(P), mint)
    act = np.ones(len(P), bool)
    for _ in range(steps):
        if not act.any(): break
        idx = np.nonzero(act)[0]
        d, _ = scene_sdf(parts, P[idx] + np.outer(t[idx], L))
        blocked = d < 0.03
        res[idx[blocked]] = 0
        t[idx] += np.clip(d, 0.12, 6.0)
        act[idx[blocked | (t[idx] > maxt)]] = False
    return res
def _perp(L):
    a = unit(np.cross(L, [0, 0, 1])); b = unit(np.cross(L, a)); return a, b
def soft_shadow(parts, P, L, mint=0.6, maxt=90.0, k=7.0, steps=64, spread=0.07):
    """빛 방향 셋(가운데 · 조금 비낀 둘)으로 가린 정도 — 1 밝음 · 0 완전 그늘"""
    a, b = _perp(L)
    s = hard_shadow(parts, P, L, mint, maxt, steps)
    s += hard_shadow(parts, P, unit(L + a * spread + b * spread * 0.5), mint, maxt, steps)
    s += hard_shadow(parts, P, unit(L - a * spread - b * spread * 0.5), mint, maxt, steps)
    return s / 3.0

def ambient_occ(parts, P, N):
    occ = np.zeros(len(P)); sca = 1.0
    for i in range(1, 6):
        h = 0.7 * i
        d, _ = scene_sdf(parts, P + N * h)
        occ += (h - d) * sca; sca *= 0.6
    return np.clip(1 - 0.22 * occ, 0, 1)

def bounds_px(bmin, bmax, pad=3):
    """세계 상자 → 화면 범위 (그림자까지)"""
    xs, ys = [], []
    for x in (bmin[0], bmax[0]):
        for y in (bmin[1], bmax[1]):
            for z in (bmin[2], bmax[2]):
                p = np.array([x, y, z])
                for q in (p, p - LIGHT * (z / LIGHT[2])):          # 책상 위 그림자 끝
                    xs.append(q @ RGT); ys.append(-(q @ UPV))
    x0, x1 = int(np.floor(min(xs))) - pad, int(np.ceil(max(xs))) + pad
    y0, y1 = int(np.floor(min(ys))) - pad, int(np.ceil(max(ys))) + pad
    return x0, y0, x1 - x0, y1 - y0

def render(parts, bmin, bmax, ss=4, shadow=(0.42, 0.2), out=OUT, inner_lines=True, ground_shadow=True, steps=140, info=False):
    """parts 를 그린다 — 돌려주는 것: RGBA 그림, 세계 원점의 그림 속 픽셀 위치 (ox, oy)"""
    _rebuild()
    x0, y0, w, h = bounds_px(bmin, bmax)
    n = w * h * ss * ss
    o = (np.arange(ss) + 0.5) / ss
    sx = (np.arange(w)[None, :, None, None] + o[None, None, None, :] + x0)
    sy = (np.arange(h)[:, None, None, None] + o[None, None, :, None] + y0)
    sx, sy = np.broadcast_arrays(sx, sy)
    sx = sx.reshape(-1); sy = -sy.reshape(-1)                      # 화면 위가 +
    O = np.outer(sx, RGT) + np.outer(sy, UPV) - FWD * T0
    rb = np.linalg.norm(np.maximum(np.abs(bmin), np.abs(bmax))) + 2
    t = np.full(n, T0 - rb)
    tpl = -O[:, 2] / FWD[2]                                        # 책상 면 z=0
    hit = np.zeros(n, bool); alive = np.ones(n, bool)
    for _ in range(steps):
        idx = np.nonzero(alive)[0]
        if len(idx) == 0: break
        P = O[idx] + np.outer(t[idx], FWD)
        d, _ = scene_sdf(parts, P)
        h_ = d < 0.01
        hit[idx[h_]] = True
        t[idx] += np.maximum(d, 0.005) * 0.9
        gone = h_ | (t[idx] > tpl[idx] + 0.5) | (t[idx] > T0 + rb)
        alive[idx[gone]] = False
    hit &= t <= tpl + 0.6
    key = np.zeros(n, np.int64)                                    # 0 투명 · 1 · 2 그림자 · 그 밖 = 색 번호
    cols = {0: (0, 0, 0, 0), 1: out[:3] + (int(255 * shadow[0]),), 2: out[:3] + (int(255 * shadow[1]),)}
    col_index = {}
    def colkey(rgba):
        if rgba not in col_index:
            col_index[rgba] = 10 + len(col_index); cols[col_index[rgba]] = rgba
        return col_index[rgba]
    part_of = np.full(n, -1); depth = np.full(n, np.inf)
    if hit.any():
        hi = np.nonzero(hit)[0]
        P = O[hi] + np.outer(t[hi], FWD)
        e = 0.06
        def f(Q): return scene_sdf(parts, Q)[0]
        N = np.stack([f(P + [e, 0, 0]) - f(P - [e, 0, 0]), f(P + [0, e, 0]) - f(P - [0, e, 0]), f(P + [0, 0, e]) - f(P - [0, 0, e])], 1)
        N /= np.linalg.norm(N, axis=1, keepdims=True) + 1e-9
        _, pid = scene_sdf(parts, P)
        part_of[hi] = pid; depth[hi] = t[hi]
        mids = np.zeros(len(hi), int)
        for k, pt in enumerate(parts):
            sel = pid == k
            if not sel.any(): continue
            if callable(pt.m): mids[sel] = pt.m(P[sel], N[sel])
            else: mids[sel] = MAT[pt.m]['id']
        ndl = np.clip(N @ LIGHT, 0, 1)
        sh = hard_shadow(parts, P + N * 0.08, LIGHT, mint=0.8)
        ao = ambient_occ(parts, P, N)
        v = 0.16 + 0.84 * ndl * (0.35 + 0.65 * sh)
        v = v * (0.7 + 0.3 * ao)
        spec = np.clip(N @ HALF, 0, 1)
        for m_id in np.unique(mids):
            M = MAT[MID2[m_id]]; sel = mids == m_id
            pal = M['pal']
            if M['emit']:
                vv = np.clip(-(N[sel] @ FWD), 0, 1)                  # 정면을 볼수록 밝게
                b = np.digitize(vv, np.linspace(0.35, 0.92, len(pal) - 1))
            elif M['flat']:
                b = np.full(int(sel.sum()), len(pal) - 1)
            else:
                b = np.clip(np.digitize(v[sel], M['bands']), 0, len(pal) - 1)
            ks = np.array([colkey(pal[bb] + (M['alpha'],)) for bb in range(len(pal))])
            kk = ks[b]
            if M['spec'] and not M['emit']:
                shin, thr, sc = M['spec']
                hl = (spec[sel] ** shin > thr) & (sh[sel] > 0.5)
                kk = np.where(hl, colkey(C(sc) + (255,)), kk)
            key[hi[np.nonzero(sel)[0]]] = kk
    if ground_shadow:
        # 그림자가 생길 수 있는 곳만 — 물체 픽셀을 빛 반대쪽으로 쓸어 낸 범위
        hp = hit.reshape(h, w, ss * ss).any(2)
        vx, vy = -(LIGHT @ RGT) / LIGHT[2], (LIGHT @ UPV) / LIGHT[2]
        zmax = float(bmax[2]) * 1.12 + 1
        sweep = hp.copy()
        nstep = int(np.ceil(zmax * np.hypot(vx, vy))) + 2
        for k in range(1, nstep + 1):
            f = k / nstep * zmax
            dx, dy = int(round(vx * f)), int(round(vy * f))
            sh_ = np.zeros_like(hp)
            ys0, ys1 = max(0, dy), min(h, h + dy); xs0, xs1 = max(0, dx), min(w, w + dx)
            sh_[ys0:ys1, xs0:xs1] = hp[ys0 - dy:ys1 - dy, xs0 - dx:xs1 - dx]
            sweep |= sh_
        grow = sweep.copy()
        for dy_ in (-2, -1, 0, 1, 2):
            for dx_ in (-2, -1, 0, 1, 2):
                grow |= np.roll(np.roll(sweep, dy_, 0), dx_, 1)
        cand = np.repeat(grow.reshape(-1), ss * ss)
        gi = np.nonzero(~hit & cand)[0]
        G = O[gi] + np.outer(tpl[gi], FWD); G[:, 2] = 0.02
        s = soft_shadow(parts, G, LIGHT, mint=0.3, spread=0.09)
        key[gi] = np.where(s < 0.2, 1, np.where(s < 0.9, 2, 0))
    # 픽셀마다 가장 많은 색 (덮인 표본이 절반 넘으면 물체 색 중에서)
    K = key.reshape(h, w, ss * ss)
    objk = K >= 10
    cover = objk.sum(2)
    Kobj = np.where(objk, K, -1); Kgnd = np.where(objk, -1, K)
    def mode(A):
        cnt = np.zeros(A.shape, int)
        for j in range(A.shape[2]): cnt[..., j] = (A == A[..., j:j + 1]).sum(2) * (A[..., j] >= 0)
        j = cnt.argmax(2)
        return np.take_along_axis(A, j[..., None], 2)[..., 0]
    res = np.where(cover * 2 >= ss * ss, mode(Kobj), mode(Kgnd))
    res = np.where(res < 0, 0, res)
    PO = part_of.reshape(h, w, ss * ss)
    DP = depth.reshape(h, w, ss * ss)
    pix_part = mode(np.where(PO >= 0, PO, -1))
    with np.errstate(all='ignore'):
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            pix_depth = np.nanmedian(np.where(np.isfinite(DP), DP, np.nan), axis=2)
    img = np.zeros((h, w, 4), np.uint8)
    for k_, rgba in cols.items():
        img[res == k_] = rgba
    obj = res >= 10
    # 안쪽 선 — 앞뒤로 떨어진 부품 경계(먼 쪽)를 어둡게
    if inner_lines:
        dk = np.zeros((h, w), bool)
        for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            pp = np.roll(np.roll(pix_part, dy, 0), dx, 1); dd = np.roll(np.roll(pix_depth, dy, 0), dx, 1); oo = np.roll(np.roll(obj, dy, 0), dx, 1)
            dk |= obj & oo & (pp != pix_part) & (pix_depth - dd > 2.2)
        img[dk] = out[:3] + (255,)
    # 바깥 테두리 — 물체 밖 1px (그림자 위에도)
    ring = np.zeros((h, w), bool)
    for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
        ring |= np.roll(np.roll(obj, dy, 0), dx, 1)
    ring &= ~obj
    img[ring] = out[:3] + (255,)
    if info: return Image.fromarray(img), (-x0, -y0), pix_part, obj
    return Image.fromarray(img), (-x0, -y0)

def render_glass(base_parts, glass_parts, bmin, bmax, glass_alpha=0.55, over_ground=120, **kw):
    """유리 — 안쪽(base)을 먼저 그리고, 유리가 맨 앞인 픽셀만 반투명하게 얹는다. 반짝임은 그대로"""
    base, org = render(base_parts, bmin, bmax, **kw)
    kw2 = dict(kw); kw2['ground_shadow'] = False
    allp = base_parts + glass_parts
    gimg, _, pp, obj = render(allp, bmin, bmax, info=True, **kw2)
    b = np.array(base).astype(float); g = np.array(gimg).astype(float)
    gl = obj & (pp >= len(base_parts))
    out = b.copy()
    hl = gl & (g[..., 3] == 255)                                   # 반짝임(불투명) 픽셀
    soft = gl & ~hl
    a = glass_alpha
    out[soft, :3] = b[soft, :3] * (1 - a) + g[soft, :3] * a
    under = soft & (b[..., 3] == 0)
    out[under, :3] = g[under, :3]; out[under, 3] = over_ground
    shade = soft & (b[..., 3] > 0) & (b[..., 3] < 255)            # 그림자 위 유리
    out[shade, 3] = np.maximum(b[shade, 3], over_ground)
    out[hl] = g[hl]
    ring = (g[..., 3] == 255) & ~obj & (np.abs(g[..., :3] - np.array(OUT)).sum(-1) < 3)
    out[ring] = list(OUT) + [255]
    return Image.fromarray(out.astype(np.uint8)), org

def proj(p):
    """세계 점 → 화면(원점 기준) 픽셀"""
    p = np.asarray(p, float)
    return p @ RGT, -(p @ UPV)

def scale_parts(parts, s):
    """부품 크기를 s 배로"""
    out = []
    for p in parts:
        f = (lambda g: (lambda P: s * g(P / s)))(p.sdf)
        m = (lambda g: (lambda P, N: g(P / s, N)))(p.m) if callable(p.m) else p.m
        out.append(Part(f, m, p.name))
    return out
