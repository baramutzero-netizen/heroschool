"""영웅의 기상 원화 → 게임 그림 (1015 · 스타일리시 전투 체크포인트 ②)

    python3 tools/gen/heroic/heroic_art.py            # 저장소 맨 위에서

tools/herospirit/heroic-resolve-<직업>[-vN]/resolve-character.png · resolve-aura.png (직업마다 고른 판 — PICK)
→ assets/heroic/<직업>-character.webp · <직업>-aura.webp (WebP 품질 90 · 사용자 1015: 'webp 90 으로 변환해서 적용' · 원래 크기 그대로 ·
  가운데에 놓아 정사각으로만 맞춘다) + game.html 의 HR_ART 한 줄(tools/gen/heroic/HR_ART.js.txt) (그림 주소 ?v=내용 해시 · 캐릭터 불투명 범위 bb · 앞쪽 입자 두 색 acc).
원화의 머리색은 직업 기본색 그대로 (사용자: 게임의 머리색은 실제로 하나).
"""
import hashlib, io, json, os, sys
import numpy as np
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SRC = os.path.join(ROOT, "tools", "herospirit")
OUT = os.path.join(ROOT, "assets", "heroic")
# 직업 → 원화 폴더 (사용자 1015: 시안이 여러 벌이면 가장 최신)
PICK = {"archer": "archer", "bard": "bard", "darkpriest": "darkpriest", "druid": "druid-v2", "enchanter": "enchanter",
        "forcemage": "forcemage", "gunner": "gunner", "monk": "monk-v2", "ninja": "ninja", "paladin": "paladin-v4",
        "priest": "priest", "rogue": "rogue", "spellsword": "spellsword-v6", "sword": "sword", "timemage": "timemage", "wizard": "wizard"}
# 앞쪽 입자 두 색 — 목업(mockups/heroic-resolve)에서 고른 일곱 직업은 그대로, 나머지는 하양 + 후광의 짙은 색(accents)
ACC_PICK = {"sword": ["#fff1bf", "#a8e7ff"], "wizard": ["#ffe39a", "#c9a2ff"], "priest": ["#fff1bf", "#a8e7ff"], "archer": ["#fff1bf", "#c8f5b0"],
            "rogue": ["#d7e2ff", "#7d9cff"], "darkpriest": ["#ffd0e0", "#ff6f9e"], "paladin": ["#fff1bf", "#a8e7ff"]}


def square(im):
    w, h = im.size
    n = max(w, h)
    c = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    c.paste(im, ((n - w) // 2, (n - h) // 2))
    return c


def webp(im, path):
    b = io.BytesIO()
    im.save(b, "WEBP", quality=90, method=6, exact=False)
    raw = b.getvalue()
    open(path, "wb").write(raw)
    return hashlib.sha1(raw).hexdigest()[:10], len(raw)


def accents(au):
    """앞쪽 반짝이 두 색 — 후광에서 밝은 쪽의 중간색(하양에 가깝게) · 가장 흔한 짙은 색(조금 밝게)"""
    a = np.asarray(au).reshape(-1, 4).astype(np.float32)
    a = a[a[:, 3] > 160][:, :3]
    if not len(a):
        return ["#fff1bf", "#a8e7ff"]
    lum = a @ np.array([.299, .587, .114], np.float32)
    hi = a[lum >= np.percentile(lum, 85)].mean(0)
    sat = a.max(1) - a.min(1)
    mid = a[(sat >= np.percentile(sat, 70))]
    c2 = mid.mean(0) if len(mid) else a.mean(0)
    c1 = hi * .55 + 255 * .45
    c2 = np.minimum(255, c2 * .7 + 255 * .3)
    return ["#%02x%02x%02x" % tuple(int(round(v)) for v in c) for c in (c1, c2)]


def main():
    os.makedirs(OUT, exist_ok=True)
    art, total = {}, 0
    for job, d in PICK.items():
        f = os.path.join(SRC, "heroic-resolve-" + d)
        ch = square(Image.open(os.path.join(f, "resolve-character.png")).convert("RGBA"))
        au = square(Image.open(os.path.join(f, "resolve-aura.png")).convert("RGBA"))
        al = np.asarray(ch)[:, :, 3]
        ys, xs = np.nonzero(al > 24)
        n = ch.size[0]
        bb = [round(float(xs.min()) / n, 4), round(float(ys.min()) / n, 4), round(float(xs.max() + 1) / n, 4), round(float(ys.max() + 1) / n, 4)]
        hc, nc = webp(ch, os.path.join(OUT, job + "-character.webp"))
        ha, na = webp(au, os.path.join(OUT, job + "-aura.webp"))
        total += nc + na
        art[job] = {"c": "assets/heroic/%s-character.webp?v=%s" % (job, hc), "a": "assets/heroic/%s-aura.webp?v=%s" % (job, ha),
                    "bb": bb, "acc": ACC_PICK.get(job) or ["#fff1bf", accents(au)[1]]}
        print("%-11s %-15s %4d px  character %4.0f KB · aura %4.0f KB  bb %s  acc %s" % (job, d, n, nc / 1024, na / 1024, bb, art[job]["acc"]))
    print("합계 %.1f MB" % (total / 1048576))
    line = "const HR_ART = " + json.dumps(art, ensure_ascii=False, separators=(",", ":")) + ";"
    open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "HR_ART.js.txt"), "w", encoding="utf-8").write(line + "\n")
    print("→ tools/gen/heroic/HR_ART.js.txt (game.html 의 const HR_ART 줄 — 그림을 바꾸면 이 줄로 갈아 끼운다)")


if __name__ == "__main__":
    main()
