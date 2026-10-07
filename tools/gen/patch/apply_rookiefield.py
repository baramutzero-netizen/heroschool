"""봄 신인전 경기 필드를 시내 대회로 (1007) — 몇 번을 돌려도 같은 결과.

    python3 apply_rookiefield.py <game.html>

예전에는 필드를 주지 않아 그 계절 필드였다. 시내 대회 필드로 바꾸면 가로 화면에서는 시내 대회 쿼터뷰 지도가 뜬다.
같은 함수를 쓰는 다른 대회(isSpring 이 아닌 쪽)는 그대로."""
import sys

OLD = '        else openBattle(b, {titleA:S.acadName, titleB:oppName, bgm:"tour", jingle:true, victory:true, defeat:true,\n'
NEW = ('        else openBattle(b, {titleA:S.acadName, titleB:oppName, field:isSpring? "citytournament" : null, bgm:"tour", jingle:true, victory:true, defeat:true,'
       '   // 1007 — 봄 신인전은 시내 대회 필드 (가로 화면은 시내 대회 쿼터뷰)\n')


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
