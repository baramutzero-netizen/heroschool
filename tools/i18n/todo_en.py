"""영어 표에 아직 없는 번역 단위 (1010 · 2단계) — 갈래별 개수 · 작업 칸 TSV 뽑기 · 채운 TSV 를 en/*.json 에 넣기

    python3 tools/i18n/todo_en.py                         갈래별 남은 수 (ui · log · tut · battle · data · names · dialogue · story · opening)
    python3 tools/i18n/todo_en.py --cat data --out a.tsv   그 갈래의 남은 키를 작업 칸으로 (키 · 빈 영어 칸 · 맨 위 선언 · 줄 · 자리표 식)
    python3 tools/i18n/todo_en.py --merge a.tsv en/data.json   영어 칸을 채운 TSV 를 영어 표 파일에 더한다 (없으면 만든다 · 맨 위 선언으로 묶는다)

작업 칸 TSV: 한 줄에 `키<TAB>영어<TAB>설명…`. 키는 JSON 문자열 그대로(따옴표 포함)라 앞뒤 빈칸 · 줄바꿈이 지켜진다.
영어 칸이 빈 줄은 --merge 가 건너뛴다. 문맥 키(같은 한국어를 곳마다 달리)는 키 칸에 "맨위선언|한국어" 를 JSON 문자열로 쓴다.
갈래는 classify_ko.py 의 규칙 (Object 리터럴 = data · 블록 IIFE = ui). 저장소 맨 위에서 돌린다.
"""
import argparse, collections, glob, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, ROOT)


def units():
    """game.html 의 단위 (줄 번호는 game.html 그대로) — 배포 빌드에서 빠지는 개발용 블록의 것은 뺀다"""
    import i18n_build as B
    from build_strip import strip_dev
    src = open(os.path.join(ROOT, 'game.html'), encoding='utf-8').read().replace('\r\n', '\n')
    en = B.load_en()
    prod = {u[0] for u, _ in B._units_of(strip_dev(src), en)[0]}
    rows, _ = B._units_of(src, en)
    return [(u, line) for u, line in rows if u[0] in prod]


def cat_of(top, callee):
    import classify_ko as C
    if top == 'Object':
        return 'data'
    if top == '(IIFE)':
        return 'ui'
    return C.cat({'top': top, 'callee': callee, 'role': 'text', 'dev': False})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--cat')
    ap.add_argument('--out')
    ap.add_argument('--merge', nargs=2, metavar=('TSV', 'JSON'))
    o = ap.parse_args()
    import i18n_build as B
    if o.merge:
        tsv, dst = o.merge
        dst = dst if os.path.isabs(dst) else os.path.join(HERE, dst)
        d = json.load(open(dst, encoding='utf-8'), object_pairs_hook=collections.OrderedDict) if os.path.exists(dst) else collections.OrderedDict()
        n = 0
        for ln in open(tsv, encoding='utf-8'):
            p = ln.rstrip('\n').split('\t')
            if len(p) < 2 or not p[1].strip() or p[0].startswith('#'):
                continue
            k = json.loads(p[0]); top = p[2] if len(p) > 2 and p[2] else '?'
            h = '_' + top
            if h not in d:
                d[h] = ''
            d[k] = p[1]; n += 1
        json.dump(d, open(dst, 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)
        open(dst, 'a', encoding='utf-8', newline='\n').write('\n')
        print('넣음 %d줄 → %s' % (n, os.path.relpath(dst, ROOT)))
        return
    en = B.load_en()
    seen, left = set(), collections.defaultdict(list)
    for (key, top, callee, pos, kind, exprs), line in units():
        if key in seen:
            continue
        seen.add(key)
        c = B._ctx_name(top)
        if key in en or (c + '|' + key) in en:
            continue
        left[cat_of(top, callee)].append((key, top, line, exprs))
    if not o.cat:
        for c, rs in sorted(left.items(), key=lambda x: -len(x[1])):
            print('%-9s %5d' % (c, len(rs)))
        return
    rs = left.get(o.cat, [])
    out = open(o.out, 'w', encoding='utf-8') if o.out else sys.stdout
    for key, top, line, exprs in rs:
        out.write('%s\t\t%s\tL%d\t%s\n' % (json.dumps(key, ensure_ascii=False), top[:-2] if top.endswith('()') else top, line,
                                           ' ¦ '.join(' '.join(e.split())[:60] for e in exprs)))
    if o.out:
        print('%s %d줄 → %s' % (o.cat, len(rs), o.out))


if __name__ == '__main__':
    main()
