#!/usr/bin/env python3
"""
illus_filters.py — 학원이 망했다 · 양피지 삽화 필터 레퍼런스 구현
=================================================================
세 가지 프리셋을 제공한다.
  pastel : 원색을 유지한 파스텔 톤 + 옅은 종이 결          (밝은 야외 배경용)
  book   : 종이색으로 톤을 끌어당긴 책 삽화 톤             (일지/책 UI 안에 들어가는 배경용)
  crayon : 도트 스프라이트를 크레파스로 그린 듯 뭉갠 처리   (캐릭터 스프라이트/프레임용, 투명도 유지)
보조:
  woodcut: 단색 동판화(선화+크로스해칭). 채택되지 않았지만 참고용으로 남김.

의존성: numpy, opencv-python(cv2), Pillow
사용:   python3 illus_filters.py <preset> <in.png> <out.png> [key=value ...]
예:     python3 illus_filters.py book field_summer.png out.png sat=0.78
        python3 illus_filters.py crayon wizard.png out.png tooth=0.8 wobble=1.4
모든 좌표/시그마 값은 "픽셀" 단위이며 입력 해상도 기준이다(crayon은 내부 4배 확대 기준으로 별도 표기).
"""
import sys, numpy as np, cv2
from PIL import Image

# ───────────────────────────── 공통 상수 ─────────────────────────────
PAPER_PASTEL = np.array([236, 222, 192], np.float32)   # pastel 프리셋의 종이색
PAPER_BOOK   = np.array([228, 210, 182], np.float32)   # book 프리셋의 종이색(목업에서 샘플링: 224,206,187)
UMBER        = np.array([62, 44, 38],   np.float32)    # 최암부 색(목업 그림자 샘플: 58,43,42)
INK          = np.array([54, 34, 20],   np.float32)    # woodcut 잉크색
PARCH_BASE   = np.array([232, 214, 176], np.float32)   # 절차적 양피지 밝은색
PARCH_DARK   = np.array([176, 142, 92],  np.float32)   # 절차적 양피지 어두운색

# ───────────────────────────── 노이즈 / 종이 ─────────────────────────────
def fbm(h, w, octaves=5, seed=7):
    """값 노이즈를 옥타브별로 겹친 fBm. 0..1 근처, 평균 ≈0.5."""
    rng = np.random.default_rng(seed); acc = np.zeros((h, w), np.float32); amp = 1.0; tot = 0.0
    for o in range(octaves):
        sh, sw = max(2, h >> (octaves - o)), max(2, w >> (octaves - o))
        n = cv2.resize(rng.random((sh, sw)).astype(np.float32), (w, h), interpolation=cv2.INTER_CUBIC)
        acc += n * amp; tot += amp; amp *= .5
    return acc / tot

def parchment(h, w, seed=7):
    """절차적 양피지 텍스처(RGB float). 결 + 섬유 + 가장자리 얼룩."""
    n = fbm(h, w, 6, seed); n = (n - n.min()) / (n.max() - n.min() + 1e-6)
    fiber = cv2.GaussianBlur(np.random.default_rng(seed + 1).random((h, w)).astype(np.float32), (0, 0), 1.2)
    t = np.clip(n * .9 + (fiber - .5) * .12, 0, 1)[..., None]
    p = PARCH_BASE * (1 - t * .45) + PARCH_DARK * (t * .45)
    yy, xx = np.mgrid[0:h, 0:w]; r = np.sqrt(((yy - h / 2) / (h / 2)) ** 2 + ((xx - w / 2) / (w / 2)) ** 2)
    v = np.clip((r - .75) / .55, 0, 1) ** 1.6
    stain = fbm(h, w, 4, seed + 3); stain = (stain - stain.min()) / (stain.max() - stain.min() + 1e-6)
    v = v * (0.55 + 0.45 * stain)
    p = p * (1 - v[..., None] * .38) + PARCH_DARK * (v[..., None] * .38)
    return np.clip(p, 0, 255)

def stroke_noise(h, w, angle_deg, seed, cell=3.0, length=10):
    """한 방향으로 늘어진 획 결. 저해상도 노이즈 → 방향 블러 → 확대. 0..1"""
    rng = np.random.default_rng(seed)
    sh, sw = max(2, int(h / cell)), max(2, int(w / cell))
    n = rng.random((sh, sw)).astype(np.float32)
    k = int(length) | 1; ker = np.zeros((k, k), np.float32); c = k // 2; a = np.deg2rad(angle_deg)
    for t in np.linspace(-c, c, k * 3):
        x = int(round(c + t * np.cos(a))); y = int(round(c + t * np.sin(a)))
        if 0 <= x < k and 0 <= y < k: ker[y, x] = 1
    ker /= ker.sum(); n = cv2.filter2D(n, -1, ker, borderType=cv2.BORDER_REFLECT)
    n = cv2.resize(n, (w, h), interpolation=cv2.INTER_CUBIC)
    return (n - n.min()) / (n.max() - n.min() + 1e-6)

def smoothstep(x, a, b):
    t = np.clip((x - a) / (b - a), 0, 1); return t * t * (3 - 2 * t)

def to_lab(rgb):  return cv2.cvtColor(np.clip(rgb, 0, 255).astype(np.uint8), cv2.COLOR_RGB2LAB).astype(np.float32)
def from_lab(lab): return cv2.cvtColor(np.clip(lab, 0, 255).astype(np.uint8), cv2.COLOR_LAB2RGB).astype(np.float32)

# ───────────────────────────── 톤 조정 ─────────────────────────────
def pastel_tone(rgb, sat=.72, lift=.28, gamma=.90, warm=.10, paper=PAPER_PASTEL):
    """색상(hue)은 유지하고 채도↓, 검정 들어올림(lift), 종이색 쪽으로 warm 만큼 혼합."""
    lab = to_lab(rgb); L = (lab[..., 0] / 255) ** gamma; L = L * (1 - lift) + lift
    lab[..., 0] = L * 255
    lab[..., 1] = (lab[..., 1] - 128) * sat + 128; lab[..., 2] = (lab[..., 2] - 128) * sat + 128
    out = from_lab(lab)
    lum = out.mean(axis=2, keepdims=True) / 255
    out = out * (1 - warm) + paper * warm * (lum * .6 + .4)
    return np.clip(out, 0, 255)

def book_tone(rgb, sat=.68, lift=.14, warm_a=(3, 6), warm_b=(4, 16), paper_hi=.36, umber_lo=.50):
    """책 삽화 톤. Lab의 a/b에 따뜻한 편향을 더하고(밝을수록 더), 하이라이트→종이색, 최암부→엄버."""
    lab = to_lab(rgb); L = lab[..., 0] / 255; a = lab[..., 1] - 128; b = lab[..., 2] - 128
    L = L ** .95 * (1 - lift) + lift
    a = a * sat + warm_a[0] + warm_a[1] * L
    b = b * sat + warm_b[0] + warm_b[1] * L
    lab[..., 0] = L * 255; lab[..., 1] = a + 128; lab[..., 2] = b + 128
    out = from_lab(lab)
    hi = np.clip((L - .55) / .45, 0, 1) ** 1.5 * paper_hi
    lo = np.clip((.30 - L) / .30, 0, 1) ** 1.2 * umber_lo
    out = out * (1 - hi[..., None]) + PAPER_BOOK * hi[..., None]
    out = out * (1 - lo[..., None]) + UMBER * lo[..., None]
    return np.clip(out, 0, 255)

# ───────────────────────────── 선 ─────────────────────────────
def xdog_lines(gray_u8, strength=1.0, sigma=1.1, k=1.6, p=22, eps=.015):
    """XDoG 선화. 반환 0(잉크)..1(없음)."""
    g = gray_u8.astype(np.float32) / 255
    g1 = cv2.GaussianBlur(g, (0, 0), sigma); g2 = cv2.GaussianBlur(g, (0, 0), sigma * k)
    d = (1 + p) * g1 - p * g2
    e = np.where(d >= eps, 1.0, 1 + np.tanh(8 * (d - eps))); e = np.clip(e, 0, 1)
    e = cv2.GaussianBlur(e, (0, 0), .6)
    return 1 - np.clip((1 - e) * strength, 0, 1)

def soft_line(rgb, alpha=None, strength=.35, sigma=1.0):
    """연한 색연필 선 마스크(0=선). 투명 경계는 제외."""
    g = cv2.cvtColor(np.clip(rgb, 0, 255).astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float32) / 255
    g1 = cv2.GaussianBlur(g, (0, 0), sigma); g2 = cv2.GaussianBlur(g, (0, 0), sigma * 1.6)
    d = 19 * g1 - 18 * g2
    e = np.clip(1 - np.clip((0.02 - d) * 12, 0, 1), 0, 1)
    if alpha is not None:
        am = cv2.GaussianBlur(alpha, (0, 0), 1.0); e = 1 - (1 - e) * np.clip(am * 1.2 - .1, 0, 1)
    return 1 - (1 - e) * strength

def wash_edges(rgb, sigma=1.3, strength=.28):
    """수채 삽화의 색면 경계 어두워짐(잉크 워시)."""
    g = cv2.cvtColor(np.clip(rgb, 0, 255).astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float32) / 255
    g1 = cv2.GaussianBlur(g, (0, 0), sigma); g2 = cv2.GaussianBlur(g, (0, 0), sigma * 1.7)
    d = np.clip((g2 - g1) * 6, 0, 1)
    ink = rgb * .5 + UMBER * .5
    return rgb * (1 - d[..., None] * strength) + ink * (d[..., None] * strength)

# ───────────────────────────── 프리셋 ─────────────────────────────
def preset_pastel(rgba, sat=.72, lift=.28, gamma=.90, warm=.10, line=.35, paper_mix=.22, vignette=.18, smooth=1, seed=7):
    rgb, a = rgba[..., :3].astype(np.float32), rgba[..., 3].astype(np.float32) / 255
    h, w = rgb.shape[:2]
    if smooth: rgb = cv2.bilateralFilter(rgb.astype(np.uint8), 7, 35, 5).astype(np.float32)
    out = pastel_tone(rgb, sat, lift, gamma, warm)
    k = soft_line(rgb, None, strength=line, sigma=1.1)
    dark = pastel_tone(rgb, sat=.9, lift=.05, gamma=1.4, warm=0) * .7
    out = out * k[..., None] + dark * (1 - k[..., None])
    paper = parchment(h, w, seed)
    out = out * (1 - paper_mix) + (out * paper / 255) * paper_mix
    yy, xx = np.mgrid[0:h, 0:w]; r = np.sqrt(((yy - h / 2) / (h / 2)) ** 2 + ((xx - w / 2) / (w / 2)) ** 2)
    v = np.clip((r - .85) / .5, 0, 1) ** 1.5 * vignette
    out = out * (1 - v[..., None]) + PAPER_PASTEL * .8 * v[..., None]
    return np.dstack([np.clip(out, 0, 255), a * 255]).astype(np.uint8)

def preset_book(rgba, sat=.68, lift=.14, warm_a=(3, 6), warm_b=(4, 16), paper_hi=.36, umber_lo=.50,
                wash=.28, paper_mix=.34, stain=.12, smooth=1.0, seed=7):
    rgb, a = rgba[..., :3].astype(np.float32), rgba[..., 3].astype(np.float32)
    h, w = rgb.shape[:2]
    rgb = cv2.bilateralFilter(rgb.astype(np.uint8), 9, 40 * smooth, 6 * smooth).astype(np.float32)
    rgb = cv2.edgePreservingFilter(rgb.astype(np.uint8), flags=1, sigma_s=30, sigma_r=.25).astype(np.float32)
    out = book_tone(rgb, sat, lift, warm_a, warm_b, paper_hi, umber_lo)
    out = wash_edges(out, 1.3, wash)
    paper = parchment(h, w, seed)
    out = out * (1 - paper_mix) + (out * paper / 255) * paper_mix
    st = fbm(h, w, 4, seed + 5); st = (st - st.mean()) * stain
    out = out * (1 + st[..., None])
    return np.dstack([np.clip(out, 0, 255), a]).astype(np.uint8)

def preset_crayon(rgba, up=4, wobble=1.0, tooth=.55, smudge=1.0, angle=35, out_scale=2, seed=7,
                  sat=.85, lift=.14, outline=.6):
    """입력(h,w,4) → 출력(h*out_scale, w*out_scale, 4). 내부에서 up배 확대 후 처리."""
    h, w = rgba.shape[:2]; H, W = h * up, w * up
    src = rgba.astype(np.float32); a0 = src[..., 3] / 255
    rgb0 = cv2.inpaint(src[..., :3].astype(np.uint8), (a0 < .05).astype(np.uint8), 3, cv2.INPAINT_TELEA).astype(np.float32)
    rgb = cv2.resize(rgb0, (W, H), interpolation=cv2.INTER_CUBIC)
    a = cv2.resize(a0, (W, H), interpolation=cv2.INTER_CUBIC)
    # 1) 픽셀 계단 녹이기
    rgb = cv2.bilateralFilter(np.clip(rgb, 0, 255).astype(np.uint8), 0, 22, 1.1 * up * smudge).astype(np.float32)
    rgb = cv2.GaussianBlur(rgb, (0, 0), .35 * up * smudge)
    a = cv2.GaussianBlur(a, (0, 0), .5 * up)
    # 2) 손 흔들림(좌표 변위)
    amp = wobble * up
    dx = (fbm(H, W, 3, seed + 1) - .5) * 2 * amp; dy = (fbm(H, W, 3, seed + 2) - .5) * 2 * amp
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32); mx, my = xx + dx, yy + dy
    rgb = cv2.remap(rgb, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    a = cv2.remap(a, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    # 3) 파스텔 톤
    rgb = pastel_tone(rgb, sat=sat, lift=lift, gamma=.95, warm=.06)
    # 4) 크레파스 획 결(두 방향)
    g1 = stroke_noise(H, W, angle, seed + 3, cell=2.6, length=14)
    g2 = stroke_noise(H, W, angle + 70, seed + 4, cell=3.4, length=9)
    grain = (g1 * .65 + g2 * .35 - .5) * 2                      # -1..1
    light = np.clip(grain, 0, 1) ** 1.4 * tooth                  # 종이 비침
    dark = np.clip(-grain, 0, 1) ** 1.6 * tooth * .5             # 왁스 뭉침
    paper = np.array([246, 240, 226], np.float32)
    rgb = rgb * (1 - light[..., None] * .6) + paper * (light[..., None] * .6)
    rgb = rgb * (1 - dark[..., None] * .35)
    # 5) 알파 조이기 + 가장자리 결
    a = smoothstep(a, .32, .68)
    edge = np.clip(1 - np.abs(a - .5) * 2, 0, 1)
    a = np.clip(a - edge * np.clip(grain, 0, 1) * .5, 0, 1)
    # 6) 끊긴 어두운 윤곽
    ga = cv2.GaussianBlur(a, (0, 0), .6 * up)
    gx = cv2.Sobel(ga, cv2.CV_32F, 1, 0); gy = cv2.Sobel(ga, cv2.CV_32F, 0, 1)
    ed = np.clip(np.sqrt(gx * gx + gy * gy) * 1.3, 0, 1) * (1 - np.clip(grain, 0, 1) * .7)
    ink = rgb * .45
    rgb = rgb * (1 - ed[..., None] * outline) + ink * (ed[..., None] * outline)
    a = np.clip(np.maximum(a, ed * .85 * (ga > .08)), 0, 1)
    out = np.dstack([np.clip(rgb, 0, 255), a * 255])
    return cv2.resize(out, (w * out_scale, h * out_scale), interpolation=cv2.INTER_AREA).astype(np.uint8)

def preset_woodcut(rgba, spacing=5, seed=7):
    """참고용: 단색 동판화. 선화 + 어두울수록 굵어지는 크로스해칭."""
    rgb, a = rgba[..., :3].astype(np.float32), rgba[..., 3].astype(np.float32)
    h, w = rgb.shape[:2]
    g = cv2.cvtColor(rgb.astype(np.uint8), cv2.COLOR_RGB2GRAY); g = cv2.bilateralFilter(g, 9, 40, 7)
    lo, hi = np.percentile(g, 2), np.percentile(g, 99); g = np.clip((g.astype(np.float32) - lo) / max(hi - lo, 1), 0, 1)
    lines = xdog_lines((g * 255).astype(np.uint8), 1.0, 1.0, 1.7, 24, .012)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32); jit = (fbm(h, w, 3, seed + 9) - .5) * 4
    gs = cv2.GaussianBlur(g, (0, 0), 2.0); hz = np.ones((h, w), np.float32)
    for ang, thr in ((38, .72), (-35, .40), (90, .20)):
        s = xx * np.cos(np.deg2rad(ang)) + yy * np.sin(np.deg2rad(ang)) + jit
        phase = np.abs(((s / spacing) % 1.0) - .5); dark = np.clip((thr - gs) / thr, 0, 1)
        width = .04 + .30 * dark ** 1.3; line = np.clip((width - phase) / .06, 0, 1)
        hz = np.minimum(hz, 1 - line * np.clip(dark * 3, 0, 1) * .9)
    paper = parchment(h, w, seed); wash = 1 - np.clip((.75 - g) / .75, 0, 1) * .18
    out = paper * wash[..., None]; k = np.minimum(lines, hz)
    out = out * k[..., None] + INK * (1 - k[..., None])
    grain = (fbm(h, w, 2, seed + 21) - .5) * .08; out = np.clip(out * (1 + grain[..., None]), 0, 255)
    return np.dstack([out, a]).astype(np.uint8)

# ───────────────────────────── 합성(책 페이지에 넣기) ─────────────────────────────
def torn_mask(w, h, seed=11, margin=16, feather=16, amp=60, blur=3.0):
    """직사각형 칸을 붓 자국처럼 뜯은 알파 마스크 0..1."""
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    dist = np.minimum(np.minimum(xx, w - 1 - xx), np.minimum(yy, h - 1 - yy))
    n = fbm(h, w, 4, seed); n = (n - n.mean()) * amp
    m = np.clip((dist + n - margin) / feather, 0, 1)
    return cv2.GaussianBlur(m, (0, 0), blur)

def place_on_paper(paper_rgb, art_rgb, paper_mult=.20, seed=11):
    """그림을 종이 위에 놓기: 종이색과 20% 멀티플라이 후 뜯긴 경계로 종이와 혼합."""
    h, w = art_rgb.shape[:2]
    mix = art_rgb * (1 - paper_mult) + (art_rgb * paper_rgb / 255) * paper_mult
    m = torn_mask(w, h, seed)[..., None]
    return np.clip(mix * m + paper_rgb * (1 - m), 0, 255)

# ───────────────────────────── CLI ─────────────────────────────
PRESETS = {"pastel": preset_pastel, "book": preset_book, "crayon": preset_crayon, "woodcut": preset_woodcut}

def _parse_kv(args):
    kv = {}
    for s in args:
        k, v = s.split("=", 1)
        if "," in v: kv[k] = tuple(float(x) for x in v.split(","))
        else:
            try: kv[k] = int(v) if v.lstrip("-").isdigit() else float(v)
            except ValueError: kv[k] = v
    return kv

if __name__ == "__main__":
    if len(sys.argv) < 4 or sys.argv[1] not in PRESETS:
        print(__doc__); sys.exit(1)
    preset, src, dst = sys.argv[1:4]; kv = _parse_kv(sys.argv[4:])
    rgba = np.array(Image.open(src).convert("RGBA"))
    Image.fromarray(PRESETS[preset](rgba, **kv), "RGBA").save(dst)
    print("ok", dst)

