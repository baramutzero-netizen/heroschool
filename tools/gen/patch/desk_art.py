"""마스터 노트 책상 그림 (1006) — 사용자가 책상 소품 배치판(2판)에서 만든 배치 JSON 을 배치판 자신의 그리기 코드로 굽는다.

    python3 desk_art.py <배치 JSON> [배치판 HTML]

배치판(desk_editor.html — 사용자가 쓴 것)을 Playwright 로 열고, 안쪽 함수(poseOf · tl · applyLayout)를 꺼내
소품마다 돌린 그림(RotSprite) · 그림자를 배치판과 똑같이 만든 뒤 겹으로 나눠 그린다 (1배 607×466).

  base   — 책상 판자 + 남색 천 + 빈 두루마리
  items  — 두루마리 위 내용(띠 · 카드 · 아이콘 · 점선 · 서명) — 스케줄로 넘어갈 때 먼저 사라진다
  props  — 나머지 소품 (목록 차례 그대로)
  vig    — 가장자리 그늘 (배치판 vignette)
  light  — 촛불 빛 (화면 섞기)
  hl_*   — 누를 수 있는 소품 묶음의 테두리 빛 (마우스를 올리면)

누르는 자리(hit) — 픽셀마다 맨 위 소품(알파 > 40, 배치판과 같은 기준)이 어느 묶음인지. 줄마다 [시작, 길이, 묶음] 으로 줄여 둔다.
겹을 나눠도 배치판 그림과 같은지 마지막에 비교한다."""
import base64, io, json, os, re, sys
import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__)) + "/"
OUT = HERE + "desk_out/"
EDITOR = os.path.join(os.path.dirname(HERE.rstrip("/")), "kit", "desk_editor.html")   # 사용자가 쓴 책상 소품 배치판 (그리기 엔진)
DW, DH = 607, 466

ITEM_CATS = {"line", "sign", "ribbon", "label", "card", "icon", "text"}       # 두루마리 위 내용
BASE_IDS = {"runner", "scroll"}
GROUPS = [   # 묶음 번호(1부터) · 이름 · 소품
    ("map",    "튜토리얼",   ["rolled_map"]),
    ("books",  "마스터 육성", ["book_stack", "wax_seal"]),
    ("info",   "학원 정보",   ["pocket_watch", "spectacles"]),
    ("book",   "학생",       ["open_book"]),
    ("scroll", "스케줄",     None),          # 두루마리 + 그 위 내용
]
HOOK = "    buildCatalog(); ready = true; refresh();\n"
HOOK_ADD = ("    window.__desk = { poseOf, tl, K, applyLayout, getObjs: () => objs, bg: () => bgImg, vig: () => vigImg, compose };\n")


def b64png(url):
    return Image.open(io.BytesIO(base64.b64decode(url.split(",", 1)[1]))).convert("RGBA")


def render(layout_path, editor=EDITOR):
    L = json.load(open(layout_path, encoding="utf-8"))
    html = open(editor, encoding="utf-8").read()
    assert html.count(HOOK) == 1, "배치판 HTML 에서 고리 자리를 못 찾았다"
    os.makedirs(OUT, exist_ok=True)
    hooked = OUT + "_editor_hook.html"
    open(hooked, "w", encoding="utf-8").write(html.replace(HOOK, HOOK + HOOK_ADD))
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1400, "height": 900})
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto("file://" + hooked)
        pg.wait_for_function("() => !!window.__desk", timeout=30000)
        res = pg.evaluate("""(L) => {
          const D = window.__desk; D.applyLayout(L);
          const objs = D.getObjs();
          const cv = (w, h) => { const c = document.createElement('canvas'); c.width = w; c.height = h; const g = c.getContext('2d'); g.imageSmoothingEnabled = false; return [c, g]; };
          const poses = objs.map((o, i) => { const p = D.poseOf(o), t = D.tl(o, p), k = D.K(o.id);
            return {i, id: o.id, x: t.x, y: t.y, w: p.w, h: p.h, cat: k.cat, blend: k.blend, src: p.c.toDataURL('image/png')}; });
          const full = cv(%d, %d); D.compose(full[1], 0, 0, {vig: true, light: true});
          const vig = cv(%d, %d); vig[1].drawImage(D.vig(), 0, 0);
          const bg = cv(%d, %d); bg[1].drawImage(D.bg(), 0, 0);
          return {poses, full: full[0].toDataURL('image/png'), vig: vig[0].toDataURL('image/png'), bg: bg[0].toDataURL('image/png')};
        }""" % (DW, DH, DW, DH, DW, DH), L)
        # 겹마다 그리기 — 브라우저 캔버스로 (배치판과 같은 섞기)
        layers = pg.evaluate("""([L, sets]) => {
          const D = window.__desk; D.applyLayout(L);
          const objs = D.getObjs();
          const out = {};
          for (const [name, idx, withBg] of sets) {
            const c = document.createElement('canvas'); c.width = %d; c.height = %d; const g = c.getContext('2d'); g.imageSmoothingEnabled = false;
            if (withBg) g.drawImage(D.bg(), 0, 0);
            for (const i of idx) { const o = objs[i], p = D.poseOf(o), t = D.tl(o, p); g.drawImage(p.c, t.x, t.y); }
            out[name] = c.toDataURL('image/png');
          }
          return out;
        }""" % (DW, DH), [L, layer_sets(L)])
        b.close()
    assert not errs, errs
    return L, res, layers


def layer_sets(L):
    """겹마다 들어갈 소품 번호 (목록 차례 그대로) — 이름, 번호들, 책상 판자를 깔지"""
    kit = kit_cats()
    base, items, props, light = [], [], [], []
    for i, o in enumerate(L["objects"]):
        cat, blend = kit[o["id"]]
        if blend == "screen": light.append(i)
        elif o["id"] in BASE_IDS: base.append(i)
        elif cat in ITEM_CATS: items.append(i)
        else: props.append(i)
    return [("base", base, True), ("items", items, False), ("props", props, False), ("light", light, False)]


_KIT = None
def kit_cats():
    global _KIT
    if _KIT is None:
        h = open(EDITOR, encoding="utf-8").read()
        m = re.search(r"const KIT = (\{.*?\});\n", h, re.S)
        K = json.loads(m.group(1))
        _KIT = {k: (v["cat"], v["blend"]) for k, v in K["objects"].items()}
    return _KIT


def group_of(oid, cat):
    for gi, (key, nm, ids) in enumerate(GROUPS, 1):
        if ids is None:
            if oid == "scroll" or cat in ITEM_CATS: return gi
        elif oid in ids: return gi
    return 0


def rle_rows(lab):
    """줄마다 [시작, 길이, 묶음] — 0(누를 수 없는 곳)은 적지 않는다. 글자로: 줄은 ';', 토막은 ',' 셋씩"""
    rows = []
    for y in range(lab.shape[0]):
        r = lab[y]; runs = []; x = 0
        while x < len(r):
            v = r[x]; x0 = x
            while x < len(r) and r[x] == v: x += 1
            if v: runs += [x0, x - x0, int(v)]
        rows.append(",".join(map(str, runs)))
    return ";".join(rows)


BADGE_DX, BADGE_DY = 10, 5


def scroll_axes(a, sc=None, row=None):
    """두루마리의 두 축(밝은 상아색 기둥)의 가운데 x · 종이 세로 가운데 y — 줌 맞춤용 [왼쪽, 오른쪽, 종이 가운데]
    a = 겹친 그림(RGBA int 배열). sc = 두루마리 자리(없으면 그림 전체)"""
    x0, x1 = (sc["x"] - 4, sc["x"] + sc["w"] + 4) if sc else (0, a.shape[1])
    y = row if row is not None else (sc["y"] + sc["h"] // 2 if sc else a.shape[0] // 2)
    r = a[y]
    xs = [x for x in range(max(0, x0), min(a.shape[1], x1)) if r[x][0] > 225 and r[x][1] > 212 and r[x][2] > 180]
    gs = []
    for x in xs:
        if gs and x - gs[-1][-1] <= 2: gs[-1].append(x)
        else: gs.append([x])
    gs = [g for g in gs if len(g) >= 5]
    assert len(gs) >= 2, gs
    L, R = (gs[0][0] + gs[0][-1]) / 2, (gs[-1][0] + gs[-1][-1]) / 2
    mid = int((L + R) / 2) - 70                                                   # 남색 천을 피한 종이 한 줄
    col = a[:, mid]
    ok = [col[i][0] > 200 and col[i][1] > 180 and col[i][2] > 120 and (not sc or sc["y"] - 4 <= i <= sc["y"] + sc["h"] + 4) for i in range(a.shape[0])]
    runs, cur = [], None                                                          # 이어진 줄 — 12칸 안쪽 틈(종이 위 가로줄 · 얼룩)은 잇는다
    for i, v in enumerate(ok + [False]):
        if v and cur is None: cur = i
        elif not v and cur is not None:
            if runs and cur - runs[-1][1] <= 12: runs[-1][1] = i
            else: runs.append([cur, i])
            cur = None
    best = max(runs, key=lambda r: r[1] - r[0])                                   # 가장 긴 것 = 종이 (액자 금줄 같은 한 줄짜리는 빠진다)
    return [L, R, (best[0] + best[1] - 1) / 2]


def ring(mask, r):
    m = mask.copy()
    for _ in range(r):
        d = m.copy()
        d[1:, :] |= m[:-1, :]; d[:-1, :] |= m[1:, :]; d[:, 1:] |= m[:, :-1]; d[:, :-1] |= m[:, 1:]
        m = d
    return m


def build(layout_path, editor=EDITOR):
    global EDITOR
    EDITOR = editor
    L, res, layers = render(layout_path, editor)
    os.makedirs(OUT, exist_ok=True)
    imgs = {k: b64png(v) for k, v in layers.items()}
    imgs["vig"] = b64png(res["vig"])
    full = b64png(res["full"])
    # 맞춰 보기 — 겹을 차례로 얹은 그림 == 배치판 그림
    chk = Image.new("RGBA", (DW, DH)); [chk.alpha_composite(imgs[k]) for k in ("base", "items", "props", "vig")]
    a = np.array(chk).astype(np.float32) / 255; l = np.array(imgs["light"]).astype(np.float32) / 255
    rgb = a[..., :3]; la = l[..., 3:4]; lc = l[..., :3]                                  # 화면 섞기 (불투명 바탕 위)
    scr = rgb + lc * la - rgb * lc * la
    chk2 = np.dstack([np.round(scr * 255), np.full((DH, DW), 255)]).astype(np.uint8)
    diff = np.abs(chk2.astype(int) - np.array(full).astype(int))[..., :3]
    print("겹 합친 그림 vs 배치판 — 최대 차이", int(diff.max()), "· 다른 픽셀", int((diff.max(axis=2) > 2).sum()))
    # 빛 — 그림 크기만 잘라서 자리와 함께
    lb = imgs["light"].getbbox()
    light = dict(x=lb[0], y=lb[1], w=lb[2] - lb[0], h=lb[3] - lb[1]); imgs["light"] = imgs["light"].crop(lb)
    # 누르는 자리 — 맨 위 소품의 묶음
    kit = kit_cats()
    lab = np.zeros((DH, DW), np.uint8)              # 누르는 자리 — 알파 > 40 (배치판과 같은 기준 · 그림자까지)
    body = np.zeros((DH, DW), np.uint8)             # 테두리 빛 — 불투명한 몸만 (그림자는 빼고)
    for p in res["poses"]:
        cat, blend = kit[p["id"]]
        if blend == "screen": continue
        al = np.array(b64png(p["src"]))[..., 3]
        g = group_of(p["id"], cat)
        for M, th in ((lab, 40), (body, 250)):
            ys, xs = np.nonzero(al > th)
            X, Y = xs + p["x"], ys + p["y"]
            ok = (X >= 0) & (Y >= 0) & (X < DW) & (Y < DH)
            M[Y[ok], X[ok]] = g
    groups = []
    for gi, (key, nm, ids) in enumerate(GROUPS, 1):
        ys, xs = np.nonzero(lab == gi)
        bb = [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1]
        m = body == gi
        # 테두리 빛 — 바깥 1칸 밝은 금빛 + 그 바깥 1칸 옅게 · 안쪽은 아주 옅게 밝힌다
        r1 = ring(m, 1) & ~m; r2 = ring(m, 2) & ~ring(m, 1)
        hl = np.zeros((DH, DW, 4), np.uint8)
        hl[m] = (255, 246, 214, 34)
        hl[r2] = (255, 214, 120, 120)
        hl[r1] = (255, 244, 200, 255)
        X0, Y0, X1, Y1 = max(bb[0] - 2, 0), max(bb[1] - 2, 0), min(bb[2] + 2, DW), min(bb[3] + 2, DH)
        Image.fromarray(hl[Y0:Y1, X0:X1]).save(OUT + f"hl_{key}.png")
        groups.append(dict(k=key, n=nm, bb=bb, hl=[X0, Y0, X1 - X0, Y1 - Y0]))
    # 두루마리 몸(그림자 빼고) · 책 더미 오른쪽 위
    P = {p["id"]: p for p in res["poses"]}
    sc = P["scroll"]
    scroll = dict(x=sc["x"], y=sc["y"], w=sc["w"] - 3, h=sc["h"] - 3)
    bs = P["book_stack"]; ba = np.array(b64png(bs["src"]))[..., 3] > 200
    ys, xs = np.nonzero(ba)
    top = ys.min()
    # 오른쪽 위 모서리 — x + y 가 가장 큰 x 에 가까운 · y 가 작은 점 (오른쪽 위로 가장 튀어나온 곳)
    score = xs - ys
    k = int(np.argmax(score))
    books = dict(x=int(bs["x"] + xs[k]), y=int(bs["y"] + ys[k]), bb=[int(bs["x"] + xs.min()), int(bs["y"] + top), int(bs["x"] + xs.max()) + 1, int(bs["y"] + ys.max()) + 1])
    books["bx"], books["by"] = books["x"] + BADGE_DX, books["y"] + BADGE_DY      # 표식 가운데 — 맨 위 책의 오른쪽 위 모서리에 걸치게
    for k2 in ("base", "items", "props", "vig", "light"):
        imgs[k2].save(OUT + f"{k2}.png", optimize=True)
    full.save(OUT + "_editor_full.png")
    geo = dict(size=[DW, DH], light=light, groups=groups, scroll=scroll, books=books, hit=rle_rows(lab),
               zoom=dict(m=scroll_axes(np.array(imgs["base"]).astype(int), scroll)), src=os.path.basename(layout_path))
    json.dump(geo, open(OUT + "geo.json", "w", encoding="utf-8"), ensure_ascii=False)
    print("묶음", [(g["k"], g["bb"]) for g in groups])
    print("두루마리", scroll, "책 더미 오른쪽 위", books)
    print("hit 글자 수", len(geo["hit"]), "· 파일", {k: os.path.getsize(OUT + f"{k}.png") for k in ("base", "items", "props", "vig", "light")})
    return geo


if __name__ == "__main__":
    build(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else EDITOR)
