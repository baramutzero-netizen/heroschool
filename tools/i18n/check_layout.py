"""영어판 화면 점검 (1010 · 2단계) — 영어로 띄운 화면에서 넘치거나 잘린 칸을 찾는다.

    python3 tools/i18n/check_layout.py [--sizes 1440x900,900x1000,390x844] [--only home,plan] [--shots 폴더] [--years 3]
    hs.py 를 쓰는 세션이면:  python3 ~/hs.py layout   (빌드 뒤에)

check_i18n.py 와 같은 빌드(변환함 · 그림은 저장소 것)를 같은 시드로 몇 해 돌린 뒤, 화면마다 크기마다
  · 잘림   — overflow 가 hidden/clip 인데 글이 상자보다 넓거나(가로) 높다(세로) · 말줄임(…)도
  · 삐져나옴 — 글만 든 상자에서 글이 상자 밖으로 나간다 (overflow 는 보이지만 옆 칸을 덮는다)
  · 화면 밖 — 가로 스크롤 상자 안이 아닌데 화면 오른쪽 · 왼쪽 밖으로 나간다 / 페이지 전체가 가로로 스크롤된다
  · 세로 쌓임 — 좁은 칸에 영어 글자가 한 글자씩 세로로 쌓인다
를 모은다. 같은 화면을 한국어로도 재서 한국어에도 있는 것은 빼고 영어에서 새로 생긴 것만 알린다 (하나라도 있으면 실패).
영어 화면에 남은 한글(글 · title · aria-label 등)도 모은다 — 언어 이름 '한국어' · 'Language · 언어' 말고는 하나라도 있으면 실패 (5단계).
단추 · 제목 · 표 머리처럼 짧은 칸이 한국어보다 줄이 늘어난 것은 넘침이 아니라 개수만 알린다 (--wrap 이면 목록).
화면: 메뉴 화면 전부 · 마을 탭 · 학생 명부 책 · 목표 · 운영 안내 14장 · 스킬 강화 · 상담창 · 이야기 팝업(4단계 — cer_*) · 프롤로그 · 마을 손님
    · 경과 보고 · 대회(시내 · 광역 · 신인전) · 전투.
바깥 주소는 전부 막는다. --shots 를 주면 영어 화면을 크기별로 찍어 둔다 (--ko-shots 면 한국어도 · --full 이면 세로 화면은 페이지 전체).
"""
import argparse, json, os, re, shutil, sys, tempfile, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import check_i18n as C

# 화면 목록 — 이름: 띄우는 코드 (UI.sel = 첫 학생). 없는 화면(아직 열리지 않은 서브탭 등)은 건너뛴다
SCENES = r"""(() => {
  const RBC = () => { if (window.RBK && RBK.isOpen()) RBK.close(true); };
  const V = v => () => { RBC(); closeModal(); UI.view = v; render(); };
  const fac = k => () => { RBC(); closeModal(); UI.view = 'facil'; UI.facTab = k; render(); };
  const sc = {};
  ['home','master','roster','team','plan','relic','skill','counsel','league','lgentry','spshop','rank','log','csllog','record','codex','opt']
    .forEach(v => sc[v] = V(v));
  sc['roster_nosel'] = () => { RBC(); closeModal(); UI.view = 'roster'; UI.sel = null; render(); };
  if (window.RBK && RBK.on()) {
    sc['rbook_detail'] = () => { RBC(); closeModal(); UI.view = 'home'; render(); RBK.open({mode: 'detail', sel: S.students[0].id}); };
    sc['rbook_team'] = () => { RBC(); closeModal(); UI.view = 'home'; render(); RBK.open({mode: 'team'}); };
  }
  facTabs().forEach(t => sc['facil_' + t.k] = fac(t.k));
  sc['mission'] = () => { RBC(); closeModal(); UI.view = 'home'; render(); missionModal(); };
  [1,2,3,4,5,6,7,8,9,10,11,12,13,14].forEach(k => sc['tut' + k] = () => { RBC(); closeModal(); showModal(tutGuideHTML(k)); });
  sc['skillup'] = () => { RBC(); closeModal(); const s = S.students.find(x => (x.skPts|0) > 0) || S.students[0]; skillUpModal(s.id); };
  sc['cslwin'] = () => { RBC(); closeModal(); UI.view = 'counsel'; render(); cslwOpen(); };
  /* 4단계 (1010) — 이야기 팝업 · 프롤로그 · 마을 손님. 팝업은 대기열을 비우고 하나만 띄운다 */
  const cer = c => () => { RBC(); closeModal(); UI.ceremonies = [c]; showCeremony(); };
  const s0 = S.students[0], s1 = S.students[1] || S.students[0];
  const who = st => ({sid: st.id, name: dn(st), raw: st.name, job: st.job});
  [1, 2, 3, 4].forEach(p => sc['cer_sparkler' + p] = cer(Object.assign({type: 'sparkler', year: S.year, pers: 'tsun', page: p}, who(s0))));
  sc['cer_sparkler_dp1'] = cer(Object.assign({type: 'sparkler', year: S.year, pers: 'genius', page: 4, uniq: 'dp1'}, who(s0)));
  [1, 2, 3].forEach(p => sc['cer_valentine' + p] = cer({type: 'valentine', page: p, year: S.year, n: 2,
    notes: [{name: s0.name, pers: 'boast', msg: VALENTINE_MSG.boast[1]}, {name: s1.name, pers: 'hot', msg: VALENTINE_MSG.hot[1]}]}));
  [1, 2, 3, 4, 5].forEach(p => sc['cer_guild' + p] = cer({type: 'guild', page: p, year: S.year, phase: 'spring', week: 7}));
  [1, 2].forEach(p => sc['cer_rivalintro' + p] = cer({type: 'rivalintro', page: p, year: S.year}));
  sc['cer_rival'] = cer({type: 'rival', year: S.year, phase: 'spring', week: 2, scene: RIVAL_SCENE[3], a: s0, b: s1});
  sc['cer_bro'] = cer({type: 'bro', year: S.year, phase: 'summer', week: 2, scene: BRO_SCENE[1], a: s0, b: s1});
  sc['cer_jobgrade'] = cer({type: 'jobgrade', k: 'tavern', grade: 2, max: false, year: S.year, phase: 'spring', week: 8, count: 20});
  sc['cer_jobev'] = cer({type: 'jobev', k: 'salon', lv: 1, year: S.year, phase: 'spring', week: 8});
  sc['cer_insight'] = cer({type: 'insight', year: S.year, ins: CAMP_INSIGHT[4], pts: 3});
  sc['cer_friendly'] = () => { RBC(); closeModal(); const F = friendlyState('spring'); F.offers = genFriendlyOffers(); UI.ceremonies = [{type: 'friendly', year: S.year, phase: 'spring'}]; showCeremony(); };
  sc['cer_evolve1'] = cer(Object.assign({type: 'evolve', page: 1, year: S.year, phase: 'spring', week: 3, kind: 'ment', d: 2}, who(s0)));
  sc['cer_evolve2'] = cer(Object.assign({type: 'evolve', page: 2, year: S.year, phase: 'spring', week: 3, kind: 'ment', d: 2}, who(s0)));
  sc['cer_evolve3'] = cer(Object.assign({type: 'evolve', page: 2, year: S.year, phase: 'spring', week: 3, kind: 'cond', d: 10}, who(s0)));
  sc['cer_shopopen'] = cer({type: 'shopopen', year: S.year});
  if (S.graduates && S.graduates.length) sc['cer_grad'] = cer({type: 'grad', year: S.year, fame: 120, gold: 900,
    list: S.graduates.slice(0, 3).map(g => Object.assign({}, g, {gift: g.career}))});
  sc['cer_portal'] = cer({type: 'portal', year: S.year});
  sc['cer_fame'] = cer({type: 'fame', year: S.year, mark: FAME_MARKS[0]});
  sc['cer_fall'] = cer({type: 'fall', year: S.year});
  sc['cer_camp'] = cer({type: 'camp', year: S.year, drop: 2});
  sc['cer_scout'] = cer({type: 'scout', year: S.year, tries: 5, cap: 3, n: 6, idx: 2, title: fameTitle(S.fame).n, grad: 3});
  sc['cer_unlock'] = cer({type: 'unlock', year: S.year, kind: 'fest', rest: true});
  sc['cer_enroll'] = cer({type: 'enroll', year: S.year, list: S.students.slice(0, 2), back: S.students.slice(2, 5)});
  sc['cer_lvup'] = cer({type: 'lvup', sid: s0.id, lv0: Math.max(1, s0.level - 2), lv1: s0.level});
  [0, 1, 2].forEach(i => sc['prologue' + (i + 1)] = () => { RBC(); closeModal(); showPrologue(i); });
  sc['townev_farm'] = () => { RBC(); closeModal(); const R = TOWN_EV_RWD.farm(PHASES[S.phase].n); showModal(townEvPage({k: 'farm', line: R.line, rwd: R.rwd})); };
  sc['townev_bank'] = () => { RBC(); closeModal(); townEvBank({amt: 2000}); };
  /* 이명 팝업은 학생의 이명을 바꾸므로 학생 화면들 뒤에 */
  sc['cer_epithet'] = () => { RBC(); closeModal(); UI.ceremonies = []; grantEpithet('exped', s0, {event: DUNGEONS[0].n, place: DUNGEONS[0].n, foe: typeof _T === 'function' ? _T('망령 기사', 'MON') : '망령 기사'}); showCeremony(); };
  sc['cer_epithet_tour'] = () => { RBC(); closeModal(); UI.ceremonies = []; grantEpithet('tour', s1, {event: LADDER.city.n, foeAcad: acadNames(1)[0], foe: s0.name}); showCeremony(); };
  /* 아래는 게임을 진행시킨다 — 맨 뒤에 둔다 */
  sc['report'] = () => { RBC(); closeModal(); if (S.master) S.master.pts = 0; UI.view = 'plan'; render(); autoFillSlots(); runWithReport(); };
  sc['tour_prep'] = () => { RBC(); closeModal(); UI.ceremonies = []; UI.view = 'home'; render(); startLadder('city'); render(); };
  sc['tour_entry'] = () => { if (UI.tour) { UI.tour._prepOpen = false; UI.tour.stage = 'entry'; } render(); };
  sc['tour_region'] = () => { closeModal(); UI.tour = null; UI.pendingTour = null; startLadder('region'); if (UI.tour) { UI.tour._prepOpen = false; UI.tour.stage = 'entry'; } render(); };
  sc['tour_spring'] = () => { closeModal(); UI.tour = null; UI.pendingTour = null; startSpringTour(); render(); };
  /* 전투 화면은 닫는 길이 따로라 맨 끝에 */
  sc['battle'] = () => {
    RBC(); closeModal(); UI.tour = null; UI.pendingTour = null; UI.view = 'home'; render();
    const ids = S.students.map(x => x.id), A = tourMatchStudents(ids.slice(0,3)), B = tourMatchStudents(ids.slice(3,6).length ? ids.slice(3,6) : ids.slice(0,3));
    openBattle(runBattle(A, B, {titleA: S.acadName, titleB: 'B'}), {intro: false});
  };
  return sc;
})()"""

MEASURE = r"""() => {
  const W = innerWidth, out = [];
  const roots = [document.getElementById('app'), document.getElementById('modalRoot'), document.getElementById('nav'),
                 window.RBK && RBK.isOpen() && RBK.state.root].filter(Boolean);
  const lines = {};
  const vis = (el, cs) => cs.display !== 'none' && cs.visibility !== 'hidden' && el.getClientRects().length;
  const ownText = el => [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim());
  const leaf = el => [...el.children].every(c => /^(B|I|EM|STRONG|SMALL|SPAN|SUB|SUP|BR|U|S|MARK|CODE|KBD)$/.test(c.tagName) && !c.children.length);
  const path = el => { const p = []; for (let e = el; e && e !== document.body; e = e.parentElement) {
      const i = e.parentElement ? [...e.parentElement.children].indexOf(e) : 0; p.unshift(e.tagName.toLowerCase() + ':' + i); } return p.join('>'); };
  const desc = el => el.tagName.toLowerCase() + (el.id ? '#' + el.id : '') + (el.classList.length ? '.' + [...el.classList].slice(0, 3).join('.') : '');
  const scrollX = el => { for (let e = el.parentElement; e; e = e.parentElement) { const o = getComputedStyle(e).overflowX; if (o === 'auto' || o === 'scroll') return true; } return false; };
  const seen = new Set();
  for (const root of roots) for (const el of root.querySelectorAll('*')) {
    const cs = getComputedStyle(el);
    if (!vis(el, cs) || cs.position === 'fixed' && el.closest('.toast, #toastRoot')) continue;
    const text = (el.textContent || '').replace(/\s+/g, ' ').trim();
    if (!text || el.tagName === 'SCRIPT' || el.tagName === 'STYLE' || el.tagName === 'svg' || el.closest('svg')) continue;
    const r = el.getBoundingClientRect();
    const add = (kind, over) => { const k = path(el) + '|' + kind; if (seen.has(k)) return; seen.add(k);
      out.push({kind, over: Math.round(over), path: path(el), el: desc(el), text: text.slice(0, 70), w: Math.round(r.width)}); };
    const ox = cs.overflowX, oy = cs.overflowY;
    if ((ox === 'hidden' || ox === 'clip') && el.scrollWidth > el.clientWidth + 1 && (ownText(el) || leaf(el) || cs.textOverflow === 'ellipsis'))
      add(cs.textOverflow === 'ellipsis' ? 'ellipsis' : 'clipX', el.scrollWidth - el.clientWidth);
    if ((oy === 'hidden' || oy === 'clip') && el.scrollHeight > el.clientHeight + 2 && (ownText(el) || leaf(el)) && !cs.webkitLineClamp?.match?.(/^\d/))
      add('clipY', el.scrollHeight - el.clientHeight);
    if (ox === 'visible' && ownText(el) && leaf(el) && el.scrollWidth > el.clientWidth + 2 && el.clientWidth > 0)
      add('spill', el.scrollWidth - el.clientWidth);
    if ((r.right > W + 1 || r.left < -1) && ownText(el) && !scrollX(el) && r.width < W * 1.5)
      add('offscreen', Math.max(r.right - W, -r.left));
    if (ownText(el) && leaf(el)) {
      const rg = document.createRange(); rg.selectNodeContents(el);
      const tops = new Set([...rg.getClientRects()].filter(q => q.width > 0.5).map(q => Math.round(q.top / 3)));
      const n = Math.max(1, tops.size);
      const letters = text.replace(/[^A-Za-z가-힣]/g, '').length;
      if (n >= 3 && letters >= 4 && n >= letters * 0.6 && cs.writingMode === 'horizontal-tb') add('stack', n);
      if (r.width < 420 && (/^(BUTTON|TH|H1|H2|H3|H4|LABEL|SUMMARY|A)$/.test(el.tagName) || el.closest('button, th, h1, h2, h3, nav, .ttab, .tab, .eyebrow, .btn, [role=tab]')))
        lines[path(el)] = {n, el: desc(el), text: text.slice(0, 60), w: Math.round(r.width)};
    }
  }
  const pageX = document.documentElement.scrollWidth - innerWidth;
  if (pageX > 1) out.push({kind: 'pageX', over: pageX, path: 'html', el: 'html', text: '', w: innerWidth});
  return {out, lines};
}"""


HAN_JS = r"""() => {
  const roots = [document.getElementById('app'), document.getElementById('modalRoot'), document.getElementById('nav'), document.getElementById('toastRoot'),
                 window.RBK && RBK.isOpen() && RBK.state.root].filter(Boolean);
  const out = [], seen = new Set(), OK = /^(한국어|Language · 언어)$/;
  const vis = el => { const cs = getComputedStyle(el); return cs.display !== 'none' && cs.visibility !== 'hidden' && el.getClientRects().length; };
  for (const root of roots) {
    const w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    let t;
    while ((t = w.nextNode())) {
      const v = t.nodeValue.replace(/\s+/g, ' ').trim(), el = t.parentElement;
      if (!/[가-힣]/.test(v) || OK.test(v) || !el || el.closest('script,style') || !vis(el) || seen.has(v)) continue;
      seen.add(v); out.push({el: el.tagName.toLowerCase() + (typeof el.className === 'string' && el.className ? '.' + el.className.split(' ')[0] : ''), text: v.slice(0, 120)});
    }
    for (const el of root.querySelectorAll('[title],[aria-label],[placeholder],[alt]')) for (const a of ['title', 'aria-label', 'placeholder', 'alt']) {
      const v = el.getAttribute(a);
      if (v && /[가-힣]/.test(v) && !OK.test(v) && !seen.has(a + v)) { seen.add(a + v); out.push({el: el.tagName.toLowerCase() + '@' + a, text: v.slice(0, 120)}); }
    }
  }
  return out;
}"""


FULL = False


def run(br, path, query, size, scenes_only, shots, years, tag):
    w, h = size
    c = br.new_context(viewport={'width': w, 'height': h}, device_scale_factor=1, locale='ko-KR' if tag == 'ko' else 'en-US')   # 브라우저 언어도 맞춘다 (공개 뒤)
    c.route(re.compile(r'^https?://'), lambda r: r.abort())
    c.add_init_script(C.INIT_JS)
    pg = c.new_page()
    errs = []
    pg.on('pageerror', lambda e: errs.append('pageerror: ' + str(e)[:300]))
    pg.goto('file://' + path + query, wait_until='commit')
    pg.wait_for_function("() => typeof S !== 'undefined' && S && Array.isArray(S.students) && S.students.length > 0"
                         " && !document.getElementById('bootLoader')", polling=250, timeout=60000)
    pg.wait_for_timeout(300)
    r = pg.evaluate(C.SIM_JS, years)
    if r['err']:
        errs += ['sim: ' + e for e in r['err'][:3]]
    names = pg.evaluate("() => { UI.ceremonies = []; UI.pendingTour = null; UI.tour = null; closeModal();"
                        " window.__SC = %s; UI.sel = S.students[0] && S.students[0].id; return Object.keys(__SC); }" % SCENES)
    res = {}
    for n in names:
        if scenes_only and n not in scenes_only and n.split('_')[0] not in scenes_only:
            continue
        try:
            pg.evaluate("n => { UI.ceremonies = []; UI.sel = S.students[0] && S.students[0].id; __SC[n](); }", n)
        except Exception as e:
            res[n] = {'error': str(e)[:200]}
            continue
        pg.wait_for_timeout(1500 if n in ('report', 'cslwin') or n.startswith('tour') else 900 if n == 'battle' or n.startswith('rbook') or n in ('roster', 'team') else 250)
        m = pg.evaluate(MEASURE)
        res[n] = {'issues': m['out'], 'lines': m['lines'], 'han': pg.evaluate(HAN_JS) if tag == 'en' else []}
        if shots:
            pg.screenshot(path=os.path.join(shots, '%s_%dx%d_%s.png' % (tag, w, h, n)), full_page=FULL and w < 1100)   # 가로 넓은 화면은 페이지 전체로 찍으면 세로가 되어 배치가 바뀐다
    c.close()
    return res, C.real_errors(errs)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--sizes', default='1440x900,900x1000,390x844')
    ap.add_argument('--only', default='', help='화면 이름 (쉼표) — home,plan,facil,tut …')
    ap.add_argument('--shots', help='영어 화면 스크린샷 폴더')
    ap.add_argument('--years', type=int, default=3)
    ap.add_argument('--json', help='결과 전체를 JSON 으로')
    ap.add_argument('--no-ko', action='store_true', help='한국어 기준을 재지 않는다 (영어에서 찾은 것 전부)')
    ap.add_argument('--full', action='store_true', help='스크린샷을 페이지 전체로')
    ap.add_argument('--wrap', action='store_true', help='한국어보다 줄이 늘어난 칸도 하나하나 보여 준다 (넘침은 아님 · 기본은 개수만)')
    ap.add_argument('--ko-shots', action='store_true', help='한국어 화면도 찍는다 (견주기용)')
    o = ap.parse_args()
    global FULL
    FULL = o.full
    sizes = [tuple(int(x) for x in s.split('x')) for s in o.sizes.split(',')]
    only = set(filter(None, o.only.split(',')))
    from playwright.sync_api import sync_playwright
    tmp = tempfile.mkdtemp(prefix='hs_layout_')
    t0 = time.time()
    report, bad, info = {}, 0, [0]
    try:
        pb = os.path.join(tmp, 'en.html')
        open(pb, 'w', encoding='utf-8').write(C.build(True, 'layout-check'))
        if o.shots:
            os.makedirs(o.shots, exist_ok=True)
        with sync_playwright() as p:
            br = p.chromium.launch()
            for size in sizes:
                en, e_err = run(br, pb, '?lang=en', size, only, o.shots, o.years, 'en')
                ko, k_err = ({}, []) if o.no_ko else run(br, pb, '?lang=ko', size, only, o.shots if o.ko_shots else None, o.years, 'ko')
                key = '%dx%d' % size
                report[key] = {}
                lines = []
                for n, r in en.items():
                    if 'error' in r:
                        lines.append('  %-14s 띄우지 못함: %s' % (n, r['error'])); continue
                    kr = ko.get(n) or {}
                    base = {(x['path'], x['kind']) for x in kr.get('issues', [])}
                    new = [x for x in r['issues'] if (x['path'], x['kind']) not in base]
                    kl = kr.get('lines', {})
                    for pth, x in r.get('lines', {}).items():
                        if pth in kl and x['n'] > kl[pth]['n'] and x['n'] >= 2:
                            new.append({'kind': 'wrap', 'over': x['n'] - kl[pth]['n'], 'path': pth, 'el': x['el'], 'text': x['text'], 'w': x['w']})
                    new += [{'kind': 'han', 'over': 0, 'path': '', 'el': x['el'], 'text': x['text'], 'w': 0} for x in r.get('han', [])]   # 남은 한글
                    report[key][n] = new
                    hard = [x for x in new if x['kind'] != 'wrap']
                    soft = [x for x in new if x['kind'] == 'wrap']
                    if hard or (soft and o.wrap):
                        bad += len(hard); info[0] += len(soft)
                        nh = sum(1 for x in hard if x['kind'] == 'han')
                        lines.append('  %-14s 넘침 %d%s%s' % (n, len(hard) - nh, (' · 남은 한글 %d' % nh) if nh else '', (' · 줄 늘어남 %d' % len(soft)) if soft else ''))
                        for x in sorted(hard, key=lambda x: -x['over'])[:6] + (sorted(soft, key=lambda x: -x['over'])[:4] if o.wrap else []):
                            lines.append('      %-9s +%-4d %-38s %s' % (x['kind'], x['over'], x['el'][:38], x['text'][:60]))
                    elif soft:
                        info[0] += len(soft)
                print('── %s · 화면 %d · 영어에서 새로 넘친 칸 %d · 남은 한글 %d%s' % (key, len(en), sum(1 for v in report[key].values() for x in v if x['kind'] not in ('wrap', 'han')),
                      sum(1 for v in report[key].values() for x in v if x['kind'] == 'han'),
                      (' · 오류 ' + ' / '.join(e_err[:2])) if e_err else ''))
                print('\n'.join(lines) if lines else '  (없음)')
            br.close()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if o.json:
        json.dump(report, open(o.json, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('\n%s — 넘치거나 잘린 칸 · 남은 한글 %d · 한국어보다 줄이 늘어난 칸 %d (넘침 아님 · --wrap 으로 목록) (%.0f초)' % (
        '통과' if not bad else '확인 필요', bad, info[0], time.time() - t0))
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
