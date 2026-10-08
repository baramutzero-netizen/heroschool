"""상담창 (1008) — 상담 메뉴를 누르면 뜨는 창을 game.html 에 넣는다. 몇 번을 돌려도 같은 결과 (이전 블록은 지우고 다시 넣는다).

    python tools/gen/patch/apply_cslwin.py game.html [--force]   (저장소 맨 위에서 — 그림은 game.html 옆 mockups/counsel-window 에서)

· 창 — mockups/counsel-window/counsel_mockup.html 목업 그대로 (학생이 책상 뒤로 들어온다 → 고민 → 답변 구름 셋 → 대답 · 효과 → 다음 학생).
  지침을 무시한 학생이 먼저, 그다음 고민 상담 대기열 차례로. 답을 고르는 순간 게임에 반영한다
· 그림 — mockups/counsel-window/art 의 배경(bg.webp) · 책상(desk.png, 러너를 끈 배치면 desk_plain.png) 위에 배치(art/desk_layout.json)대로
  소품을 구워(src/compose_desk.py — 배치판 · 목업과 같은 규칙) 1배 280 × 180 한 장(front · 무손실 WebP)으로.
  CSL_ART 에 data: 로 넣고, wrap.py · wrap_site.py 의 split_assets 가 assets/csl_art/ 로 뺀다
· 학생 — 게임 안에서 전투 idle 도트(머리색 치환)를 잘라 #111 테두리를 둘러 쓴다 (그림 파일은 따로 없다)
· 코드 — cslwin_block.js(창 · 상담 화면 · 상담 기록) · cslwin_block.css(모양)를 넣고 다음을 고친다
  - answerCounsel · answerDefy — 셋째 인자 win: 화면을 다시 그리지 않고 결과(대답 · 서술 · 효과 · 신뢰 단계)를 돌려준다
  - 메뉴의 상담(가로 화면 사이드 · 폰 메뉴) — 화면을 바꾸지 않고 창을 연다
  - 일지 서브탭에 '상담 기록'(csllog · viewCslLog) — 예전 상담 탭 아래쪽의 올해 상담 기록
  - 예전 상담 화면(viewCounsel — 상담 카드 · 기록)은 지우고, 블록 안의 새 viewCounsel(안내 + 상담실 열기)로
· 효과음 — SFX 표 끝에 csl_tap · csl_pick · csl_ok · csl_ng · csl_stu · csl_mst (bgm/counsel_*.ogg)
· 상담 책상 배치를 바꿨으면 — 배치판에서 저장한 desk_layout.json 을 mockups/counsel-window/art/ 에 덮어쓰고 이 스크립트를 다시 돌린다
· 블록(/* CSLWIN_START … */ ~ /* CSLWIN_END */ · CSS 블록)은 돌릴 때마다 블록 파일로 통째로 갈아 끼운다 — blockguard 가 game.html 쪽을 직접 고친 걸 막는다
"""
import base64, io, json, os, re, sys
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__)) + "/"
CSS_START, CSS_END = "/* CSLWIN_CSS_START", "/* CSLWIN_CSS_END */"
JS_START, JS_END = "/* CSLWIN_START", "/* CSLWIN_END */"
CSS_ANCHOR = ".cslq{margin-top:8px;font-size:14px;line-height:1.75;color:var(--text)}\n"
JS_ANCHOR = "/* ============================================================\n   시즌 전환\n   ============================================================ */\n"
OLD_VIEW_START = "function viewCounsel(){\n  const C = counselState();\n  const q = C.queue;\n"
OLD_VIEW_END = "\n/* ---------- 도감 ---------- */"

EDITS = [
    # 고민 상담 — 상담창이 부르면 화면을 다시 그리지 않고 결과를 돌려준다
    ("function answerCounsel(qi, oi){\n",
     "function answerCounsel(qi, oi, win){   // win — 상담창(1008): 화면을 다시 그리지 않고 결과를 돌려준다\n"),
    ("  if(!st || !c){ C.queue.splice(qi,1); save(); render(); return; }\n",
     "  if(!st || !c){ C.queue.splice(qi,1); save(); if(!win) render(); return null; }\n"),
    ("  const tUp = ok ? (addTrust(st, 1), true) : false;\n",
     "  const tb0 = trustBand(trustOf(st)).step, tr0 = trustRaw(st);\n  const tUp = ok ? (addTrust(st, 1), true) : false;\n  const tb1 = trustBand(trustOf(st)).step;\n"),
    ("  save(); render();\n  toast(ok? (gain? `${dn(st)} — ${gain.n} +${gain.d}",
     "  save();\n"
     "  const res = {ok, fit, byLead, byTrust, gain, dbl, capped, say:ans.say, r:ans.r, trustUp: trustRaw(st) > tr0, trustDown:false, band: tb1 !== tb0 ? tb1 : null};   // 1008 — 상담창\n"
     "  if(win) return res;\n"
     "  render();\n  toast(ok? (gain? `${dn(st)} — ${gain.n} +${gain.d}"),
    # 지침 무시 상담 — 같은 방식 (학생의 반응은 따옴표 안 = 말 · 밖 = 서술로 나눠 돌려준다)
    ("function answerDefy(pi, oi){\n",
     "function answerDefy(pi, oi, win){   // win — 상담창(1008): 화면을 다시 그리지 않고 결과를 돌려준다\n"),
    ("  if(!st){ D.pend.splice(pi,1); save(); render(); return; }\n",
     "  if(!st){ D.pend.splice(pi,1); save(); if(!win) render(); return null; }\n"),
    ("  let gain = null, dbl = false, capped = false, cond = 0;\n",
     "  const tb0 = trustBand(trustOf(st)).step, tr0 = trustRaw(st);\n  let gain = null, dbl = false, capped = false, cond = 0;\n"),
    ("  } else addTrust(st, -1);\n",
     "  } else addTrust(st, -1);\n  const tb1 = trustBand(trustOf(st)).step;\n"),
    ("  save(); render();\n  toast(ok ? `${dn(st)} — 지침을 따르겠다고 한다",
     "  save();\n"
     "  const rx = masterQ(ok ? R2[0] : R2[1], st, true), rq = rx.match(/“([^”]*)”/);   // 1008 — 상담창\n"
     "  const res = {ok, fit, byLead, byTrust, gain, dbl, capped, cond, say: rq ? rq[1] : rx, r: rx.replace(/“[^”]*”/, \"\").trim(), trustUp: trustRaw(st) > tr0, trustDown: trustRaw(st) < tr0, band: tb1 !== tb0 ? tb1 : null};\n"
     "  if(win) return res;\n"
     "  render();\n  toast(ok ? `${dn(st)} — 지침을 따르겠다고 한다"),
    # 메뉴의 상담 — 화면을 바꾸지 않고 상담창을 연다 (가로 화면 사이드 · 폰 메뉴)
    ("      nav.querySelectorAll(\"button[data-view]\").forEach(b=> b.onclick=()=>{ if(b.dataset.view===\"facil\") UI.facTab = null;",
     "      nav.querySelectorAll(\"button[data-view]\").forEach(b=> b.onclick=()=>{ if(b.dataset.view===\"counsel\"){ cslwOpen(); return; }   /* 1008 — 상담은 창으로 */ if(b.dataset.view===\"facil\") UI.facTab = null;"),
    ("      nm.querySelectorAll(\"[data-view]\").forEach(b=> b.onclick=()=>{ if(b.dataset.view===\"facil\") UI.facTab = null;",
     "      nm.querySelectorAll(\"[data-view]\").forEach(b=> b.onclick=()=>{ if(b.dataset.view===\"counsel\"){ cslwOpen(); return; }   /* 1008 — 상담은 창으로 */ if(b.dataset.view===\"facil\") UI.facTab = null;"),
    # 일지 서브탭 — 상담 기록
    ("  log:    [{id:\"log\", n:\"학원 일지\"}, {id:\"record\", n:\"졸업생 명부\"}, {id:\"codex\", n:\"도감\"}]\n",
     "  log:    [{id:\"log\", n:\"학원 일지\"}, {id:\"csllog\", n:\"상담 기록\"}, {id:\"record\", n:\"졸업생 명부\"}, {id:\"codex\", n:\"도감\"}]   // 1008 — 상담 기록 (상담은 창으로)\n"),
    ("  else if(UI.view===\"log\") v.innerHTML = viewLog();\n",
     "  else if(UI.view===\"log\") v.innerHTML = viewLog();\n  else if(UI.view===\"csllog\") v.innerHTML = viewCslLog();   // 1008 — 일지 › 상담 기록\n"),
    # 상담 화면 · 상담 기록의 단추
    ("  v.querySelectorAll(\"[data-defy]\").forEach(b=> b.onclick=()=>{   // 1008 — 지침 무시 상담\n",
     "  v.querySelectorAll(\"[data-cslw]\").forEach(b=> b.onclick=()=> cslwOpen());   // 1008 — 상담창 열기\n"
     "  v.querySelectorAll(\"[data-cslrec]\").forEach(b=> b.onclick=()=>{ UI.view = \"csllog\"; render(); });\n"
     "  v.querySelectorAll(\"[data-defy]\").forEach(b=> b.onclick=()=>{   // 1008 — 지침 무시 상담\n"),
]


def b64(data):
    return base64.b64encode(data).decode()


def webp_lossless(img):
    b = io.BytesIO(); img.save(b, "WEBP", lossless=True, quality=100, method=6)
    return b.getvalue()


def art(root):
    """배경 · 책상 + 소품 (1배 280 × 180) — data: 두 장"""
    A = os.path.join(root, "mockups", "counsel-window")
    sys.path.insert(0, os.path.join(A, "src"))
    import compose_desk
    layout = json.load(open(os.path.join(A, "art", "desk_layout.json"), encoding="utf-8"))
    kit = compose_desk.load_kit()
    W, H = kit["stage"]
    front = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    desk = Image.open(os.path.join(A, "art", "desk.png" if layout.get("runner", True) else "desk_plain.png")).convert("RGBA")
    front.alpha_composite(desk, (0, kit["desk"]["top"]))
    front.alpha_composite(compose_desk.compose(layout, kit))
    bg = open(os.path.join(A, "art", "bg.webp"), "rb").read()
    return {"bg": "data:image/webp;base64," + b64(bg), "front": "data:image/webp;base64," + b64(webp_lossless(front))}


# 효과음 (SFX 표 끝에) — bgm/counsel_*.ogg (원본 mp3 도 bgm/ 에). 글자 소리는 다른 소리보다 조금 작게
SFX_MARK = "  csl_tap:"
SFX_NEW = ("  /* 상담창 (1008) — 학생을 누를 때 · 답변 구름을 고를 때 · 반응 성공 / 실패 · 학생 / 마스터의 말이 한 글자씩 찍힐 때(cwBlip).\n"
           "     앞뒤 무음을 잘라 Ogg 로 (원본 mp3 도 bgm/ 에 — 같은 이름 파일을 바꾸면 소리만 갈아 끼울 수 있다) */\n"
           "  csl_tap: {f:\"counsel_tap.ogg\"},\n"
           "  csl_pick:{f:\"counsel_pick.ogg\"},\n"
           "  csl_ok:  {f:\"counsel_ok.ogg\"},\n"
           "  csl_ng:  {f:\"counsel_ng.ogg\"},\n"
           "  csl_stu: {f:\"counsel_type_student.ogg\", v:.8},\n"
           "  csl_mst: {f:\"counsel_type_master.ogg\", v:.8}")


def sfx(src):
    if SFX_MARK in src:
        return src
    m = re.search(r'\n(  sk_glow: \{f:"sched_glow\.ogg", v:\.4\})([^\n]*)\n\};', src)
    if not m:
        raise RuntimeError("자리를 못 찾았다: SFX 표 끝 (sk_glow)")
    return src[:m.start()] + "\n" + m.group(1) + "," + m.group(2) + "\n" + SFX_NEW + "\n};" + src[m.end():]


def sub1(src, old, new):
    if new in src:
        return src
    n = src.count(old)
    if n != 1:
        raise RuntimeError("자리를 못 찾았다 (%d): %s" % (n, old[:120]))
    return src.replace(old, new)


def apply(src, root):
    js = open(HERE + "cslwin_block.js", encoding="utf-8").read()
    js = js.replace("__CSL_ART__", json.dumps(art(root), separators=(",", ":")), 1)
    css = open(HERE + "cslwin_block.css", encoding="utf-8").read()
    # 이전 블록 지우기 → 넣기
    src = re.sub(re.escape(CSS_START) + r".*?" + re.escape(CSS_END) + r"\n?", "", src, flags=re.S)
    src = re.sub(re.escape(JS_START) + r".*?" + re.escape(JS_END) + r"\n?", "", src, flags=re.S)
    i = src.index(CSS_ANCHOR) + len(CSS_ANCHOR)
    src = src[:i] + css.rstrip("\n") + "\n" + src[i:]
    j = src.index(JS_ANCHOR)
    src = src[:j] + js.rstrip("\n") + "\n" + src[j:]
    # 예전 상담 화면 (상담 카드 · 올해의 상담 기록) — 새 viewCounsel · viewCslLog 가 맡는다
    a = src.find(OLD_VIEW_START)
    if a >= 0:
        b = src.index(OLD_VIEW_END, a)
        src = src[:a] + src[b:]
    for old, new in EDITS:
        src = sub1(src, old, new)
    src = sfx(src)
    for k, n in (("function viewCounsel(", 1), ("function viewCslLog(", 1), ("function cslwOpen(", 1), (JS_START, 1), (CSS_START, 1)):
        if src.count(k) != n:
            raise RuntimeError("확인 실패 — %s 이(가) %d 개" % (k, src.count(k)))
    return src


BLOCKS = [("cslwin_js", JS_START, JS_END), ("cslwin_css", CSS_START, CSS_END)]


if __name__ == "__main__":
    sys.path.insert(0, HERE)
    import blockguard                                          # game.html 에서 블록 안을 직접 고친 게 있으면 멈춘다 (--force 로 덮어쓴다)
    blockguard.SKIP = tuple(blockguard.SKIP) + ("const CSL_ART = ",)   # 그림 줄은 빌드(split_assets)가 바꾸므로 비교에서 뺀다
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
