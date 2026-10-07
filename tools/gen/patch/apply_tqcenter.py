"""대회 쿼터뷰 화면을 나무 테두리 가운데로 맞춘다 (1008) — 몇 번을 돌려도 같은 결과. apply_tqalign.py 다음에 돌린다.

    python3 apply_tqcenter.py <game.html>

· 나무 테두리(TOURNAMENT_LAYOUT.frame) 가운데가 전투판(field) 가운데보다 오른쪽으로 27px(편집기) 치우쳐 있다 —
  왼쪽(용)보다 오른쪽(기사) 장식이 넓다. 전투판을 화면 가운데에 두면 화면 전체가 오른쪽으로 치우쳐 보였다
· 전투 화면 전체를 그만큼 왼쪽으로 옮겨 테두리 가운데를 화면 가운데에 맞춘다 (tournamentLayoutFit)
· BATTLE START · VICTORY · DEFEAT 배너는 전투판 가운데에 놓여 테두리보다 왼쪽으로 보였다 — 테두리 가운데로 (bannerPlace)"""
import sys

FN = """/* 1008 — 쿼터뷰 나무 테두리 가운데가 전투판 가운데보다 오른쪽으로 치우친 만큼 (편집기 px · 왼쪽 용보다 오른쪽 기사 장식이 넓다).
   전투 화면 전체를 그만큼 왼쪽으로 옮기고(tournamentLayoutFit), 배너는 그만큼 오른쪽으로 놓아(bannerPlace) 둘 다 화면 가운데에 온다 */
function tqFrameDx(){ const L = TOURNAMENT_LAYOUT; return (L.frame.x + L.frame.w/2) - (L.field.x + L.field.w/2); }
"""

EDITS = [
    ("  if(r && r.width > 40 && r.height > 40){ L = Math.max(0, r.left); T = Math.max(0, r.top); R = Math.min(vw, r.right); Bt = Math.min(vh, r.bottom); }\n",
     "  if(r && r.width > 40 && r.height > 40){\n"
     "    const dx = st.closest(\".tournament-quarter\") ? tqFrameDx() * (r.width / (st.offsetWidth || r.width)) : 0;   // 1008 — 쿼터뷰는 나무 테두리 가운데로\n"
     "    L = Math.max(0, r.left + dx); T = Math.max(0, r.top); R = Math.min(vw, r.right + dx); Bt = Math.min(vh, r.bottom); }\n"),
    ("function tournamentLayoutFit(){const m=document.querySelector('.tournament-quarter');if(m)m.style.setProperty('transform','scale('+Math.min(1,(innerWidth-16)/1800,(innerHeight-16)/1120)+')','important');}\n",
     FN +
     "function tournamentLayoutFit(){const m=document.querySelector('.tournament-quarter');if(!m)return;const s=Math.min(1,(innerWidth-16)/1800,(innerHeight-16)/1120);\n"
     " m.style.setProperty('transform','translateX('+(-tqFrameDx()*s).toFixed(1)+'px) scale('+s+')','important');   // 1008 — 테두리 가운데를 화면 가운데로\n"
     " document.querySelectorAll('.bt-banner').forEach(bannerPlace);}   // 창 크기가 바뀌면 배너도 새 자리로\n"),
]


def sub1(src, old, new):
    n = src.count(old)
    if n != 1:
        raise RuntimeError("자리를 못 찾았다 (%d): %s" % (n, old[:100]))
    return src.replace(old, new)


def apply(src):
    if "function tqFrameDx(){" in src:
        return src
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
