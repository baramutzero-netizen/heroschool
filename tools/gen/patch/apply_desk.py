"""마스터 노트 책상 (1006) — game.html 에 넣는다. 몇 번을 돌려도 같은 결과 (이전 블록은 지우고 다시 넣는다).

    python3 apply_desk.py <game.html> [배치 JSON — 주면 desk_art.py 로 다시 굽는다] [--force]

desk_art.py 로 구운 그림(desk_out/*.png)과 자리(desk_out/geo.json)를 MDESK_ART · MDESK_GEO 로 넣고(data: — wrap.py · wrap_site.py 의
split_assets 가 assets/mdesk_art/ 로 뺀다), mdesk_block.js · mdesk_block.css 를 넣은 뒤 render · bindView · viewHome · 메뉴 단추를 고친다.
스케줄 두루마리의 축 자리(줌 맞춤)는 game.html 옆 assets/sched_art/ 그림에서 잰다."""
import base64, json, os, re, sys
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__)) + "/"
sys.path.insert(0, HERE)
import desk_art


def sub1(src, old, new, done_mark):
    if done_mark in src: return src
    n = src.count(old)
    if n != 1: raise RuntimeError("자리를 못 찾았다 (%d): %s" % (n, old[:90]))
    return src.replace(old, new, 1)


def uri(path):
    return "data:image/png;base64," + base64.b64encode(open(path, "rb").read()).decode()


def sched_axes(root):
    A = os.path.join(root, "assets", "sched_art") + "/"
    c = Image.open(A + "under.png").convert("RGBA")
    for n in ("over1", "over2"): c.alpha_composite(Image.open(A + n + ".png").convert("RGBA"))
    a = np.array(c).astype(int)
    return desk_art.scroll_axes(a, None, a.shape[0] // 2)


def apply(src, root, layout=None):
    geo = desk_art.build(layout) if layout else json.load(open(desk_art.OUT + "geo.json", encoding="utf-8"))
    geo["zoom"]["s"] = sched_axes(root)
    geo.pop("src", None)
    art = {k: uri(desk_art.OUT + k + ".png") for k in ("base", "items", "props", "vig", "light")}
    for g in geo["groups"]: art["hl_" + g["k"]] = uri(desk_art.OUT + "hl_" + g["k"] + ".png")
    js = open(HERE + "mdesk_block.js", encoding="utf-8").read()
    js = js.replace("__MDESK_ART__", json.dumps(art, separators=(",", ":")), 1)
    js = js.replace("__MDESK_GEO__", json.dumps(geo, ensure_ascii=False, separators=(",", ":")), 1)
    css = open(HERE + "mdesk_block.css", encoding="utf-8").read()
    # 이전 블록 지우기 → 넣기
    src = re.sub(r'/\* MDESK_CSS_START.*?/\* MDESK_CSS_END \*/\n?', '', src, flags=re.S)
    src = re.sub(r'/\* MDESK_START.*?/\* MDESK_END \*/\n?', '', src, flags=re.S)
    i = src.index('</style>')
    src = src[:i] + css.rstrip('\n') + '\n' + src[i:]
    j = src.index('function viewHome(')
    src = src[:j] + js.rstrip('\n') + '\n' + src[j:]
    # 학원 정보 팝업 — 예전 '학원 정보' 서브탭 그대로, 튜토리얼 단추만 뺀다 (말린 지도가 맡는다)
    src = sub1(src, 'function viewHome(){\n  const next = PHASES[S.phase];',
               'function viewHome(o){   // o.desk — 마스터 노트 책상의 학원 정보 팝업 (튜토리얼 단추는 말린 지도가 맡는다 · 1006)\n  const next = PHASES[S.phase];',
               'function viewHome(o){')
    src = sub1(src, '${(typeof TUT_ICON!=="undefined" && TUT_ICON)? `<div><button class="tutbtn" id="btnTut"',
               '${(!(o && o.desk) && typeof TUT_ICON!=="undefined" && TUT_ICON)? `<div><button class="tutbtn" id="btnTut"',
               '!(o && o.desk) && typeof TUT_ICON')
    # render — 가로 화면이면 책상
    src = sub1(src, '  if(UI.view==="home") v.innerHTML = viewHome();\n',
               '  if(UI.view==="home") v.innerHTML = mdeskOn() ? viewHomeDesk() : viewHome();   // 마스터 노트 책상 (1006) — 가로 화면\n',
               'mdeskOn() ? viewHomeDesk() : viewHome()')
    old = '  if(UI.view!=="facil") UI.facTab = null;                     // 1002 — 마을 팝업은 마을을 떠나면 닫힌다\n'
    src = sub1(src, old, old
               + '  if(UI.view==="master" && mdeskOn()){ UI.view = "home"; UI.mdeskPop = "master"; }   // 1006 — 책상에서는 마스터 육성이 책 더미 팝업\n'
               + '  if(UI.view!=="home") UI.mdeskPop = null;                   // 책상 팝업은 마스터 노트를 떠나면 닫힌다\n',
               'UI.mdeskPop = "master"; }')
    src = sub1(src, 'document.documentElement.classList.toggle("town-on", UI.view==="facil" && townMode());',
               'document.documentElement.classList.toggle("town-on", (UI.view==="facil" || UI.view==="home") && townMode());   // 1006 — 마스터 노트 책상도 마을 지도처럼',
               '(UI.view==="facil" || UI.view==="home") && townMode()')
    src = sub1(src, '  { const sub = subTabsHtml(UI.view);',
               '  { const sub = (UI.view==="home" && mdeskOn()) ? "" : subTabsHtml(UI.view);   // 1006 — 책상에는 서브탭 대신 소품',
               '(UI.view==="home" && mdeskOn()) ? "" : subTabsHtml')
    # bindView — 책상 소품
    old = '  const v = $("#view");\n  v.querySelectorAll("[data-sid]").forEach(b=> b.onclick=()=>{ UI.sel = (UI.sel===b.dataset.sid?null:b.dataset.sid);'
    src = sub1(src, old, old.replace('  const v = $("#view");\n', '  const v = $("#view");\n  if(UI.view==="home" && typeof bindMasterDesk === "function") bindMasterDesk(v);   // 마스터 노트 책상 (1006)\n'),
               'bindMasterDesk(v);   // 마스터 노트 책상')
    # 메뉴 단추로 마스터 노트에 오면 팝업은 닫힌 채로
    src = sub1(src, 'nav.querySelectorAll("button[data-view]").forEach(b=> b.onclick=()=>{ if(b.dataset.view==="facil") UI.facTab = null; UI.view=b.dataset.view; render(); });',
               'nav.querySelectorAll("button[data-view]").forEach(b=> b.onclick=()=>{ if(b.dataset.view==="facil") UI.facTab = null; if(b.dataset.view==="home") UI.mdeskPop = null; UI.view=b.dataset.view; render(); });',
               'if(b.dataset.view==="home") UI.mdeskPop = null;')
    # 가로 ↔ 세로가 바뀌면 마스터 노트도 다시 그린다 (책상 ↔ 예전 화면)
    src = sub1(src, 'if(TOWN_MQ){ const h = ()=>{ if(typeof UI !== "undefined" && UI.view === "facil") render(); };',
               'if(TOWN_MQ){ const h = ()=>{ if(typeof UI !== "undefined" && (UI.view === "facil" || UI.view === "home" || UI.view === "master")) render(); };   // 1006 — 마스터 노트 책상도',
               'UI.view === "home" || UI.view === "master")) render(); };')
    return src, geo


BLOCKS = [("mdesk_js", "/* MDESK_START", "/* MDESK_END */"), ("mdesk_css", "/* MDESK_CSS_START", "/* MDESK_CSS_END */")]

if __name__ == "__main__":
    import blockguard                                          # game.html 에서 블록 안을 직접 고친 게 있으면 멈춘다 (--force 로 덮어쓴다)
    force = "--force" in sys.argv
    args = [a for a in sys.argv[1:] if a != "--force"]
    path = args[0]
    lay = args[1] if len(args) > 1 else None
    raw = open(path, encoding="utf-8", newline="").read()
    crlf = "\r\n" in raw
    blockguard.check(raw.replace("\r\n", "\n"), BLOCKS, force)
    src, geo = apply(raw.replace("\r\n", "\n"), os.path.dirname(os.path.abspath(path)), lay)
    blockguard.record(src, BLOCKS)
    if crlf: src = src.replace("\n", "\r\n")
    open(path, "w", encoding="utf-8", newline="").write(src)
    print("applied", len(raw), "->", len(src), "chars", "· crlf" if crlf else "", "· zoom", geo["zoom"])
