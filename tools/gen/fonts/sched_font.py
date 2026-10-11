"""스케줄 단추 글자 글꼴 (1011) — Jacquard 12 를 영문자만 남겨 자르고 game.html 의 @font-face 한 줄(HsSchedFont · data:)로 넣는다.

    python3 tools/gen/fonts/sched_font.py [game.html]     # 저장소 맨 위에서 · 있으면 바꿔 끼우고, 없으면 "Mulmaru Mono" @font-face 다음 줄에
원본: tools/gen/fonts/Jacquard12-latin.woff2 (Google Fonts Jacquard 12 · @fontsource/jacquard-12 의 latin 400)
  · Copyright 2023 The Soft Type Project Authors · SIL OFL 1.1 (Jacquard12-OFL.txt · 배포본은 assets/fonts/Jacquard12-OFL.txt)
글자: A–Z a–z 와 빈칸 (2.6KB). OS/2 의 win 높이를 typo(960 / 300)와 같게 바꾼다 — 윈도우 · 맥 · 리눅스가 같은 줄 높이를 써서
단추 안 기준선이 어디서나 같은 자리에 온다 (원래 win 은 1020 / 720 이라 윈도우에서만 6px 위로 뜰 수 있었다).
21칸/em — 42px(2배)에서 또렷하다. 사이드 단추(.side-sched) · 운영 안내 단추(.tg-schedbtn)가 쓴다 (CSS 는 game.html).
"""
import base64, io, os, re, sys
from fontTools import subset
from fontTools.ttLib import TTFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
SRC = os.path.join(HERE, "Jacquard12-latin.woff2")
TEXT = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz "
NOTE = ("/* 스케줄 단추 글자 (1011) — Jacquard 12 (The Soft Type Project · SIL OFL 1.1 · assets/fonts/Jacquard12-OFL.txt) · "
        "영문자만 · win 높이를 typo 와 맞춤 — tools/gen/fonts/sched_font.py 가 만든다 */")


def build():
    f = TTFont(SRC)
    opt = subset.Options()
    opt.layout_features = ["*"]
    opt.hinting = False
    opt.desubroutinize = True
    opt.flavor = "woff2"
    s = subset.Subsetter(opt)
    s.populate(text=TEXT)
    s.subset(f)
    os2, hh = f["OS/2"], f["hhea"]
    os2.usWinAscent, os2.usWinDescent = os2.sTypoAscender, -os2.sTypoDescender
    assert (hh.ascent, hh.descent) == (os2.sTypoAscender, os2.sTypoDescender), "hhea 와 typo 가 다르다 — 여기서 같이 맞춘다"
    b = io.BytesIO()
    f.flavor = "woff2"
    f.save(b)
    return b.getvalue()


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "game.html")
    data = build()
    line = ('@font-face{font-family:"HsSchedFont";src:url(data:font/woff2;base64,%s) format("woff2");font-display:block}   %s'
            % (base64.b64encode(data).decode(), NOTE))
    raw = open(path, encoding="utf-8", newline="").read()
    nl = "\r\n" if "\r\n" in raw else "\n"
    lines = raw.split(nl)
    hit = [i for i, t in enumerate(lines) if t.startswith('@font-face{font-family:"HsSchedFont"')]
    if hit:
        lines[hit[0]] = line
    else:
        at = [i for i, t in enumerate(lines) if t.startswith('@font-face{font-family:"Mulmaru Mono"')]
        if not at:
            sys.exit('멈춤 — "Mulmaru Mono" @font-face 줄을 못 찾았다')
        lines.insert(at[0] + 1, line)
    out = nl.join(lines)
    if out != raw:
        open(path, "w", encoding="utf-8", newline="").write(out)
    print("HsSchedFont %d B (base64 %d) → %s %s" % (len(data), len(line), os.path.relpath(path, ROOT), "바꿈" if out != raw else "그대로"))


if __name__ == "__main__":
    main()
