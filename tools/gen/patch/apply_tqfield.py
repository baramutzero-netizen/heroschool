"""쿼터뷰 지도도 필드 배치 실험실의 '전투 필드' 확대 · 이동을 받는다 (1007) — 몇 번을 돌려도 같은 결과. apply_tqui.py 다음에 돌린다.

    python3 apply_tqfield.py <game.html>

· BATTLE_TUNE.field[필드].quarter = {zoom, x, y} — 가로 화면 쿼터뷰 지도. 확대는 전투판 가운데를 기준으로, x · y 는 전투판 크기의 % 만큼 옮긴다
  (예전 landscape 값은 쿼터뷰가 아닌 옛 필드 그림 몫이라 쿼터뷰 지도에는 쓰지 않는다)
· 지도를 옮기면 클로즈업 가운데(바닥 문장) · 카메라 줌 가운데도 같이 따라간다"""
import sys

FN = r"""/* 1007 — 쿼터뷰 지도 자리 + 필드 배치 실험실 '전투 필드'의 확대 · 이동 (BATTLE_TUNE.field[필드].quarter = {zoom, x, y}).
   확대는 전투판 가운데를 기준으로 · x · y 는 전투판 크기의 % 만큼 옮긴다. 편집기 좌표 {x,y,w,h} 로 돌려준다 */
function tqMapRect(fk, m, F){
  const t = (((bfTune().field)||{})[fk]||{}).quarter; if(!t) return m;
  const z = +t.zoom || 1, cx = F.x + F.w/2, cy = F.y + F.h/2;
  return Object.assign({}, m, {x: cx + (m.x - cx)*z + (+t.x||0)*F.w/100, y: cy + (m.y - cy)*z + (+t.y||0)*F.h/100, w: m.w*z, h: m.h*z});
}
"""
FN_AT = "function tournamentLayoutApply(fk){\n"

EDITS = [
    (" const L=TQ_MAPS[qk].map?{...TOURNAMENT_LAYOUT,map:TQ_MAPS[qk].map}:TOURNAMENT_LAYOUT,F=L.field;\n",
     " const L=TQ_MAPS[qk].map?{...TOURNAMENT_LAYOUT,map:TQ_MAPS[qk].map}:TOURNAMENT_LAYOUT,F=L.field;\n"
     " const M=tqMapRect(fk,L.map,F);   // 1007 — 지도 자리 (필드 배치 실험실의 확대 · 이동을 얹은 것)\n"),
    ("place(im,L.map,F);set(im,'transform-origin',(F.w/2-(L.map.x-F.x))+'px '+(F.h/2-(L.map.y-F.y))+'px');",
     "place(im,M,F);set(im,'transform-origin',(F.w/2-(M.x-F.x))+'px '+(F.h/2-(M.y-F.y))+'px');"),
    ("stage._tqMark={x:L.map.x-F.x+mk.mx*L.map.w/1536,y:L.map.y-F.y+mk.my*L.map.h/1024};",
     "stage._tqMark={x:M.x-F.x+mk.mx*M.w/1536,y:M.y-F.y+mk.my*M.h/1024};"),
    ("     — 배율은 땅이 시작하는 선을 기준으로 키운다(유닛 발밑이 그대로 남게).\n",
     "     — 배율은 땅이 시작하는 선을 기준으로 키운다(유닛 발밑이 그대로 남게).\n"
     "   field[필드].quarter = {zoom, x, y} — 가로 화면의 대회 쿼터뷰 지도 (1007). 배율은 전투판 가운데 기준 · x · y 는 전투판 크기 %.\n"
     "     쿼터뷰로 보이는 필드는 가로 화면에서 옛 필드 그림(landscape 값)을 쓰지 않는다.\n"),
]


def sub1(src, old, new):
    n = src.count(old)
    if n != 1:
        raise RuntimeError("자리를 못 찾았다 (%d): %s" % (n, old[:100]))
    return src.replace(old, new)


def apply(src):
    if "function tqMapRect(" in src:
        return src
    if "function tqTune(){" not in src:
        raise RuntimeError("apply_tqui.py 를 먼저 돌린다")
    src = sub1(src, FN_AT, FN + FN_AT)
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
