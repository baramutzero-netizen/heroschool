"""학생 명부 책 (1009) — 가로 넓은 화면에서 책상의 펼친 책 · 메뉴의 '학생 명부' · '팀 편성'을 누르면 뜨는 책 팝업을 game.html 에 넣는다.
몇 번을 돌려도 같은 결과 (이전 블록은 지우고 다시 넣는다).

    python tools/gen/patch/apply_roster.py game.html [--force]   (저장소 맨 위에서 — 목업은 game.html 옆 mockups/student-roster 에서)

· 책 — mockups/student-roster 목업 그대로. 목업 원본 src/roster_tpl.html 의 CORE_CSS(모양) · CORE_HTML(뼈대)을 그대로 가져와
  roster_block.css(게임에서만 — 덮개 · 스킬 강화 · 유물 해제 단추)와 함께 그림자 DOM 안에 넣는다. 책을 다시 디자인하면 목업을 고치고 이 스크립트를 다시 돌린다
· 그림 — art/book.png(책) · art/ribbon.png(책갈피 끈)을 무손실 WebP data: 로 ROSTER_ART 에 넣고, wrap.py · wrap_site.py 의 split_assets 가 assets/roster_art/ 로 뺀다
· 배치 — art/roster_layout.json (학생 명부 배치판에서 저장한 것) → RB_LAYOUT. 배치를 바꿨으면 그 파일을 덮어쓰고 다시 돌린다
· 코드 — roster_block.js 를 넣고 render() 의 앞 · 끝에 한 줄씩:
  - 앞: 가로 넓은 화면(townMode)에서 학생 명부 · 팀 편성(UI.view roster · team)으로 가려 하면 책을 연다 (화면은 원래 보던 곳 그대로)
  - 끝: 책에서 연 게임 팝업(이름 변경 · 스킬 강화 · 스킬 임의로 강화)이 끝나면 책을 다시 그린다
· 블록(/* ROSTERBK_START … */ ~ /* ROSTERBK_END */)은 돌릴 때마다 통째로 갈아 끼운다 — blockguard 가 game.html 쪽을 직접 고친 걸 막는다
"""
import base64, io, json, os, re, sys
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__)) + "/"
JS_START, JS_END = "/* ROSTERBK_START", "/* ROSTERBK_END */"
JS_ANCHOR = "/* ============================================================\n   시즌 전환\n   ============================================================ */\n"

EDITS = [
    # render() 맨 앞 — 가로 넓은 화면의 학생 명부 · 팀 편성은 책으로
    ("function render(){\n  { const fb = $(\"#btnFeed\");\n",
     "function render(){\n  if(window.RBK) RBK.intercept();   // 1009 — 가로 넓은 화면: 학생 명부 · 팀 편성은 책 팝업 (apply_roster)\n  { const fb = $(\"#btnFeed\");\n"),
    # render() 맨 끝 — 책에서 연 팝업이 끝나면 책을 다시 그린다
    ("  audBase(S && PHASES[S.phase] ? S.phase : null);\n}\n/* 학원 이름 (1007)",
     "  audBase(S && PHASES[S.phase] ? S.phase : null);\n  if(window.RBK) RBK.after();   // 1009 — 책에서 연 이름 변경 · 스킬 강화 팝업이 끝나면 책을 다시 그린다 (apply_roster)\n}\n/* 학원 이름 (1007)"),
]


def b64(data):
    return base64.b64encode(data).decode()


def webp_lossless(img):
    b = io.BytesIO(); img.save(b, "WEBP", lossless=True, quality=100, method=6)
    return b.getvalue()


def section(t, a, b):
    i = t.index(a) + len(a)
    return t[i:t.index(b, i)]


def mockup(root):
    """목업 원본에서 책의 CSS · HTML · 그림 · 배치"""
    M = os.path.join(root, "mockups", "student-roster")
    tpl = open(os.path.join(M, "src", "roster_tpl.html"), encoding="utf-8").read().replace("\r\n", "\n")
    css = section(tpl, "/*@@CORE_CSS*/", "/*@@/CORE_CSS*/")
    css = css.replace("url({{BOOK}})", "var(--rb-book)").replace("url({{RIBBON}})", "var(--rb-ribbon)").replace("url({{DESK}})", "none")
    html = section(tpl, "<!--@@CORE_HTML-->", "<!--@@/CORE_HTML-->").strip("\n")
    for s, what in ((css, "CSS"), (html, "HTML")):
        if "{{" in s:
            raise RuntimeError("목업 %s 에 채우지 못한 자리표가 남았다: %s" % (what, re.findall(r"\{\{\w+\}\}", s)))
    art = {k: "data:image/webp;base64," + b64(webp_lossless(Image.open(os.path.join(M, "art", k + ".png")).convert("RGBA"))) for k in ("book", "ribbon")}
    lay = {}
    p = os.path.join(M, "art", "roster_layout.json")
    if os.path.exists(p):
        L = json.load(open(p, encoding="utf-8"))
        lay = {"items": L.get("items") or {},
               "face": {"jobs": {j: {k: v[k] for k in ("scale", "x", "y") if k in v} for j, v in ((L.get("face") or {}).get("jobs") or {}).items() if isinstance(v, dict)}}}
    return css, html, art, lay


def js_str(s):
    """JS 문자열 — <script> 안이라 '</' 를 끊어 둔다"""
    return json.dumps(s, ensure_ascii=False).replace("</", "<\\/")


def sub1(src, old, new):
    if new in src:
        return src
    n = src.count(old)
    if n != 1:
        raise RuntimeError("자리를 못 찾았다 (%d): %s" % (n, old[:120]))
    return src.replace(old, new)


def apply(src, root):
    css, html, art, lay = mockup(root)
    extra = open(HERE + "roster_block.css", encoding="utf-8").read()
    js = open(HERE + "roster_block.js", encoding="utf-8").read()
    js = js.replace("__ROSTER_ART__", json.dumps(art, separators=(",", ":")), 1)
    js = js.replace("__RB_LAYOUT__", json.dumps(lay, ensure_ascii=False, separators=(",", ":")), 1)
    js = js.replace("__RB_CSS__", js_str(css.strip("\n") + "\n" + extra), 1)
    js = js.replace("__RB_HTML__", js_str(html), 1)
    if re.search(r"__[A-Z_]+__", js.replace("__proto__", "")):
        raise RuntimeError("블록에 채우지 못한 자리표가 남았다: %s" % re.findall(r"__[A-Z_]+__", js)[:3])
    # 이전 블록 지우기 → 넣기
    src = re.sub(re.escape(JS_START) + r".*?" + re.escape(JS_END) + r"\n?", "", src, flags=re.S)
    j = src.index(JS_ANCHOR)
    src = src[:j] + js.rstrip("\n") + "\n" + src[j:]
    for old, new in EDITS:
        src = sub1(src, old, new)
    for k, n in ((JS_START, 1), ("const ROSTER_ART = ", 1), ("RBK.intercept()", 1), ("RBK.after()", 1)):
        if src.count(k) != n:
            raise RuntimeError("확인 실패 — %s 이(가) %d 개" % (k, src.count(k)))
    return src


BLOCKS = [("roster_js", JS_START, JS_END)]


if __name__ == "__main__":
    sys.path.insert(0, HERE)
    import blockguard                                          # game.html 에서 블록 안을 직접 고친 게 있으면 멈춘다 (--force 로 덮어쓴다)
    blockguard.SKIP = tuple(blockguard.SKIP) + ("const ROSTER_ART = ",)   # 그림 줄은 빌드(split_assets)가 바꾸므로 비교에서 뺀다
    force = "--force" in sys.argv
    path = [a for a in sys.argv[1:] if a != "--force"][0]
    root = os.path.dirname(os.path.abspath(path))
    raw = open(path, encoding="utf-8", newline="").read()
    crlf = "\r\n" in raw
    blockguard.check(raw.replace("\r\n", "\n"), BLOCKS, force)
    src = apply(raw.replace("\r\n", "\n"), root)
    blockguard.record(src, BLOCKS)
    if crlf:
        src = src.replace("\n", "\r\n")
    open(path, "w", encoding="utf-8", newline="").write(src)
    print("applied", len(raw), "->", len(src), "chars", "· crlf" if crlf else "")
