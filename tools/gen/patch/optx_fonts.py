"""오프닝 글 글꼴 조각 (1010) — OpTxSerif(나눔명조 ExtraBold) · OpTxSans(고운돋움) · OpTxSerifEn(EB Garamond ExtraBold · 영어판)
를 optx_block.js 의 글자만 남겨 optx_fonts.css 로.

    npm i @fontsource/nanum-myeongjo @fontsource/gowun-dodum @fontsource/eb-garamond         (아무 폴더에서)
    python tools/gen/patch/optx_fonts.py <그 폴더>/node_modules/@fontsource
    python tools/gen/patch/apply_optx.py game.html

· 명조는 인트로 · 날짜 둘(intro · date · winter), 나머지 장면은 고운돋움 — fontsource 의 글자 묶음(woff2)마다 쓰는 글자만 남겨 unicode-range 로 나눈다
· 영어판(SC_EN)은 같은 세 장면이 EB Garamond(OpTxSerifEn — 한국어 장면의 숫자 · 문장부호가 바뀌지 않게 다른 이름), 나머지는 고운돋움의 라틴 글자(OpTxSans 에 더한다)
"""
import json, glob, base64, io, re, os, sys
from fontTools.ttLib import TTFont
from fontTools import subset
HERE = os.path.dirname(os.path.abspath(__file__)) + "/"
NPM = sys.argv[1] if len(sys.argv) > 1 else "node_modules/@fontsource"
js = open(HERE + "optx_block.js", encoding="utf-8").read()
# SC 안의 t:[…] 글만 모은다
texts = re.findall(r't:\[([^\]]*)\]', js)
serif_scenes, all_lines = {"intro", "date", "winter"}, []
def scenes(block):
    out = {}
    for m in re.finditer(r'\n    (\w+): \{ms:(.*?)(?=\n    \w+: \{ms:|\n  \};)', block, re.S):
        name, body = m.group(1), m.group(2)
        out[name] = "".join("".join(re.findall(r'"([^"]*)"', t)) for t in re.findall(r't:\[([^\]]*)\]', body))
    return out
a, b = js.index("  const SC = {"), js.index("  const SC_EN = {")
sc_text, sc_en = scenes(js[a:b]), scenes(js[b:js.index("  const SCX = ")])
print({k: len(v) for k, v in sc_text.items()}, {k: len(v) for k, v in sc_en.items()})
serif = sorted(set("".join(v for k, v in sc_text.items() if k in serif_scenes)) - {" "}) + [" "]
sans = sorted(set("".join(v for k, v in list(sc_text.items()) + list(sc_en.items()) if k not in serif_scenes)) - {" "}) + [" "]
serif_en = sorted(set("".join(v for k, v in sc_en.items() if k in serif_scenes)) - {" "}) + [" "]
def sub_font(font, cps):
    opt = subset.Options(); opt.flavor = "woff2"; opt.layout_features = ["kern"]; opt.name_IDs = ["*"]; opt.notdef_outline = False; opt.hinting = False; opt.desubroutinize = True
    s = subset.Subsetter(opt); s.populate(unicodes=cps); s.subset(font)
    buf = io.BytesIO(); font.flavor = "woff2"; font.save(buf); return buf.getvalue()
def urange(cps):
    cps = sorted(cps); out = []; i = 0
    while i < len(cps):
        j = i
        while j + 1 < len(cps) and cps[j + 1] == cps[j] + 1: j += 1
        out.append(f"U+{cps[i]:X}" if i == j else f"U+{cps[i]:X}-{cps[j]:X}"); i = j + 1
    return ",".join(out)
rules = []; total = 0
for fam_css, fam, weight, need in [("OpTxSerif", "nanum-myeongjo", 800, serif), ("OpTxSans", "gowun-dodum", 400, sans), ("OpTxSerifEn", "eb-garamond", 800, serif_en)]:
    left = set(ord(c) for c in need); size = 0
    files = sorted(glob.glob(f"{NPM}/{fam}/files/{fam}-*-{weight}-normal.woff2"))
    if fam_css != "OpTxSerif":   # 영어판 글자는 latin 묶음 한 곳에서 — 고운돋움은 한글 묶음에도 라틴 글자가 흩어져 있어, 나뉘면 글자 사이 커닝이 빠진다
        files.sort(key=lambda f: (0 if f"{fam}-latin-{weight}" in f else 1, f))
    for f in files:
        cm = TTFont(f).getBestCmap(); have = left & set(cm)
        if not have: continue
        data = sub_font(TTFont(f, recalcTimestamp=False), sorted(have)); left -= have; size += len(data)
        rules.append(f'@font-face{{font-family:"{fam_css}";font-weight:{weight};font-display:block;src:url(data:font/woff2;base64,{base64.b64encode(data).decode()}) format("woff2");unicode-range:{urange(have)}}}')
    print(fam_css, "glyph chars", len(need), "bytes", size, "missing", "".join(chr(c) for c in sorted(left - {32})))
    total += size
open(HERE + "optx_fonts.css", "w").write("\n".join(rules))
print("rules", len(rules), "total", total, "css chars", sum(len(r) for r in rules))
