"""전투 대사 (1015 · 스타일리시 전투) — 선공 · 막타 · 첫 치명타(입힘 · 맞고 버팀) 대사 표를 게임에 넣는다

    python3 tools/gen/blines/apply_blines.py            # 저장소 맨 위에서 · 몇 번 돌려도 같다

원본 tools/gen/blines/lines.json (한국어 ko · 영어 en · 일본어 ja) →
  game.html 의 BL_LINES 덩어리 (/* BL_LINES — … */ ~ /* BL_LINES 끝 */ · 없으면 function hrFill 앞에 넣는다 · CRLF 그대로)
  tools/i18n/en/battle.json · ja/battle.json 의 '_BL_LINES' 칸 (그 칸의 예전 줄은 지우고 새로 — 한국어를 고쳐도 옛 키가 남지 않는다)
first · last = 성격마다 셋 / crit · taken = 직업 × 성격. 학생은 성별이 없다 · 허세의 ‘ ’ 는 혼잣말 표시.
"""
import json, os, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lines.json")
GAME = os.path.join(ROOT, "game.html")
P9 = ["intro", "hot", "stone", "dilig", "tsun", "lively", "boast", "plain", "genius"]
JOBS = ["sword", "paladin", "monk", "archer", "rogue", "priest", "timemage", "wizard", "druid", "forcemage", "enchanter", "darkpriest", "bard",
        "spellsword", "gunner", "ninja"]
START = "/* BL_LINES — 전투 대사"
END = "/* BL_LINES 끝 */"
SECTION = "_BL_LINES"


def check(L):
    for cat in ("first", "last"):
        assert set(L[cat]) == set(P9), cat
        for p in P9:
            assert len(L[cat][p]) == 3, (cat, p)
    for cat in ("crit", "taken"):
        assert set(L[cat]) == set(JOBS), cat
        for j in JOBS:
            assert set(L[cat][j]) == set(P9), (cat, j)
    for x in entries(L):
        assert x.get("ko") and x.get("en") and x.get("ja"), x


def entries(L):
    for cat in ("first", "last"):
        for p in P9:
            for x in L[cat][p]:
                yield x
    for cat in ("crit", "taken"):
        for j in JOBS:
            for p in P9:
                yield L[cat][j][p]


def js(s):
    return json.dumps(s, ensure_ascii=False)


def block(L):
    out = [START + " (1015 · 스타일리시 전투 — 학생만): 선공 · 막타 · 첫 치명타(입힘 · 맞고 버팀). 원본 tools/gen/blines/lines.json → apply_blines.py 가 이 덩어리를 통째로 쓴다 (여기서 고치지 않는다) */",
           "const BL_LINES = {"]
    for cat, note in (("first", "선공 — 전투에서 처음 행동하는 학생 · 성격마다 셋"), ("last", "막타 — 진 쪽 마지막 학생을 쓰러뜨리는 차례 · 성격마다 셋")):
        out.append("  %s: {   /* %s */" % (cat, note))
        rows = ["    %s:[%s]" % (p, ", ".join(js(x["ko"]) for x in L[cat][p])) for p in P9]
        out.append(",\n".join(rows))
        out.append("  },")
    for cat, note in (("crit", "첫 치명타를 입힌 뒤 — 직업 × 성격"), ("taken", "첫 치명타를 맞고 버텼을 때 (쓰러지지 않고 · 기절 · 영웅의 기상이 아닐 때) — 직업 × 성격")):
        out.append("  %s: {   /* %s */" % (cat, note))
        rows = ["    %s:{%s}" % (j, ", ".join("%s:%s" % (p, js(L[cat][j][p]["ko"])) for p in P9)) for j in JOBS]
        out.append(",\n".join(rows))
        out.append("  }" + ("," if cat == "crit" else ""))
    out.append("};")
    out.append(END)
    return "\n".join(out)


def put_game(L):
    s = open(GAME, "rb").read().decode("utf-8")
    b = block(L).replace("\n", "\r\n")
    a = s.find(START)
    if a >= 0:
        e = s.find(END, a)
        assert e > a, "BL_LINES 끝 표시가 없다"
        s2 = s[:a] + b + s[e + len(END):]
    else:
        anchor = "function hrFill(s, n){"
        assert s.count(anchor) == 1, "넣을 자리(function hrFill)를 못 찾았다"
        k = s.find(anchor)
        s2 = s[:k] + b + "\r\n" + s[k:]
    if s2 != s:
        open(GAME, "wb").write(s2.encode("utf-8"))
    return s2 != s


def put_table(lang, indent, L):
    path = os.path.join(ROOT, "tools", "i18n", lang, "battle.json")
    d = json.load(open(path, encoding="utf-8"))
    keys = list(d.keys())
    rows = [(SECTION, "")] + [(x["ko"], x[lang]) for x in entries(L)]
    if SECTION in keys:
        i = keys.index(SECTION)
        j = i + 1
        while j < len(keys) and not keys[j].startswith("_"):
            j += 1
        before, after = keys[:i], keys[j:]
    else:
        before, after = keys, []
    new_keys = set(k for k, _ in rows)
    clash = [k for k in before + after if k in new_keys]
    assert not clash, "다른 칸에 같은 한국어 키가 있다: %r" % clash[:5]
    out = {}
    for k in before:
        out[k] = d[k]
    for k, v in rows:
        out[k] = v
    for k in after:
        out[k] = d[k]
    txt = json.dumps(out, ensure_ascii=False, indent=indent) + "\n"
    old = open(path, encoding="utf-8").read()
    if txt != old:
        open(path, "w", encoding="utf-8").write(txt)
    return txt != old, len(rows) - 1


def main():
    L = json.load(open(SRC, encoding="utf-8"))
    check(L)
    g = put_game(L)
    e = put_table("en", 1, L)
    j = put_table("ja", 2, L)
    print("game.html BL_LINES %s · en battle.json %s (%d줄) · ja battle.json %s (%d줄)"
          % ("바뀜" if g else "같음", "바뀜" if e[0] else "같음", e[1], "바뀜" if j[0] else "같음", j[1]))


if __name__ == "__main__":
    main()
