"""스케줄(가까이 본 책상)용 새 소품 — 만년필 · 만년필 뚜껑 · 잉크병(마개) · 압지 · 문진.
props3d 와 같은 렌더러 · 같은 빛 · 같은 재질 규칙. 크기(SCALE)는 kit3 가 정한다."""
import numpy as np
from px3d import *
import props3d as PR
from props3d import sprite

# ── 재질 ──
mat('lacq',    ['080c1c', '101a36', '1a2a52', '2a4174', '43609a'], spec=(70, .42, 'e6eeff'))     # 남색 옻칠
mat('lacqblk', ['060608', '0e0e12', '18181e', '26262e', '3a3a46'], spec=(60, .45, 'd4d8e4'))     # 검은 수지
mat('labelp',  ['a49272', 'c6b48e', 'e2d4b0', 'f0e6c8', 'fbf5e2'])                                # 잉크병 상표 종이
mat('blotp',   ['5c7a5a', '78967a', '96b296', 'b2cab0', 'cce0c8'])                                # 압지 (연두빛 흡묵지)
mat('walnut',  ['24140c', '3a2214', '54321e', '6e4428', '8a5834'])                                # 호두나무
mat('bronze',  ['22160c', '3c2814', '5a3e1e', '7c5a2c', 'a0783e'], spec=(40, .55, 'f2d8a0'))     # 검은 청동 (문진)
mat('capgray', ['141418', '202026', '2e2e36', '40404a', '585866'], spec=(50, .5, 'e0e4ee'))     # 마개 골

def _along_x(P, T):
    """만년필 축(lathe z)을 세계 x 로 눕힌다 — q = (P - T) @ rotm('y', 90): q_z = 세계 x, q_x = -세계 z(위쪽이 음수)"""
    return local(P, T, rotm('y', 90))

# ───────────────────────── 만년필 ─────────────────────────
PEN_R = 2.5
def pen():
    """뚜껑을 연 만년필 — 펜촉(금, 가운데 틈) · 검은 그립 · 금 고리 · 남색 몸통 · 끝 금장. 펜촉은 −x 쪽"""
    T = np.array([-23.0, 0.0, PEN_R])
    section = [(0, 5.0), (1.5, 5.0), (1.62, 5.8), (1.78, 8.2), (1.98, 10.3), (2.12, 10.9), (0, 10.9)]
    barrel = [(0, 11.4), (2.46, 11.4), (2.52, 12.2), (2.52, 39.4), (2.42, 41.6), (2.05, 43.6), (1.5, 44.6), (0, 44.6)]
    def nib(P):
        q = _along_x(P, T)
        cone = sd_poly2(np.stack([np.hypot(q[:, 0], q[:, 1]), q[:, 2]], 1), [(0, 0.0), (0.35, 0.0), (1.55, 5.6), (0, 5.6)])
        return np.maximum(cone, q[:, 0] + 0.15)                          # 위쪽 반(조금 더)만 — 휘어진 금판
    def nibm(P, N):
        q = _along_x(P, T)
        out = np.full(len(P), mid('gold'))
        slit = (np.abs(q[:, 1]) < 0.2) & (q[:, 2] < 3.9)
        hole = (np.hypot(q[:, 1], q[:, 2] - 4.1) < 0.42)
        out[slit | hole] = mid('lacqblk')
        return out
    def feed(P):
        q = _along_x(P, T)
        c = sd_poly2(np.stack([np.hypot(q[:, 0], q[:, 1]), q[:, 2]], 1), [(0, 1.4), (0.9, 1.4), (1.35, 5.6), (0, 5.6)])
        return np.maximum(c, -q[:, 0] - 0.05)                            # 아래쪽 반 — 검은 잉크 길
    P_ = [
        Part(nib, nibm),
        Part(feed, 'lacqblk'),
        Part(lambda P: sd_lathe(_along_x(P, T), [0, 0, 0], section), 'lacqblk'),
        Part(lambda P: sd_cyl(_along_x(P, T), [0, 0, 11.15], 2.3, 0.42, 0.15), 'gold'),
        Part(lambda P: sd_lathe(_along_x(P, T), [0, 0, 0], barrel), 'lacq'),
        Part(lambda P: sd_cyl(_along_x(P, T), [0, 0, 39.9], 2.58, 0.36, 0.12), 'gold'),
        Part(lambda P: sd_sphere(_along_x(P, T), [0, 0, 44.4], 1.15), 'gold'),
    ]
    return sprite(P_, [-24, -4, 0], [24, 4, 5.4])

def pen_cap():
    """만년필 뚜껑 — 남색 몸 · 입구 금띠 · 끝 금장 · 위로 향한 금 클립"""
    R = 2.92
    T = np.array([-10.0, 0.0, R])
    body = [(0, 0.0), (2.98, 0.0), (2.95, 1.2), (R, 15.6), (2.6, 17.6), (2.0, 18.6), (0, 18.9)]
    def clip(P):
        q = _along_x(P, T)
        bar = sd_rbox(q, [-(R + 0.42), 0, 10.4], [0.32, 0.55, 6.6], 0.2)
        tip = sd_sphere(q, [-(R + 0.55), 0, 4.0], 0.72)
        root = sd_rbox(q, [-(R + 0.2), 0, 16.4], [0.5, 0.75, 0.7], 0.3)
        return np.minimum(np.minimum(bar, tip), root)
    P_ = [
        Part(lambda P: sd_lathe(_along_x(P, T), [0, 0, 0], body), 'lacq'),
        Part(lambda P: sd_cyl(_along_x(P, T), [0, 0, 0.75], 3.06, 0.62, 0.2), 'gold'),
        Part(lambda P: sd_sphere(_along_x(P, T), [0, 0, 18.4], 1.4), 'gold'),
        Part(clip, 'gold'),
    ]
    return sprite(P_, [-11, -4.5, 0], [11, 4.5, 7.4])

# ───────────────────────── 잉크병 (마개) ─────────────────────────
def ink_bottle():
    """네모난 유리 잉크병 — 앞에 상표 종이, 짧은 목, 골이 진 검은 마개"""
    bx, by, bz = 8.6, 6.6, 6.2
    def body_m(P, N):
        out = np.full(len(P), mid('inkglass'))
        front = N[:, 1] < -0.72
        lab = front & (np.abs(P[:, 0]) < 6.3) & (P[:, 2] > 2.4) & (P[:, 2] < 9.8)
        out[lab] = mid('labelp')
        frame = lab & ((np.abs(np.abs(P[:, 0]) - 5.5) < 0.42) | (np.abs(P[:, 2] - 3.2) < 0.4) | (np.abs(P[:, 2] - 9.0) < 0.4))
        out[frame] = mid('paperln')
        band = lab & (np.abs(P[:, 2] - 6.1) < 0.9) & (np.abs(P[:, 0]) < 3.6)
        out[band] = mid('navycov')
        return out
    neck = [(0, 11.6), (5.6, 11.6), (4.6, 12.8), (3.5, 13.8), (3.4, 14.8), (0, 14.8)]
    def cap_m(P, N):
        th = np.arctan2(P[:, 1], P[:, 0])
        side = np.abs(N[:, 2]) < 0.6
        ridge = side & (((th / (2 * np.pi) * 16) % 1) < 0.42)
        return np.where(ridge, mid('capgray'), mid('lacqblk'))
    P_ = [
        Part(lambda P: sd_rbox(P, [0, 0, bz], [bx, by, bz], 2.6), body_m),
        Part(lambda P: sd_lathe(P, [0, 0, 0], neck), 'inkglass'),
        Part(lambda P: sd_cyl(P, [0, 0, 17.0], 4.1, 2.4, 0.7), cap_m),
    ]
    return sprite(P_, [-11, -9, 0], [11, 9, 19.6])

# ───────────────────────── 압지 ─────────────────────────
def blotter():
    """흔들 압지 — 둥근 바닥에 연두 흡묵지, 호두나무 몸, 위판 양끝 놋쇠 나사, 가운데 놋쇠 손잡이"""
    RR = 30.0
    def curve(P, r): return np.hypot(P[:, 0], P[:, 2] - RR) - r           # y 축 둥근 바닥 (반지름 r)
    def wood(P): return np.maximum(sd_rbox(P, [0, 0, 3.6], [11.0, 6.4, 3.6], 0.8), curve(P, RR - 0.7))
    def paper(P):
        shell = np.maximum(curve(P, RR), -curve(P, RR - 0.75))
        return np.maximum(np.maximum(shell, sd_rbox(P, [0, 0, 2.2], [11.6, 6.9, 2.2], 0.0)), P[:, 2] - 2.4)
    knob = [(0, 7.0), (1.7, 7.0), (1.25, 8.0), (1.05, 9.2), (2.15, 10.3), (2.35, 11.4), (1.6, 12.3), (0, 12.5)]
    P_ = [
        Part(wood, 'walnut'),
        Part(paper, 'blotp'),
        Part(lambda P: sd_rbox(P, [0, 0, 7.4], [9.2, 5.4, 0.55], 0.35), 'walnut'),
        Part(lambda P: sd_lathe(P, [0, 0, 0], knob), 'brass'),
        Part(lambda P: sd_cyl(P, [-7.3, 0, 8.0], 0.95, 0.25, 0.1), 'brass'),
        Part(lambda P: sd_cyl(P, [7.3, 0, 8.0], 0.95, 0.25, 0.1), 'brass'),
    ]
    return sprite(P_, [-13, -8, 0], [13, 8, 12.8])

# ───────────────────────── 문진 ─────────────────────────
def paperweight():
    """청동 문진 — 긴 검은 청동 막대 위 금 띠 무늬 · 가운데 금 손잡이 (밝은 종이 위에서 또렷하게)"""
    hx, hy, hz = 17.0, 3.3, 1.9
    def bar_m(P, N):
        out = np.full(len(P), mid('bronze'))
        top = N[:, 2] > 0.8
        rim = top & ((np.abs(np.abs(P[:, 0]) - (hx - 2.2)) < 0.38) | (np.abs(np.abs(P[:, 1]) - (hy - 1.1)) < 0.34))
        rim &= (np.abs(P[:, 0]) < hx - 1.8) & (np.abs(P[:, 1]) < hy - 0.7)
        dots = top & (np.abs(P[:, 1]) < 0.5) & (((np.abs(P[:, 0]) - 6.0) % 3.0) < 0.9) & (np.abs(P[:, 0]) > 5.5) & (np.abs(P[:, 0]) < hx - 3.0)
        out[rim | dots] = mid('gold')
        return out
    knob = [(0, 3.6), (2.4, 3.6), (1.6, 4.4), (1.3, 5.3), (2.0, 6.2), (1.5, 7.2), (0, 7.4)]
    P_ = [
        Part(lambda P: sd_rbox(P, [0, 0, hz], [hx, hy, hz], 0.75), bar_m),
        Part(lambda P: sd_lathe(P, [0, 0, 0], knob), 'gold'),
    ]
    return sprite(P_, [-18, -5, 0], [18, 5, 7.8])

NEW = [('pen', '만년필'), ('pen_cap', '만년필 뚜껑'), ('ink_bottle', '잉크병'), ('blotter', '압지'), ('paperweight', '문진')]
if __name__ == "__main__":
    import os, sys, time
    from PIL import Image
    PR.SCALE = float(sys.argv[1]) if len(sys.argv) > 1 else 2.2
    PR.YAW_MODE = True
    out = []
    for name, _ in NEW:
        for yaw in (0, -30, -90):
            PR.YAW = yaw
            t0 = time.time(); img, org = globals()[name](); out.append(img)
            print(name, yaw, img.size, org, '%.1fs' % (time.time() - t0), flush=True)
    W_ = sum(i.width for i in out) + 6 * len(out) + 6; H_ = max(i.height for i in out) + 12
    sh = Image.new('RGBA', (W_, H_), (150, 96, 56, 255)); x = 6
    for i in out: sh.alpha_composite(i, (x, 6)); x += i.width + 6
    sh.resize((W_ * 2, H_ * 2), Image.NEAREST).save(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'newprops.png'))
