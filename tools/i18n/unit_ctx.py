"""번역 단위가 game.html 어디에 쓰이는지 (1014 · 일본어판 번역에 썼다 — 새 글을 옮길 때도).

    python3 tools/i18n/unit_ctx.py '키' ['키' …]       키(한국어 원문 · 문맥 키 'TOP|원문' 도 된다)마다 맨 위 선언 · 줄 · 자리표 식 · 그 줄의 코드
    python3 tools/i18n/unit_ctx.py --grep '정규식'       키에 정규식이 맞는 단위 목록 (최대 60)
    python3 tools/i18n/unit_ctx.py --line 12345 [앞뒤]   game.html 의 그 줄 근처
    python3 tools/i18n/unit_ctx.py --todo ja            일본어 표에 아직 없는 단위 (영어 표에만 있거나 둘 다 없는 것)

단위 목록은 i18n_build.py --dump 로 만들어 임시 폴더에 둔다 (game.html 이 바뀌면 다시 만든다). 저장소 맨 위에서 돌린다.
'자리표' 식이 iga · eunn · gwa · eulr · ro · jo 이면 조사 자리 — 일본어 · 영어 값에서는 쓰지 않는다.
"""
import hashlib, json, os, re, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
GAME = os.path.join(ROOT, 'game.html')
PART = re.compile(r'^\s*(jo|ro|iga|eunn|gwa|eulr)\(')


def units():
    st = os.stat(GAME)
    tag = hashlib.sha1(('%s:%s' % (st.st_mtime_ns, st.st_size)).encode()).hexdigest()[:10]
    p = os.path.join(tempfile.gettempdir(), 'hs_units_%s.json' % tag)
    if not os.path.exists(p):
        subprocess.run([sys.executable, os.path.join(HERE, 'i18n_build.py'), '--dump', GAME, p], check=True,
                       stdout=subprocess.DEVNULL)
    return [x for x in json.load(open(p, encoding='utf-8')) if 'key' in x]


def show_line(L, n, w=0):
    for i in range(max(1, n - w), min(len(L), n + w) + 1):
        s = L[i - 1].strip()
        print('    %6d| %s' % (i, s[:400] + (' …' if len(s) > 400 else '')))


def main(a):
    if not a:
        print(__doc__)
        return
    L = open(GAME, encoding='utf-8').read().split('\n')
    if a[0] == '--line':
        show_line(L, int(a[1]), int(a[2]) if len(a) > 2 else 3)
        return
    U = units()
    if a[0] == '--grep':
        rx, n = re.compile(a[1]), 0
        for x in U:
            if rx.search(x['key']):
                print('%s | %s | %d | %s' % (x['key'][:120], x['top'], x['line'], x['kind']))
                n += 1
                if n >= 60:
                    break
        return
    if a[0] == '--todo':
        sys.path.insert(0, HERE)
        import i18n_build as B
        tab = B.load_ja() if a[1:] == ['ja'] else B.load_en()
        seen = set()
        for x in U:
            if x.get('dev') or x['key'] in seen:
                continue
            c = B._ctx_name(x['top'])
            if (c and (c + '|' + x['key']) in tab) or x['key'] in tab:
                continue
            seen.add(x['key'])
            print('%s | %s | %d' % (x['key'][:120], x['top'], x['line']))
        return
    for k in a:
        ctx, k2 = (k.split('|', 1) if ('|' in k and re.match(r'^[\w$.()]+\|', k)) else (None, k))
        hits = [x for x in U if x['key'] == k2 and (ctx is None or x['top'].replace('()', '') == ctx.replace('()', ''))]
        print('== %r — %d곳' % (k, len(hits)))
        seen = set()
        for x in hits[:12]:
            if x['line'] in seen:
                continue
            seen.add(x['line'])
            ex = x.get('exprs') or []
            part = [i for i, e in enumerate(ex) if PART.match(e)]
            print('  [%s] 줄 %d · %s%s%s' % (x['top'], x['line'], x['kind'], (' · 자리표 ' + ', '.join(ex)[:200]) if ex else '',
                                          (' · 조사 자리 ' + ' '.join('{%d}' % i for i in part)) if part else ''))
            show_line(L, x['line'], 0)


if __name__ == '__main__':
    main(sys.argv[1:])
