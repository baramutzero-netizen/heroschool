"""스케줄 배치판(3판) 묶음 — 두루마리 세 시기(2배 그림) · 축 끝 마개 · 책상 판자 · 남색 천 · 깃펜 · 불빛 · 3D 소품 시트 · 액자 · 메뉴 참고 그림 → out3/props.json · layout.json.
3D 프레임은 kit3.py frames 로 먼저 구워 둔다 (out3/frames)."""
import json, os, random, shutil, sys
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__)) + "/"
sys.path.insert(0, HERE); sys.path.insert(0, HERE + "..")
import kit3 as K3
import scene2d as S
import schedule_mock as SM
import schedule_mock2 as M2

OUT = K3.OUT
SHOT = HERE + "town_shot.png"   # 실제 마을 화면 (메뉴판 288 CSS = 317px — 화면 배율 1.1)
DESK_W, DESK_H = 746, 478          # 기본 책상 안쪽 (1배) — 사용자가 그린 범위: 액자 + 메뉴 ≈ 바깥 772x504
MAX_W, MAX_H = 1000, 660           # 배치판에서 늘릴 수 있는 최대 책상
# 메뉴판 — 실제 마을 화면에서 잰 값(게임 CSS px). 288×616, 액자 바깥 모서리에서 위 · 오른쪽으로 16씩 나온다.
# 스케줄 액자도 마을 지도처럼 화면 폭 1208(앱 최대 폭 1240 - 여백 32)에 맞춰 보인다고 보고 배치판이 1배로 바꿔 그린다
MENU = dict(w=288, h=616, top=16, right=16, screen=1208)
ZOOM = K3.SCALE / 1.4              # 책상 전체 그림 대비 확대

def desk_planks(w, h, seed=4):
    """가까이 본 책상 판자 (35px) — 남색 천 없이. schedule_mock.desk_zoom 과 같은 결"""
    rng = random.Random(seed)
    W = S.WOOD
    L = Image.new('RGB', (w, h)); D = ImageDraw.Draw(L)
    y = -12; k = 0
    while y < h:
        hh = 35; tone = [2, 3][k % 2]
        D.rectangle([0, y, w - 1, y + hh - 1], fill=W[tone])
        for _ in range(int(60 * w / 607)):
            x0 = rng.randrange(-30, w); ln = rng.randrange(20, 110); yy = y + 3 + rng.randrange(hh - 6)
            c = W[max(tone - 1, 0)] if rng.random() < .6 else W[min(tone + 1, 5)]
            amp = rng.uniform(0, 1.6); ph = rng.uniform(0, 6)
            pts = [(x0 + i, yy + round(amp * np.sin(ph + i / 14))) for i in range(0, ln, 3)]
            if len(pts) > 1: D.line(pts, fill=c)
        for x in range(rng.randrange(60, 220), w, rng.randrange(240, 380)):        # 판자 이음 · 못
            D.line([(x, y), (x, y + hh - 1)], fill=W[0]); D.line([(x + 1, y), (x + 1, y + hh - 1)], fill=W[min(tone + 1, 5)])
            for ny in (y + 6, y + hh - 7):
                for nx in (x - 5, x + 6):
                    D.point((nx, ny), fill=S.C('2e1a10')); D.point((nx - 1, ny - 1), fill=W[5])
        D.line([(0, y), (w, y)], fill=S.C('2e1a10')); D.line([(0, y + 1), (w, y + 1)], fill=W[min(tone + 2, 5)])
        y += hh; k += 1
    return L.convert('RGBA')

def crop_pivot(img, pivot):
    bb = img.getbbox()
    return img.crop(bb), (pivot[0] - bb[0], pivot[1] - bb[1])

def quill_zoom():
    img, nib = S.quill(length=int(round(92 * ZOOM * 0.75)), ang=-32)
    a = np.array(img); body = a[..., 3] == 255; a[~body] = 0                  # 구운 그림자를 빼고 몸만 (배치판이 돌린 모양으로 다시 만든다)
    return crop_pivot(Image.fromarray(a), nib)

def menu_ref():
    if not os.path.exists(SHOT): return Image.open(OUT + "menu_ref.png").convert('RGBA')   # 마을 화면 캡처(town_shot.png)가 없으면 전에 오려 둔 것
    im = Image.open(SHOT).convert('RGBA')
    return im.crop((1060, 14, 1377, 692))                                   # 메뉴판 테두리까지 (그림자 빼고) 317×678

NOTE = ("x, y = 기준점(돌리는 중심 — 3D 소품은 책상에 닿는 점, 2D 는 그림 가운데 · 깃펜은 펜촉 · 두루마리는 종이 가운데)의 책상 1배 좌표. "
        "화면(2배)에서는 2를 곱한다. angle = 화면에서 시계 방향 각도(도). 3D 소품은 15도마다 그린 그림에서 가까운 것을 고르고 남은 각만 돌린다. "
        "그리는 순서 = 목록 순서. 불빛(blend: screen)은 가장자리 그늘 위에 화면 섞기로 얹는다. "
        "desk = 책상(액자 안쪽) 크기. menu = 메뉴판 — 게임 화면 CSS px: 폭 w · 높이 h, 액자 바깥 모서리에서 위로 나온 만큼 top · 오른쪽으로 나온 만큼 right, "
        "screen = 액자가 화면에서 차지하는 폭. 1배로는 k = screen / (desk 폭 + 26) 으로 나눠 그린다. "
        "knob_bottom · knob_top = 축 끝 마개 — 두루마리 그림 밖으로 잘린 금 마개 · 꼭지. 기준점(잘린 줄 바로 바깥 한 줄의 축 가운데)을 "
        "두루마리 기준점 + ends(props.json) 자리에 놓으면 이음매 없이 붙는다.")

def build(scrolls=True):
    objs, order, groups = {}, [], []
    def add(oid, name, group, cat, img, piv, kind='2d', frames=1, shadow=None, carry=0, level=0, blend='normal', cell=None, norot=False, variant=None, **extra):
        img.save(OUT + f"props/{oid}.png")
        cw, ch = cell if cell else img.size
        objs[oid] = dict(id=oid, name=name, group=group, cat=cat, kind=kind, frames=frames, step=K3.STEP, cw=cw, ch=ch, px=int(piv[0]), py=int(piv[1]),
                         blend=blend, shadow=shadow, carry=carry, level=level, norot=norot, variant=variant, file=f"props/{oid}.png", **extra)
        order.append(oid)
        if group not in groups: groups.append(group)
    # 두루마리 — 시기 셋 (글자가 2배 화면에 있어 2배 그림 그대로 · 돌리지 않는다)
    # ends = 축 끝 마개를 붙일 자리 (종이 가운데에서 dx, dy · 1배) — 위 · 아래 각각 왼쪽 축, 오른쪽 축
    pieces, ends = M2.end_pieces()
    ENDS = {k: [[int(a), int(b)] for a, b in v] for k, v in ends.items()}
    SCR = [('scroll_late', '두루마리 — 3년차 가을 (15명 · 의뢰)'), ('scroll_mid', '두루마리 — 봄 5주 (6명 · 개인 행동)'), ('scroll_early', '두루마리 — 봄 2주 (3명)')]
    pivs = set()
    for oid, nm in SCR:
        key = oid.split('_')[1]
        path = OUT + f"props/{oid}.png"
        if scrolls or not os.path.exists(path):
            img, pv = M2.scroll_sprite(key)
            json.dump(dict(px=int(pv[0]), py=int(pv[1])), open(path + ".json", "w"))
        else:
            img = Image.open(path); pv = tuple(json.load(open(path + ".json")).values())
        pivs.add((img.size, tuple(pv)))
        add(oid, nm, '두루마리', 'paper', img, pv, kind='2x', carry=3, level=3, norot=True, variant='scroll', ends=ENDS)
    assert len(pivs) == 1, pivs                                                # 시기를 바꿔도 붙인 마개 자리가 그대로이게
    # 축 끝 마개 — 두루마리 그림(캔버스) 밖으로 잘려 나간 금 마개 · 꼭지. 왼쪽 · 오른쪽 축 조각이 같은 그림이라 하나씩
    for side, nm in (('bottom', '축 끝 마개 — 아래'), ('top', '축 끝 마개 — 위')):
        (iL, pL), (iR, pR) = pieces[side]
        assert iL.size == iR.size and tuple(pL) == tuple(pR) and np.array_equal(np.array(iL), np.array(iR)), side
        add('knob_' + side, nm, '두루마리', 'paper', iL, pL, norot=True, level=2, attach=side)
    # 3D 소품
    for name, nm, nf, new in K3.PROPS3D:
        if PARTIAL and not all(os.path.exists(OUT + f"frames/{name}_{k:02d}.png.json") for k in range(nf)): continue   # 시험용 — 다 구운 것만
        sh, cw, ch, px, py = K3.sheet3d(name, nf)
        grp = '필기구' if name in ('pen', 'pen_cap', 'ink_bottle', 'inkwell', 'blotter', 'paperweight') else '소품'
        add(name, nm, grp, 'prop', sh, (px, py), kind='3d', frames=nf, cell=(cw, ch), level=0)
    img, pv = quill_zoom(); add('quill', '깃펜', '필기구', 'prop', img, pv, shadow=[3, 2, 95], level=0)
    rn = S.runner(w=156, h=720); add('runner', '남색 천', '천', 'cloth', rn, (rn.width // 2, rn.height // 2), level=4)
    g = S.glow(int(92 * ZOOM), col=(255, 178, 92), strength=(.46, .30, .17, .07)); add('lamp_glow', '등잔 불빛', '불빛', 'light', g, (int(92 * ZOOM), g.height // 2), blend='screen', level=-1)
    g = S.glow(int(62 * ZOOM), col=(255, 178, 92), strength=(.40, .25, .14, .06)); add('candle_glow', '촛불 빛', '불빛', 'light', g, (int(62 * ZOOM), g.height // 2), blend='screen', level=-1)
    pref = ['두루마리', '필기구', '소품', '천', '불빛']                      # 소품 상자 차례 — 만년필 · 잉크병 묶음을 앞에
    groups.sort(key=lambda g: pref.index(g) if g in pref else len(pref))
    # 책상 · 액자 · 메뉴
    desk_planks(MAX_W, MAX_H).save(OUT + "desk_bg.png")
    shutil.copy(HERE + "out/frame_1x.png", OUT + "frame_1x.png")
    menu_ref().save(OUT + "menu_ref.png")
    # 기본 배치 — 두루마리는 예전 목업 자리(종이 가운데 303) · 아래 오른쪽 메뉴 밑 책상에 잉크병 · 만년필
    SX, SY = 292, 239
    knobs = [('knob_' + k, SX + dx, SY + dy) for k in ('bottom', 'top') for dx, dy in ENDS[k]]
    lay = [('runner', SX, SY), ('scroll_late', SX, SY)] + knobs + [
           ('ink_bottle', 638, 412, 0), ('pen_cap', 712, 410, -45), ('pen', 676, 457, 15)]
    lay = [t for t in lay if t[0] in objs]
    layout = dict(version=3, desk=[DESK_W, DESK_H], menu=MENU, note=NOTE,
                  objects=[dict(id=t[0], name=objs[t[0]]['name'], x=t[1], y=t[2], angle=(t[3] if len(t) > 3 else 0)) for t in lay])
    kit = dict(version=3, inset=13, step=K3.STEP, desk=dict(w=DESK_W, h=DESK_H, max=[MAX_W, MAX_H]), menu=MENU,
               follow=dict(lamp='lamp_glow', candle='candle_glow'), objects=objs, order=order, groups=groups)
    json.dump(kit, open(OUT + "props.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(layout, open(OUT + "layout.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(len(objs), "objects;", len(layout['objects']), "placed")
    return kit, layout

PARTIAL = False
if __name__ == "__main__":
    PARTIAL = 'partial' in sys.argv
    build(scrolls='noscroll' not in sys.argv)
