"""얼굴 프로필을 전투 스프라이트에서 다시 찍는다 (0929).
    python tools/faces_from_sprites.py            # assets/face_img/<직업>.webp 를 덮어쓴다
· 새로 다듬은 전투 스프라이트(assets/spr_x_img/<직업>.png.js)의 대기(idle) 첫 장에서 머리 · 어깨를 잘라 낸다.
· 얼굴 크기 맞춤 (0929) — 눈 크기를 기준으로 맞춘다. EYES 에 적은 두 눈의 가로 위치 · 눈높이(대기 첫 장 256px 기준)로
  두 눈 사이가 늘 같은 비율이 되게 자를 크기를 정하고(46px × 눈 사이 / 17, 38~60px — 얼굴만), 눈이 위에서 62% 에 오게 한다.
  4배 NEAREST 로 키운 뒤 잘라 144×144 로 줄인다. EYES 에 없는 직업은 머리 꼭대기 기준 72×72 로 자른다.
· 머리색은 원본 그대로 (학생마다 바꾸지 않는다). 예전 sprites/faces.py(face_src 원화)는 더 이상 쓰지 않는다.
· 다 찍은 뒤 game.html 의 FACE_IMG ?v= 를 새 파일 해시로 고친다."""
import base64, hashlib, io, json, os, re
import numpy as np
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SZ, DY = 72, 10            # 자르는 크기 · 머리 꼭대기에서 위로 남길 여백(-4) 다음 아래로 내리는 양
ADJ = {}                   # 직업별 미세 조정 {"bard": [dx, dy]} (EYES 없는 직업만)
D0, EYE_Y, FACE_BASE = 17.0, .62, 46   # 얼굴만 (0929) — 몸통이 거의 안 들어오게
EYES = {"archer": [127.5, 148, 106], "bard": [129, 149, 107.5], "darkpriest": [123.7, 142.8, 110], "druid": [132, 150.5, 106.7], "enchanter": [129, 147.5, 110], "forcemage": [128.5, 145, 116.7], "gunner": [134.5, 150.5, 109], "monk": [138.8, 155.5, 115], "ninja": [138, 154, 119], "paladin": [122, 138.5, 107.5], "priest": [124.5, 141, 109], "rogue": [128.8, 146.3, 115.8], "spellsword": [134, 150, 117.5], "sword": [126.8, 146.8, 111.7], "timemage": [128.7, 147.8, 111.7], "wizard": [126.3, 143.8, 121.7]}   # 직업: [왼눈 x, 오른눈 x, 눈높이 y]
src = open(os.path.join(ROOT, "game.html"), encoding="utf-8", newline="").read()
face = re.search(r'const FACE_IMG=(\{.*?\});', src)
jobs = list(json.loads(face.group(1)).keys())
paths = {}
for j in jobs:
    m = re.search(r'SPR_META\.%s=(\[\[.*?\]\]);' % j, src)
    js = os.path.join(ROOT, "assets", "spr_x_img", j + ".png.js")
    if not m or not os.path.exists(js):
        print("건너뜀 —", j); continue
    rect = json.loads(m.group(1))[0][0]["rect"]
    b64 = re.search(r'base64,([A-Za-z0-9+/=]+)', open(js, encoding="utf-8").read()).group(1)
    sheet = Image.open(io.BytesIO(base64.b64decode(b64))).convert("RGBA")
    fr = sheet.crop((rect[0], rect[1], rect[0] + rect[2], rect[1] + rect[3]))
    if j in EYES:
        lx, rx, ey = EYES[j]; sz = max(38, min(60, FACE_BASE * (rx - lx) / D0)); cx = (lx + rx) / 2
        x0, y0 = cx - sz / 2, ey - sz * EYE_Y
        big = fr.resize((fr.width * 4, fr.height * 4), Image.NEAREST)
        out = big.crop((round(x0 * 4), round(y0 * 4), round((x0 + sz) * 4), round((y0 + sz) * 4))).resize((SZ * 2, SZ * 2), Image.LANCZOS)
        p = os.path.join(ROOT, "assets", "face_img", j + ".webp")
        out.save(p, lossless=True, method=6)
        paths[j] = f"assets/face_img/{j}.webp?v={hashlib.sha1(open(p, 'rb').read()).hexdigest()[:8]}"
        print(j, "눈 기준", round(sz, 1), "px"); continue
    a = np.array(fr)[..., 3] > 40
    rows = np.where(a.sum(1) >= 6)[0]; top, bot = rows[0], rows[-1]
    band = a[top:top + int((bot - top) * .45)]
    cols = np.where(band.sum(0) >= 3)[0]; cx = (cols[0] + cols[-1]) / 2
    dx, dy = ADJ.get(j, [0, 0])
    x0 = int(round(cx - SZ / 2 + dx)); y0 = int(top - 4 + DY + dy)
    out = fr.crop((x0, y0, x0 + SZ, y0 + SZ)).resize((SZ * 2, SZ * 2), Image.NEAREST)
    p = os.path.join(ROOT, "assets", "face_img", j + ".webp")
    out.save(p, lossless=True, method=6)
    v = hashlib.sha1(open(p, "rb").read()).hexdigest()[:8]
    paths[j] = f"assets/face_img/{j}.webp?v={v}"
    print(j, os.path.getsize(p), "bytes")
new = "const FACE_IMG=" + json.dumps({k: paths.get(k, v) for k, v in json.loads(face.group(1)).items()}, separators=(",", ":")) + ";"
src = src[:face.start()] + new + src[face.end():]
open(os.path.join(ROOT, "game.html"), "w", encoding="utf-8", newline="").write(src)
print("FACE_IMG 갱신")
