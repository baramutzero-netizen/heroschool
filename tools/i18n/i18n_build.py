"""영어판 (1010) — 빌드 때 한국어 글을 번역 함수로 감싼다. game.html 원본은 한국어 그대로 둔다.

wrap.py · wrap_site.py 가 strip_dev 다음에 부른다:  src = apply_i18n(src)   (wrap_site 는 relink 앞 — 영어 표 속 그림 주소도 같이 바뀐다)

· 인라인 <script> 안의 한글 문자열 "…" → _T("…") · 한글이 든 템플릿 `…${x}…` → _L`…${x}…` (태그 템플릿).
  한국어로 실행하면 _T · _L 은 원래 글을 그대로 돌려준다 — 빌드 전과 같은 화면 · 같은 동작 (tools/i18n/check_i18n.py 가 견준다).
  이름이 _T · _L · _LC 인 것은 게임 코드의 지역 변수(T · L)와 겹치지 않게 — 게임 코드에 그 이름이 생기면 변환하지 않고 경고한다.
· HTML 이 든 글은 글 단위로 나눈다 (2단계 · 1010): 블록 태그(div · p · button · td …)가 경계, 문장 안의 b · strong · i · em · small · br …
  은 글에 남는다. span 은 앞뒤에 글이 있어 문장 안에 끼어 있을 때만 글에 남는다. title · aria-label · alt · placeholder 값은 따로 한 단위.
  그래서 영어 표의 키는 HTML 째가 아니라 '상담실' · '{0} 지난 상담은 일지의 <b>상담 기록</b>에서 본다.' 같은 글이 된다.
  템플릿은 `<h2>${_L`상담실`}</h2>…` 처럼 안쪽 템플릿으로, 문자열은 ("<p>" + _T("…") + "</p>") 처럼 이어 붙이기로 바꾼다.
· 영어 표 — tools/i18n/en.json + tools/i18n/en/*.json (이름 차례로 합친다). 키 = 한국어 원문(템플릿은 ${…} 자리를 단위마다 {0} {1} …).
  같은 한국어가 곳에 따라 다르게 옮겨져야 하면 '맨 위 선언 이름|한국어' 키 (예: "MENU_SHORT|상담") — 그 선언 안에서만 그 값이 먼저.
· 건너뛰는 곳 — 정규식 · 객체 키 · 이미 태그가 붙은 템플릿 · <style>/<script> 안 · OPTX 블록(오프닝 캔버스 글 — 4단계에서 따로) ·
  바로 앞에 /*no-i18n*/ 주석을 단 글 (언어 이름 '한국어' · 서버로 보내는 글처럼 늘 한국어여야 하는 것).
· 언어는 <head> 맨 앞의 작은 스크립트가 정한다: 주소 ?lang=en|ko > (공개 뒤) 설정에 저장한 값 > (공개 뒤) 브라우저 언어 > 한국어.
  공개 전(config.json public:false)에는 ?lang= 주소로만 영어가 된다. <html lang> 도 여기서 바꾼다.
  공개 뒤 첫 방문에 세이브가 이미 있으면(공개 전부터 하던 사람) 브라우저 언어와 상관없이 한국어로 기억한다 (head_script).
· 안전장치 — 짝이 안 맞는 등 변환이 실패하거나, node 가 있을 때 변환한 스크립트가 문법 검사(node --check)를 못 넘으면
  경고를 찍고 변환 없이 돌려준다. 한국어판은 언제나 그대로 나간다. HS_I18N=0 으로 빌드하면 변환을 아예 하지 않는다.
· 점검 — 영어 표의 키가 객체 키나 정규식에도 쓰이면 경고 (영어에서 그 글을 찾는 코드가 어긋난다) · 번역된 단위 수 · 지금 빌드에 없는 키 수.

영어 표의 값: 자리표 {0} {1} … 는 순서를 바꿔도 되고, 조사 자리처럼 안 써도 된다. 단수 · 복수는 {0|student|students} (값이 1 이면 앞).
  '_' 로 시작하는 키(설명)와 빈 값은 무시한다 — 빈 값이면 한국어가 그대로 보인다.

  python3 tools/i18n/i18n_build.py game.html out.html          변환 시험
  python3 tools/i18n/i18n_build.py --dump game.html keys.json  번역 단위 목록 (키 · 맨 위 선언 · 줄 · 자리표 식 · 번역 여부)
"""
import bisect, glob, json, os, re, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
HANG = re.compile(r'[가-힣ㄱ-ㆎ改]')     # 改 — 진형 강화 꼬리 '·改' (1010 · 3단계 — 영어에서 '+')
REGEX_KW = {'return', 'typeof', 'instanceof', 'in', 'of', 'new', 'delete', 'void', 'throw', 'case', 'do', 'else', 'yield', 'await'}
PAREN_KW = {'if', 'while', 'for', 'with'}          # 이 괄호 뒤의 / 는 정규식 (if(x) /re/.test(s))
DECL_RE = re.compile(r'\s*\*?\s*([A-Za-z_$][\w$]*)')
STMT_KW = {'if', 'for', 'while', 'do', 'switch', 'try', 'return', 'throw', 'break', 'continue', 'else', 'new', 'delete', 'void',
           'typeof', 'await', 'yield', 'async', 'import', 'export', 'debugger', 'with', 'case', 'default', 'catch', 'finally', 'in', 'of'}
SKIP_MARKERS = [("/* OPTX 시작 */", "/* OPTX 끝 */")]
SKIP_COMMENT = '/*no-i18n*/'
WS = ' \t\r\n\u00a0\ufeff\u2028\u2029'

# ── HTML 나누기 ──
INLINE = {'b', 'strong', 'i', 'em', 'u', 's', 'small', 'mark', 'sub', 'sup', 'br', 'wbr', 'code', 'kbd', 'abbr', 'q', 'cite',
          'var', 'time', 'ruby', 'rt', 'rp', 'bdi', 'bdo', 'del', 'ins'}
SPAN_LIKE = {'span', 'font', 'a'}               # 문장 안(앞뒤에 글)이면 글에 남고, 아니면 경계
RAW_TAGS = {'style', 'script'}                  # 안의 글은 옮기지 않는다
VOID = {'br', 'wbr', 'img', 'input', 'hr', 'meta', 'link', 'area', 'base', 'col', 'embed', 'source', 'track', 'param'}
ATTR_TR = {'title', 'aria-label', 'alt', 'placeholder', 'value', 'label', 'data-tip', 'aria-description', 'aria-valuetext',
           'aria-roledescription'}
TAGNAME_RE = re.compile(r'<(/?)([A-Za-z][A-Za-z0-9-]*)')
NL_RE = re.compile(r'[ \t]*\n[ \t\n]*')
OPEN_TAG_RE = re.compile(r'<([A-Za-z][A-Za-z0-9-]*)\s[^<>]*>')
CSS_RE = re.compile(r'[.#a-zA-Z][-\w.#:>\s]*\{[^{}]*:[^{}]*;')


def norm_key(k):
    """영어 표의 키 모양 — 줄바꿈이 낀 빈칸은 한 칸으로, 글 안 태그의 속성은 뺀다 (<b style=…> → <b>). 런타임(_T · _Lx)과 같은 규칙"""
    if '\n' in k:
        k = NL_RE.sub(' ', k)
    if '<' in k:
        k = OPEN_TAG_RE.sub(r'<\1>', k)
    return k
ATTR_RE = re.compile(r'([A-Za-z_:@][-A-Za-z0-9_:.@]*)\s*=\s*(\\?["\'])')


class ScanError(Exception):
    pass


def _is_id_char(c):
    return c.isalnum() or c in '_$' or ord(c) > 127


class Lit:
    __slots__ = ('kind', 'a', 'b', 'hh', 'prev', 'lastc', 'mark', 'slots', 'top', 'callee')

    def __init__(self, **kw):
        for k, v in kw.items():
            setattr(self, k, v)


class Scanner:
    """JS 한 덩어리에서 문자열 · 템플릿 · 정규식 위치를 찾는다 (주석은 건너뛴다).
    Lit: kind 'str'|'tpl'|'re' · a, b(끝 다음) · hh 한글 있음 · prev 앞 토큰 갈래 · lastc 앞 글자(주석 빼고) · mark /*no-i18n*/ ·
         slots 템플릿의 ${ } 자리 [($ 위치, } 위치)…] · top 맨 위 선언 이름 · callee 가장 가까운 호출 이름"""

    def __init__(self, code):
        self.s = code
        self.n = len(code)
        self.lits = []
        self.top = ''
        self.pstack = []           # 여는 괄호마다 [if/while 괄호인가, 호출 이름]

    def scan(self):
        i = self.code(0, False, True)
        if i != self.n:
            raise ScanError('stopped at %d' % i)
        return self.lits

    def _callee(self):
        for head, name in reversed(self.pstack):
            if name:
                return name
        return ''

    def _lit(self, kind, a, b, hh, prev, lastc, mark, slots=None):
        self.lits.append(Lit(kind=kind, a=a, b=b, hh=hh, prev=prev, lastc=lastc, mark=mark, slots=slots or [],
                             top=self.top, callee=self._callee()))

    # ── 코드 (템플릿의 ${ } 안이면 짝 맞는 } 에서 멈춘다) ──
    def code(self, i, stop_brace, toplevel=False):
        s, n = self.s, self.n
        prev = ''          # '' · 'id' · 'kw' · 'val'(값 끝: 숫자 · 문자열 · ) ] · 템플릿 · 정규식) · 'op'(연산자 · 여는 괄호 등)
        lastc = ''         # 주석 · 빈칸을 뺀 바로 앞 글자 (객체 키 판단)
        word = ''          # 바로 앞 낱말 (if · while 괄호 · 호출 이름)
        skip = False       # 바로 앞이 /*no-i18n*/
        depth = 0
        base = len(self.pstack)
        stmt = toplevel    # 맨 위 문장의 첫 토큰 자리 (top 이름: NAME.x = … · NAME(…) · (IIFE))
        while i < n:
            c = s[i]
            if c in WS:
                i += 1; continue
            if c == '/' and i + 1 < n and s[i + 1] == '/':
                j = s.find('\n', i)
                i = n if j < 0 else j
                continue
            if c == '/' and i + 1 < n and s[i + 1] == '*':
                j = s.find('*/', i + 2)
                if j < 0:
                    raise ScanError('unterminated comment at %d' % i)
                skip = s[i:j + 2] == SKIP_COMMENT
                i = j + 2; continue
            if toplevel and depth == 0:
                if stmt and c == '(':
                    self.top = '(IIFE)'
                if stmt and not _is_id_char(c):
                    stmt = False
            if c == '"' or c == "'":
                j = self.string(i)
                self._lit('str', i, j, HANG.search(s, i, j) is not None, prev, lastc, skip)
                prev, lastc, word, skip = 'val', c, '', False
                i = j; continue
            if c == '`':
                tagged = prev in ('id', 'val')
                j, hh, slots = self.template(i)
                self._lit('tpl', i, j, hh, 'tagged' if tagged else prev, lastc, skip, slots)
                prev, lastc, word, skip = 'val', c, '', False
                i = j; continue
            skip = False
            if c == '/':
                if prev in ('', 'op', 'kw'):
                    j = self.regex(i)
                    self._lit('re', i, j, HANG.search(s, i, j) is not None, prev, lastc, False)
                    prev, lastc, word = 'val', '/', ''
                    i = j; continue
                prev, lastc, word = 'op', c, ''
                i += 1; continue
            if c == '{':
                depth += 1; prev, lastc, word = 'op', c, ''; i += 1; continue
            if c == '}':
                if stop_brace and depth == 0:
                    del self.pstack[base:]
                    return i
                depth -= 1; prev, lastc, word = 'op', c, ''; i += 1
                if toplevel and depth == 0:
                    stmt = True
                continue
            if c in '([':
                callee = word if (c == '(' and prev == 'id') else ''
                self.pstack.append((c == '(' and word in PAREN_KW, callee))
                prev, lastc, word = 'op', c, ''; i += 1; continue
            if c in ')]':
                head = self.pstack.pop()[0] if len(self.pstack) > base else False
                prev, lastc, word = ('op' if head else 'val'), c, ''
                i += 1; continue
            if c.isdigit() or (c == '.' and i + 1 < n and s[i + 1].isdigit()):
                j = i + 1
                while j < n and (s[j].isalnum() or s[j] in '._'):
                    if s[j] in 'eE' and j + 1 < n and s[j + 1] in '+-' and not s[i:j].lower().startswith('0x'):
                        j += 2; continue
                    j += 1
                prev, lastc, word = 'val', s[j - 1], ''
                i = j; continue
            if _is_id_char(c):
                j = i + 1
                while j < n and _is_id_char(s[j]):
                    j += 1
                w = s[i:j]
                if toplevel and depth == 0 and w in ('function', 'class', 'const', 'let', 'var') and lastc != '.':
                    m = DECL_RE.match(s, j)
                    if m:
                        self.top = m.group(1) + ('()' if w == 'function' else '')
                elif toplevel and depth == 0 and stmt and w not in STMT_KW and lastc != '.':
                    self.top = w                                   # NAME.x = … · NAME(…) 같은 맨 위 문장
                stmt = False
                prev, lastc, word = ('kw' if w in REGEX_KW else 'id'), s[j - 1], w
                i = j; continue
            if c in '+-' and i + 1 < n and s[i + 1] == c:      # ++ / -- 뒤의 / 는 나눗셈
                prev, lastc, word = 'val', c, ''
                i += 2; continue
            prev, lastc, word = 'op', c, ''
            if c == ';' and toplevel and depth == 0:
                stmt = True
            i += 1
        if stop_brace:
            raise ScanError('unterminated ${ at end')
        return i

    def string(self, i):
        s, n, q = self.s, self.n, self.s[i]
        j = i + 1
        while j < n:
            c = s[j]
            if c == '\\':
                j += 2; continue
            if c == q:
                return j + 1
            if c == '\n':
                raise ScanError('newline in string at %d' % i)
            j += 1
        raise ScanError('unterminated string at %d' % i)

    def regex(self, i):
        s, n = self.s, self.n
        j = i + 1
        cls = False
        while j < n:
            c = s[j]
            if c == '\\':
                j += 2; continue
            if c == '\n':
                raise ScanError('newline in regex at %d' % i)
            if cls:
                if c == ']':
                    cls = False
            elif c == '[':
                cls = True
            elif c == '/':
                j += 1
                while j < n and _is_id_char(s[j]):
                    j += 1
                return j
            j += 1
        raise ScanError('unterminated regex at %d' % i)

    def template(self, i):
        s, n = self.s, self.n
        j = i + 1
        hh = False
        slots = []
        while j < n:
            c = s[j]
            if c == '\\':
                j += 2; continue
            if c == '`':
                return j + 1, hh, slots
            if c == '$' and j + 1 < n and s[j + 1] == '{':
                k = self.code(j + 2, True)
                slots.append((j, k))
                j = k + 1; continue
            if not hh and HANG.match(c):
                hh = True
            j += 1
        raise ScanError('unterminated template at %d' % i)


def _next_sig(s, j):
    """j 부터 공백 · 주석을 건너뛴 첫 글자"""
    n = len(s)
    while j < n:
        c = s[j]
        if c in WS:
            j += 1; continue
        if s.startswith('//', j):
            k = s.find('\n', j); j = n if k < 0 else k; continue
        if s.startswith('/*', j):
            k = s.find('*/', j + 2); j = n if k < 0 else k + 2; continue
        return c
    return ''


def _skip_ranges(code):
    out = []
    for a, b in SKIP_MARKERS:
        i = code.find(a)
        while i >= 0:
            j = code.find(b, i)
            if j < 0:
                break
            out.append((i, j + len(b)))
            i = code.find(a, j)
    return out


_ESC = {'n': '\n', 't': '\t', 'r': '\r', 'b': '\b', 'f': '\f', 'v': '\v'}


def cook(raw):
    """JS 문자열 · 템플릿 원문 → 실제 글 (런타임이 보는 키와 같게)"""
    out, i, n = [], 0, len(raw)
    while i < n:
        c = raw[i]
        if c != '\\':
            out.append('\n' if c == '\r' and raw[i + 1:i + 2] != '\n' else ('' if c == '\r' else c)); i += 1; continue
        d = raw[i + 1:i + 2]
        if d in _ESC:
            out.append(_ESC[d]); i += 2
        elif d == '0' and not raw[i + 2:i + 3].isdigit():
            out.append('\0'); i += 2
        elif d == 'x':
            out.append(chr(int(raw[i + 2:i + 4], 16))); i += 4
        elif d == 'u' and raw[i + 2:i + 3] == '{':
            k = raw.index('}', i); out.append(chr(int(raw[i + 3:k], 16))); i = k + 1
        elif d == 'u':
            out.append(chr(int(raw[i + 2:i + 6], 16))); i += 6
        elif d == '\r':
            i += 3 if raw[i + 2:i + 3] == '\n' else 2
        elif d in ('\n', '\u2028', '\u2029'):
            i += 2
        else:
            out.append(d); i += 2
    return ''.join(out)


def js_str(s):
    """글 → JS 문자열 리터럴 (큰따옴표)"""
    return json.dumps(s, ensure_ascii=False).replace('</script', '<\\/script').replace('\u2028', '\\u2028').replace('\u2029', '\\u2029')


# ── HTML 글 단위 나누기 ────────────────────────────────────────────────
class Tok:
    __slots__ = ('t', 'a', 'b', 'name', 'kind', 'inline', 'raw')

    def __init__(self, t, a, b, name='', kind='', inline=False, raw=False):
        self.t, self.a, self.b, self.name, self.kind, self.inline, self.raw = t, a, b, name, kind, inline, raw


def _tokenize(s, a, b, slots):
    """s[a:b] 를 TEXT · SLOT · TAG 토큰으로. slots = [($ 위치, } 위치)…] (템플릿만). 태그가 아니면 글로 둔다."""
    toks, i = [], a
    sl = {p: q for p, q in slots}

    def slot_at(p):
        return sl.get(p)

    text_start = None
    while i < b:
        q = slot_at(i)
        if q is not None:
            if text_start is not None:
                toks.append(Tok('TEXT', text_start, i)); text_start = None
            toks.append(Tok('SLOT', i, q + 1)); i = q + 1; continue
        c = s[i]
        if c == '<' and i + 1 < b and (('a' <= s[i + 1].lower() <= 'z') or s[i + 1] in '/!' or slot_at(i + 1) is not None):
            if s.startswith('<!--', i):
                k = s.find('-->', i, b)
                end = (k + 3) if k >= 0 else -1
                name, kind = '!--', 'self'
            else:
                j, quote, end = i + 1, None, -1
                while j < b:
                    q2 = slot_at(j)
                    if q2 is not None:
                        j = q2 + 1; continue
                    ch = s[j]
                    if ch == '\\':
                        j += 2; continue
                    if quote:
                        if ch == quote:
                            quote = None
                    elif ch in '"\'':
                        quote = ch
                    elif ch == '>':
                        end = j + 1; break
                    elif ch == '<' and quote is None:
                        break
                    j += 1
                m = TAGNAME_RE.match(s, i)
                name = m.group(2).lower() if m else ''
                kind = 'close' if (m and m.group(1)) else ('self' if (name in VOID or s[end - 2:end] == '/>') else 'open')
            if end > 0:
                if text_start is not None:
                    toks.append(Tok('TEXT', text_start, i)); text_start = None
                toks.append(Tok('TAG', i, end, name, kind)); i = end; continue
        if text_start is None:
            text_start = i
        i += 1
    if text_start is not None:
        toks.append(Tok('TEXT', text_start, b))
    return toks


def _match(toks, i):
    """toks[i] 가 여는 태그면 짝 닫는 태그 번호 (없으면 None)"""
    name, d = toks[i].name, 0
    for j in range(i + 1, len(toks)):
        t = toks[j]
        if t.t != 'TAG' or t.name != name:
            continue
        if t.kind == 'open':
            d += 1
        elif t.kind == 'close':
            if d == 0:
                return j
            d -= 1
    return None


def _match_back(toks, i):
    name, d = toks[i].name, 0
    for j in range(i - 1, -1, -1):
        t = toks[j]
        if t.t != 'TAG' or t.name != name:
            continue
        if t.kind == 'close':
            d += 1
        elif t.kind == 'open':
            if d == 0:
                return j
            d -= 1
    return None


def _classify(s, toks):
    """태그마다 글에 남는지(inline) 경계인지 정하고, <style>/<script> 안을 raw 로 표시"""
    for i, t in enumerate(toks):
        if t.t == 'TAG':
            t.inline = t.name in INLINE
    i = 0
    while i < len(toks):                                     # <style> · <script> 안은 옮기지 않는다
        t = toks[i]
        if t.t == 'TAG' and t.kind == 'open' and t.name in RAW_TAGS:
            j = _match(toks, i)
            j = len(toks) - 1 if j is None else j
            for k in range(i, j + 1):
                toks[k].raw = True
                if toks[k].t == 'TAG':
                    toks[k].inline = False
            i = j + 1; continue
        i += 1

    def content(rng):
        has, hang = False, False
        for k in rng:
            u = toks[k]
            if u.t == 'SLOT':
                has = True
            elif u.t == 'TEXT':
                txt = s[u.a:u.b]
                if txt.strip(WS):
                    has = True
                if HANG.search(txt):
                    hang = True
        return has, hang

    def side(k, step):
        out = []
        while 0 <= k < len(toks):
            u = toks[k]
            if u.t == 'TAG' and not (u.name in INLINE):
                break
            out.append(k); k += step
        return out

    for i, t in enumerate(toks):
        if t.t == 'TAG' and t.kind == 'open' and t.name in SPAN_LIKE and not t.raw:
            j = _match(toks, i)
            if j is None:
                continue
            bh, bg = content(side(i - 1, -1))
            ah, ag = content(side(j + 1, 1))
            _, ig = content(range(i + 1, j))
            if bh and ah and (bg or ag or ig):
                t.inline = toks[j].inline = True


def _trim(s, seg):
    """글 단위 양끝의 빈칸 · 짝 없는 태그 · 통째로 감싼 태그를 밖으로. 반환 (시작, 끝, 남은 토큰) 또는 None"""
    seg = [Tok(t.t, t.a, t.b, t.name, t.kind, t.inline, t.raw) for t in seg]
    while seg:
        f = seg[0]
        if f.t == 'TEXT':
            txt = s[f.a:f.b]; k = len(txt) - len(txt.lstrip(WS))
            if k == len(txt):
                seg.pop(0); continue
            f.a += k
        l = seg[-1]
        if l.t == 'TEXT':
            txt = s[l.a:l.b]; k = len(txt) - len(txt.rstrip(WS))
            if k == len(txt):
                seg.pop(); continue
            l.b -= k
        f = seg[0]
        if f.t == 'TAG':
            j = _match(seg, 0) if f.kind == 'open' else None
            if j is None:
                seg.pop(0); continue
            if all(u.t == 'TEXT' and not s[u.a:u.b].strip(WS) for u in seg[1:j]):
                del seg[:j + 1]; continue
            if j == len(seg) - 1:
                seg.pop(); seg.pop(0); continue
        l = seg[-1]
        if l.t == 'TAG':
            i = _match_back(seg, len(seg) - 1) if l.kind == 'close' else None
            if i is None:
                seg.pop(); continue
            if all(u.t == 'TEXT' and not s[u.a:u.b].strip(WS) for u in seg[i + 1:-1]):
                del seg[i:]; continue
        break
    if not seg:
        return None
    if not any(u.t == 'TEXT' and HANG.search(s[u.a:u.b]) for u in seg):
        return None
    return seg[0].a, seg[-1].b, seg


def _attr_units(s, tag, slots):
    """태그 안의 옮길 속성 값 [(시작, 끝)…] 과 옮기지 않는 한글 속성 이름들"""
    out, other = [], []
    sl = {p: q for p, q in slots}
    i, b = tag.a, tag.b
    while i < b:
        m = ATTR_RE.search(s, i, b)
        if not m:
            break
        inside = next((q for p, q in slots if p <= m.start() <= q), None)
        if inside is not None:                       # ${ } 안의 글은 그 안쪽 리터럴이 따로 다룬다
            i = inside + 1
            continue
        name, quote = m.group(1).lower(), m.group(2)
        v0 = m.end()
        j = v0
        end = -1
        while j < b:
            q = sl.get(j)
            if q is not None:
                j = q + 1; continue
            if s.startswith(quote, j):
                end = j; break
            if s[j] == '\\' and len(quote) == 1:
                j += 2; continue
            j += 1
        if end < 0:
            break
        val = s[v0:end]
        for p, q in sorted(slots, reverse=True):              # ${ } 안의 한글은 그 안쪽 리터럴의 몫
            if v0 <= p and q < end:
                val = val[:p - v0] + val[q + 1 - v0:]
        if HANG.search(val):
            (out if name in ATTR_TR else other).append((v0, end) if name in ATTR_TR else name)
        i = end + len(quote)
    return out, other


def segment(s, a, b, slots=()):
    """s[a:b] (문자열 · 템플릿 안쪽)의 옮길 단위 [(시작, 끝, 'text'|'attr')…] 과 메모"""
    toks = _tokenize(s, a, b, slots)
    if not any(t.t == 'TAG' for t in toks):
        r = _trim(s, toks)
        return ([(r[0], r[1], 'text')] if r else []), [], False
    _classify(s, toks)
    units, notes, seg = [], [], []
    covered = []

    def flush():
        if seg:
            r = _trim(s, seg)
            if r:
                units.append((r[0], r[1], 'text')); covered.append((r[0], r[1]))
        seg.clear()

    for t in toks:
        if t.raw:
            flush()
            if t.t == 'TEXT' and HANG.search(s[t.a:t.b]):
                notes.append('raw')
            continue
        if t.t == 'TAG' and not t.inline:
            flush(); continue
        seg.append(t)
    flush()
    for t in toks:                                           # 글 단위 밖에 있는 태그의 속성
        if t.t != 'TAG' or t.raw or any(x <= t.a < y for x, y in covered):
            continue
        au, other = _attr_units(s, t, slots)
        units.extend((x, y, 'attr') for x, y in au)
        notes.extend('attr:' + o for o in other)
    units.sort()
    return units, notes, True


def tpl_key(code, a, b, slots):
    """템플릿 조각 code[a:b] (그 안의 ${ } 는 slots) → 런타임 키"""
    parts, i, n = [], a, 0
    for p, q in slots:
        if a <= p and q < b:
            parts.append(cook(code[i:p])); parts.append('{%d}' % n); n += 1; i = q + 1
    parts.append(cook(code[i:b]))
    return ''.join(parts), n


# ── 변환 ──────────────────────────────────────────────────────────────
def _ctx_name(top):
    return top[:-2] if top.endswith('()') else top


def transform_js(code, info=None, en=None):
    """반환: (새 코드, 감싼 문자열 수, 감싼 템플릿 단위 수). 실패하면 ScanError.
    info 를 주면 모은다: keys(객체 키 한글) · res(한글 정규식) · units[(키, 맨 위 선언, 호출, 위치, 종류, 자리표 식)] · notes · ctx(쓴 문맥)"""
    if re.search(r'(?<![\w$])_(?:T|L|LC|Lt|Lx)(?![\w$])', code) or \
            re.search(r'\b(?:function|var|let|const|class)\s+(?:I18N\w*|i18nKey|i18nFind)\b', code):
        raise ScanError('game code already uses a runtime name (_T · _L · _LC · I18N… · i18nKey · i18nFind)')
    en = en or {}
    info = info if info is not None else {}
    units_out = info.setdefault('units', [])
    ctx_used = info.setdefault('ctx', set())
    lits = Scanner(code).scan()
    skips = _skip_ranges(code)
    edits = []      # (위치, 차례, 끼울 글) 또는 (시작, 차례, 글, 끝) — 뒤에서부터 바꾼다
    seq = [0]
    nT = nL = 0

    def ins(pos, txt):
        seq[0] += 1; edits.append((pos, seq[0], txt, pos))

    def rep(a, b, txt):
        seq[0] += 1; edits.append((a, seq[0], txt, b))

    def ctx_for(lit, key):
        c = _ctx_name(lit.top)
        if c and (c + '|' + norm_key(key)) in en:
            return c
        return None

    def note_unit(lit, key, pos, kind, exprs=()):
        units_out.append((norm_key(key), lit.top, lit.callee, pos, kind, list(exprs)))

    for lit in lits:
        if not lit.hh or lit.mark or any(x <= lit.a < y for x, y in skips):
            continue
        a, b = lit.a, lit.b
        if lit.kind == 're':
            info.setdefault('res', []).append(code[a:b])
            continue
        if lit.kind == 'str':
            if lit.prev == 'op' and lit.lastc in '{,' and _next_sig(code, b) == ':':
                info.setdefault('keys', set()).add(cook(code[a + 1:b - 1]))
                continue                                        # 객체 키
            val = cook(code[a + 1:b - 1])
            if len(val) > 80 and '<' not in val and CSS_RE.search(val):
                info.setdefault('notes', []).append(('css', lit.top, a))
                continue                                        # CSS 글 (content:"…") — 영어는 따로 (html[lang=en] 규칙)
            units, notes, has_tags = segment(val, 0, len(val))
            info.setdefault('notes', []).extend((n, lit.top, a) for n in notes)
            if not has_tags:
                if not units:
                    continue
                c = ctx_for(lit, val)
                sp = ' ' if a > 0 and _is_id_char(code[a - 1]) else ''
                ins(b, (',%s)' % js_str(c)) if c else ')')
                ins(a, sp + '_T(')
                note_unit(lit, val, a, 'str')
                nT += 1
                continue
            if not units:
                continue
            pieces, i = [], 0
            for x, y, k in units:
                if x > i:
                    pieces.append(js_str(val[i:x]))
                key = val[x:y]
                c = ctx_for(lit, key)
                pieces.append('_T(%s%s)' % (js_str(key), (',' + js_str(c)) if c else ''))
                note_unit(lit, key, a, 'str-' + k)
                nT += 1
                i = y
            if i < len(val):
                pieces.append(js_str(val[i:]))
            sp = ' ' if a > 0 and _is_id_char(code[a - 1]) else ''
            rep(a, b, sp + '(' + ' + '.join(pieces) + ')')
            continue
        # 템플릿
        if lit.prev == 'tagged':
            continue
        units, notes, has_tags = segment(code, a + 1, b - 1, lit.slots)
        info.setdefault('notes', []).extend((n, lit.top, a) for n in notes)
        if not units:
            continue
        whole = (not has_tags) and len(units) == 1 and units[0][0] == a + 1 and units[0][1] == b - 1
        for x, y, k in units:
            key, nslot = tpl_key(code, x, y, lit.slots)
            exprs = [code[p + 2:q] for p, q in lit.slots if x <= p and q < y]
            c = ctx_for(lit, key)
            tag = ('_LC.' + c) if c else '_L'
            if c:
                ctx_used.add(c)
            if whole:
                sp = ' ' if a > 0 and _is_id_char(code[a - 1]) else ''
                ins(a, sp + tag)
            else:
                ins(x, '${' + tag + '`')
                ins(y, '`}')
            note_unit(lit, key, a, 'tpl' if whole else 'tpl-' + k, exprs)
            nL += 1
    edits.sort(key=lambda e: (e[0], e[1]), reverse=True)
    parts, end = [], len(code)
    for pos, _, txt, stop in edits:                            # 뒤에서부터 잘라 붙인다
        if stop > end:
            raise ScanError('overlapping edits at %d' % pos)
        parts.append(code[stop:end]); parts.append(txt); end = pos
    parts.append(code[:end])
    return ''.join(reversed(parts)), nT, nL


def _load_json(name, default):
    p = os.path.join(HERE, name)
    if not os.path.exists(p):
        return default
    with open(p, encoding='utf-8') as f:
        return json.load(f)


def load_en(verbose=False):
    """영어 표 — en.json + en/*.json (파일 이름 차례). 같은 키가 다른 값으로 두 번 나오면 앞의 것 + 경고"""
    files = [os.path.join(HERE, 'en.json')] + sorted(glob.glob(os.path.join(HERE, 'en', '*.json')))
    en, src, dup = {}, {}, []
    for p in files:
        if not os.path.exists(p):
            continue
        with open(p, encoding='utf-8') as f:
            d = json.load(f)
        for k, v in d.items():
            if k.startswith('_') or not isinstance(v, str) or not v.strip():
                continue
            if v == '∅':                                     # 영어에서는 비운다 (한국어 단위 조각 등)
                v = ''
            if k in en:
                if en[k] != v:
                    dup.append((k, os.path.relpath(src[k], HERE), os.path.relpath(p, HERE)))
                continue
            en[k] = v; src[k] = p
    for k, a, b in dup[:12]:
        print('i18n: 확인 — 같은 키가 두 파일에 다른 값으로: %r (%s · %s — 앞의 것을 쓴다)' % (k, a, b), file=sys.stderr)
    return en


def head_script(public, save_key=None):
    """<head> 맨 앞의 언어 정하기 — 주소 ?lang > (공개 뒤) 저장한 값 hs_lang > (공개 뒤) 브라우저 언어 > 한국어.
    공개 뒤 첫 방문(hs_lang0 표시가 없을 때)에 세이브가 이미 있으면 공개 전부터 한국어로 하던 사람 → 한국어로 기억해 둔다
    (브라우저가 영어여도 하던 언어 그대로 · 설정의 '자동'을 고르면 그때부터 브라우저를 따른다 — 표시가 남아 다시 걸리지 않는다)."""
    return ('<script>/* I18N 언어 (tools/i18n) */(function(){var P=%s,K=%s,q=null,s=null,L="ko";'
            'try{q=new URLSearchParams(location.search).get("lang")}catch(e){}'
            'if(P){try{s=localStorage.getItem("hs_lang");'
            'if(!localStorage.getItem("hs_lang0")){if(!s&&K&&localStorage.getItem(K)){s="ko";localStorage.setItem("hs_lang",s)}'
            'localStorage.setItem("hs_lang0","1")}}catch(e){}}'
            'var n=(navigator.languages&&navigator.languages[0])||navigator.language||"ko";'
            'L=(q==="en"||q==="ko")?q:(s==="en"||s==="ko")?s:P?(/^ko\\b/i.test(n)?"ko":"en"):"ko";'
            'window.HS_LANG=L;window.HS_LANG_PUBLIC=P;document.documentElement.lang=L;})();</script>') % (
        'true' if public else 'false', json.dumps(save_key) if save_key else 'null')


def _node_ok(code):
    """node --check 결과: True · False · None(node 가 없다)"""
    node = shutil.which('node')
    if not node:
        return None
    fd, p = tempfile.mkstemp(suffix='.js')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(code)
        r = subprocess.run([node, '--check', p], capture_output=True, text=True, timeout=120)
        return r.returncode == 0
    except (OSError, subprocess.SubprocessError):
        return None
    finally:
        try:
            os.unlink(p)
        except OSError:
            pass


def _report(en, info, verbose):
    """영어 표 점검 — 객체 키 · 정규식 · 번역된 단위 · 지금 빌드에 없는 키"""
    keys, res = info.get('keys', set()), info.get('res', [])
    warn = []
    for k in en:
        if '|' in k or '{' in k:
            continue
        if k in keys:
            warn.append('객체 키로도 쓰인다: %r' % k)
        elif len(k) >= 2 and any(k in r for r in res):
            warn.append('정규식에도 들어 있다: %r' % k)
    for w in warn[:20]:
        print('i18n: 확인 — ' + w + ' (영어에서 이 글로 찾는 코드를 먼저 고친다)', file=sys.stderr)
    seen, done, used = set(), 0, set()
    for key, top, callee, pos, kind, exprs in info.get('units', []):
        c = _ctx_name(top)
        hit = (c + '|' + key) if (c and (c + '|' + key) in en) else (key if key in en else None)
        if key not in seen:
            seen.add(key)
            done += hit is not None
        if hit:
            used.add(hit)
    used |= info.get('static', set())                      # 스크립트 밖 HTML(I18N.dom 이 바꾸는 글)
    stale = [k for k in en if k not in used]
    info['stale'] = stale
    if verbose:
        print('i18n: 번역 단위 %d가지 중 %d 번역됨 · 영어 표에만 있고 지금 빌드에 없는 키 %d' % (len(seen), done, len(stale)))


def _static_texts(src):
    """스크립트 · 스타일 밖 HTML 의 한글 글 · 속성 값 (런타임 I18N.dom 이 처음 한 번 바꾸는 것)"""
    html = re.sub(r'<(script|style)\b[^>]*>[\s\S]*?</\1>', ' ', src)
    out = {t.strip() for t in re.findall(r'>([^<>]+)<', html) if HANG.search(t)}
    out |= {m.group(2) for m in re.finditer(r'\b(title|aria-label|placeholder|alt)="([^"]*)"', html) if HANG.search(m.group(2))}
    return out


def js_css(path):
    """영어 화면 고침 CSS 파일 → JS 문자열 (없으면 빈 글). 주석은 뺀다"""
    if not os.path.exists(path):
        return '""'
    css = re.sub(r'/\*[\s\S]*?\*/', '', open(path, encoding='utf-8').read())
    css = re.sub(r'\s*\n\s*', '\n', css).strip()
    return json.dumps(css, ensure_ascii=False).replace('</', '<\\/')


def apply_i18n(src, verbose=True, info=None):
    """빌드 HTML 전체 → 변환한 HTML. 실패하면 경고 후 src 그대로."""
    if os.environ.get('HS_I18N') == '0':
        if verbose:
            print('i18n: HS_I18N=0 — 변환하지 않는다 (한국어만)')
        return src
    cfg = _load_json('config.json', {"public": False})
    en = load_en(verbose)
    info = {} if info is None else info
    try:
        runtime = open(os.path.join(HERE, 'i18n_runtime.js'), encoding='utf-8').read()
        parts, pos, nT, nL, main_at, checked = [], 0, 0, 0, None, None
        for m in re.finditer(r'<script\b([^>]*)>([\s\S]*?)</script>', src):
            if re.search(r'\bsrc\s*=', m.group(1)) or not HANG.search(m.group(2)):
                continue
            b0, old = m.start(2), m.group(2)
            new, t, l = transform_js(old, info, en)
            ok = _node_ok(new) if (t or l) else True
            if ok is False and _node_ok(old):
                raise ScanError('변환한 스크립트가 문법 검사(node --check)를 못 넘는다 — %d번째 글자부터의 스크립트' % b0)
            checked = checked if ok is None else True
            parts.append(src[pos:b0])
            if main_at is None:
                main_at = len(parts)
                parts.append(None)                               # 런타임 자리 — 문맥 태그를 다 모은 뒤 채운다
            parts.append(new)
            pos = m.end(2)
            nT += t; nL += l
        parts.append(src[pos:])
        info['static'] = _static_texts(src)
        if main_at is not None:
            table = json.dumps(en, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/').replace('<!--', '<\\!--')
            ctx = '{' + ','.join('%s:_Lt(%s)' % (js_str(c), js_str(c)) for c in sorted(info.get('ctx', ()))) + '}'
            css = [js_css(os.path.join(HERE, n)) for n in ('en_layout.css', 'en_layout_rbook.css')]
            parts[main_at] = '\n' + runtime.replace('/*@@EN@@*/{}', table).replace('/*@@CTX@@*/{}', ctx) \
                .replace('/*@@CSS@@*/""', css[0]).replace('/*@@RBCSS@@*/""', css[1]) + '\n'
        out = ''.join(parts)
        sk = re.search(r'const SAVE_KEY = "([^"]+)";', src)              # 공개 뒤 첫 방문 — 이미 세이브가 있으면 한국어 그대로
        out = head_script(bool(cfg.get('public')), sk.group(1) if sk else None) + out   # game.html 은 머리말 없는 조각 — 맨 앞이 곧 <head> 안
        if verbose:
            print(f"i18n: 문자열 {nT} · 템플릿 단위 {nL} 감쌈 · 영어 표 {len(en)}줄 · 공개 {bool(cfg.get('public'))}"
                  + (" · 문법 검사 통과" if checked else " · 문법 검사 못 함(node 없음)"))
        _report(en, info, verbose)
        return out
    except (ScanError, OSError, ValueError) as e:
        print(f"i18n: 경고 — 변환하지 못해 한국어만으로 빌드한다 ({e})", file=sys.stderr)
        return src


def _units_of(src, en):
    """HTML 전체 → [(단위, 줄 번호)…] · 메모"""
    rows, notes = [], []
    for m in re.finditer(r'<script\b([^>]*)>([\s\S]*?)</script>', src):
        if re.search(r'\bsrc\s*=', m.group(1)) or not HANG.search(m.group(2)):
            continue
        info = {}
        transform_js(m.group(2), info, en)
        base = src.count('\n', 0, m.start(2))
        nl = [i for i, c in enumerate(m.group(2)) if c == '\n']
        for u in info['units']:
            rows.append((u, base + bisect.bisect_right(nl, u[3]) + 1))
        for n, top, pos in info.get('notes', []):
            notes.append({'note': n, 'top': top, 'line': base + bisect.bisect_right(nl, pos) + 1})
    return rows, notes


def dump_units(src_path, out_path):
    """번역 단위 목록 — 키 · 맨 위 선언 · 호출 · 줄(game.html) · 종류 · 자리표 식 · 영어 값 · dev(배포 빌드에 없음)"""
    src = open(src_path, encoding='utf-8').read().replace('\r\n', '\n')
    en = load_en()
    prod = None
    root = os.path.dirname(os.path.dirname(HERE))
    if root not in sys.path:
        sys.path.insert(0, root)
    try:                                                     # 배포 빌드(개발용 블록을 뺀 것)에 있는 키
        from build_strip import strip_dev
        prod = {u[0] for u, _ in _units_of(strip_dev(src), en)[0]}
    except ImportError:
        pass
    units, notes = _units_of(src, en)
    rows = []
    for (key, top, callee, pos, kind, exprs), line in units:
        c = _ctx_name(top)
        hit = (c + '|' + key) if (c and (c + '|' + key) in en) else (key if key in en else None)
        rows.append({'key': key, 'top': top, 'callee': callee, 'line': line, 'kind': kind, 'exprs': exprs,
                     'en': en.get(hit) if hit else None, 'via': hit, 'dev': prod is not None and key not in prod})
    rows.extend(notes)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(rows, f, ensure_ascii=False, indent=0)
    u = [r for r in rows if 'key' in r and not r['dev']]
    print('단위 %d (고유 %d) · 번역 %d · 메모 %d → %s' % (len(u), len({r['key'] for r in u}), sum(1 for r in u if r['en']),
                                                     len(notes), out_path))


if __name__ == '__main__':
    if sys.argv[1:2] == ['--dump']:
        dump_units(sys.argv[2], sys.argv[3])
    else:
        src = open(sys.argv[1], encoding='utf-8').read()
        open(sys.argv[2], 'w', encoding='utf-8').write(apply_i18n(src))
