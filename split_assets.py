"""분리 1단계 (0928) — game.html 에 박혀 있던 그림 · 효과음(data: URI)을 assets/ 폴더의 파일로 뺀다.

· 그냥 보여 주는 그림 · 효과음 → assets/<묶음>/<이름>.webp 같은 실제 파일. 코드에는 "assets/…?v=해시" 경로가 남는다.
· 캔버스에서 픽셀을 읽는 그림(학생 스프라이트 머리색 치환 · 이펙트 색 입히기) → assets/…​.js 로 감싼다.
  파일로 연 문서(file://)에서는 그림 파일을 캔버스로 읽을 수 없어서(보안) data: 를 그대로 JS 파일에 담아
  <script src> 로 먼저 읽고, 코드에서는 HS_A["이름"] 으로 꺼내 쓴다.
· 글꼴(학원 일지 테스트용) · 애니메이션 테스트 안의 그림은 개발 전용이라 그대로 둔다.

pack 스크립트(sprites/pack.py 등)가 game.html 에 data: 를 다시 넣어도 괜찮다 — wrap.py · wrap_site.py 가
빌드 전에 이 스크립트를 돌려 다시 뺀다. 이름이 같으면 같은 파일을 덮어쓰고, 경로 뒤 ?v= 가 바뀌어 캐시도 새로 받는다.

    python split_assets.py        # game.html 을 제자리에서 정리 (바뀐 게 없으면 그대로)
"""
import base64, hashlib, os, re, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR = "assets"
EXT = {"image/webp": "webp", "image/png": "png", "image/jpeg": "jpg", "image/gif": "gif", "audio/mpeg": "mp3"}
CANVAS = {"SPR_IMG", "SPR_X_IMG", "FX_IMG"}          # getImageData 로 픽셀을 읽는 그림
SKIP_BLOCKS = ["AVATAR_LAB"]                        # 개발 전용 — 문자열 안에 HTML 로 들어 있다

# 따옴표로 감싼 JS 문자열 하나가 통째로 data: 인 경우만 (CSS url(…) · 이스케이프된 \" 안쪽은 건드리지 않는다)
URI = re.compile(r'(?<!\\)"data:([a-z]+/[a-z0-9+.-]+);base64,([A-Za-z0-9+/=]+)"')
KEY = re.compile(r'(?:([A-Za-z_$][\w$]*)|"([^"\\]{1,80})")\s*[:=]\s*$')
OBJKEY = re.compile(r'"([^"\\]{1,80})"\s*:\s*\{[^{}]*$')
HEADNAME = re.compile(r'\s*(?:(?:const|let|var)\s+)?([A-Za-z_$][\w$]*)')
HSREF = re.compile(r'HS_A\["([^"]+)"\]')
TAGS = re.compile(r'<!-- ASSET_SCRIPTS_START -->.*?<!-- ASSET_SCRIPTS_END -->\n?', re.S)


def _slug(t):
    t = re.sub(r"[^A-Za-z0-9_.-]+", "-", t).strip("-").lower()
    return t or "x"


def _ver(data):
    return hashlib.sha1(data).hexdigest()[:8]


def _write(path, data):
    """내용이 같으면 건드리지 않는다 (수정 시각이 그대로 남게)"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if os.path.exists(path):
        with open(path, "rb") as f:
            if f.read() == data:
                return False
    with open(path, "wb") as f:
        f.write(data)
    return True


def _name(s, start):
    """data: 앞 글자를 보고 '묶음/이름' 을 정한다 — 예: FIELD_IMG={"spring":"…" → field_img/spring"""
    pre = s[max(0, start - 300):start]
    m = KEY.search(pre)
    key = (m.group(1) or m.group(2)) if m else None
    if key == "src":                                   # MON_IMG={"mon_x":{"w":..,"src":"…"}}
        o = OBJKEY.search(pre)
        key = o.group(1) if o else key
    ls = s.rfind("\n", 0, start) + 1
    h = HEADNAME.match(s, ls, min(start, ls + 200))
    head = h.group(1) if h else None
    if not head or head in ("return",):
        head = "misc"
    if not key or key == head:
        return head, _slug(head)
    return head, _slug(head) + "/" + _slug(key)


def split(src, root=ROOT, log=print):
    skip = []
    for b in SKIP_BLOCKS:
        a = src.find("/* %s_START */" % b)
        e = src.find("/* %s_END */" % b, a)
        if a >= 0 and e > a:
            skip.append((a, e))
    used, out, pos, n, nbytes, changed = {}, [], 0, 0, 0, 0
    for m in URI.finditer(src):
        if any(a < m.start() < e for a, e in skip):
            continue
        ext = EXT.get(m.group(1))
        if not ext:
            continue
        data = base64.b64decode(m.group(2))
        head, name = _name(src, m.start())
        rel = name + "." + ext
        if rel in used and used[rel] != data:          # 같은 이름에 다른 그림 — 뒤에 번호
            i = 2
            while f"{name}-{i}.{ext}" in used and used[f"{name}-{i}.{ext}"] != data:
                i += 1
            rel = f"{name}-{i}.{ext}"
        used[rel] = data
        if head in CANVAS:
            js = ('HS_A["%s"]="data:%s;base64,%s";\n' % (rel, m.group(1), m.group(2))).encode()
            changed += _write(os.path.join(root, ASSET_DIR, rel + ".js"), js)
            rep = 'HS_A["%s"]' % rel
        else:
            changed += _write(os.path.join(root, ASSET_DIR, rel), data)
            rep = '"%s/%s?v=%s"' % (ASSET_DIR, rel, _ver(data))
        out.append(src[pos:m.start()]); out.append(rep); pos = m.end()
        n += 1; nbytes += m.end() - m.start()
    out.append(src[pos:])
    src = "".join(out)
    src = asset_tags(src, root)
    if n:
        log(f"split_assets: {n}개를 assets/ 로 뺐다 (-{nbytes/1e6:.2f}MB · 새로 쓰거나 바뀐 파일 {changed}개)")
    return src


def asset_tags(src, root=ROOT):
    """HS_A["…"] 로 쓰는 그림의 <script src> 를 게임 코드 바로 앞에 다시 적는다"""
    keys = list(dict.fromkeys(HSREF.findall(src)))
    src = TAGS.sub("", src)
    if not keys:
        return src
    tags = ["<!-- ASSET_SCRIPTS_START -->", "<script>var HS_A = {};</script>"]
    for k in keys:
        p = os.path.join(root, ASSET_DIR, k + ".js")
        if not os.path.exists(p):
            raise RuntimeError(f"split_assets: {ASSET_DIR}/{k}.js 가 없다 — pack 스크립트를 다시 돌리거나 파일을 되살려야 한다")
        with open(p, "rb") as f:
            v = _ver(f.read())
        tags.append(f'<script src="{ASSET_DIR}/{k}.js?v={v}"></script>')
    tags.append("<!-- ASSET_SCRIPTS_END -->\n")
    i = src.index("<div id=\"app\">")
    j = src.index("\n<script>", i) + 1                  # 게임 코드(첫 <script>) 바로 앞
    return src[:j] + "\n".join(tags) + src[j:]


def relink(src, prefix):
    """배포본(site/index.html)처럼 다른 폴더에 놓이는 문서 — assets/ 경로 앞에 prefix 를 붙인다"""
    return re.sub(r'(["\'(])' + ASSET_DIR + r'/', lambda m: m.group(1) + prefix + ASSET_DIR + "/", src)


def split_file(path=os.path.join(ROOT, "game.html")):
    with open(path, encoding="utf-8", newline="") as f:
        src = f.read()
    new = split(src, os.path.dirname(os.path.abspath(path)))
    if new != src:
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(new)
    return new


if __name__ == "__main__":
    split_file(sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "game.html"))
