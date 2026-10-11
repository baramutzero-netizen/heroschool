"""두루마리 스케줄 (게임용) 그림 — 배치판에서 정한 배치(JSON)대로 1배로 굽는다.

게임은 이 그림들 위 · 사이에 스케줄을 HTML 로 얹는다 (글자 · 카드 · 단추는 HTML).
  under  = 액자 안 검정 · 책상 판자 · 남색 천 · 두루마리 종이(그림자) · 종이에 늘 있는 줄(머리 줄 · 아래 띠 줄 · 요일 칸 점선)
  over1  = 두루마리 축(위아래가 잘린 그대로) · 붙인 축 끝 마개 · 소품 (깃펜 앞까지 — 배치 순서)
  over2  = 가장자리 그늘 · 액자
  frame  = 액자만 (1011 — 마을 지도 · 마스터 노트 책상도 이 액자 · 이 크기로. 마스터 노트는 over2 를 쓴다)
  quill  = 깃펜 (움직인다 — 따로)
  sheet  = 카드 바탕(색 6 + 빈 칸) · 요일 띠(색 7) · 카드 그림 13 · 작은 그림(단추 · 십자 · 압정) · 행동 칸 4 · 결재란 2 · 의뢰 쪽지
  chain  = 체인 고리 (가로로 되풀이)
돌려주는 것: art (이름 → PNG bytes), geo (게임이 쓰는 자리 · 크기)
"""
import io, json, os, random, sys
import numpy as np
from PIL import Image, ImageDraw

KIT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "kit") + "/"   # tools/gen/kit
sys.path.insert(0, KIT)
import schedule_mock as SM
import schedule_mock2 as M2
import desk_top as DT
import compose3 as C3

OUT3 = KIT + "out3/"
IN = 13
# 게임 카드는 목업보다 2칸 높다 (1006) — 훈련 이름을 화면 12px 로 키우려고 색 머리(HB 27 → 29)와 카드(80 → 82)를 늘렸다.
# 손패 줄 아래 잉크 줄(Y_RULE2)도 4칸 내린다 (손패가 2칸 내려가고 2칸 길어졌다). 게임 쪽 숫자는 sched_block.js 의 SK_CH · SK_YHANDL · SK_YHAND
M2.HB, M2.CH, M2.Y_RULE2 = 29, 82, 276
C = M2.C
new = M2.new
rect = M2.rect
P = M2.P


def png(img):
    b = io.BytesIO(); img.save(b, "PNG", optimize=True); return b.getvalue()


def frame_of(d, k=0):
    sh = Image.open(OUT3 + d['file']).convert('RGBA')
    return sh.crop((k * d['cw'], 0, (k + 1) * d['cw'], d['ch']))


# ───────────────────────── 책상 장면 (배치대로) ─────────────────────────
def scene(layout):
    kit = json.load(open(OUT3 + "props.json", encoding="utf-8"))
    W, H = layout['desk']; FW, FH = W + IN * 2, H + IN * 2
    objs = layout['objects']
    if M2.ROLLERS is None: M2.ROLLERS = M2.rollers()
    pcx, pcy = M2.paper_center()
    scr = [o for o in objs if o['id'].startswith('scroll_')]
    assert len(scr) == 1, "두루마리는 하나만"
    so = scr[0]; si = objs.index(so)
    org = (round(so['x']) - pcx, round(so['y']) - pcy)        # 두루마리 캔버스(607×466) 원점의 책상 좌표
    qs = [o for o in objs if o['id'] == 'quill']
    assert len(qs) == 1, "깃펜은 하나만"
    qo = qs[0]; qi = objs.index(qo)
    assert abs(qo.get('angle', 0)) < .01, "깃펜은 0도로"
    ink = [o for o in objs if o['id'] in ('inkwell', 'ink_bottle')]
    assert ink, "잉크 단지가 있어야 서명한다"
    io_ = ink[0]

    desk = Image.open(OUT3 + "desk_bg.png").convert('RGBA').crop((0, 0, W, H))
    under = new(W, H); under.alpha_composite(desk)
    over1 = new(W, H)

    boxes = []                                                # 두루마리 위 소품이 차지한 자리 (캔버스 좌표) — 명부가 내려갈 수 있는 끝을 정한다
    def put(layer, o):
        d = kit['objects'][o['id']]
        if d['kind'] == '2x': raise ValueError(o['id'])
        a = o.get('angle', 0)
        k = int(round(a / d['step'])) % d['frames'] if d['frames'] > 1 else 0
        img = frame_of(d, k)
        A0 = np.array(img)[..., 3] > 40
        if A0.any():
            ys_, xs_ = np.nonzero(A0); dx0, dy0 = round(o['x']) - d['px'], round(o['y']) - d['py']
            boxes.append((o['id'], dx0 + xs_.min() - org[0], dy0 + ys_.min() - org[1], dx0 + xs_.max() + 1 - org[0], dy0 + ys_.max() + 1 - org[1]))
        if d.get('shadow'):
            dx, dy, al = d['shadow']; A = np.array(img)
            out = np.zeros((A.shape[0] + dy, A.shape[1] + dx, 4), np.uint8)
            body = A[..., 3] == 255
            out[dy:dy + A.shape[0], dx:dx + A.shape[1]][body] = [24, 12, 8, al]
            base = Image.fromarray(out); top = new(*base.size); top.paste(img, (0, 0)); base.alpha_composite(top); img = base
        L = new(W, H); L.paste(img, (round(o['x']) - d['px'], round(o['y']) - d['py'])); layer.alpha_composite(L)

    for o in objs[:si]:                                       # 두루마리 밑 (천 등)
        if kit['objects'][o['id']]['blend'] == 'screen': continue
        put(under, o)
    # 두루마리 종이 + 늘 있는 줄 (내용과 상관없이 같은 자리)
    paper = M2.paper_base()
    deco = new(M2.DW, M2.DH)
    SM.ink_rule(deco, M2.X0, M2.X1, 48, seed=5)
    SM.ink_rule(deco, M2.X0, M2.X1, M2.Y_RULE2, seed=9)
    colw = (M2.X1 - M2.X0) / 5
    for i in range(1, 5):
        xx = int(M2.X0 + colw * i)
        for yy in range(M2.Y_RIB + 2, M2.Y_DAY + M2.CH + 2):
            if (yy // 3) % 4 != 3: P(deco, xx, yy, C('b89c72'), 200)
    paper.alpha_composite(deco)
    L = new(W, H); L.paste(paper, org); under.alpha_composite(L)
    # 축 — 두루마리 그림처럼 캔버스 위아래(0 ~ DH)에서 잘린 그대로
    rimg = M2.ROLLERS[0]; rX, rY = M2.roller_place()
    rc = rimg.crop((0, -rY, rimg.width, M2.DH - rY))           # 캔버스 y 0..DH
    L = new(W, H); L.paste(rc, (org[0] + rX, org[1])); over1.alpha_composite(L)
    for o in objs[si + 1:qi]:                                 # 두루마리 위 · 깃펜 밑
        if kit['objects'][o['id']]['blend'] == 'screen': continue
        put(over1, o)
    after = [o for o in objs[qi + 1:] if kit['objects'][o['id']]['blend'] != 'screen']
    assert not after, "깃펜 뒤에 그린 소품이 있다 — 깃펜을 맨 앞으로 두거나 순서를 정해야 한다: " + ", ".join(o['id'] for o in after)
    assert not any(kit['objects'][o['id']]['blend'] == 'screen' for o in objs), "불빛은 아직 게임에 넣지 않았다"

    frame = C3.frame9(W, H)
    FU = Image.new('RGBA', (FW, FH), (0, 0, 0, 255)); FU.alpha_composite(under, (IN, IN))
    F1 = new(FW, FH); F1.alpha_composite(over1, (IN, IN))
    F2 = new(FW, FH); F2.alpha_composite(C3.vignette(W, H), (IN, IN)); F2.alpha_composite(frame)
    FR = new(FW, FH); FR.alpha_composite(frame)               # 액자만 (그늘 없이) — 마을 지도도 스케줄과 같은 액자 · 같은 크기로 (1011)

    # 깃펜 · 잉크 단지 입구
    dq = kit['objects']['quill']; quill = frame_of(dq)
    di = kit['objects'][io_['id']]; iw = np.array(frame_of(di, int(round(io_.get('angle', 0) / di['step'])) % di['frames']))
    # 입구 = 금 고리 안의 어두운 잉크 면 — 고리(밝은 금색) 범위 안에서 테두리 색(281a14)이 아닌 어두운 칸
    rgb = iw[..., :3].astype(int); lum = rgb.sum(-1); solid = iw[..., 3] == 255
    gold = solid & (rgb[..., 0] > 200) & (rgb[..., 1] > 160) & (rgb[..., 2] < 140)
    gy, gx = np.nonzero(gold[:di['py']])
    ring = np.zeros_like(solid); ring[gy.min():gy.max() + 1, gx.min():gx.max() + 1] = True
    outline = (rgb[..., 0] == 40) & (rgb[..., 1] == 26) & (rgb[..., 2] == 20)
    dark = solid & ring & (lum < 130) & ~outline
    ys, xs = np.nonzero(dark)
    ix0, iy0, ix1, iy1 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
    ox, oy = round(io_['x']) - di['px'], round(io_['y']) - di['py']
    inkhole = dict(x=int(ox + ix0), y=int(oy + iy0), w=int(ix1 - ix0), h=int(iy1 - iy0))
    # 잉크 단지 몸통만 (구운 반투명 그림자는 뺀다) — 깃펜을 집으면 over1 의 단지 위에 그대로 겹쳐 빛 테두리를 씌운다 (1006)
    bys, bxs = np.nonzero(solid)
    bx0, by0, bx1, by1 = bxs.min(), bys.min(), bxs.max() + 1, bys.max() + 1
    ibody = iw.copy(); ibody[~solid] = 0
    inkwell_img = Image.fromarray(ibody[by0:by1, bx0:bx1])
    inkwell = dict(x=int(ox + bx0) + IN, y=int(oy + by0) + IN, w=int(bx1 - bx0), h=int(by1 - by0))

    # 명부(아래 띠 왼쪽 · x 44~432)가 내려갈 수 있는 끝 — 그 아래 놓인 소품(문진 등) 바로 위 · 종이 아래 여백 위
    ros_bottom = M2.PY1 - 6
    for (oid, bx0, by0, bx1, by1) in boxes:
        if bx1 > M2.X0 + 2 and bx0 < M2.XL1 and by0 > M2.Y_BAND:
            ros_bottom = min(ros_bottom, by0 - 3)
    # 오른쪽 띠(의뢰 쪽지 · 결재란 · x 440~565)의 아래 끝 — 결재란을 이 위에 붙인다 (1006)
    right_bottom = M2.PY1 - 6
    for (oid, bx0, by0, bx1, by1) in boxes:
        if bx1 > M2.XR0 and bx0 < M2.X1 and by0 > M2.Y_BAND:
            right_bottom = min(right_bottom, by0 - 3)
    geo = dict(desk=[W, H], inset=IN, frame=[FW, FH], ros_bottom=int(ros_bottom), right_bottom=int(right_bottom),
               paper=dict(x=int(org[0] + IN), y=int(org[1] + IN), w=M2.DW, h=M2.DH),   # 두루마리 캔버스 왼쪽 위 (액자 1배 좌표)
               quill=dict(x=int(round(qo['x'])) + IN, y=int(round(qo['y'])) + IN, px=dq['px'], py=dq['py'], w=quill.width, h=quill.height),
               ink=dict(x=inkhole['x'] + IN, y=inkhole['y'] + IN, w=inkhole['w'], h=inkhole['h']),
               inkwell=inkwell, menu=layout.get('menu'))
    return dict(under=FU, over1=F1, over2=F2, quill=quill, inkwell=inkwell_img, frame=FR), geo


# ───────────────────────── 스케줄 조각 그림 (시트) ─────────────────────────
CARD_KEYS = ['red', 'green', 'blue', 'sky', 'gold', 'none']
ICONS = ['dumbbell', 'barbell', 'swords', 'shield', 'book', 'flag', 'leaf', 'lotus', 'target', 'arrow', 'map', 'cup']
MINIS = ['wand', 'bowl', 'eraser', 'book', 'water']
CHIPS = ['auto', 'train', 'rest', 'job']
APPR_W, APPR_H = M2.X1 - M2.XR0 + 1, 72
SLIP_W, SLIP_H = (M2.X1 - 1) - (M2.XR0 + 1) + 1, 61


def card_base(key):
    """카드 바탕 (59×83 · 그림자 포함) — 글자 · 그림 · 남은 기간 꼬리표 · 표식은 게임이 얹는다"""
    sc = M2.Sc()
    old = (M2.icon, M2.life_tab, M2.mark_badge)
    M2.icon = lambda kind: new(16, 14); M2.life_tab = lambda *a, **k: None; M2.mark_badge = lambda *a, **k: None
    try:
        M2.card(sc, 10, 10, dict(col=key, name='----', kind='cup', cost='', fx=[], cond='', life='3', mark=None))
    finally:
        M2.icon, M2.life_tab, M2.mark_badge = old
    L = sc.L.crop((10, 10, 10 + M2.CW + 3, 10 + M2.CH + 3))
    rect(L, 4, 32, 5, 33, C('f6ecd3'))                         # 색 점 — 카드 색이 바로 보여 색 이름과 함께 뺐다 (1006)
    return L


def empty_slot():
    sc = M2.Sc(); M2.slot_empty(sc, 10, 10)
    return sc.L.crop((10, 10, 10 + M2.CW, 10 + M2.CH))


def ribbon_img(pal):
    sc = M2.Sc(); cx, y = 100, 20
    M2.ribbon(sc, cx, y, '', pal)
    return sc.L.crop((cx - 49, y, cx + 50, y + 18))


CHIP_W, CHIP_H = 15, 9


def chip_img(act):
    """행동 칸 (15×9) — 목업(15×8)보다 한 줄 높게: 물마루 글자(잉크 11칸)가 아래 테두리에 묻히지 않게 (1006).
    게임의 명부 줄 간격도 9 → 10 으로 같이 늘렸다 (SK_ROW)"""
    lab, tc, fill, edge = M2.CHIP[act]
    w, h = CHIP_W, CHIP_H
    L = new(w, h)
    if fill is None:                                          # 점선 테두리 (임의)
        for i in range(w):
            if i % 2 == 0: P(L, i, 0, edge); P(L, i, h - 1, edge)
        for j in range(h):
            if j % 2 == 0: P(L, 0, j, edge); P(L, w - 1, j, edge)
    else:
        rect(L, 0, 0, w - 1, h - 1, edge); rect(L, 1, 1, w - 2, h - 2, fill)
        rect(L, 1, 1, w - 2, 1, tuple(min(255, v + 18) for v in fill))
    return L


APPR_SIG_Y = 58          # 서명 줄 (결재란 위에서) — 아래쪽. 그 밑 줄에 '학원장' · 쓰는 법 (1006, 예전 27 · 그 아래 잉크 줄은 뺐다)


def appr_img(enabled):
    """결재란 (126×72 + 그림자 2) — 위에 '결재' · 가운데 진행 비용 · 아래쪽에 서명 줄과 '학원장'"""
    w, h = APPR_W, APPR_H
    L = new(w + 2, h + 2); x = y = 0
    rect(L, x + 2, y + 2, x + w + 1, y + h + 1, (60, 36, 20), 60)
    rect(L, x, y, x + w - 1, y + h - 1, M2.INK2); rect(L, x + 1, y + 1, x + w - 2, y + h - 2, C('efe0bc') if enabled else C('eadbb7'))
    rect(L, x + 3, y + 3, x + w - 4, y + h - 4, C('b89c72')); rect(L, x + 4, y + 4, x + w - 5, y + h - 5, C('f3e6c6') if enabled else C('ece0c0'))
    # 서명 줄 — 양 끝이 살짝 흐린 잉크 줄
    for xx in range(x + 9, x + w - 9):
        a = 150 if xx in (x + 9, x + w - 10) else 210
        P(L, xx, y + APPR_SIG_Y, M2.FADE if not enabled else C('9c8566'), a)
    return L


def slip_img():
    """의뢰 공고 쪽지 (124×61 + 그림자) — 찢긴 아래 결 · 놋쇠 압정"""
    w, h = SLIP_W, SLIP_H
    L = new(w + 3, h + 4); x0, y0, x1, y1 = 0, 0, w - 1, h - 1
    rect(L, x0 + 2, y0 + 3, x1 + 2, y1 + 3, (40, 22, 10), 60)
    top = new(w + 3, h + 4)
    rect(top, x0, y0, x1, y1, C('c2a274')); rect(top, x0 + 1, y0 + 1, x1 - 1, y1 - 1, C('f9f0da'))
    rect(top, x0 + 1, y0 + 1, x1 - 1, y0 + 1, C('fffaea'))
    rng = random.Random(3)
    for x in range(x0, x1 + 1):
        r = rng.random()
        if r < .28: P(top, x, y1, (0, 0, 0), 0)
        elif r < .4: P(top, x, y1, C('d9c39a'))
    cx, py = x1 - 12, y0 + 4
    for (dx, dy, a) in ((1, 2, 90), (2, 2, 70), (2, 1, 70), (3, 2, 40), (2, 3, 40)): P(top, cx + dx, py + dy, (60, 36, 20), a)
    pin = ['.ddd.', 'dhLLd', 'dLLMd', 'dLMMd', '.ddd.']
    pc = {'d': '6a4618', 'L': 'ecc874', 'M': 'c99a3e', 'h': 'fff2c0'}
    for j, r in enumerate(pin):
        for i, ch in enumerate(r):
            if ch in pc: P(top, cx - 2 + i, py - 2 + j, C(pc[ch]))
    L.alpha_composite(top)
    return L


def cross_img():
    L = new(6, 6); M2.cross(L, 0, 0); return L


def chain_tile():
    sc = M2.Sc(); y = 20
    M2.chain(sc, 10, 120, y, 25)
    strip = sc.L.crop((10, y - 3, 120, y + 4))
    return strip.crop((20, 0, 30, 7))                          # 한 주기 (고리 둘 = 10칸)


def sheet():
    """조각을 한 장에 — 자리(1배)는 SHEET 에 적어 게임으로 넘긴다"""
    parts, pos = [], {}
    x = y = 0
    def row(items, gap=1):
        nonlocal x, y
        x = 0; hmax = 0
        for name, im in items:
            pos[name] = [x, y, im.width, im.height]; parts.append((im, x, y))
            x += im.width + gap; hmax = max(hmax, im.height)
        y += hmax + 1
    row([('card_' + k, card_base(k)) for k in CARD_KEYS] + [('slot_empty', empty_slot())])
    row([('rib_' + k, ribbon_img(DT.CARD[k][1])) for k in CARD_KEYS] + [('rib_empty', ribbon_img(SM.EMPTY_PAL))])
    icons = [('ic_' + k, DT.icon(k)) for k in ICONS]
    row(icons)
    row([('mi_' + k, M2.mini(k)) for k in MINIS] + [('cross', cross_img())] + [('chip_' + k, chip_img(k)) for k in CHIPS])
    row([('appr_on', appr_img(True)), ('appr_off', appr_img(False)), ('slip', slip_img())])
    W = max(p[1] + p[0].width for p in parts); H = max(p[2] + p[0].height for p in parts)
    S = new(W, H)
    for im, px, py in parts: S.alpha_composite(im, (px, py))
    return S, pos


def build(layout_path, out_dir=None):
    layout = json.load(open(layout_path, encoding="utf-8"))
    sc, geo = scene(layout)
    sh, pos = sheet()
    art = {k: png(v) for k, v in sc.items()}
    art['sheet'] = png(sh); art['chain'] = png(chain_tile())
    geo['sheet'] = dict(w=sh.width, h=sh.height, pos=pos)
    # 1006 — 의뢰 쪽지가 위, 결재란이 아래 (예전엔 반대). 결재란 아래 끝(그림자 2 포함)은 오른쪽 띠 아래 끝(문진 바로 위)에 붙인다
    geo['slip'] = dict(x=M2.XR0 + 1, y=M2.Y_BAND, w=SLIP_W, h=SLIP_H)
    ay = geo['right_bottom'] - (APPR_H + 2) + 1
    assert ay >= M2.Y_BAND + SLIP_H + 6, "의뢰 쪽지와 결재란이 겹친다"
    geo['appr'] = dict(x=M2.XR0, y=ay, w=APPR_W, h=APPR_H, sig_y=APPR_SIG_Y)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
        for k, v in sc.items(): v.save(os.path.join(out_dir, k + ".png"))
        sh.save(os.path.join(out_dir, "sheet.png")); chain_tile().save(os.path.join(out_dir, "chain.png"))
        json.dump(geo, open(os.path.join(out_dir, "geo.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return art, geo


if __name__ == "__main__":
    a, g = build(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
    print({k: len(v) for k, v in a.items()})
    print(json.dumps({k: v for k, v in g.items() if k != 'sheet'}, ensure_ascii=False))
