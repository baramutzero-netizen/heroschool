"""책상 꾸미기 묶음 2판 — 두루마리를 낱낱이(띠 · 글자 · 카드 · 아이콘) 나누고, 3D 소품은 15도마다 돌린 그림 24장(한 줄 시트)으로.
좌표는 기준점(돌리는 중심 · 3D 소품은 책상에 닿는 점). 그림자 — 3D 는 구운 그대로, 2D 는 배치판이 돌린 모양을 따라 만든다."""
import json, os, sys, time
import numpy as np
from PIL import Image
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__)) + "/"
OUT = HERE + "out2/"
os.makedirs(OUT + "props", exist_ok=True); os.makedirs(OUT + "frames", exist_ok=True)
STEP, NF = 15, 24
PROPS3D = [  # id · 이름 · 프레임 수
    ('lamp', '유리 등잔', NF), ('candle', '촛대', NF), ('globe', '지구의', NF), ('vase_flowers', '꽃병', NF), ('hourglass', '모래시계', NF),
    ('book_stack', '책 더미', NF), ('book_pair', '책 두 권', NF), ('open_book', '펼친 책', NF), ('inkwell', '잉크병', NF),
    ('envelope', '편지', NF), ('wax_seal', '봉랍 인장', NF), ('rolled_map', '말린 지도', NF), ('teacup', '찻잔', NF),
    ('spectacles', '안경', NF), ('pocket_watch', '회중시계', NF), ('pouch', '동전 주머니', NF), ('coin_stack', '동전 더미', 1), ('coin', '동전', 1),
]

def _frame(task):
    name, k = task
    path = OUT + f"frames/{name}_{k:02d}.png"
    meta = path + ".json"
    if os.path.exists(path) and os.path.exists(meta): return name, k
    import props3d as PR
    PR.YAW_MODE = True; PR.YAW = -STEP * k
    t0 = time.time()
    img, org = getattr(PR, name)()
    img.save(path); json.dump(dict(ox=int(org[0]), oy=int(org[1]), sec=round(time.time() - t0, 1)), open(meta, "w"))
    return name, k

def render_frames(procs=2):
    tasks = [(n, k) for n, _, nf in PROPS3D for k in range(nf)]
    todo = [t for t in tasks if not os.path.exists(OUT + f"frames/{t[0]}_{t[1]:02d}.png.json")]
    print(len(tasks), "frames,", len(todo), "to render", flush=True)
    t0 = time.time()
    with Pool(procs) as pool:
        for i, (n, k) in enumerate(pool.imap_unordered(_frame, todo)):
            if i % 10 == 0: print(f"  {i + 1}/{len(todo)} {n} {k} {time.time() - t0:.0f}s", flush=True)

def sheet3d(name, nf):
    frames = [Image.open(OUT + f"frames/{name}_{k:02d}.png").convert('RGBA') for k in range(nf)]
    metas = [json.load(open(OUT + f"frames/{name}_{k:02d}.png.json")) for k in range(nf)]
    assert all(m['ox'] == metas[0]['ox'] and m['oy'] == metas[0]['oy'] for m in metas) and all(f.size == frames[0].size for f in frames)
    al = np.zeros(frames[0].size[::-1], bool)
    for f in frames: al |= np.array(f)[..., 3] > 0
    ys, xs = np.nonzero(al); x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    cw, ch = int(x1 - x0), int(y1 - y0)
    sh = Image.new('RGBA', (cw * nf, ch), (0, 0, 0, 0))
    for k, f in enumerate(frames): sh.paste(f.crop((x0, y0, x1, y1)), (k * cw, 0))
    return sh, cw, ch, int(metas[0]['ox'] - x0), int(metas[0]['oy'] - y0)

def build(render=True):
    import objs2d as O
    from scene2d import CARD, COLS, DECK
    if render: render_frames()
    objs, order, groups = {}, [], []
    def add(oid, name, group, cat, img, piv, kind='2d', frames=1, shadow=None, carry=0, level=0, blend='normal', cell=None):
        img.save(OUT + f"props/{oid}.png")
        cw, ch = cell if cell else img.size
        objs[oid] = dict(id=oid, name=name, group=group, cat=cat, kind=kind, frames=frames, step=STEP, cw=cw, ch=ch, px=int(piv[0]), py=int(piv[1]),
                         blend=blend, shadow=shadow, carry=carry, level=level, file=f"props/{oid}.png")
        order.append(oid)
        if group not in groups: groups.append(group)
    # 두루마리와 그 위
    img, pv = O.blank_scroll(); add('scroll', '빈 두루마리', '두루마리', 'paper', img, pv, shadow=[3, 3, 70], carry=3, level=3)
    img, pv = O.separator(); add('sep_line', '점선', '두루마리', 'line', img, pv, level=1)
    img, pv = O.signature(); add('signature', '서명', '두루마리', 'sign', img, pv, level=1)
    for key in COLS:
        img, pv = O.ribbon(key); add(f'ribbon_{key}', f'{CARD[key][0]} 띠', '색 띠', 'ribbon', img, pv, shadow=[1, 2, 50], carry=2, level=2)
    for key in COLS:
        img, pv = O.ribbon_label(key); add(f'label_{key}', f'글자 {CARD[key][0]}', '띠 글자', 'label', img, pv, level=1)
    for key in COLS:
        img, pv = O.card_blank(key); add(f'card_{key}', f'빈 카드 {CARD[key][0]}', '카드', 'card', img, pv, shadow=[2, 2, 55], carry=2, level=2)
    ICN = [('swords', '칼 두 자루'), ('shield', '방패'), ('dumbbell', '아령'), ('barbell', '역기'), ('book', '책'), ('flag', '깃발'), ('leaf', '잎'),
           ('lotus', '연꽃'), ('target', '과녁'), ('arrow', '과녁과 화살'), ('map', '지도'), ('cup', '찻잔')]
    for kind, nm in ICN:
        img, pv = O.icon(kind); add(f'icon_{kind}', f'아이콘 {nm}', '아이콘', 'icon', img, pv, level=1)
    for key in COLS:
        for label, kind in DECK[key]:
            tid = O.text_id(label, key)
            if tid in objs: continue
            nm = f'글자 {label}' + (f' ({CARD[key][0]})' if label == '휴식' else '')
            img, pv = O.card_text(label, key); add(tid, nm, '카드 글자', 'text', img, pv, level=1)
    # 소품
    for name, nm, nf in PROPS3D:
        sh, cw, ch, px, py = sheet3d(name, nf)
        add(name, nm, '소품', 'prop', sh, (px, py), kind='3d', frames=nf, cell=(cw, ch), level=0)
    img, pv = O.quill(); add('quill', '깃펜', '소품', 'prop', img, pv, shadow=[3, 2, 95], level=0)
    img, pv = O.runner(); add('runner', '남색 천', '천', 'cloth', img, pv, level=4)
    img, pv = O.glow(92, col=(255, 178, 92), strength=(.46, .30, .17, .07)); add('lamp_glow', '등잔 불빛', '불빛', 'light', img, pv, blend='screen', level=-1)
    img, pv = O.glow(62, col=(255, 178, 92), strength=(.40, .25, .14, .06)); add('candle_glow', '촛불 빛', '불빛', 'light', img, pv, blend='screen', level=-1)
    # 기본 배치 (기준점 · 각도 0)
    lay = [('runner', 236, 233)] + O.scroll_layout() + [
        ('wax_seal', 371, 244), ('vase_flowers', 32, 76), ('lamp', 100, 88), ('envelope', 178, 62), ('rolled_map', 332, 58), ('candle', 432, 90),
        ('book_stack', 62, 418), ('pouch', 146, 406), ('coin_stack', 184, 432), ('coin', 170, 448), ('coin', 199, 410), ('coin', 206, 448),
        ('spectacles', 240, 390), ('pocket_watch', 290, 444), ('teacup', 338, 406), ('inkwell', 408, 392), ('quill', 410, 381),
        ('hourglass', 422, 442), ('globe', 548, 386), ('open_book', 538, 440), ('lamp_glow', 100, 74), ('candle_glow', 432, 74)]
    layout = dict(version=2, size=[607, 466], note=NOTE, objects=[dict(id=i, name=objs[i]['name'], x=x, y=y, angle=0) for i, x, y in lay])
    kit = dict(version=2, desk=dict(w=607, h=466), inset=13, menu=dict(w=288, h=616, top=16, right=16, screen=1208), follow=dict(lamp='lamp_glow', candle='candle_glow'),
               step=STEP, objects=objs, order=order, groups=groups)
    json.dump(kit, open(OUT + "props.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(layout, open(OUT + "layout.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(len(objs), "objects;", len(layout['objects']), "placed")
    return kit, layout

NOTE = ("x, y = 기준점(돌리는 중심 — 3D 소품은 책상에 닿는 점, 2D 는 그림 가운데 · 깃펜은 펜촉)의 책상 1배 좌표. 2배 화면에서는 2를 곱한다. "
        "angle = 화면에서 시계 방향 각도(도). 3D 소품은 15도마다 그린 프레임(kit.json 의 frames · step)에서 가까운 것을 고르고 남은 각만 돌린다. "
        "그리는 순서 = 목록 순서. 불빛(blend: screen)은 가장자리 그늘 위에 화면 섞기로 얹는다.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'frames': render_frames(int(sys.argv[2]) if len(sys.argv) > 2 else 2)
    else: build(render=False)
