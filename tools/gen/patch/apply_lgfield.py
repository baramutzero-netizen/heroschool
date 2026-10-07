"""3인 리그(졸업생 리그) 경기 필드를 시내 대회로 (1007) — 몇 번을 돌려도 같은 결과.

    python3 apply_lgfield.py <game.html>

예전에는 본선(final) 필드였다. 시내 대회 필드로 바꾸면 가로 화면에서는 시내 대회와 같은 쿼터뷰 판(지도 · 액자 · 단추 판)이 뜬다.
5인 리그는 그대로 본선 필드."""
import sys

OLD = '  openBattle(m.b, {titleA:m.A.acad, titleB:m.B.acad, field:"final", bgm:"league", jingle:true,   /* 졸업생 리그 — 본선 필드 · 본선 세팅 (0930) */\n'
NEW = '  openBattle(m.b, {titleA:m.A.acad, titleB:m.B.acad, field:"citytournament", bgm:"league", jingle:true,   /* 3인 리그 — 시내 대회 필드 (1007 · 예전: 본선 필드) */\n'


def apply(src):
    if NEW in src:
        return src
    n = src.count(OLD)
    if n != 1:
        raise RuntimeError("자리를 못 찾았다 (%d): %s" % (n, OLD[:80]))
    return src.replace(OLD, NEW)


if __name__ == "__main__":
    path = sys.argv[1]
    raw = open(path, encoding="utf-8", newline="").read()
    crlf = "\r\n" in raw
    src = apply(raw.replace("\r\n", "\n"))
    if crlf:
        src = src.replace("\n", "\r\n")
    open(path, "w", encoding="utf-8", newline="").write(src)
    print("applied", len(raw), "->", len(src), "chars", "· crlf" if crlf else "")
