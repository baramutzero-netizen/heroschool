"""일본어 글꼴 (1014) — 일본어판에서 게임 글꼴 이름에 일본어 글자를 더하는 조각 글꼴을 만든다.

    python tools/gen/fonts/ja_fonts.py FONTSRC        (저장소 맨 위에서 · pip: fonttools brotli)

FONTSRC (저장소 밖 폴더) 에 받아 둘 원본:
  fusion-pixel-12px-proportional-ja.ttf   github.com/TakWolf/fusion-pixel-font/releases — fusion-pixel-font-12px-proportional-ttf-v<판>.zip
  fusion-pixel-12px-monospaced-ja.ttf     같은 곳 — fusion-pixel-font-12px-monospaced-ttf-v<판>.zip
  MochiyPopOne-Regular.ttf                github.com/google/fonts — ofl/mochiypopone/MochiyPopOne-Regular.ttf (+ OFL.txt → MochiyPopOne-OFL.txt)
  ShipporiMinchoB1-ExtraBold.ttf          github.com/google/fonts — ofl/shipporiminchob1/ (+ OFL.txt → ShipporiMinchoB1-OFL.txt)
  KiwiMaru-Regular.ttf                    github.com/google/fonts — ofl/kiwimaru/ (+ OFL.txt → KiwiMaru-OFL.txt)
  (Fusion 의 OFL.txt 와 LICENSES/ 폴더도 zip 에서 같이 풀어 둔다 — 라이선스 파일을 만들 때 읽는다)

만드는 것:
  assets/fonts/ja/ja-pixel.woff2       물마루 자리 — Fusion Pixel 12px 비례폭 (ja) · JIS X 0208 전부(한자 6,355 · 가나 · 기호) + 라틴
  assets/fonts/ja/ja-pixel-mono.woff2  물마루 Mono 자리 — 반각 글자(라틴 · 기호)는 Fusion Pixel 12px 고정폭 (ja) 의 6px 칸,
                                       숫자 0 ~ 9 · 가나 · 전각 기호는 비례폭 판의 것 (숫자 폭은 둘 다 6px — 본문 숫자와 같은 높이 9px).
                                       한자는 넣지 않는다 (게임 CSS 가 늘 '물마루 Mono, 물마루' 차례라 한자는 물마루 자리 글꼴이 받는다)
  assets/fonts/ja/ja-boast.woff2       허세 말풍선(HS봄바람체) 자리 — Mochiy Pop One · 가나 · 기호 · 라틴 + 번역 표에 쓰인 한자
  assets/fonts/ja/ja-op-serif.woff2    오프닝 캔버스 글(OPTX) 명조 — Shippori Mincho B1 ExtraBold (OpTxSerifJa · 굵기 800)
  assets/fonts/ja/ja-op-sans.woff2     오프닝 캔버스 글 돋움 — Kiwi Maru (OpTxSansJa) · 둘 다 optx_block.js 의 SC_JA 글자만
  assets/fonts/ja/*-LICENSE.txt        라이선스 (SIL OFL 1.1 — Fusion 은 Ark Pixel · Cubic 11(M+) · Galmuri 고지를 이어 붙인다)
  tools/i18n/ja_fonts.css              @font-face — 게임 글꼴 이름(Mulmaru · Mulmaru Mono · HsBombaram21) 그대로, 일본어판에서만 붙는다
                                       (i18n_build.py 가 빌드 맨 끝 — lateFonts 뒤 — 에 넣어 원래 글꼴보다 앞선다 · 한글은 원래 글꼴 그대로)
세 글꼴 모두 일본어 번역 표(tools/i18n/ja.json · ja/*.json)의 글자를 더 넣는다 — 표에 새 글자가 생기면 다시 돌린다
(빌드가 '일본어 글꼴에 없는 글자 N' 으로 알려 준다).
세로 값은 원래 글꼴과 같게 — 줄 높이 · 글자 자리가 한국어판과 같다. 도트 둘은 물마루(위 10 · 아래 2 · 줄 간격 4px), 허세는 봄바람체의 줄 상자(1.2em)에
가나 · 한자 가운데가 한글 가운데와 같은 높이에 오게 (위 0.876 · 아래 0.324em).
"""
import base64, glob, hashlib, io, json, os, re, sys
from fontTools.ttLib import TTFont
from fontTools import subset

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "assets", "fonts", "ja")
CSS_OUT = os.path.join(ROOT, "tools", "i18n", "ja_fonts.css")
FEATURES = ["kern", "palt", "locl", "ccmp", "liga", "calt", "mark", "mkmk"]


def jis(rows):
    """JIS X 0208 의 구(區) — 1 ~ 8 기호 · 영숫자 · 가나 · 그리스 · 키릴 · 괘선, 16 ~ 47 제1수준 한자, 48 ~ 84 제2수준 한자"""
    out = []
    for r in rows:
        for c in range(1, 95):
            try:
                ch = bytes([0xA0 + r, 0xA0 + c]).decode("euc_jp")
            except UnicodeDecodeError:
                continue
            if len(ch) == 1:
                out.append(ch)
    return out


def rng(a, b):
    return [chr(c) for c in range(a, b + 1)]


BASE = (rng(0x20, 0x7E) + rng(0xA0, 0xFF) + rng(0x2010, 0x2027) + rng(0x2030, 0x203E) + rng(0x3000, 0x303F)
        + rng(0x3041, 0x3096) + rng(0x3099, 0x30FF) + rng(0xFF01, 0xFF5E))
SYM = jis(range(1, 9))
L1, L2 = jis(range(16, 48)), jis(range(48, 85))
JOYO = list(open(os.path.join(HERE, "joyo2136.txt"), encoding="utf-8").read().strip())
HAN = re.compile(r"[㐀-䶿一-鿿豈-﫿]")
HANGUL = re.compile(r"[ᄀ-ᇿ㄰-㆏가-힯]")


def table_chars():
    """일본어 번역 표의 값에 쓰인 글자 (없으면 빈 글)"""
    files = [os.path.join(ROOT, "tools", "i18n", "ja.json")] + sorted(glob.glob(os.path.join(ROOT, "tools", "i18n", "ja", "*.json")))
    s = []
    for p in files:
        if os.path.exists(p):
            for k, v in json.load(open(p, encoding="utf-8")).items():
                if not k.startswith("_") and isinstance(v, str):
                    s.append(v)
    return set("".join(s)) - set("\n\r\t")


def optx_chars():
    """오프닝 캔버스 글 — tools/gen/patch/optx_block.js 의 SC_JA 안 글(따옴표 글)의 글자"""
    p = os.path.join(ROOT, "tools", "gen", "patch", "optx_block.js")
    s = open(p, encoding="utf-8").read()
    i = s.find("const SC_JA = {")
    j = s.find("\n  };", i)
    if i < 0 or j < 0:
        return set()
    body = s[i:j]
    return set("".join(re.findall(r'"([^"\\]*)"', body))) | set("0123456789")


def cut(path, chars, keep_bitmaps=False):
    f = TTFont(path, recalcTimestamp=False)                # 같은 원본 · 같은 글자면 같은 파일 (주소의 ?v= 가 그대로)
    o = subset.Options()
    o.layout_features = FEATURES
    o.name_IDs = ["*"]
    o.name_languages = ["*"]
    o.notdef_outline = True
    o.hinting = False
    o.desubroutinize = True
    o.drop_tables += ["FFTM", "BDF ", "vhea", "vmtx", "VORG", "EBDT", "EBLC", "EBSC"]
    s = subset.Subsetter(o)
    s.populate(text="".join(sorted(set(chars))))
    s.subset(f)
    for t in ("hdmx", "VDMX", "LTSH", "kern", "gasp"):
        if t in f:
            del f[t]
    return f


def metrics(f, asc, desc, gap, typo_gap, use_typo):
    """세로 값 (글꼴 단위) — hhea · OS/2 typo · win"""
    hh, o2 = f["hhea"], f["OS/2"]
    hh.ascent, hh.descent, hh.lineGap = asc, -desc, gap
    o2.sTypoAscender, o2.sTypoDescender, o2.sTypoLineGap = asc, -desc, typo_gap
    o2.usWinAscent, o2.usWinDescent = asc, desc
    o2.fsSelection = (o2.fsSelection & ~((1 << 0) | (1 << 5))) | (1 << 6)     # REGULAR — 기울임 · 굵게 표시는 끈다
    if use_typo:
        if o2.version < 4:
            o2.version = 4
        o2.fsSelection |= 1 << 7
    else:
        o2.fsSelection &= ~(1 << 7)


def rename(f, family):
    for rec in f["name"].names:
        if rec.nameID in (1, 4, 16, 18):
            rec.string = family
        elif rec.nameID == 6:
            rec.string = family.replace(" ", "")
        elif rec.nameID == 3:
            rec.string = family.replace(" ", "") + "-1014"


def woff2(f):
    f.flavor = "woff2"
    b = io.BytesIO()
    f.save(b)
    return b.getvalue()


def urange(cps):
    """unicode-range — 한자(CJK 통합 · 확장 A · 호환)는 블록째, 나머지는 실제 글자만 (없는 기호는 원래 글꼴이 받게)"""
    cps = sorted(c for c in cps if c >= 0x20)
    blocks = [(0x3400, 0x4DBF), (0x4E00, 0x9FFF), (0xF900, 0xFAFF)]
    out, rest = [], []
    for a, b in blocks:
        if any(a <= c <= b for c in cps):
            out.append((a, b))
    rest = [c for c in cps if not any(a <= c <= b for a, b in blocks)]
    i = 0
    while i < len(rest):
        j = i
        while j + 1 < len(rest) and rest[j + 1] == rest[j] + 1:
            j += 1
        out.append((rest[i], rest[j]))
        i = j + 1
    out.sort()
    return ",".join(("U+%X" % a) if a == b else ("U+%X-%X" % (a, b)) for a, b in out)


def take_glyphs(dst, src, cps):
    """src 글꼴의 글자 모양 · 폭을 dst 의 같은 글자 자리에 옮긴다 (둘 다 1200 단위 · 같은 12px 칸). 부품 글리프는 풀어서"""
    from fontTools.pens.recordingPen import DecomposingRecordingPen
    from fontTools.pens.ttGlyphPen import TTGlyphPen
    cm_d, cm_s, gs = dst.getBestCmap(), src.getBestCmap(), src.getGlyphSet()
    for cp in cps:
        a, b = cm_d.get(cp), cm_s.get(cp)
        if not a or not b:
            continue
        rec = DecomposingRecordingPen(gs)
        gs[b].draw(rec)
        pen = TTGlyphPen(None)
        rec.replay(pen)
        dst["glyf"][a] = pen.glyph()
        dst["hmtx"][a] = src["hmtx"][b]


def license_text(src_dir, name, extra=()):
    parts = []
    for p in [os.path.join(src_dir, name)] + list(extra):
        if os.path.exists(p):
            parts.append(open(p, encoding="utf-8", errors="replace").read().strip())
    return parts


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    src = sys.argv[1]
    os.makedirs(OUT, exist_ok=True)
    tab = table_chars()
    tab_han = {c for c in tab if HAN.match(c)}
    tab_other = {c for c in tab if not HAN.match(c) and not HANGUL.match(c)}
    made, css, report = {}, [], []

    # 1) 물마루 자리 — Fusion Pixel 12px 비례폭
    need = set(BASE) | set(SYM) | set(L1) | set(L2) | set(JOYO) | tab_han | tab_other
    prop_path = os.path.join(src, "fusion-pixel-12px-proportional-ja.ttf")
    f = cut(prop_path, need)
    metrics(f, 1000, 200, 400, 0, False)                 # 물마루와 같다 (upm 1200 — 10 · 2 · 4px)
    rename(f, "HS JA Pixel")
    made["ja-pixel"] = (woff2(f), set(f.getBestCmap()), need)

    # 2) 물마루 Mono 자리 — 반각(U+3000 앞 · 숫자 빼고)은 Fusion Pixel 12px 고정폭, 숫자 · 가나 · 전각 기호는 비례폭 판의 것 (본문과 같은 모양 · 같은 칸)
    need_m = (set(BASE) | set(SYM) | tab_other) - {c for c in SYM if HAN.match(c)}
    f = cut(prop_path, need_m)
    mono = TTFont(os.path.join(src, "fusion-pixel-12px-monospaced-ja.ttf"), recalcTimestamp=False)
    take_glyphs(f, mono, [ord(c) for c in need_m if ord(c) < 0x3000 and not c.isdigit()])
    metrics(f, 1000, 200, 400, 0, False)
    rename(f, "HS JA Pixel Mono")
    made["ja-pixel-mono"] = (woff2(f), set(f.getBestCmap()), need_m)

    # 3) 허세 말풍선 — Mochiy Pop One · 한자는 번역 표에 쓰인 것만 (말풍선 글 = 표의 대사 · 스킬 이름 — 표가 바뀌면 다시 돌린다)
    need_b = set(BASE) | {c for c in SYM if not HAN.match(c)} | tab_han | tab_other
    f = cut(os.path.join(src, "MochiyPopOne-Regular.ttf"), need_b)
    metrics(f, 876, 324, 0, 0, True)                     # 봄바람체 줄 상자 1.2em · 가나 · 한자 가운데를 한글 가운데에
    rename(f, "HS JA Boast")
    made["ja-boast"] = (woff2(f), set(f.getBestCmap()), need_b)

    # 4) 오프닝 캔버스 글 (OPTX · SC_JA) — 세로 값은 원본 그대로 (캔버스가 글꼴 상자로 줄을 놓는다)
    op = optx_chars()
    for key, fn, fam_name in (("ja-op-serif", "ShipporiMinchoB1-ExtraBold.ttf", "HS JA Opening Serif"), ("ja-op-sans", "KiwiMaru-Regular.ttf", "HS JA Opening Sans")):
        f = cut(os.path.join(src, fn), op)
        rename(f, fam_name)
        made[key] = (woff2(f), set(f.getBestCmap()), op)

    fam = {"ja-pixel": "Mulmaru", "ja-pixel-mono": "Mulmaru Mono", "ja-boast": "HsBombaram21", "ja-op-serif": "OpTxSerifJa", "ja-op-sans": "OpTxSansJa"}
    weight = {"ja-op-serif": 800, "ja-op-sans": 400}
    for key, (data, cps, need) in made.items():
        p = os.path.join(OUT, key + ".woff2")
        old = open(p, "rb").read() if os.path.exists(p) else None
        if old != data:
            open(p, "wb").write(data)
        ver = hashlib.sha1(data).hexdigest()[:8]
        if key in weight:            # 오프닝 — 캔버스가 이 이름 · 굵기로 부른다 (unicode-range 없이)
            css.append('@font-face{font-family:"%s";font-weight:%d;src:url(assets/fonts/ja/%s.woff2?v=%s) format("woff2");font-display:block}'
                       % (fam[key], weight[key], key, ver))
        else:
            css.append('@font-face{font-family:"%s";src:url(assets/fonts/ja/%s.woff2?v=%s) format("woff2");unicode-range:%s;font-display:block}'
                       % (fam[key], key, ver, urange(cps - {ord(c) for c in "\n\r\t"})))
        miss = sorted(c for c in need if ord(c) not in cps and not HANGUL.match(c) and c not in " 　")
        report.append("%s %.0fKB · 글자 %d%s" % (key, len(data) / 1024, len(cps),
                      (" · 원본에 없음 %d (%s…)" % (len(miss), "".join(miss[:24]))) if miss else ""))

    lic_fusion = license_text(src, "OFL.txt", sorted(glob.glob(os.path.join(src, "LICENSES", "*", "*"))))
    with open(os.path.join(OUT, "FusionPixel-LICENSE.txt"), "w", encoding="utf-8", newline="\n") as fo:
        fo.write("ja-pixel.woff2 · ja-pixel-mono.woff2 — Fusion Pixel Font 12px (ja) 에서 글자를 골라 남기고 세로 값을 고친 것 (용사 학원 1014).\n"
                 "https://github.com/TakWolf/fusion-pixel-font — SIL Open Font License 1.1. 원본과 합친 글꼴들의 라이선스를 차례로 붙인다.\n\n")
        sep = "\n\n" + ("-" * 60) + "\n\n"
        fo.write((sep.join(lic_fusion) + "\n") if lic_fusion else "(OFL.txt 를 찾지 못했다 — FONTSRC 에 zip 의 OFL.txt · LICENSES/ 를 풀어 둔다)\n")
    mochiy_ofl = os.path.join(src, "MochiyPopOne-OFL.txt")
    with open(os.path.join(OUT, "MochiyPopOne-LICENSE.txt"), "w", encoding="utf-8", newline="\n") as fo:
        fo.write("ja-boast.woff2 — Mochiy Pop One 에서 글자를 골라 남기고 세로 값을 고친 것 (용사 학원 1014).\n"
                 "https://github.com/fontdasu/Mochiypop — SIL Open Font License 1.1 (아래 원문).\n\n")
        if os.path.exists(mochiy_ofl):
            fo.write(open(mochiy_ofl, encoding="utf-8").read().strip() + "\n")
        else:
            fo.write("(MochiyPopOne-OFL.txt 를 찾지 못했다 — google/fonts 의 ofl/mochiypopone/OFL.txt 를 FONTSRC 에 받아 둔다)\n")

    for key, src_name, out_name, url in (("ja-op-serif", "ShipporiMinchoB1-OFL.txt", "ShipporiMinchoB1-LICENSE.txt", "https://github.com/fontdasu/ShipporiMincho"),
                                         ("ja-op-sans", "KiwiMaru-OFL.txt", "KiwiMaru-LICENSE.txt", "https://github.com/Kiwi-KawagotoKajiru/Kiwi-Maru")):
        with open(os.path.join(OUT, out_name), "w", encoding="utf-8", newline="\n") as fo:
            fo.write("%s.woff2 — 오프닝 캔버스 글자만 골라 남긴 것 (용사 학원 1014).\n%s — SIL Open Font License 1.1 (아래 원문).\n\n" % (key, url))
            lp = os.path.join(src, src_name)
            fo.write((open(lp, encoding="utf-8").read().strip() + "\n") if os.path.exists(lp)
                     else "(%s 를 찾지 못했다 — google/fonts 의 OFL.txt 를 FONTSRC 에 받아 둔다)\n" % src_name)

    with open(CSS_OUT, "w", encoding="utf-8", newline="\n") as fo:
        fo.write("/* 일본어 글꼴 (1014) — tools/gen/fonts/ja_fonts.py 가 만든다 (손으로 고치지 않는다). 일본어판에서만 빌드 맨 끝(lateFonts 뒤)에 붙는다 */\n")
        fo.write("\n".join(css) + "\n")
    for r in report:
        print("ja_fonts:", r)
    print("ja_fonts: 번역 표 글자 %d (한자 %d) · %s · %s" % (len(tab), len(tab_han), os.path.relpath(CSS_OUT, ROOT), os.path.relpath(OUT, ROOT)))


if __name__ == "__main__":
    main()
