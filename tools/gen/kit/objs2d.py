"""두루마리를 낱낱이 — 빈 두루마리 · 색 띠 · 띠 글자 · 빈 카드 · 아이콘 · 카드 글자 · 점선 · 서명 · 깃펜 · 남색 천 · 불빛.
모두 그림자 없이 몸만 (종이 위 그림자는 배치판이 돌린 모양을 따라 만든다). 돌려주는 것: (그림, 기준점) — 기준점 = 돌리는 중심이자 놓는 좌표."""
import numpy as np
from PIL import Image, ImageDraw
import scene2d as S
from scene2d import DT, CARD, COLS, DECK, CW, CH, PITCH, PARCH, C, new, rect, poly, text, P_
from px3d import OUT

def crop_pivot(img, pivot):
    bb = img.getbbox()
    return img.crop(bb), (pivot[0] - bb[0], pivot[1] - bb[1])

# ── 빈 두루마리 — 종이 + 두 축 (축 그림자는 3D 로 구운 그대로) ──
SC_W = len(COLS) * PITCH + 24; SC_H = 206
def blank_scroll():
    pad = 26
    L = new(SC_W + pad * 2, SC_H + pad * 2)
    L.alpha_composite(S.paper(SC_W, SC_H), (pad, pad))
    rimg, (rx, ry) = S.rollers_sprite(SC_W, SC_H)
    cx, cy = pad + SC_W / 2, pad + SC_H / 2
    L.alpha_composite(rimg, (int(round(cx - rx)), int(round(cy - ry + 5.6 * np.cos(S.TH)))))
    return crop_pivot(L, (int(cx), int(cy)))

# ── 색 띠 (글자 없이) ──
def ribbon(key):
    name, pal = CARD[key]
    L = new(60, 24); cx, y = 30, 4
    x0, x1 = cx - 20, cx + 20
    poly(L, [(x0 - 6, y + 2), (x0 + 2, y + 2), (x0 + 2, y + 14), (x0 - 6, y + 14), (x0 - 2, y + 8)], pal[1])
    poly(L, [(x1 + 6, y + 2), (x1 - 2, y + 2), (x1 - 2, y + 14), (x1 + 6, y + 14), (x1 + 2, y + 8)], pal[1])
    poly(L, [(x0, y + 13), (x0 + 3, y + 16), (x0 + 3, y + 13)], pal[0]); poly(L, [(x1, y + 13), (x1 - 3, y + 16), (x1 - 3, y + 13)], pal[0])
    rect(L, x0, y, x1, y + 13, pal[2]); rect(L, x0, y, x1, y, pal[3]); rect(L, x0, y + 1, x1, y + 1, pal[3])
    rect(L, x0, y + 13, x1, y + 13, pal[1])
    return crop_pivot(L, (cx, y + 7))

def _text_sprite(s, font, fg, shadow):
    tw = int(font.getlength(s)) + 4
    L = new(tw + 4, 16)
    text(L, (3, 2), s, font, shadow); text(L, (2, 1), s, font, fg)
    bb = L.getbbox(); L = L.crop(bb)
    return L, (L.width // 2, L.height // 2)
def ribbon_label(key):
    name, pal = CARD[key]
    return _text_sprite(name, DT.F9, C('fffaf0'), pal[0])
def card_text(label, key):
    name, pal = CARD[key]
    return _text_sprite(label, DT.F7, C('fffaf0'), pal[0])

# ── 빈 카드 (그림 칸만, 아이콘 · 글자 없이) ──
def card_blank(key):
    name, pal = CARD[key]
    L = new(CW, CH); x, y = 0, 0
    rect(L, x, y + CH - 1, x + CW - 1, y + CH - 1, pal[0])
    rect(L, x, y, x + CW - 1, y + CH - 2, pal[2])
    rect(L, x, y, x + CW - 1, y, pal[3]); rect(L, x, y, x, y + CH - 2, pal[3])
    rect(L, x + CW - 1, y + 1, x + CW - 1, y + CH - 2, pal[1])
    px0, py0, px1, py1 = x + 3, y + 3, x + CW - 4, y + 22
    rect(L, px0, py0, px1, py1, pal[4]); rect(L, px0, py0, px1, py0, pal[1]); rect(L, px0, py0, px0, py1, pal[1])
    rect(L, px0 + 1, py1, px1, py1, pal[3]); rect(L, px1, py0 + 1, px1, py1, pal[3])
    return L, (CW // 2, CH // 2)

def icon(kind):
    im = DT.icon(kind)
    return crop_pivot(im, (8, 7))

def separator(h=160):
    L = new(1, h)
    for y in range(h):
        if (y // 3) % 4 != 3: P_(L, 0, y, PARCH[1])
    return L, (0, h // 2)

def signature():
    L = new(110, 30)
    S.signature(L, 8, 12)
    return crop_pivot(L, (55, 15))

def quill():
    """깃펜 — 구운 그림자를 빼고 몸만. 기준점 = 펜촉"""
    img, nib = S.quill(length=92)
    a = np.array(img)
    body = (a[..., 3] == 255)
    a[~body] = 0
    out = Image.fromarray(a)
    return crop_pivot(out, nib)

def runner():
    img = S.runner()
    return img, (img.width // 2, img.height // 2)

def glow(rad, **kw):
    img = S.glow(rad, **kw)
    return img, (rad, img.height // 2)

# ── 기본 배치 — 예전 두루마리 그림과 같은 자리 (책상 1배 좌표) ──
SCROLL_C = (236, 230)
def scroll_layout():
    """[(id, x, y)] — 기준점 좌표"""
    out = [('scroll', SCROLL_C[0], SCROLL_C[1])]
    left, top = SCROLL_C[0] - SC_W // 2, SCROLL_C[1] - SC_H // 2
    colx = [left + 12 + PITCH // 2 + PITCH * i for i in range(len(COLS))]
    tab_y = top + 12; card_y = [top + 36, top + 82, top + 128]
    sep_top, sep_bot = tab_y - 2, card_y[-1] + CH + 4
    for i in range(1, len(COLS)):
        out.append(('sep_line', colx[i] - PITCH // 2, (sep_top + sep_bot) // 2))
    for i, key in enumerate(COLS):
        out.append((f'ribbon_{key}', colx[i], tab_y + 7))
        name, pal = CARD[key]
        out.append((f'label_{key}', colx[i], tab_y + 8))
        for j, (label, kind) in enumerate(DECK[key]):
            cy = card_y[j]
            out.append((f'card_{key}', colx[i], cy + CH // 2))
            out.append((f'icon_{kind}', colx[i], cy + 3 + 3 + 7))
            out.append((text_id(label, key), colx[i], cy + 25 + 5))
    out.append(('signature', left + 24 + 47, top + SC_H - 20 + 3))
    return out

def text_id(label, key):
    base = {'대련': 'spar', '모의전': 'mock', '휴식': 'rest', '기초 체력': 'basic', '고강도 단련': 'heavy', '전술 연구': 'tact', '진형 훈련': 'form',
            '명상': 'medit', '심층 명상': 'deep', '자율 훈련': 'free', '실전 타격': 'strike', '원정 파견': 'exped'}[label]
    return f'text_{base}' + (f'_{key}' if base == 'rest' else '')
