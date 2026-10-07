"""3판 미리보기 — 배치판과 같은 순서 · 같은 그림(2배)으로 합친다. 각도는 15도 배수만 (그 사이는 배치판의 도트 돌리기)."""
import json, numpy as np
from PIL import Image
import os
OUT3 = os.path.dirname(os.path.abspath(__file__)) + "/" + "out3/"
IN, SC = 13, 2

def pose(d, angle):
    sh = Image.open(OUT3 + d['file']).convert('RGBA')
    if d['kind'] == '2x': return sh, d['px'], d['py'], True
    k = 0
    if d['frames'] > 1:
        k = int(round(angle / d['step'])) % d['frames']
        assert abs(angle - round(angle / d['step']) * d['step']) < 1e-6, "15도 배수만"
    img = sh.crop((k * d['cw'], 0, (k + 1) * d['cw'], d['ch']))
    if d.get('shadow'):
        dx, dy, al = d['shadow']; a = np.array(img)
        out = np.zeros((a.shape[0] + dy, a.shape[1] + dx, 4), np.uint8)
        body = a[..., 3] == 255
        out[dy:dy + a.shape[0], dx:dx + a.shape[1]][body] = [24, 12, 8, al]
        base = Image.fromarray(out); top = Image.new('RGBA', base.size, (0, 0, 0, 0)); top.paste(img, (0, 0)); base.alpha_composite(top)
        img = base
    return img, d['px'], d['py'], False

def screen(base, layer):
    b = np.array(base).astype(float) / 255; t = np.array(layer).astype(float) / 255
    out = b.copy(); out[..., :3] = 1 - (1 - b[..., :3]) * (1 - t[..., :3] * t[..., 3:4])
    return Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8))

def vignette(W, H):
    yy, xx = np.mgrid[0:H, 0:W]
    v = (((xx - W * .42) / (W * .62)) ** 2 + ((yy - H * .48) / (H * .62)) ** 2)
    a = np.clip((v - 0.55) / 1.1, 0, 1)
    bands = np.digitize(a, [.12, .3, .5, .72])
    AL = np.round(np.array([0, 26, 52, 80, 110]) * .45).astype(int)
    edge = np.digitize(np.clip(a + 0.03, 0, 1), [.12, .3, .5, .72]) != bands
    b2 = np.where(edge & ((xx + yy) % 2 == 0), np.minimum(bands + 1, 4), bands)
    img = np.zeros((H, W, 4), np.uint8); img[..., :3] = (24, 12, 8); img[..., 3] = AL[b2]
    return Image.fromarray(img)

def frame9(W, H):
    src = Image.open(OUT3 + "frame_1x.png").convert('RGBA'); SW, SH = src.size; Cn = 24
    fw, fh = W + IN * 2, H + IN * 2
    out = Image.new('RGBA', (fw, fh), (0, 0, 0, 0))
    def run(box, dx, dy, length, horiz):
        seg = src.crop(box); p = 0; L = seg.width if horiz else seg.height
        while p < length:
            n = min(L, length - p)
            piece = seg.crop((0, 0, n, seg.height)) if horiz else seg.crop((0, 0, seg.width, n))
            out.paste(piece, (dx + p, dy) if horiz else (dx, dy + p)); p += n
    run((Cn, 0, SW - Cn, Cn), Cn, 0, fw - Cn * 2, True)
    run((Cn, SH - Cn, SW - Cn, SH), Cn, fh - Cn, fw - Cn * 2, True)
    run((0, Cn, Cn, SH - Cn), 0, Cn, fh - Cn * 2, False)
    run((SW - Cn, Cn, SW, SH - Cn), fw - Cn, Cn, fh - Cn * 2, False)
    for (sx, sy, dx, dy) in ((0, 0, 0, 0), (SW - Cn, 0, fw - Cn, 0), (0, SH - Cn, 0, fh - Cn), (SW - Cn, SH - Cn, fw - Cn, fh - Cn)):
        out.paste(src.crop((sx, sy, sx + Cn, sy + Cn)), (dx, dy))
    return out

def compose(layout, vig=True, frame=True, menu=True, pad=16):
    """menu=True 면 액자 밖 여백(pad, 게임 바탕색)까지 — 메뉴판이 액자 위 · 오른쪽으로 나온 자리"""
    kit = json.load(open(OUT3 + "props.json", encoding="utf-8"))
    W, H = layout['desk']
    desk = Image.open(OUT3 + "desk_bg.png").convert('RGBA').crop((0, 0, W, H)).resize((W * SC, H * SC), Image.NEAREST)
    lights = []
    def put(base, o, d):
        img, px, py, k2 = pose(d, o.get('angle', 0))
        if not k2: img = img.resize((img.width * SC, img.height * SC), Image.NEAREST)
        L = Image.new('RGBA', base.size, (0, 0, 0, 0)); L.paste(img, ((round(o['x']) - px) * SC, (round(o['y']) - py) * SC)); return L
    for o in layout['objects']:
        d = kit['objects'][o['id']]
        if d['blend'] == 'screen': lights.append((o, d)); continue
        desk.alpha_composite(put(desk, o, d))
    if vig: desk.alpha_composite(vignette(W, H).resize((W * SC, H * SC), Image.NEAREST))
    for o, d in lights: desk = screen(desk, put(desk, o, d))
    FW, FH = W + IN * 2, H + IN * 2
    P = pad if menu else 0
    out = Image.new('RGBA', ((FW + P * 2) * SC, (FH + P * 2) * SC), (0xf6, 0xf3, 0xe9, 255))
    fr = Image.new('RGBA', (FW * SC, FH * SC), (0, 0, 0, 255)); fr.alpha_composite(desk, (IN * SC, IN * SC))
    if frame: fr.alpha_composite(frame9(W, H).resize(fr.size, Image.NEAREST))
    out.alpha_composite(fr, (P * SC, P * SC))
    if menu:
        m = layout['menu']; k = m['screen'] / FW                         # 1배 한 칸 = CSS px
        x = P + FW + m['right'] / k - m['w'] / k; y = P - m['top'] / k; w, h = m['w'] / k, m['h'] / k
        mi = Image.open(OUT3 + "menu_ref.png").convert('RGBA').resize((round(w * SC), round(h * SC)), Image.LANCZOS)
        L = Image.new('RGBA', out.size, (0, 0, 0, 0)); L.paste(mi, (round(x * SC), round(y * SC))); out.alpha_composite(L)
    return out

if __name__ == "__main__":
    lay = json.load(open(OUT3 + "layout.json", encoding="utf-8"))
    compose(lay).save(OUT3 + "preview_framed_2x.png")
