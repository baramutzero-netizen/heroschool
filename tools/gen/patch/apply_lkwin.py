"""락커룸 창 (1013) — 경기 직전 한마디를 상담창 같은 창으로 game.html 에 넣는다. 몇 번을 돌려도 같은 결과 (이전 블록은 그 자리에서 갈아 끼운다).

    python tools/gen/patch/apply_lkwin.py game.html [--force]   (저장소 맨 위에서)

· 창 — mockups/locker-room/locker_room_mockup.html 목업 그대로 (출전 학생이 둥글게 모인다 → 구름 넷 → 고민 … → 납득 ~♪ · 못 납득 | | | → 경기 시작).
  배경은 그 경기의 대회 쿼터뷰 지도(assets/battle-fields/quarter — 게임이 이미 쓰는 그림)를 흐리게, 학생은 상담창의 전투 idle 도트(cslwSprUrl),
  구름 그림은 상담창의 cslwCloudArt 를 그대로 쓴다 (새 그림 파일은 없다). 상담창(CSLWIN)이 먼저 들어가 있어야 한다
· 코드 — lkwin_block.js(창 · 경기 화면의 락커룸 칸 lockerHtml · bindLocker) · lkwin_block.css(모양)를 넣고 다음을 고친다
  - 예전 lockerHtml(한마디 넷이 2 × 2 단추) · bindLocker 는 지우고 블록 안의 새 것으로 — 경기 화면의 락커룸 칸은 학생 기분 카드 그대로
    (창을 여는 단추는 없다 — 한마디는 창에서)
  - 경기 화면 셋(가을 대회 renderLadder · 친선전 renderFriendly · 봄 신인전 renderTournament)의 bindLocker 에 창이 쓸 것
    (탭 제목 · 상대 이름 · 배경 필드 · 전투를 여는 함수)을 넘기고, '경기 시작'은 lkwGate — 한마디 전이면 창부터
  - 경기 화면으로 넘어가는 단추(출전 · 친선전 시작 · 엔트리 확정 · 대진 확정)는 lkwAuto(t) — 그 경기 화면이 그려지면 한마디 전일 때 창이 같이 뜬다
    (1013 사용자: '출전을 누르고 한마디를 안 했으면 락커룸이 같이 팝업'). 창이나 '경기 시작'으로 전투를 보고 '결과 확정'으로 다음 경기에 와도 같이 뜬다
  - '빠르게 결과만' · '남은 경기 한 번에'는 그대로 (창 없이 · 그 뒤 경기 화면에도 창이 저절로 뜨지 않는다)
· 블록(/* LKWIN_START … */ ~ /* LKWIN_END */ · CSS 블록)은 돌릴 때마다 블록 파일로 통째로 갈아 끼운다 — blockguard 가 game.html 쪽을 직접 고친 걸 막는다
"""
import os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__)) + "/"
CSS_START, CSS_END = "/* LKWIN_CSS_START", "/* LKWIN_CSS_END */"
JS_START, JS_END = "/* LKWIN_START", "/* LKWIN_END */"
CSS_ANCHOR = "/* CSLWIN_CSS_END */\n"                                # 상담창 CSS 바로 뒤 — .cw-* 를 덮어쓰므로
JS_ANCHOR = "/* ============================================================\n   대회 진행\n   ============================================================ */\n"
OLD_START = "function lockerHtml(L, my){\n  const said = (L.said!=null) ? L.offers[L.said] : null;\n"   # 예전 락커룸 칸 (블록 밖)
OLD_END = "  if(!tutSeen(\"8\")) tutOverPage(\"8\");\n}\n"

EDITS = [
    # 친선전 — 경기 화면
    ("      bindLocker(t, fL, fMy, renderFriendly);\n      $(\"#fPlay\").onclick = ()=> friendlyRun(t,false);\n",
     "      bindLocker(t, fL, fMy, renderFriendly, {title:\"친선전\", label:`제${i+1}경기`, foe:t.foe.name, field:\"dummy\", start:()=> friendlyRun(t,false)});   // 1013 — 락커룸 창\n"
     "      $(\"#fPlay\").onclick = ()=> lkwGate();   // 1013 — 한마디 전이면 락커룸 창부터\n"),
    # 가을 대회 (시내 · 광역 · 예선 · 본선)
    ("      bindLocker(t, lL, lMy, renderLadder);\n",
     "      bindLocker(t, lL, lMy, renderLadder, {title:cfg.n, label:ladderMatchLabel(t), foe:foe.name, field:t.step, start:()=> ladderRun(t,false)});   // 1013 — 락커룸 창\n"),
    ("      $(\"#tPlay\").onclick = ()=> ladderRun(t,false);\n",
     "      $(\"#tPlay\").onclick = ()=> lkwGate();   // 1013 — 한마디 전이면 락커룸 창부터\n"),
    # 봄 신인전 (renderTournament — 예전 가을 토너먼트도 같은 화면)
    ("      bindLocker(t, mL, mMy, renderTournament);\n",
     "      bindLocker(t, mL, mMy, renderTournament, {title:isSpring? \"봄 신인전\" : t.title, label:head, foe:oppName, field:isSpring? \"citytournament\" : null, start:()=> run(false)});   // 1013 — 락커룸 창\n"),
    ("      $(\"#tPlay\").onclick=()=>run(false);\n",
     "      $(\"#tPlay\").onclick=()=> lkwGate();   // 1013 — 한마디 전이면 락커룸 창부터\n"),
    # 경기 화면으로 넘어가는 단추 — 한마디 전이면 락커룸 창이 같이 뜬다 (1013 사용자)
    ("        t.matchIdx=0; t.roundWins=0; t.roundScore=[0,0];\n        renderTournament();\n",                     # 봄 신인전 '○팀 출전'
     "        t.matchIdx=0; t.roundWins=0; t.roundScore=[0,0];\n"
     "        lkwAuto(t);   // 1013 — 경기 화면이 뜨면 한마디 전일 때 락커룸 창이 같이\n        renderTournament();\n"),
    ("      $(\"#tGo\").onclick = ()=>{ t.stage=\"match\"; t.matchIdx=0; t.roundScore=[0,0]; renderTournament(); };\n",   # 예전 가을 토너먼트 '대진 확정'
     "      $(\"#tGo\").onclick = ()=>{ t.stage=\"match\"; t.matchIdx=0; t.roundScore=[0,0]; lkwAuto(t); renderTournament(); };   // 1013 — 락커룸 창이 같이\n"),
    ("        t.stage=\"match\"; renderFriendly();\n",                                                                  # 친선전 '친선전 시작'
     "        t.stage=\"match\"; lkwAuto(t); renderFriendly();   // 1013 — 경기 화면이 뜨면 한마디 전일 때 락커룸 창이 같이\n"),
    ("        t.stage = (t.cfg.kind===\"cup\" && U>1) ? \"scout\" : \"match\";\n        renderLadder();\n",              # 가을 대회 '엔트리 확정'
     "        t.stage = (t.cfg.kind===\"cup\" && U>1) ? \"scout\" : \"match\";\n"
     "        lkwAuto(t);   // 1013 — 경기 화면이 뜨면 한마디 전일 때 락커룸 창이 같이 (대진 확정 화면을 거치면 그 뒤에)\n        renderLadder();\n"),
    ("      $(\"#tGo\").onclick = ()=>{ t.stage=\"match\"; renderLadder(); };\n",                                       # 가을 대회 '대진 확정'
     "      $(\"#tGo\").onclick = ()=>{ t.stage=\"match\"; lkwAuto(t); renderLadder(); };   // 1013 — 락커룸 창이 같이\n"),
]


def sub1(src, old, new):
    if new in src:
        return src
    n = src.count(old)
    if n != 1:
        raise RuntimeError("자리를 못 찾았다 (%d): %s" % (n, old[:120]))
    return src.replace(old, new)


def put(src, start, end, body, anchor, after):
    """이전 블록이 있으면 그 자리에서 갈아 끼우고, 없으면 기준 줄에 넣는다"""
    m = re.search(re.escape(start) + r".*?" + re.escape(end) + r"\n?", src, flags=re.S)
    if m:
        return src[:m.start()] + body.rstrip("\n") + "\n" + src[m.end():]
    if src.count(anchor) != 1:
        raise RuntimeError("자리를 못 찾았다 (%d): %s" % (src.count(anchor), anchor[:80]))
    k = src.index(anchor) + (len(anchor) if after else 0)
    return src[:k] + body.rstrip("\n") + "\n" + src[k:]


def apply(src):
    if "/* CSLWIN_START" not in src or CSLWIN_CSS_OK not in src:
        raise RuntimeError("상담창(CSLWIN)이 먼저 들어가 있어야 한다 — apply_cslwin 부터")
    js = open(HERE + "lkwin_block.js", encoding="utf-8").read()
    css = open(HERE + "lkwin_block.css", encoding="utf-8").read()
    # 예전 락커룸 칸 (lockerHtml · bindLocker — 블록 밖) — 블록 안의 새 것이 맡는다
    a = src.find(OLD_START)
    if a >= 0 and (JS_START not in src or a < src.find(JS_START) or a > src.find(JS_END)):
        b = src.index(OLD_END, a) + len(OLD_END)
        src = src[:a] + src[b:]
    src = put(src, CSS_START, CSS_END, css, CSS_ANCHOR, True)
    src = put(src, JS_START, JS_END, js, JS_ANCHOR, False)
    for old, new in EDITS:
        src = sub1(src, old, new)
    for k, n in (("function lockerHtml(", 1), ("function bindLocker(", 1), ("function lkwOpen(", 1), ("lkwGate()", 4), ("lkwAuto(t);", 5),
                 ("data-lkw", 0), (JS_START, 1), (CSS_START, 1)):
        if src.count(k) != n:
            raise RuntimeError("확인 실패 — %s 이(가) %d 개 (%d 개여야)" % (k, src.count(k), n))
    return src


CSLWIN_CSS_OK = "/* CSLWIN_CSS_END */"
BLOCKS = [("lkwin_js", JS_START, JS_END), ("lkwin_css", CSS_START, CSS_END)]


if __name__ == "__main__":
    sys.path.insert(0, HERE)
    import blockguard                                          # game.html 에서 블록 안을 직접 고친 게 있으면 멈춘다 (--force 로 덮어쓴다)
    force = "--force" in sys.argv
    path = [a for a in sys.argv[1:] if a != "--force"][0]
    raw = open(path, encoding="utf-8", newline="").read()
    crlf = "\r\n" in raw
    blockguard.check(raw.replace("\r\n", "\n"), BLOCKS, force)
    src = apply(raw.replace("\r\n", "\n"))
    blockguard.record(src, BLOCKS)
    if crlf:
        src = src.replace("\n", "\r\n")
    open(path, "w", encoding="utf-8", newline="").write(src)
    print("applied", len(raw), "->", len(src), "chars", "· crlf" if crlf else "")
