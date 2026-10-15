"""itch.io 영어 체험판 빌드 (1011) — game.html → index.html (+ 그 HTML 이 부르는 assets/ · bgm/ 만) → ZIP

    python tools/itch/build_itch.py              # 저장소 맨 위에서 · 결과: Claude outputs/itch/heroschool_demo_en_<빌드>.zip
    python tools/itch/build_itch.py --folder     # ZIP 과 함께 풀어 놓은 폴더도 (Claude outputs/itch/web/ — 로컬 서버로 띄워 볼 때)
    python tools/itch/build_itch.py --root D:\\다른\\사본   # 그림 · 소리를 찾을 폴더를 더한다 (앞에 준 것부터 찾는다 · 저장소 맨 위는 늘 처음)

wrap.py 와 같은 빌드(그림 빼기 · 테스트 기능 빼기 · 영어판 변환 · 로딩 화면)에 세 가지를 더한다.
· 체험판 — game.html 의 DEMO_END 를 2년차 봄 2주차 시작으로: 그때 끝 화면을 띄우고 주를 더 넘기지 못한다 (demoOver · demoEndShow).
· 영어가 기본 — 주소의 ?lang= · 설정에서 고른 언어(hs_lang)가 없으면 브라우저 언어와 상관없이 English. 한국어 · 日本語(1014)는 설정에서 고른다.
· 화면 크기 틀(UISCALE)을 itch 의 iframe 안에서도 켠다 (EMBED) — '전체 화면으로 실행'으로 큰 모니터에 띄워도 게임이 커진다.
ZIP 에는 index.html 과 빌드된 HTML 에 적힌 그림 · 소리만 넣는다. itch 제한(파일 1000개 · 풀었을 때 500MB · 파일 하나 200MB)을 넘으면 멈춘다.
빌드 번호는 '<날짜-시각>-itch' — 설정 화면 · 의견 보내기에 그대로 찍혀서 itch 에서 온 의견을 가릴 수 있다.
"""
import argparse, datetime, os, re, sys, zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEMO_END = '{year:2, phase:"spring", week:1}'          # 2년차 봄 2주차가 시작되면 끝 (주차는 0 부터)
LIMIT_FILES, LIMIT_TOTAL, LIMIT_FILE = 1000, 500e6, 200e6
STORE = ('.webp', '.png', '.jpg', '.jpeg', '.gif', '.ogg', '.mp3', '.wav', '.woff', '.woff2', '.zip')   # 이미 눌려 있어 다시 누르지 않는다


def build_html():
    """wrap.py 와 같은 단계 + 체험판 · 영어 기본 · iframe 안 화면 크기"""
    os.chdir(ROOT)
    sys.path.insert(0, ROOT)
    from split_assets import split_file
    from build_guard import validate_game_source
    from build_strip import strip_dev
    from build_boot import boot_split
    src = split_file('game.html')
    validate_game_source(src)
    stamp = datetime.datetime.now().strftime('%m%d-%H%M')
    src = re.sub(r'const BUILD = "[^"]*";', 'const BUILD = "%s-itch";' % stamp, src, count=1)
    src = strip_dev(src)
    sys.path.insert(0, os.path.join(ROOT, 'tools', 'i18n'))
    from i18n_build import apply_i18n
    src = apply_i18n(src)

    def once(s, old, new, what):
        n = s.count(old)
        if n != 1:
            raise SystemExit('build_itch: %s — 바꿀 자리를 %d곳 찾았다 (1곳이어야 한다): %r' % (what, n, old[:60]))
        return s.replace(old, new)
    src = once(src, 'const DEMO_END = null;', 'const DEMO_END = %s;' % DEMO_END, '체험판 끝')
    src = once(src, 'var EMBED = false;', 'var EMBED = true;', '화면 크기 틀 (iframe 안)')
    src = once(src, r'L=(q==="en"||q==="ko"||q==="ja")?q:(s==="en"||s==="ko"||(J&&s==="ja"))?s:P?(/^ko\b/i.test(n)?"ko":(J&&/^ja\b/i.test(n))?"ja":"en"):"ko";',
               r'L=(q==="en"||q==="ko"||q==="ja")?q:(s==="en"||s==="ko"||(J&&s==="ja"))?s:"en";', '영어 기본')
    i = src.index('<div id="app">')
    head, body, tail = boot_split(src[:i], src[i:])
    out = f'''<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<style>:root{{color-scheme:light dark}}body{{margin:0}}img{{max-width:100%}}[hidden]{{display:none!important}}</style>
{head}</head>
<body>
{body}
{tail}
</body></html>'''
    return out, stamp


def find(rel, roots):
    for r in roots:
        p = os.path.join(r, rel)
        if os.path.isfile(p):
            return p
    return None


def collect(html, roots):
    """빌드된 HTML 이 부르는 파일 (저장소 기준 경로 → 실제 파일)"""
    files = {}
    pool = {}                                            # assets/ · bgm/ 아래에 있는 모든 파일 (찾는 폴더 전부)
    for r in reversed(roots):
        for top in ('assets', 'bgm'):
            base = os.path.join(r, top)
            for dp, dn, fn in os.walk(base):
                for f in fn:
                    full = os.path.join(dp, f)
                    pool[os.path.relpath(full, r).replace(os.sep, '/')] = full
    # 1) 글자 그대로 적힌 assets/… (뒤에 ?v= · .js 같은 것이 붙어도 — 실제 있는 가장 긴 이름)
    for m in re.finditer(r'assets/[A-Za-z0-9_\-./]+', html):
        t = m.group(0)
        for j in range(len(t), 7, -1):
            if t[:j] in pool:
                files[t[:j]] = pool[t[:j]]
                break
    # 2) assets/ 를 떼고 적힌 것 (HS_A["counsel-cookie/x.png"] 등) · 대회 쿼터뷰 지도(이름만) · 운영 안내 그림(번호로 만든다) · 스킬 강화 창 그림(이어 붙인다 · 1014)
    for rel, full in pool.items():
        if not rel.startswith('assets/') or rel in files:
            continue
        parts = rel.split('/')
        tail = '/'.join(parts[1:])
        fb = '/'.join(parts[-2:])
        if re.search(r'["\'`]' + re.escape(tail) + r'["\'`?]', html) or re.search(r'["\'`/]' + re.escape(fb) + r'["\'`?]', html):
            files[rel] = full
        elif rel.startswith('assets/battle-fields/quarter/') and re.search(r'["\'`]' + re.escape(parts[-1]) + r'[?"\'`]', html):
            files[rel] = full
        elif rel.startswith('assets/tutorial-illustrated/'):
            files[rel] = full
        elif rel.startswith('assets/skill-upgrade/') and rel.endswith('.png'):   # 스킬 강화 창 (1014) — SK_CHOICE_ROOT + 직업 그림(SK_CHOICE_ART) + '/' + 표정 이름 + '.png' 로 만든다
            name = parts[-1][:-4]
            if len(parts) == 4 and re.search(r'["\']' + re.escape(parts[2]) + r'["\']', html) and re.search(r'["\']' + re.escape(name) + r'["\']', html):
                files[rel] = full                                             # 직업 그림 폴더 — 표에 있는 직업 그림 · 코드에 적힌 표정 이름
            elif len(parts) == 3 and re.search(r'["\'`]' + re.escape(name) + r'(\.png)?["\'`]', html):
                files[rel] = full                                             # 표시 · 부채 (anticipation · impact · SK_CHOICE_FAN)
    # 3) 소리 — BGM_DIR("bgm/") 뒤에 붙는 이름은 표에 따옴표로 적혀 있다
    for rel, full in pool.items():
        if rel.startswith('bgm/') and re.search(r'["\'`]' + re.escape(rel[4:]) + r'["\'`]', html):
            files[rel] = full
    return files


def main():
    ap = argparse.ArgumentParser(description='itch.io 영어 체험판 ZIP')
    ap.add_argument('--out', default=os.path.join(ROOT, 'Claude outputs', 'itch'))
    ap.add_argument('--root', action='append', default=[], help='그림 · 소리를 더 찾을 폴더 (저장소와 같은 모양 — assets/ · bgm/)')
    ap.add_argument('--folder', action='store_true', help='풀어 놓은 폴더(web/)도 만든다')
    o = ap.parse_args()
    roots = [ROOT] + [os.path.abspath(r) for r in o.root]
    html, stamp = build_html()
    files = collect(html, roots)
    data = html.encode('utf-8')
    sizes = {rel: os.path.getsize(p) for rel, p in files.items()}
    total = sum(sizes.values()) + len(data)
    big = [r for r, s in sizes.items() if s > LIMIT_FILE]
    print('build_itch: 빌드 %s-itch · index.html %.1fMB · 파일 %d개 (+ index.html) · 합계 %.1fMB' % (stamp, len(data) / 1e6, len(files), total / 1e6))
    if len(files) + 1 > LIMIT_FILES or total > LIMIT_TOTAL or big:
        raise SystemExit('build_itch: itch 제한을 넘는다 — 파일 %d개 / 합계 %.1fMB / 200MB 넘는 파일 %s' % (len(files) + 1, total / 1e6, big))
    os.makedirs(o.out, exist_ok=True)
    zp = os.path.join(o.out, 'heroschool_demo_en_%s.zip' % stamp)
    with zipfile.ZipFile(zp, 'w') as z:
        z.writestr(zipfile.ZipInfo('index.html', date_time=datetime.datetime.now().timetuple()[:6]), data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
        for rel in sorted(files):
            ct = zipfile.ZIP_STORED if rel.lower().endswith(STORE) else zipfile.ZIP_DEFLATED
            z.write(files[rel], rel, compress_type=ct)
    print('build_itch: ZIP %s (%.1fMB)' % (zp, os.path.getsize(zp) / 1e6))
    if o.folder:
        import shutil
        web = os.path.join(o.out, 'web')
        if os.path.isdir(web):
            shutil.rmtree(web)
        os.makedirs(web)
        open(os.path.join(web, 'index.html'), 'wb').write(data)
        for rel, p in files.items():
            dst = os.path.join(web, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copyfile(p, dst)
        print('build_itch: 폴더 %s' % web)


if __name__ == '__main__':
    main()
