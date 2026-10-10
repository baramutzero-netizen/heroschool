"""영어판 시험 (1010) — 한국어로 띄운 게임이 변환 전과 똑같은지, 영어 시험 단어가 보이는지 본다.

    python3 tools/i18n/check_i18n.py [--years 3] [--shots 폴더]     (저장소 맨 위에서 · Playwright + 크로미움)
    hs.py 를 쓰는 세션이면:  python3 ~/hs.py i18n

1. game.html 로 빌드를 두 벌 만든다 — 변환 안 함(A) · 변환함(B). wrap.py 와 같은 차례 · 같은 빌드 번호.
   파일은 임시 폴더에 쓰고, <base> 를 달아 그림 · 소리는 저장소의 것을 읽는다 (저장소에는 아무것도 쓰지 않는다).
2. 한국어 — A · B 를 각각 띄워 같은 시드 · 같은 시계로 새 학원을 열고 몇 해를 돌린다(대회 · 원정 포함).
   계절마다 세이브(S)와 화면(#app)을, 끝에는 화면 열몇 개 · 운영 안내 · 목표 창을 견준다. 한 글자라도 다르면 실패.
3. 영어 — B 를 ?lang=en 으로 띄워 오류가 없는지, 영어 표의 시험 단어가 보이는지, <html lang> · 조사 함수 · 운영 안내(글 안내) ·
   리그 잠금 토스트 · 설정의 언어 칸을 본다. 설정에서 언어를 바꾸면 저장 후 다시 불러오는지도.
4. 공개(config.json public:true) 뒤에는 — 브라우저 언어(크로미움 locale)로 고르는지 (ko-KR → 한국어 · en-US → 영어),
   공개 전부터 세이브가 있던 사람은 영어 브라우저여도 한국어로 기억되는지, 설정의 '자동'이 그 기억을 지우고 브라우저를 따르는지.
   한국어 견주기(2)는 한국어 브라우저(ko-KR)로 띄우고, B 에만 있는 설정의 언어 칸은 빼고 견준다.
바깥 주소(firebase · 글꼴 등)는 전부 막는다. 끝나면 임시 폴더를 지운다 (--shots 를 주면 스크린샷을 거기에 남긴다).
"""
import argparse, json, os, re, shutil, sys, tempfile, time

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'tools', 'i18n'))

# 같은 시드 · 같은 시계 — 페이지 스크립트보다 먼저 들어간다. 시뮬레이션 직전에 __hsReset() 으로 다시 맞춘다
INIT_JS = r"""(() => {
  let a = 0x2545F491 >>> 0, t = 0;
  const rng = () => { a = (a + 0x6D2B79F5) >>> 0; let x = Math.imul(a ^ (a >>> 15), 1 | a);
    x = (x + Math.imul(x ^ (x >>> 7), 61 | x)) ^ x; return ((x ^ (x >>> 14)) >>> 0) / 4294967296; };
  Math.random = rng;
  const T0 = 1791600000000;
  Date.now = () => T0 + (t += 7);
  window.__hsReset = s => { a = s >>> 0; t = 0; };
})();"""

# 시뮬레이션 — 대회 · 친선전 · 원정을 자동으로 넘긴다 (예전 test.py 의 진행기를 다듬은 것)
SIM_JS = r"""async (years) => {
  const out = {snaps: [], views: [], err: []};
  const snap = tag => { try { out.snaps.push({tag, s: JSON.stringify(S), app: document.getElementById('app').innerHTML,
                                               modal: document.getElementById('modalRoot').innerHTML}); }
                        catch(e) { out.err.push(tag + ': ' + e.message); } };
  function fillTeams(){
    teamsOf().forEach(t=>{
      const taken = new Set();
      teamsOf().forEach(x=>{ if(x!==t) formSlots(x.form).forEach(k=>{ if(x.slots[k]) taken.add(x.slots[k]); }); });
      const pool = S.students.filter(x=> !taken.has(x.id)).sort((a,b)=> power(b)-power(a));
      t.slots = {}; formSlots(t.form).forEach((k,i)=>{ if(pool[i]) t.slots[k] = pool[i].id; });
    });
  }
  function autoLadder(){
    let g = 0;
    while(UI.tour && UI.tour.kind==='ladder' && g++ < 80){
      const t = UI.tour;
      if(t.stage==='prep'){ t.stage='entry'; continue; }
      if(t.stage==='entry'){
        fillTeams();
        t.entryTeams = ['A','B','C'].filter(n=> teamFull(teamByName(n)));
        t.myTeams = t.entryTeams.map(n=> teamMembers(teamByName(n)).map(x=>x.id));
        t.stage = 'match'; S.fallRun.entry = t.entryTeams.slice(); continue;
      }
      if(t.stage==='scout'){ t.stage='match'; continue; }
      if(t.stage==='match'){
        const ids = t.myTeams[ladderTeamIdx(t)], my = tourMatchStudents(ids), foe = t.foes[t.round], opp = ladderFoeTeam(t);
        ladderRecord(t, runBattle(my, opp, {}), foe.name, ids); continue;
      }
      if(t.stage==='result'){ finishLadder(t); continue; }
      break;
    }
    closeModal();
  }
  function autoTour(){
    if(!UI.pendingTour || !UI.tour) return;
    if(UI.tour.kind==='ladder'){ autoLadder(); return; }
    if(UI.tour.kind==='friendly'){
      const ft = UI.tour; fillTeams();
      if(ft.stage==='prep') ft.stage='entry';
      ft.entryTeams = ['A','B','C'].filter(n=> teamFull(teamByName(n)));
      ft.myTeams = ft.entryTeams.map(n=> teamMembers(teamByName(n)).map(x=>x.id));
      ft.stage = 'match';
      let fg = 0; while(UI.tour===ft && ft.stage==='match' && fg++ < 5) friendlyRun(ft, true);
      if(ft.stage==='result') finishFriendly(ft);
      closeModal(); return;
    }
    const t = UI.tour;
    fillTeams();
    t.entryTeams = teamsOf().filter(x=> teamFull(x)).map(x=> x.n).slice(0, tourNeedTeams(t));
    t.myTeams = t.entryTeams.map(n=> teamMembers(teamByName(n)).map(x=>x.id));
    if(!t.myTeams.length) t.myTeams = [S.students.slice(0,3).map(x=>x.id)];
    t.stage = t.kind==='spring' ? 'match' : 'scout'; t.matchIdx = 0; t.roundWins = 0; t.roundScore = [0,0];
    let guard = 0;
    while(UI.tour && guard++ < 40){
      const tt = UI.tour;
      if(tt.stage==='prep'){ tt.stage='entry'; continue; }
      if(tt.stage==='scout'){ tt.stage='match'; tt.matchIdx=0; tt.roundScore=[0,0]; continue; }
      const sp = tt.kind==='spring';
      const myIds = sp ? tt.myTeams[0] : tt.myTeams[tt.matchIdx];
      const oppTeam = sp ? tt.opps[tt.matchIdx].teams[0] : tt.opps[tt.round].teams[tt.assign[tt.matchIdx]];
      const oppName = sp ? tt.opps[tt.matchIdx].name : tt.opps[tt.round].name;
      recordMatch(tt, runBattle(tourMatchStudents(myIds), oppTeam, {titleA:'us', titleB:oppName}), oppName, myIds);
    }
    closeModal();
  }
  try{
    __hsReset(20261010);
    closeModal();
    newScenarioStart(curData("백은 용사 학원"));   // 기본 이름 모양 — 이름 짓기 창의 기본값처럼 영어판이면 Argent Hero Academy (남은 한글 점검)
    closeModal();
    snap('start');
    for(let y=0; y<years; y++){
      for(let ph=0; ph<4; ph++){
        if(S.hand && S.hand.length){ S.hand[0] = {u: ++S.cardSeq, t: 'exped'}; fillTeams(); }
        const phase = S.phase;
        let g2 = 0;
        while(S.phase===phase && g2++ < 12){ runWeeks(30); autoTour(); }
        snap('y' + y + ' ' + phase + '→' + S.phase);
        if(S.phase===phase && !UI.pendingTour){ out.err.push('phase stuck at ' + phase); break; }
      }
    }
    closeModal();
    const sel = S.students[0] && S.students[0].id;
    ['home','master','roster','team','plan','facil','relic','skill','counsel','csllog','log','record','codex','opt'].forEach(v=>{
      try{ UI.view = v; UI.sel = sel; render(); out.views.push({v, html: document.getElementById('app').innerHTML}); }
      catch(e){ out.err.push('view ' + v + ': ' + e.message); }
    });
    [1, 2, 6, 12].forEach(k=>{ try{ out.views.push({v: 'tut' + k, html: tutGuideHTML(k)}); }catch(e){ out.err.push('tut ' + k + ': ' + e.message); } });
    try{ UI.view = 'home'; render(); const b = document.getElementById('mMis'); if(b) b.click();
         out.views.push({v: 'mission', html: document.getElementById('modalRoot').innerHTML}); closeModal(); }catch(e){ out.err.push('mission: ' + e.message); }
  }catch(e){ out.err.push('EXCEPTION: ' + e.message + ' @ ' + (e.stack||'').split('\n')[1]); }
  return out;
}"""


def build(i18n, stamp):
    """wrap.py 와 같은 차례로 빌드한 HTML (파일로 쓰지 않는다)"""
    from split_assets import split_file
    from build_guard import validate_game_source
    from build_strip import strip_dev
    from build_boot import boot_split
    from i18n_build import apply_i18n
    cwd = os.getcwd()
    os.chdir(ROOT)
    try:
        src = split_file('game.html')
        validate_game_source(src)
        src = re.sub(r'const BUILD = "[^"]*";', 'const BUILD = "%s";' % stamp, src, count=1)
        src = strip_dev(src)
        if i18n:
            src = apply_i18n(src)
    finally:
        os.chdir(cwd)
    i = src.index('<div id="app">')
    head, body, tail = boot_split(src[:i], src[i:])
    base = 'file://' + ROOT.replace(os.sep, '/').rstrip('/') + '/'
    return ('<!doctype html>\n<html lang="ko"><head>\n<base href="%s">\n<meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
            '<style>:root{color-scheme:light dark}body{margin:0}img{max-width:100%%}[hidden]{display:none!important}</style>\n'
            '%s</head>\n<body>\n%s\n%s\n</body></html>') % (base, head, body, tail)


def real_errors(errs):
    return [e for e in errs if not re.search(r'Failed to load resource|ERR_FILE_NOT_FOUND|ERR_FAILED|net::', e)]


T0_RE = re.compile(r'data-t0="[\d.]+"')     # 애니메이션 시작 때(performance.now) — 띄울 때마다 다르다
PUBLIC = bool(json.load(open(os.path.join(ROOT, 'tools', 'i18n', 'config.json'), encoding='utf-8')).get('public'))
LANG_RE = re.compile(r'<section class="panel"><div class="optrow"><div class="optlab"><b>언어 · Language</b>[\s\S]*?</section>')   # 공개 뒤 — B 에만 있는 설정의 언어 칸


def norm(h):
    h = T0_RE.sub('data-t0=""', h)
    return LANG_RE.sub('', h) if PUBLIC else h


def first_diff(a, b, ctx=80):
    n = min(len(a), len(b))
    i = next((k for k in range(n) if a[k] != b[k]), n)
    return 'at %d: A …%r… / B …%r…' % (i, a[max(0, i - ctx):i + ctx], b[max(0, i - ctx):i + ctx])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--years', type=int, default=3, help='돌릴 햇수 (한 해 = 네 계절 · 3년이면 첫 졸업까지)')
    ap.add_argument('--shots', help='영어 스크린샷을 남길 폴더')
    o = ap.parse_args()
    from playwright.sync_api import sync_playwright

    tmp = tempfile.mkdtemp(prefix='hs_i18n_')
    fails = []
    try:
        t0 = time.time()
        stamp = 'i18n-check'
        pa, pb = os.path.join(tmp, 'ko_plain.html'), os.path.join(tmp, 'ko_i18n.html')
        open(pa, 'w', encoding='utf-8').write(build(False, stamp))
        open(pb, 'w', encoding='utf-8').write(build(True, stamp))
        print('빌드 두 벌 %.1f초' % (time.time() - t0))

        with sync_playwright() as p:
            br = p.chromium.launch()

            def open_page(path, query='', w=1440, h=900, dsf=1, ctx=None, locale='ko-KR', init=None):
                c = ctx or br.new_context(viewport={'width': w, 'height': h}, device_scale_factor=dsf, locale=locale)   # 브라우저 언어 (공개 뒤에는 이걸로 고른다)
                if ctx is None:
                    c.route(re.compile(r'^https?://'), lambda r: r.abort())
                    c.add_init_script(INIT_JS)
                    if init:
                        c.add_init_script(init)
                pg = c.new_page()
                errs = []
                pg.on('pageerror', lambda e: errs.append('pageerror: ' + str(e)[:300]))
                pg.on('console', lambda m: errs.append('console: ' + m.text[:300]) if m.type == 'error' else None)
                pg.goto('file://' + path + query, wait_until='commit')
                pg.wait_for_function("() => typeof S !== 'undefined' && S && Array.isArray(S.students) && S.students.length > 0"
                                     " && !document.getElementById('bootLoader')", polling=250, timeout=60000)
                pg.wait_for_timeout(300)
                return c, pg, errs

            # ── 한국어: 변환 전(A) · 변환 후(B) ──
            res = {}
            for tag, path in (('A', pa), ('B', pb)):
                t = time.time()
                c, pg, errs = open_page(path)
                r = pg.evaluate(SIM_JS, o.years)
                r['errs'] = real_errors(errs)
                r['lang'] = pg.evaluate("() => [document.documentElement.lang, typeof I18N === 'undefined' ? null : I18N.lang]")
                res[tag] = r
                print('%s 한국어 %s · 단계 %d · 화면 %d · %.1f초 · 오류 %d%s' % (
                    tag, '변환 전' if tag == 'A' else '변환 후', len(r['snaps']), len(r['views']), time.time() - t, len(r['errs']),
                    (' — ' + ' / '.join(r['err'][:3])) if r['err'] else ''))
                c.close()
            A, B = res['A'], res['B']
            if A['err'] != B['err']:
                fails.append('진행 중 오류가 다르다: A %s / B %s' % (A['err'][:3], B['err'][:3]))
            if B['lang'] != ['ko', 'ko']:
                fails.append('B 의 언어가 한국어가 아니다: %s' % B['lang'])
            ns = nv = 0
            for x, y in zip(A['snaps'], B['snaps']):
                for k in ('s', 'app', 'modal'):
                    if norm(x[k]) != norm(y[k]):
                        fails.append('한국어 %s 의 %s 가 다르다 — %s' % (x['tag'], {'s': '세이브', 'app': '화면', 'modal': '팝업'}[k], first_diff(x[k], y[k])))
                        break
                else:
                    ns += 1
            for x, y in zip(A['views'], B['views']):
                if norm(x['html']) != norm(y['html']):
                    fails.append('한국어 화면 %s 가 다르다 — %s' % (x['v'], first_diff(x['html'], y['html'])))
                else:
                    nv += 1
            if len(A['snaps']) != len(B['snaps']) or len(A['views']) != len(B['views']):
                fails.append('단계 · 화면 수가 다르다')
            same_err = sorted(set(A['errs']) ^ set(B['errs']))
            if same_err:
                fails.append('콘솔 오류가 다르다: %s' % same_err[:4])
            last = json.loads(A['snaps'][-1]['s']) if A['snaps'] else {}
            print('한국어 견주기 — 단계 %d/%d · 화면 %d/%d 같음 · 끝 상태: %s년차 %s · 학생 %d · 졸업생 %d · 명성 %d · 일지 %d줄' % (
                ns, len(A['snaps']), nv, len(A['views']), last.get('year'), last.get('phase'), len(last.get('students') or []),
                len(last.get('graduates') or []), round(last.get('fame') or 0), len(last.get('log') or [])))

            # ── 영어: B 를 ?lang=en ──
            en = {k: v for k, v in json.load(open(os.path.join(ROOT, 'tools', 'i18n', 'en.json'), encoding='utf-8')).items()
                  if not k.startswith('_') and v}
            c, pg, errs = open_page(pb, '?lang=en')
            pg.evaluate("() => { __hsReset(7); closeModal(); newScenarioStart('Test Academy'); closeModal(); UI.view = 'home'; render(); }")
            pg.wait_for_timeout(400)
            info = pg.evaluate("""() => ({lang: document.documentElement.lang, i18n: I18N.lang, title: document.title,
                jo: jo('가', '이', '가') + ro('물') + iga('검'), nav: document.getElementById('nav').textContent,
                top: document.querySelector('.meters').textContent, tut1: tutGuideHTML(1).slice(0, 40)})""")
            want = ["Master's Notes", 'Town', 'Settings', 'Graduate League']
            miss = [w for w in want if w not in info['nav']]
            if info['lang'] != 'en' or info['i18n'] != 'en':
                fails.append('영어: 언어가 en 이 아니다 %s' % info)
            if miss:
                fails.append('영어: 메뉴에 시험 단어가 없다 %s · 메뉴 %r' % (miss, info['nav'][:200]))
            for w in ('Date', 'Fame', 'Goal'):
                if w not in info['top']:
                    fails.append('영어: 위쪽 칸에 %s 가 없다 (%r)' % (w, info['top'][:200]))
            if info['jo']:
                fails.append('영어: 조사 함수가 빈 글을 돌려주지 않는다 (%r)' % info['jo'])
            if 'tg-guide' not in info['tut1']:
                fails.append('영어: 운영 안내 1장이 글 안내가 아니다 (%r)' % info['tut1'])
            if info['title'] != en.get('용사 학원 키우기 — 학원이 망했다'):
                fails.append('영어: 페이지 제목 %r' % info['title'])
            # 리그 잠금 토스트 (첫 졸업 전)
            pg.evaluate("() => { const b = document.querySelector('#nav [data-view=league]'); if(b) b.click(); }")
            pg.wait_for_timeout(200)
            toast = pg.evaluate("() => document.getElementById('toastRoot').innerText")
            if toast.strip() != en.get('졸업생 리그는 첫 졸업생이 나오면 열린다.'):
                fails.append('영어: 리그 잠금 토스트 %r' % toast)
            if o.shots:
                os.makedirs(o.shots, exist_ok=True)
                pg.screenshot(path=os.path.join(o.shots, 'en_home.png'))
            # 설정 — 언어 칸 (시험 접속이라 보인다 · English 가 눌려 있다)
            pg.evaluate("() => { UI.view = 'opt'; render(); }")
            pg.wait_for_timeout(200)
            lp = pg.evaluate("() => [...document.querySelectorAll('[data-lang]')].map(b => b.dataset.lang + ':' + b.getAttribute('aria-pressed') + ':' + b.textContent)")
            want_lp = (['auto:false:Auto', 'ko:false:한국어', 'en:true:English'] if PUBLIC else ['ko:false:한국어', 'en:true:English'])   # 주소의 ?lang=en 이 눌려 있다
            if lp != want_lp:
                fails.append('영어: 설정의 언어 칸 %s' % lp)
            if o.shots:
                el = pg.query_selector('#view .panel')
                (el or pg).screenshot(path=os.path.join(o.shots, 'en_settings.png'))
            e_real = real_errors(errs)
            if e_real:
                fails.append('영어: 오류 %s' % e_real[:4])
            print('영어 — 메뉴 %r · 위쪽 %r · 토스트 %r · 언어 칸 %s · 오류 %d' % (
                re.sub(r'\s+', ' ', info['nav'])[:140], re.sub(r'\s+', ' ', info['top'])[:90], toast.strip()[:60], lp, len(e_real)))
            c.close()

            if not PUBLIC:
                # 한국어 B — ?lang 없이는 언어 칸이 없고, ?lang=ko 시험 접속에서는 보인다 → English 를 누르면 저장 후 ?lang=en 으로
                c, pg, errs = open_page(pb)
                none = pg.evaluate("() => { closeModal(); UI.view = 'opt'; render(); return document.querySelectorAll('[data-lang]').length; }")
                if none:
                    fails.append('한국어: ?lang 없이도 언어 칸이 보인다')
                c.close()
                c, pg, errs = open_page(pb, '?lang=ko')
                pg.evaluate("() => { __hsReset(9); closeModal(); newScenarioStart('전환 학원'); closeModal(); UI.view = 'opt'; render(); }")
                with pg.expect_navigation(timeout=30000):
                    pg.click('[data-lang=en]')
                pg.wait_for_function("() => typeof S !== 'undefined' && S && S.students && !document.getElementById('bootLoader')",
                                     polling=250, timeout=60000)
                after = pg.evaluate("() => [location.search, I18N.lang, S.acadName]")
                if not (after[0].endswith('lang=en') and after[1] == 'en' and after[2] == '전환 학원'):
                    fails.append('언어 바꾸기: 다시 불러온 뒤 %s' % after)
                print('언어 바꾸기 (?lang=ko → English) — %s' % after)
                c.close()
            else:
                # 공개 뒤 — 브라우저 언어로 고르기 · 설정의 언어 칸(자동 · 한국어 · English) · 바꾸기 · 예전 세이브
                st = "() => [I18N.lang, document.documentElement.lang, localStorage.getItem('hs_lang'), localStorage.getItem('hs_lang0')]"
                lpj = "() => [...document.querySelectorAll('[data-lang]')].map(b => b.dataset.lang + ':' + b.getAttribute('aria-pressed') + ':' + b.textContent)"
                def reloaded(pg):
                    pg.wait_for_function("() => typeof S !== 'undefined' && S && S.students && !document.getElementById('bootLoader')", polling=250, timeout=60000)
                    pg.wait_for_timeout(200)
                c, pg, errs = open_page(pb, locale='en-US')
                r1 = pg.evaluate(st)
                if r1[:2] != ['en', 'en'] or r1[2] is not None or r1[3] != '1':
                    fails.append('공개: 영어 브라우저 · 새 방문인데 영어가 아니다 %s' % r1)
                c.close()
                c, pg, errs = open_page(pb, locale='ko-KR')
                r2 = pg.evaluate(st)
                if r2[:2] != ['ko', 'ko'] or r2[2] is not None:
                    fails.append('공개: 한국어 브라우저인데 한국어가 아니다 %s' % r2)
                pg.evaluate("() => { __hsReset(9); closeModal(); newScenarioStart('전환 학원'); closeModal(); UI.view = 'opt'; render(); }")
                lp2 = pg.evaluate(lpj)
                if lp2 != ['auto:true:자동', 'ko:false:한국어', 'en:false:English']:
                    fails.append('공개: 한국어 설정의 언어 칸 %s' % lp2)
                with pg.expect_navigation(timeout=30000):
                    pg.click('[data-lang=en]')
                reloaded(pg)
                after = pg.evaluate("() => [location.search, I18N.lang, localStorage.getItem('hs_lang'), S.acadName]")
                if after != ['', 'en', 'en', '전환 학원']:
                    fails.append('공개: English 를 누른 뒤 %s' % after)
                pg.evaluate("() => { closeModal(); UI.view = 'opt'; render(); }")
                with pg.expect_navigation(timeout=30000):
                    pg.click('[data-lang=auto]')
                reloaded(pg)
                back = pg.evaluate("() => [I18N.lang, localStorage.getItem('hs_lang'), S.acadName]")
                if back != ['ko', None, '전환 학원']:
                    fails.append('공개: 자동을 누른 뒤 (한국어 브라우저) %s' % back)
                c.close()
                # 공개 전부터 하던 사람 — 세이브가 있고 hs_lang 이 없으면 영어 브라우저여도 한국어로 기억. 자동을 고르면 그때부터 브라우저(영어)
                old_save = ('if(!sessionStorage.getItem("__old")){localStorage.setItem("heroacademy_v1", %s);sessionStorage.setItem("__old","1")}'
                            % json.dumps(json.dumps({"v": 1})))
                c, pg, errs = open_page(pb, locale='en-US', init=old_save)
                r3 = pg.evaluate(st)
                if r3 != ['ko', 'ko', 'ko', '1']:
                    fails.append('공개: 예전 세이브 · 영어 브라우저 — 한국어로 기억하지 않았다 %s' % r3)
                pg.evaluate("() => { closeModal(); UI.view = 'opt'; render(); }")
                with pg.expect_navigation(timeout=30000):
                    pg.click('[data-lang=auto]')
                reloaded(pg)
                r4 = pg.evaluate(st)
                if r4 != ['en', 'en', None, '1']:
                    fails.append('공개: 예전 세이브에서 자동을 고른 뒤 영어 브라우저를 따르지 않는다 %s' % r4)
                c.close()
                print('공개 — 영어 브라우저 %s · 한국어 브라우저 %s · 언어 칸 %s · English %s · 자동 %s · 예전 세이브 %s → 자동 %s'
                      % (r1[0], r2[0], lp2, after[1], back[0], r3[0], r4[0]))
            br.close()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    if fails:
        print('\n실패 %d:' % len(fails))
        for f in fails:
            print(' ✗', f[:600])
        sys.exit(1)
    print('\n통과 — 한국어는 변환 전과 같고, 영어 시험 단어가 보인다 (%.0f초)' % (time.time() - t0))


if __name__ == '__main__':
    main()
