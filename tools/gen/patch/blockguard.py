"""블록 지킴이 (1007) — apply_sched · apply_desk 가 game.html 의 블록을 통째로 갈아 끼우기 전에,
지난번에 넣은 블록이 그대로인지 본다. 누군가 game.html 에서 블록 안을 직접 고쳤다면 멈춘다 (덮어쓰면 그 수정이 사라진다).

· 블록 = 시작 표시(/* SCHED_SCROLL_START …)부터 끝 표시(/* SCHED_SCROLL_END */)까지
· 비교할 때 그림 줄(const SCHED_ART / SCHED_GEO / MDESK_ART / MDESK_GEO = …)은 뺀다 — 빌드(split_assets)가 data: 를 assets 경로로 바꾸기 때문
· 지난번 지문은 blocks.sha.json (이 폴더). 처음이거나 지문이 없으면 그냥 지나간다
· 블록 파일(*_block.js · *_block.css)을 고친 건 상관없다 — 비교 대상은 game.html 쪽 블록이다
· 그래도 덮어써야 하면 --force"""
import hashlib, json, os, re

HERE = os.path.dirname(os.path.abspath(__file__)) + "/"
STATE = HERE + "blocks.sha.json"
SKIP = ("const SCHED_ART = ", "const SCHED_GEO = ", "const MDESK_ART = ", "const MDESK_GEO = ")


def _norm(s):
    return "\n".join(l for l in s.replace("\r\n", "\n").split("\n") if not l.startswith(SKIP)).strip()


def _sha(s):
    return hashlib.sha1(_norm(s).encode("utf-8")).hexdigest()[:16]


def _find(src, start, end):
    m = re.search(re.escape(start) + r".*?" + re.escape(end), src, flags=re.S)
    return m.group(0) if m else None


def _load():
    try:
        return json.load(open(STATE, encoding="utf-8"))
    except Exception:
        return {}


def check(src, blocks, force=False):
    """blocks = [(이름, 시작 표시, 끝 표시)] — game.html 쪽 블록이 지난번 넣은 그대로가 아니면 멈춘다"""
    st, bad = _load(), []
    for name, start, end in blocks:
        cur = _find(src, start, end)
        if cur is not None and name in st and _sha(cur) != st[name]:
            bad.append(name)
    if bad and not force:
        raise SystemExit("멈춤 — game.html 의 블록 %s 이(가) 지난번 넣은 뒤로 바뀌었다 (누군가 game.html 에서 직접 고쳤다).\n"
                         "그 수정을 블록 파일(*_block.js · *_block.css)로 옮긴 뒤 다시 돌리거나, 덮어써도 되면 --force 를 붙인다." % ", ".join(bad))
    if bad:
        print("주의 — --force: 바뀐 블록 %s 을(를) 덮어쓴다" % ", ".join(bad))


def record(src, blocks):
    st = _load()
    for name, start, end in blocks:
        cur = _find(src, start, end)
        if cur is not None:
            st[name] = _sha(cur)
    json.dump(st, open(STATE, "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)
