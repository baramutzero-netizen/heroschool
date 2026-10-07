"""대회 쿼터뷰 경기 이름 맞춤 (1008) — 몇 번을 돌려도 같은 결과. apply_tqgrow.py 다음에 돌린다.

    python3 apply_tqalign.py <game.html>

· BATTLE_TUNE.quarter.title.align — left 면 x 가 글 왼쪽 끝(오른쪽으로 길어진다) · right 면 오른쪽 끝 · 없거나 center 면 가운데
· 경기 이름이 길면 전투판 안쪽(가장자리에서 TQ_TITLE_M px 안)까지만 늘어나고 줄을 바꾼다 — 테두리 밖으로 삐져나가지 않는다
· 필드 배치 실험실의 '긴 이름으로 보기' 는 경기 이름도 긴 것으로 (5인 리그 · 긴 학원 이름 둘)
· 맞춤 값 자체(BATTLE_TUNE.quarter.title)는 apply_tune.py 로 넣는다"""
import sys

OLD_TITLE = """  if(k === "title"){ set("left", (v.x - F.x) + "px"); set("top", (v.y - F.y) + "px");
    set("font-size", v.size + "px"); set("--tq-o", Math.max(2, Math.round(v.size / 12)) + "px"); set("max-width", (F.w - 40) + "px"); return; }
"""
NEW_TITLE = """  if(k === "title"){
    /* 1008 — 맞춤(align): left 는 x 가 글 왼쪽 끝 · right 는 오른쪽 끝 · 그 밖은 가운데 (y 는 늘 글 가운데).
       길면 전투판 안쪽(가장자리에서 TQ_TITLE_M 안)까지만 늘어나고 줄을 바꾼다 — 테두리 밖으로 삐져나가지 않게 */
    const a = v.align === "left" || v.align === "right" ? v.align : "center", lo = F.x + TQ_TITLE_M, hi = F.x + F.w - TQ_TITLE_M;
    const room = a === "left" ? hi - v.x : a === "right" ? v.x - lo : 2 * Math.min(v.x - lo, hi - v.x);
    set("left", (v.x - F.x) + "px"); set("top", (v.y - F.y) + "px");
    set("transform", a === "left" ? "translate(0,-50%)" : a === "right" ? "translate(-100%,-50%)" : "translate(-50%,-50%)");
    set("text-align", a);
    set("max-width", Math.round(Math.max(160, Math.min(F.w - 2 * TQ_TITLE_M, room))) + "px");
    set("font-size", v.size + "px"); set("--tq-o", Math.max(2, Math.round(v.size / 12)) + "px"); return; }
"""

EDITS = [
    ("function tqPlace(el, k, v){\n  if(!el || !v) return;\n  const F = TOURNAMENT_LAYOUT.field, set = (p, x)=> el.style.setProperty(p, x, \"important\");\n" + OLD_TITLE,
     "const TQ_TITLE_M = 60;   // 1008 — 경기 이름이 늘어나는 한계: 전투판 가장자리에서 이만큼 안쪽 (나무 테두리 · 용 장식)\n"
     "function tqPlace(el, k, v){\n  if(!el || !v) return;\n  const F = TOURNAMENT_LAYOUT.field, set = (p, x)=> el.style.setProperty(p, x, \"important\");\n" + NEW_TITLE),
    ("  quarter:{   /* 1007 — 대회 쿼터뷰(가로) 경기 이름 · 진영 칸 — 편집기 좌표 px. title 은 글 가운데 x · y 와 글자 크기 · enemy / ally 는 칸 x · y · w · h 와 이름 글자 크기 */\n",
     "  quarter:{   /* 1007 — 대회 쿼터뷰(가로) 경기 이름 · 진영 칸 — 편집기 좌표 px. title 은 x · y(글 가운데) · 글자 크기 · align(1008 — left 면 x 가 글 왼쪽 끝 · right 면 오른쪽 끝 · 없으면 가운데) · enemy / ally 는 칸 x · y · w · h(가장 작은 크기) 와 이름 글자 크기 */\n"),
    ("  openBattle(res, {field: L.field, head: \"필드 배치 실험실 · \" + L.field, titleA:nA, titleB:nB, lab:true}, ()=>{});\n",
     "  const head = L.longName ? `5인 리그 시즌 21 · 14라운드 — ${nA} 대 ${nB}` : \"필드 배치 실험실 · \" + L.field;   // 1008 — 긴 이름이면 경기 이름도 길게\n"
     "  openBattle(res, {field: L.field, head, titleA:nA, titleB:nB, lab:true}, ()=>{});\n"),
]


def sub1(src, old, new):
    n = src.count(old)
    if n != 1:
        raise RuntimeError("자리를 못 찾았다 (%d): %s" % (n, old[:100]))
    return src.replace(old, new)


def apply(src):
    if "const TQ_TITLE_M = " in src:
        return src
    if "진영 칸은 학원 이름 길이만큼 늘어난다" not in src:
        raise RuntimeError("apply_tqgrow.py 를 먼저 돌린다")
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
