"""대회 쿼터뷰 진영 칸이 학원 이름 길이만큼 늘어난다 (1008) — 몇 번을 돌려도 같은 결과. apply_tqui.py · apply_tqfield.py 다음에 돌린다.

    python3 apply_tqgrow.py <game.html>

· BATTLE_TUNE.quarter.enemy / ally 의 w · h 는 가장 작은 크기 — 이름이 길면 칸(나무판)이 가로로 늘어난다
· 전투판 가장자리 쪽을 붙잡고 안쪽으로 늘어난다 — 오른쪽에 있는 칸은 왼쪽으로, 아래쪽에 있는 칸은 위로
· 전투판 너비의 45% 를 넘으면 두 줄 (높이도 같이 늘어난다). 학원 이름은 24자까지라 보통은 한 줄
· 필드 배치 실험실: '긴 학원 이름으로 보기' — 긴 이름 두 개로 칸이 늘어나는 모습을 미리 본다"""
import sys

OLD_PLACE = """  set("left", (v.x - F.x) + "px"); set("top", (v.y - F.y) + "px");
  if(k === "title"){ set("font-size", v.size + "px"); set("--tq-o", Math.max(2, Math.round(v.size / 12)) + "px"); set("max-width", (F.w - 40) + "px"); }
  else { set("width", v.w + "px"); set("height", v.h + "px"); set("--tq-fs", v.size + "px"); }
}
"""
NEW_PLACE = """  if(k === "title"){ set("left", (v.x - F.x) + "px"); set("top", (v.y - F.y) + "px");
    set("font-size", v.size + "px"); set("--tq-o", Math.max(2, Math.round(v.size / 12)) + "px"); set("max-width", (F.w - 40) + "px"); return; }
  /* 1008 — 진영 칸은 학원 이름 길이만큼 늘어난다 (w · h 는 가장 작은 크기). 전투판 가장자리 쪽을 붙잡고 안쪽으로 —
     오른쪽에 있는 칸은 왼쪽으로, 아래쪽에 있는 칸은 위로 늘어난다. 전투판 너비의 45% 를 넘으면 두 줄 */
  const toL = v.x + v.w/2 > F.x + F.w/2, toU = v.y + v.h/2 > F.y + F.h/2;
  set("left", toL ? "auto" : (v.x - F.x) + "px"); set("right", toL ? (F.x + F.w - v.x - v.w) + "px" : "auto");
  set("top", toU ? "auto" : (v.y - F.y) + "px"); set("bottom", toU ? (F.y + F.h - v.y - v.h) + "px" : "auto");
  set("width", "max-content"); set("min-width", v.w + "px"); set("max-width", Math.max(v.w, Math.round(F.w * .45)) + "px");
  set("height", "auto"); set("min-height", v.h + "px");
  set("--tq-fs", v.size + "px");
}
"""

EDITS = [
    ("function tqPlace(el, k, v){\n  if(!el || !v) return;\n  const F = TOURNAMENT_LAYOUT.field, set = (p, x)=> el.style.setProperty(p, x, \"important\");\n" + OLD_PLACE,
     "function tqPlace(el, k, v){\n  if(!el || !v) return;\n  const F = TOURNAMENT_LAYOUT.field, set = (p, x)=> el.style.setProperty(p, x, \"important\");\n" + NEW_PLACE),
    # 실험실 — 긴 학원 이름으로 보기
    ("  openBattle(res, {field: L.field, head: \"필드 배치 실험실 · \" + L.field, titleA:\"우리 학원\", titleB:\"상대 학원\", lab:true}, ()=>{});\n",
     "  const nA = L.longName ? \"성벽 너머 푸른 언덕 왕립 용사 양성 학원\" : \"우리 학원\", nB = L.longName ? \"북쪽 바다 끝 등대 마을 견습 기사 학원\" : \"상대 학원\";   // 1008 — 긴 학원 이름으로 보기\n"
     "  openBattle(res, {field: L.field, head: \"필드 배치 실험실 · \" + L.field, titleA:nA, titleB:nB, lab:true}, ()=>{});\n"),
    ("    if(d.tqSel !== undefined) L.tqSel = d.tqSel;\n",
     "    if(d.tqSel !== undefined) L.tqSel = d.tqSel;\n    if(d.longName != null) L.longName = !!d.longName;\n"),
    ("    const key = JSON.stringify([L.field, L.jobs, PREF.fieldPastel]);\n",
     "    const key = JSON.stringify([L.field, L.jobs, PREF.fieldPastel, !!L.longName]);\n"),
]


def sub1(src, old, new):
    n = src.count(old)
    if n != 1:
        raise RuntimeError("자리를 못 찾았다 (%d): %s" % (n, old[:100]))
    return src.replace(old, new)


def apply(src):
    if "진영 칸은 학원 이름 길이만큼 늘어난다" in src:
        return src
    if "function tqPlace(el, k, v){" not in src:
        raise RuntimeError("apply_tqui.py 를 먼저 돌린다")
    for old, new in EDITS:
        src = sub1(src, old, new)
    return src


if __name__ == "__main__":
    path = sys.argv[1]
    raw = open(path, encoding="utf-8", newline="").read()
    crlf = "\r\n" in raw
    src = apply(raw.replace("\r\n", "\n"))
    if crlf:
        src = src.replace("\n", "\r\n")
    open(path, "w", encoding="utf-8", newline="").write(src)
    print("applied", len(raw), "->", len(src), "chars", "· crlf" if crlf else "")
