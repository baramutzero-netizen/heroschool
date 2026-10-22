"""중국어 표 작업 칸 (1022) — 일본어 표의 키를 따라 번역 작업 칸(JSONL)을 뽑고, 옮긴 값(TSV)을 zh-Hans 표에 넣는다.

    python3 tools/i18n/zh_work.py export ui [--todo] [--out a.jsonl]     zh-Hans/ui.json 의 작업 칸 (표 이름: top = zh-Hans.json · ui · log · battle …)
    python3 tools/i18n/zh_work.py merge ui a.tsv [b.tsv …]               옮긴 값(줄마다 '번호<TAB>중국어')을 zh-Hans/ui.json 에 (일본어 표의 차례 그대로)
    python3 tools/i18n/zh_work.py check [ui …]                            표 점검 — 자리표 · 태그 · 한글 · 가나 · 곧은 따옴표 · GB2312 밖 글자 · 이름 겹침
    python3 tools/i18n/zh_work.py validate a.jsonl a.tsv [--partial]      옮긴 값(TSV)을 작업 칸과 견주어 점검 (빠진 번호 · 자리표 · 태그 · 글자 · --partial 은 고친 줄만)
    python3 tools/i18n/zh_work.py hant                                    번체(zh-Hant · 대만) 표를 간체 표에서 다시 만든다 — OpenCC s2twp + 대만 관례 고침
                                                                          + 손본 값(zh-Hant_fix.json) · pip: opencc
    python3 tools/i18n/zh_work.py fix ui a.tsv [b.tsv …] --lang zh-Hant   번체 검토에서 고친 값(번호 = export --lang zh-Hant ui 의 i)을 zh-Hant_fix.json 에 → hant 를 다시
    (--lang zh-Hant 로 번체 표 — export 는 간체 값 sc 도 담는다 · check 는 Big5 밖 글자를 본다)

작업 칸 한 줄 = {"i": 번호, "k": 키(한국어 원문 · 문맥 키 그대로), "keep": [값에 쓸 자리표], "josa": [조사 자리 — 쓰지 않는다],
                 "where": "맨 위 선언 · 줄", "pers": 성격 키(성격별 대사일 때 — intro · hot · … · dp1), "ja": 일본어 값, "en": 영어 값, "zh": 지금 중국어 값(있으면)}
keep 은 일본어 값이 쓴 자리표 (일본어도 조사 자리를 뺐다) — 중국어 값의 자리표 모음이 이것과 같아야 한다.
저장소 맨 위에서 돌린다. 단위 목록은 unit_ctx.py 와 같은 임시 파일(i18n_build.py --dump)을 쓴다.
"""
import glob, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import unit_ctx

JOSA = re.compile(r'^\s*(jo|ro|iga|eunn|gwa|eulr)\(')
PH = re.compile(r'\{(\d+)(?:\|[^{}|]*\|[^{}|]*)?\}')
TAG = re.compile(r'<(/?)([A-Za-z][A-Za-z0-9-]*)(?:#\d+)?[^<>]*>')
HANGUL = re.compile(r'[가-힣ㄱ-ㆎ]')
KANA = re.compile(r'[぀-ヿ]')
HAN = re.compile(r'[㐀-鿿豈-﫿]')


def path_of(lang, table):
    return os.path.join(HERE, lang + '.json') if table in ('top', '') else os.path.join(HERE, lang, table + '.json')


def load(p):
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else {}


def gb2312():
    out = set()
    for r in range(16, 88):
        for c in range(1, 95):
            try:
                out.add(bytes([0xA0 + r, 0xA0 + c]).decode('gb2312'))
            except UnicodeDecodeError:
                pass
    return out


def big5():
    """Big5(cp950) 한자 — 번체판 글자 점검 (대만 표준 자형 · 1급 5,401 + 2급 7,652 …)"""
    out = set()
    for hi in range(0xA4, 0xFA):
        for lo in list(range(0x40, 0x7F)) + list(range(0xA1, 0xFF)):
            try:
                c = bytes([hi, lo]).decode('cp950')
            except UnicodeDecodeError:
                continue
            if len(c) == 1 and HAN.match(c):
                out.add(c)
    return out


def charset(lang):
    return (big5(), 'Big5') if lang == 'zh-Hant' else (gb2312(), 'GB2312')


def unit_index():
    idx = {}
    for u in unit_ctx.units():
        idx.setdefault(u['key'], []).append(u)
    return idx


PERS_RE = re.compile(r'(?:^|[\s{,"\'])(intro|hot|stone|dilig|tsun|lively|boast|plain|genius|dp1)["\']?\s*:')
DECL_RE = re.compile(r'\n(?:const|let|var|function|async function)\s')


def pers_of(src, starts, us, base):
    """그 글이 성격별 표(intro: … genius:) 안에 있으면 성격 키 — 글이 놓인 줄에서 글자 조각을 찾아 거꾸로 가장 가까운 성격 키 (선언 경계까지)"""
    frags = sorted((f for f in re.split(r'\{\d+\}', base) if len(f.strip()) >= 2), key=len, reverse=True)
    if not frags:
        return ''
    out = []
    for u in us[:4]:
        ln = u.get('line') or 0
        if not 0 < ln <= len(starts):
            continue
        a, b = starts[max(0, ln - 2)], starts[min(len(starts) - 1, ln + 1)]
        i = src.find(frags[0], a, b)
        if i < 0:
            continue
        lo = max(0, i - 6000)
        d = [m.end() for m in DECL_RE.finditer(src, lo, i)]
        lo = d[-1] if d else lo
        ms = list(PERS_RE.finditer(src, lo, i))
        if ms:
            out.append(ms[-1].group(1))
    return ','.join(sorted(set(out)))


def export(lang, table, todo=False, out=None):
    ja, en, zh = load(path_of('ja', table)), load(path_of('en', table)), load(path_of(lang, table))
    sc = load(path_of('zh-Hans', table)) if lang == 'zh-Hant' else {}
    keys = [k for k in ja if not k.startswith('_')] + [k for k in en if not k.startswith('_') and k not in ja]
    idx = unit_index()
    src = open(unit_ctx.GAME, encoding='utf-8').read()
    starts = [0] + [m.end() for m in re.finditer(r'\n', src)]
    rows = []
    for n, k in enumerate(keys, 1):
        if todo and zh.get(k):
            continue
        ctx, base = (k.split('|', 1) if '|' in k and re.match(r'^[A-Za-z_$(][\w$()]*\|', k) else (None, k))
        us = idx.get(base, [])
        if ctx:
            us = [u for u in us if (u.get('top') or '').replace('()', '') == ctx.replace('()', '')] or us
        josa = sorted({i for u in us for i, e in enumerate(u.get('exprs') or []) if JOSA.match(str(e))})
        ref = ja.get(k) or en.get(k) or ''
        keep = sorted({int(m) for m in PH.findall(ref)})
        where = ' · '.join(sorted({'%s:%s' % (u.get('top') or '-', u.get('line')) for u in us})[:3])
        row = {'i': n, 'k': k, 'keep': keep, 'josa': josa, 'where': where}
        pr = pers_of(src, starts, us, base)
        if pr:
            row['pers'] = pr                         # 성격별 대사 — 말투는 GUIDE 3번 표
        row.update({'ja': ja.get(k, ''), 'en': en.get(k, ''), 'zh': zh.get(k, '')})
        if lang == 'zh-Hant':
            row['sc'] = sc.get(k, '')                # 간체 값 — 번체는 이것을 옮긴 것 (zh_work.py hant)
        rows.append(row)
    s = '\n'.join(json.dumps(r, ensure_ascii=False) for r in rows) + '\n'
    if out:
        open(out, 'w', encoding='utf-8').write(s)
        print('zh_work: %s %s — %d줄 → %s' % (lang, table, len(rows), out))
    else:
        sys.stdout.write(s)


def check_one(k, v, keep=None):
    """값 하나 점검 → 문제 목록"""
    bad = []
    if not isinstance(v, str) or not v.strip():
        return ['빈 값']
    if v == '∅':
        return []
    if HANGUL.search(v):
        bad.append('한글')
    if KANA.search(v):
        bad.append('가나')
    base = k.split('|', 1)[1] if re.match(r'^[A-Za-z_$(][\w$()]*\|', k) else k
    if '"' in re.sub(r'[A-Za-z][\w-]*="[^"<>]*"', '', v) or ('"' in v and '="' not in base):
        bad.append('곧은 따옴표')                   # 키가 속성 글(title="…")이면 그 따옴표만 된다
    phv = sorted({int(m) for m in PH.findall(v)})
    if keep is not None and phv != sorted(keep):
        bad.append('자리표 %s ≠ %s' % (phv, sorted(keep)))
    phk = {int(m) for m in PH.findall(base)}
    if set(phv) - phk:
        bad.append('키에 없는 자리표 %s' % sorted(set(phv) - phk))
    tk = sorted(m.group(2).lower() for m in TAG.finditer(base))
    tv = sorted(m.group(2).lower() for m in TAG.finditer(v))
    if tk != tv:
        bad.append('태그 %s ≠ %s' % (tv, tk))
    return bad


def merge(lang, table, tsvs):
    p = path_of(lang, table)
    ja, en, zh = load(path_of('ja', table)), load(path_of('en', table)), load(p)
    keys = [k for k in ja if not k.startswith('_')] + [k for k in en if not k.startswith('_') and k not in ja]
    vals, bad = {}, []
    for t in tsvs:
        for ln, line in enumerate(open(t, encoding='utf-8').read().split('\n'), 1):
            line = line.rstrip('\r')
            if not line.strip() or line.startswith('#'):
                continue
            if '\t' not in line:
                bad.append('%s:%d 탭 없음: %s' % (t, ln, line[:60]))
                continue
            i, v = line.split('\t', 1)
            try:
                i = int(i.strip())
            except ValueError:
                bad.append('%s:%d 번호가 아니다: %s' % (t, ln, i[:20]))
                continue
            if not 1 <= i <= len(keys):
                bad.append('%s:%d 번호 밖 %d' % (t, ln, i))
                continue
            vals[keys[i - 1]] = v.strip()
    for k, v in vals.items():
        ref = ja.get(k) or en.get(k) or ''
        b = check_one(k, v, sorted({int(m) for m in PH.findall(ref)}))
        if b:
            bad.append('%r → %r : %s' % (k[:50], v[:50], ' · '.join(b)))
    zh.update(vals)
    out, head = {}, None
    src = load(path_of('ja', table)) or load(path_of('en', table))
    for k in list(src.keys()) + [k for k in en if k not in src]:
        if k.startswith('_'):
            out[k] = (zh.get(k) or src[k]) if k in src else en[k]
            continue
        if k in zh:
            out[k] = zh[k]
    for k in zh:                                   # 중국어에서만 더한 문맥 키 · 일본어 표에 없는 키
        if k not in out:
            out[k] = zh[k]
    if '_' in out:
        out['_'] = '중국어 간체 표 (1022 · zh-Hans · 공개 전 — 주소 ?lang=zh-Hans 로만 · tools/i18n/i18n_build.py 가 빌드에 넣는다). 키 = game.html 한국어 원문 · 값 = 중국어 간체. 번역 지침 · 용어집: zh-Hans/GUIDE.md'
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w', encoding='utf-8', newline='\n') as f:
        f.write('{\n' + ',\n'.join(' %s: %s' % (json.dumps(k, ensure_ascii=False), json.dumps(v, ensure_ascii=False)) for k, v in out.items()) + '\n}\n')
    n = sum(1 for k in out if not k.startswith('_'))
    print('zh_work: %s — 값 %d개 넣음 · 표 %d줄 / %d · 문제 %d' % (os.path.relpath(p, HERE), len(vals), n, len(keys), len(bad)))
    for b in bad[:40]:
        print('  ' + b)
    return bad


def check(lang, tables):
    gb, gbn = charset(lang)
    names = {}
    total = 0
    for t in tables:
        ja, en, zh = load(path_of('ja', t)), load(path_of('en', t)), load(path_of(lang, t))
        for k, v in zh.items():
            if k.startswith('_'):
                continue
            total += 1
            ref = ja.get(k) or en.get(k)
            keep = sorted({int(m) for m in PH.findall(ref)}) if ref is not None else None
            b = check_one(k, v, keep)
            odd = sorted({c for c in v if HAN.match(c) and c not in gb})
            if odd:
                b.append('%s 밖 글자 %s' % (gbn, ''.join(odd)))
            if b:
                print('%s: %r → %r : %s' % (t, k[:60], v[:60], ' · '.join(b)))
            for c in ('NAME_POOL', 'SUR', 'GIV', 'ACAD', 'RELIC_ADJ', 'RELIC_NOUN', 'L5_NPC_ACAD', 'MON', 'EPI_CROWD'):
                if k.startswith(c + '|'):
                    names.setdefault((c, v), []).append(k)
    for (c, v), ks in names.items():
        if len(ks) > 1:
            print('이름 겹침 %s %r ← %s' % (c, v, ', '.join(ks)))
    print('zh_work check: %s %d줄' % (','.join(tables), total))


def validate(jsonl, tsvs, lang='zh-Hans', partial=False):
    """옮긴 값(TSV) 점검 — 작업 칸(JSONL)과 견준다: 빠진 번호 · 겹친 번호 · 자리표(keep 과 같은 모음) · 태그 · 한글 · 가나 · 곧은 따옴표 · GB2312 밖 글자(번체 · 일본 한자)"""
    rows = {}
    for l in open(jsonl, encoding='utf-8'):
        if l.strip():
            r = json.loads(l)
            rows[r['i']] = r
    (gb, gbn), got, bad = charset(lang), {}, []
    for t in tsvs:
        for ln, line in enumerate(open(t, encoding='utf-8').read().split('\n'), 1):
            line = line.rstrip('\r')
            if not line.strip():
                continue
            if '\t' not in line:
                bad.append('%s:%d 탭 없음: %s' % (os.path.basename(t), ln, line[:50]))
                continue
            i, v = line.split('\t', 1)
            try:
                i = int(i.strip())
            except ValueError:
                bad.append('%s:%d 번호가 아니다' % (os.path.basename(t), ln))
                continue
            if i not in rows:
                bad.append('%s:%d 작업 칸에 없는 번호 %d' % (os.path.basename(t), ln, i))
                continue
            if i in got:
                bad.append('번호 %d 가 두 번' % i)
            got[i] = v.strip()
    for i, v in sorted(got.items()):
        r = rows[i]
        b = check_one(r['k'], v, r['keep'])
        odd = sorted({c for c in v if HAN.match(c) and c not in gb})
        if odd:
            b.append('%s 밖 글자 %s (%s)' % (gbn, ''.join(odd), '간체 · 일본 한자인지 본다' if lang == 'zh-Hant' else '번체 · 일본 한자인지 본다'))
        if b:
            bad.append('%d %r → %r : %s' % (i, r['k'][:40], v[:40], ' · '.join(b)))
    miss = [] if partial else sorted(set(rows) - set(got))          # --partial — 고친 줄만 담은 TSV (번체 검토)
    print('zh_work validate: 작업 칸 %d · 옮김 %d · 빠짐 %d%s · 문제 %d' % (len(rows), len(got), len(miss),
          (' (%s%s)' % (','.join(map(str, miss[:30])), '…' if len(miss) > 30 else '')) if miss else '', len(bad)))
    for b in bad[:80]:
        print('  ' + b)
    return not miss and not bad


# ── 번체(대만) 표 — 간체 표에서 만든다 (1022) ─────────────────────────────────────
HANT_FIX = os.path.join(HERE, 'zh-Hant_fix.json')       # 손본 값 {키: {"sc": 그때의 간체 값, "tc": 번체 값}} — 간체 값이 바뀌면 다시 본다
HANT_KEEP = [                                            # OpenCC 보다 먼저 — 대만 게임 현지화 관례 (간체 → 번체)
    ('后台下载', '背景下載'),                            # 后台 → 後臺 가 아니라 '배경에서 받기'
    ('项目', '項目'),                                    # 专案(프로젝트)이 아니라 항목 · 종목
    ('保存实力', '保存實力'), ('保存力量', '保存力量'),     # 힘을 아낀다 (儲存 은 파일 저장)
    ('像素', '像素'),                                    # 畫素 보다 게임에서 흔한 말
    ('教程', '教學'), ('反馈', '回饋'), ('支持', '支持'), ('账号', '帳號'), ('全屏', '全螢幕'),
    ('回复任何', '回覆任何'), ('回复', '回復'),           # 회복은 回復 (回覆 은 '답장' — 邀约에 답하지 않았다 만 回覆) · 1022 검토
    ('代码', '代碼'),                                    # 이어하기 코드 (程式碼 는 프로그램 코드)
    ('指针', '指針'), ('对象', '對象'), ('远程', '遠程'), ('队列', '隊列'), ('循环', '循環'), ('扩展', '擴展'),   # OpenCC 의 IT 말(指標 · 物件 · 遠端 · 佇列 · 迴圈 · 擴充套件)이 아니다
    ('撤销', '復原'), ('拖动', '拖曳'),                  # 되돌리기 · 끌기 (대만 UI)
]
HANT_TC = [                                              # 번체에서 고치는 낱말 — 옮긴 값 · 손본 값 모두 (1022 검토)
    ('賬', '帳'), ('誒', '欸'), ('揹負', '背負'), ('最優解', '最佳解'), ('菸花', '煙花'), ('天后', '天後'), ('捱打', '挨打'), ('嗖', '咻'),
    ('哪兒', '哪裡'), ('髮條', '發條'), ('頭髮顫', '頭發顫'), ('迴圈', '循環'), ('擴充套件', '擴展'), ('程式碼', '代碼'), ('物件', '對象'),
    ('指標', '指針'), ('遠端', '遠程'), ('佇列', '隊列'), ('拖動', '拖曳'), ('撤銷', '復原'),
    ('寬屏', '寬螢幕'), ('窄屏', '窄螢幕'),                     # 1022 — 설정 '전투 연출'을 다시 보이며
]
WEEK_RE = re.compile(r'(?<![不四圓])周(?![圍邊遭到身旋折密延詳知])(?!全(?!程))')   # 대만은 주(週) — 周圍 · 周到 · 不周 · 四周(둘레) 는 그대로
HANT_AFTER = [('好嘞', '好耶'), ('嘞', '咧'), ('咔', '喀'), ('哐', '匡'), ('噼', '劈')]   # Big5 에 없는 대륙 의성어 → 대만에서 쓰는 글자
NAME_KEYS = ('NAME_POOL|', 'SUR|', 'GIV|')               # 음역 · 한국 성 — 낱말 바꿈(里 → 裡 · 朴 → 樸)을 되돌린다
_CC = None


def to_hant(s, key=''):
    """간체 값 → 대만 번체 값: OpenCC s2twp (낱말 · 대만 말) + 따옴표 「」『』 + 週 · 鐘 (이름 키는 글자만)"""
    global _CC
    if _CC is None:
        import opencc
        _CC = opencc.OpenCC('s2twp')
    for i, (a, _) in enumerate(HANT_KEEP):
        s = s.replace(a, chr(0xE000 + i))
    s = _CC.convert(s)
    for i, (_, b) in enumerate(HANT_KEEP):
        s = s.replace(chr(0xE000 + i), b)
    wrap = s.startswith('‘') and (s.endswith('’') or s.count('‘') != s.count('’'))
    if not wrap:                                         # 허세 학생의 전투 외침(‘…’ · 끝 ’ 를 코드가 붙이는 것)은 ‘ ’ 그대로
        s = s.replace('‘', '『').replace('’', '』')
    if s.count('“') == s.count('”'):
        s = s.replace('“', '「').replace('”', '」')
    if key.startswith(NAME_KEYS):
        return s.replace('裡', '里').replace('樸', '朴')
    s = WEEK_RE.sub('週', s)
    for a, b in HANT_AFTER:
        s = s.replace(a, b)
    return tc_fix(s.replace('鍾', '鐘'))


def tc_fix(s):
    for a, b in HANT_TC:
        s = s.replace(a, b)
    return re.sub(r'回覆(?!任何)', '回復', s)


def hant(write=True):
    fix = load(HANT_FIX)
    used, stale, n, nf = set(), [], 0, 0
    files = [os.path.join(HERE, 'zh-Hans.json')] + sorted(glob.glob(os.path.join(HERE, 'zh-Hans', '*.json')))
    for p in files:
        sc = load(p)
        out = {}
        for k, v in sc.items():
            if not isinstance(v, str):
                continue
            if k.startswith('_'):
                out[k] = ('중국어 번체 표 (1022 · zh-Hant · 대만 — zh-Hans 표에서 tools/i18n/zh_work.py hant 로 만든다 · 손으로 고치지 않는다: '
                          '고칠 값은 zh-Hant_fix.json). 키 = game.html 한국어 원문 · 값 = 중국어 번체. 지침: zh-Hant/GUIDE.md')
                continue
            f = fix.get(k)
            if f and f.get('sc') == v:
                out[k] = f['tc'] if k.startswith(NAME_KEYS) else tc_fix(f['tc']); used.add(k); nf += 1
            else:
                if f:
                    stale.append(k)
                out[k] = to_hant(v, k) if v != '∅' else v
            n += 1
        q = p.replace(os.sep + 'zh-Hans' + os.sep, os.sep + 'zh-Hant' + os.sep).replace('zh-Hans.json', 'zh-Hant.json')
        if write:
            os.makedirs(os.path.dirname(q), exist_ok=True)
            with open(q, 'w', encoding='utf-8', newline='\n') as fo:
                fo.write('{\n' + ',\n'.join(' %s: %s' % (json.dumps(k, ensure_ascii=False), json.dumps(v, ensure_ascii=False)) for k, v in out.items()) + '\n}\n')
    print('zh_work hant: %d줄 · 손본 값 %d%s%s' % (n, nf, (' · 간체가 바뀌어 다시 볼 손본 값 %d: %s' % (len(stale), ', '.join(repr(x[:30]) for x in stale[:8]))) if stale else '',
                                            (' · 쓰이지 않는 손본 값 %d' % len(set(fix) - used - set(stale))) if set(fix) - used - set(stale) else ''))
    return stale


def fix_merge(table, tsvs):
    """번체 검토의 고친 값(번호<TAB>번체)을 zh-Hant_fix.json 에 — 번호는 export --lang zh-Hant <table> 의 i"""
    ja, en, sc, tc = load(path_of('ja', table)), load(path_of('en', table)), load(path_of('zh-Hans', table)), load(path_of('zh-Hant', table))
    keys = [k for k in ja if not k.startswith('_')] + [k for k in en if not k.startswith('_') and k not in ja]
    fix, bad, n = load(HANT_FIX), [], 0
    big = big5()
    for t in tsvs:
        for ln, line in enumerate(open(t, encoding='utf-8').read().split('\n'), 1):
            line = line.rstrip('\r')
            if not line.strip() or line.startswith('#'):
                continue
            if '\t' not in line:
                bad.append('%s:%d 탭 없음' % (t, ln)); continue
            i, v = line.split('\t', 1)
            try:
                k = keys[int(i.strip()) - 1]
            except (ValueError, IndexError):
                bad.append('%s:%d 번호 %r' % (t, ln, i)); continue
            v = v.strip()
            ref = ja.get(k) or en.get(k) or ''
            b = check_one(k, v, sorted({int(m) for m in PH.findall(ref)}))
            odd = sorted({c for c in v if HAN.match(c) and c not in big})
            if odd:
                b.append('Big5 밖 글자 %s' % ''.join(odd))
            if b:
                bad.append('%r → %r : %s' % (k[:40], v[:40], ' · '.join(b))); continue
            if k not in sc:
                bad.append('간체 표에 없는 키 %r' % k[:40]); continue
            if v == tc.get(k):
                continue
            fix[k] = {'sc': sc[k], 'tc': v}; n += 1
    with open(HANT_FIX, 'w', encoding='utf-8', newline='\n') as fo:
        fo.write('{\n' + ',\n'.join(' %s: %s' % (json.dumps(k, ensure_ascii=False), json.dumps(v, ensure_ascii=False)) for k, v in fix.items()) + '\n}\n')
    print('zh_work fix: %s — 고친 값 %d개 · 문제 %d · 손본 값 모두 %d' % (table, n, len(bad), len(fix)))
    for b in bad[:40]:
        print('  ' + b)
    return bad


def main(a):
    lang = 'zh-Hans'
    if '--lang' in a:
        i = a.index('--lang'); lang = a[i + 1]; del a[i:i + 2]
    if not a:
        print(__doc__)
        return
    cmd = a[0]
    if cmd == 'export':
        out = None
        if '--out' in a:
            i = a.index('--out'); out = a[i + 1]; del a[i:i + 2]
        export(lang, a[1], '--todo' in a, out)
    elif cmd == 'merge':
        merge(lang, a[1], a[2:])
    elif cmd == 'validate':
        part = '--partial' in a
        a = [x for x in a if x != '--partial']
        sys.exit(0 if validate(a[1], a[2:], lang, part) else 1)
    elif cmd == 'hant':
        hant()
    elif cmd == 'fix':
        fix_merge(a[1], a[2:])
    elif cmd == 'check':
        tabs = a[1:] or ['top'] + sorted(os.path.splitext(os.path.basename(p))[0] for p in glob.glob(os.path.join(HERE, 'ja', '*.json')))
        check(lang, tabs)
    else:
        print(__doc__)


if __name__ == '__main__':
    main(sys.argv[1:])
