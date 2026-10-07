"""스케줄 배치판(3판) 재료 — 가까이 본 책상(두루마리 줌인)에 놓을 소품.
3D 소품은 SCALE 2.2 (책상 전체 그림의 1.4 보다 1.57배 — 줌인한 판자 · 축 굵기에 맞춘다) 로 15도마다 24장.
새 소품: 만년필 · 만년필 뚜껑 · 잉크병(마개) · 압지 · 문진 (props3d_z)."""
import json, os, sys, time
import numpy as np
from PIL import Image
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__)) + "/"
OUT = HERE + "out3/"
os.makedirs(OUT + "props", exist_ok=True); os.makedirs(OUT + "frames", exist_ok=True)
STEP, NF, SCALE = 15, 24, 2.2
# id · 이름 · 프레임 수 · 새 소품인가
PROPS3D = [
    ('vase_flowers', '꽃병', NF, 0),                       # 가장 오래 걸리는 것부터 — 두 일꾼이 나눠 갖게
    ('pen', '만년필', NF, 1), ('pen_cap', '만년필 뚜껑', NF, 1), ('ink_bottle', '잉크병', NF, 1), ('inkwell', '잉크 단지', NF, 0),
    ('blotter', '압지', NF, 1), ('paperweight', '문진', NF, 1),
    ('lamp', '유리 등잔', NF, 0), ('candle', '촛대', NF, 0), ('hourglass', '모래시계', NF, 0), ('globe', '지구의', NF, 0),
    ('teacup', '찻잔', NF, 0), ('book_stack', '책 더미', NF, 0), ('book_pair', '책 두 권', NF, 0), ('open_book', '펼친 책', NF, 0),
    ('envelope', '편지', NF, 0), ('wax_seal', '봉랍 인장', NF, 0), ('rolled_map', '말린 지도', NF, 0),
    ('spectacles', '안경', NF, 0), ('pocket_watch', '회중시계', NF, 0), ('pouch', '동전 주머니', NF, 0),
    ('coin_stack', '동전 더미', 1, 0), ('coin', '동전', 1, 0),
]

def _frame(task):
    name, k, new = task
    path = OUT + f"frames/{name}_{k:02d}.png"
    meta = path + ".json"
    if os.path.exists(path) and os.path.exists(meta): return name, k, 0
    import props3d as PR
    import props3d_z as PZ
    PR.SCALE = SCALE; PR.YAW_MODE = True; PR.YAW = -STEP * k
    t0 = time.time()
    img, org = getattr(PZ if new else PR, name)()
    img.save(path); json.dump(dict(ox=int(org[0]), oy=int(org[1]), sec=round(time.time() - t0, 1)), open(meta, "w"))
    return name, k, time.time() - t0

def render_frames(procs=2):
    tasks = [(n, k, new) for n, _, nf, new in PROPS3D for k in range(nf)]
    todo = [t for t in tasks if not os.path.exists(OUT + f"frames/{t[0]}_{t[1]:02d}.png.json")]
    print(len(tasks), "frames,", len(todo), "to render", flush=True)
    t0 = time.time()
    with Pool(procs) as pool:
        for i, (n, k, sec) in enumerate(pool.imap_unordered(_frame, todo, chunksize=1)):
            print(f"  {i + 1}/{len(todo)} {n} {k} {sec:.0f}s  total {time.time() - t0:.0f}s", flush=True)
    print("done", round(time.time() - t0), flush=True)

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

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'frames': render_frames(int(sys.argv[2]) if len(sys.argv) > 2 else 2)
