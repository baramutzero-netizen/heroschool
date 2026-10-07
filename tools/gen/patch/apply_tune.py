"""필드 배치 실험실(tools/field_lab.html)이 낸 BATTLE_TUNE_PATCH 를 game.html 의 BATTLE_TUNE 에 합친다 (1007).
몇 번을 돌려도 같은 결과 — 패치에 적힌 값만 바꾸고 나머지는 그대로 둔다.
묶음: field(필드 확대 · 위치) · slot(유닛 자리) · job(직업 크기) · quarter(대회 쿼터뷰 경기 이름 · 진영 칸 — apply_tqui.py 가 만든다)

    python3 apply_tune.py <game.html> <패치 파일> ["메모"]

· 패치 파일 — JSON 그대로거나, 실험실이 보여 준 글을 통째로 붙여 넣은 것 (BATTLE_TUNE_PATCH = {...} 줄을 찾아 읽는다)
· 메모 — BATTLE_TUNE 머리 주석 끝에 덧붙인다 (예: "1007 — 가로 자리 · 직업 크기 28건"). 이미 있으면 다시 붙이지 않는다
· 바뀐 값을 '이전 → 새' 로 모두 찍는다 — 실험실의 '게임에 반영할 차이점' 목록과 맞춰 보면 된다"""
import json, re, sys

HEAD = re.compile(r"^const BATTLE_TUNE = \{   /\* (.*) \*/$")
ORIENT = re.compile(r"^    (landscape|portrait):(\{.*\})$")
FIELD = re.compile(r"^    ([A-Za-z_]\w*):\{(.*)\}$")
FIELD_OR = re.compile(r"(landscape|portrait|quarter):(\{[^{}]*\})")   # quarter — 가로 화면 쿼터뷰 지도 (apply_tqfield.py)
QROW = re.compile(r"^    (title|enemy|ally):(\{.*\})$")


def read_patch(path):
    s = open(path, encoding="utf-8").read()
    i = s.find("BATTLE_TUNE_PATCH")
    j = s.index("{", i if i >= 0 else 0)
    return json.JSONDecoder().raw_decode(s[j:])[0]


def js(o):
    return json.dumps(o, ensure_ascii=False, separators=(",", ":"))


def merge(src, patch, memo=None):
    lines = src.split("\n")
    a = next(i for i, l in enumerate(lines) if l.startswith("const BATTLE_TUNE = {"))
    b = next(i for i in range(a, len(lines)) if lines[i] == "};")
    sec, changes = None, []
    out = lines[:a]
    m = HEAD.match(lines[a])
    if memo and m and memo not in m.group(1):
        out.append("const BATTLE_TUNE = {   /* %s · %s */" % (m.group(1), memo))
    else:
        out.append(lines[a])
    i = a + 1
    while i < b:
        l = lines[i]
        s = re.match(r"^  (field|slot|job|quarter):\{(\s*/\*.*\*/)?$", l)
        if not s:
            out.append(l); i += 1; continue
        sec = s.group(1); out.append(l); i += 1
        body = []                                         # 이 묶음의 줄들 ("  }," 또는 "  }" 까지)
        while not re.match(r"^  \},?$", lines[i]):
            body.append(lines[i].rstrip(",")); i += 1
        close = lines[i]; i += 1
        P = patch.get(sec) or {}
        if sec == "field":
            cur = {}                                      # 필드 → {방향 → 값}
            for l2 in body:
                f = FIELD.match(l2)
                if not f: raise RuntimeError("field 줄을 못 읽었다: " + l2[:80])
                cur[f.group(1)] = {o: json.loads(v) for o, v in FIELD_OR.findall(f.group(2))}
            for fk, po in P.items():
                for o, v in po.items():
                    old = cur.setdefault(fk, {}).get(o)
                    new = dict(old or {}, **v)
                    if new != old: changes.append(f"field {fk} {o}: {js(old)} → {js(new)}")
                    cur[fk][o] = new
            rows = ["    %s:{%s}" % (fk, ", ".join(f"{o}:{js(v)}" for o, v in d.items())) for fk, d in cur.items()]
        elif sec == "quarter":                            # 요소 → 값 (경기 이름 · 상대 진영 · 우리 진영)
            cur = {}
            for l2 in body:
                q = QROW.match(l2)
                if not q: raise RuntimeError("quarter 줄을 못 읽었다: " + l2[:80])
                cur[q.group(1)] = json.loads(q.group(2))
            for k, v in P.items():
                old = cur.get(k)
                new = dict(old or {}, **v)
                if new != old: changes.append(f"quarter {k}: {js(old) if old is not None else '없음'} → {js(new)}")
                cur[k] = new
            rows = ["    %s:%s" % (k, js(v)) for k, v in cur.items()]
        else:
            cur = {}
            for l2 in body:
                o = ORIENT.match(l2)
                if not o: raise RuntimeError(sec + " 줄을 못 읽었다: " + l2[:80])
                cur[o.group(1)] = json.loads(o.group(2))
            for orient, kv in P.items():
                d = cur.setdefault(orient, {})
                for k, v in kv.items():
                    old = d.get(k)
                    new = dict(old or {}, **v) if isinstance(v, dict) else v
                    if new != old: changes.append(f"{sec} {orient} {k}: {js(old) if old is not None else '기본값'} → {js(new)}")
                    d[k] = new
            rows = ["    %s:%s" % (o, js(v)) for o, v in cur.items()]
        out += [r + ("," if n < len(rows) - 1 else "") for n, r in enumerate(rows)]
        out.append(close)
    out += lines[b:]
    return "\n".join(out), changes


if __name__ == "__main__":
    path, ppath = sys.argv[1], sys.argv[2]
    memo = sys.argv[3] if len(sys.argv) > 3 else None
    raw = open(path, encoding="utf-8", newline="").read()
    crlf = "\r\n" in raw
    src, changes = merge(raw.replace("\r\n", "\n"), read_patch(ppath), memo)
    for c in changes: print("·", c)
    print(len(changes), "곳 바뀜")
    if crlf: src = src.replace("\n", "\r\n")
    open(path, "w", encoding="utf-8", newline="").write(src)
