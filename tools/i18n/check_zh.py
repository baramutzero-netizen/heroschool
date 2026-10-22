"""중국어판 준비 시험 (1022) — 빌드한 heroschool.html 을 ?lang=zh-Hans · zh-Hant · 한국어 · 영어 · 일본어로 띄워 중국어 글꼴 · CSS 가
그 언어에서만 붙는지 본다. check_ja.py 와 같은 방법.

    python3 tools/i18n/check_zh.py            (저장소 맨 위 · hs.py build 뒤 · playwright · 바깥 주소는 막는다)

· 간체(zh-Hans) · 번체(zh-Hant · 대만) — <html lang> · 글꼴 덧규칙(#i18nZhFonts · #i18nZhtFonts)이 lateFonts 뒤 · 물마루 · 물마루 Mono · 봄바람체 자리의
  그 언어 글꼴이 받아짐 · 메뉴 · 위쪽 칸이 그 언어 · 12px 글자가 또렷함(사이 색 없음) · keep-all → normal · line-break strict ·
  도트 폰트를 끄면 기기 글꼴(PingFang SC · Songti SC / PingFang TC · Songti TC …)이 앞에 · 학생 명부 책(그림자 DOM)의 keep-all 도 normal · 오류 없음
· 한국어 · 영어 · 일본어 — 중국어 글꼴 · CSS 가 없다 (일본어는 일본어 글꼴 · CSS 그대로)
· 공개 — 시험 빌드(check_i18n.build)를 로컬 http 로 띄운다. config.json 이 아직 공개 전이면 머리 스크립트의 Z · T 만 공개로 바꿔 흉내 낸다:
  중국어 브라우저(zh-CN · zh-SG · zh)는 간체 · 번체 지역(zh-TW · zh-HK)은 번체 · ?lang=zh · zh-cn · zh-tw 도 · 한국어 설정 칸에 简体中文 · 繁體中文 →
  누르면 기억 · 그동안 영어로 하던 중국어 브라우저는 영어 그대로 · 자동을 고르면 그때부터 중국어
"""
import json, os, re, sys
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PAGE = os.path.join(ROOT, 'heroschool.html')
LANG = {   # 간체 · 번체 — 글꼴 덧규칙 id · 화면 CSS id · 시험 글 · 메뉴 낱말 · 도트 폰트를 껐을 때 앞에 올 글꼴
    'zh-Hans': {'fonts': 'i18nZhFonts', 'css': 'i18nZhCss', 'px': '强化点数123 技能', 'mono': '战斗力 1,808', 'boast': '哈哈哈！看好了！',
                'wrap': '那个……能耽误您一点时间吗？不会太久的。', 'menu': ('谈心', '日程'), 'h2': '春季大赛', 'sans': '"PingFang SC"', 'serif': '"Songti SC"'},
    'zh-Hant': {'fonts': 'i18nZhtFonts', 'css': 'i18nZhtCss', 'px': '強化點數123 技能', 'mono': '戰鬥力 1,808', 'boast': '哈哈哈！看好了！',
                'wrap': '那個……能耽誤您一點時間嗎？不會太久的。', 'menu': ('談心', '日程'), 'h2': '春季大賽', 'sans': '"PingFang TC"', 'serif': '"Songti TC"'},
}
LOCALE = {'zh-Hans': 'zh-CN', 'zh-Hant': 'zh-TW', 'ja': 'ja-JP'}

PROBE = r"""async (L) => {
  const late = document.getElementById('lateFonts');
  const box = document.createElement('div'); box.id = 'zhT';
  box.style.cssText = 'position:fixed;left:0;top:0;z-index:99999;background:#fff;color:#000;padding:4px 6px';
  box.innerHTML = '<div id="zhPx" style="font:12px/20px Mulmaru;white-space:nowrap">' + L.px + '</div>'
    + '<div id="zhMono" style="font:12px/20px \'Mulmaru Mono\',Mulmaru;white-space:nowrap">' + L.mono + '</div>'
    + '<div class="greet boast" id="zhBoast" style="position:static;width:auto">' + L.boast + '</div>'
    + '<div class="greet" id="zhWrap" style="position:static;width:120px;font:12px/20px Mulmaru">' + L.wrap + '</div>';
  document.body.appendChild(box);
  await new Promise(r => setTimeout(r, 300)); await document.fonts.ready;
  const faces = []; document.fonts.forEach(f => { if(/^(Mulmaru|Mulmaru Mono|HsBombaram21)$/.test(f.family)) faces.push([f.family, f.status, String(f.unicodeRange)]); });
  const cs = id => getComputedStyle(document.getElementById(id)), has = id => !!document.getElementById(id);
  const tail = ['i18nJaFonts', 'i18nZhFonts', 'i18nZhtFonts'].filter(has), css = ['i18nCss', 'i18nJaCss', 'i18nZhCss', 'i18nZhtCss'].filter(has);
  const t = tail[0] && document.getElementById(tail[0]);
  return {lang: document.documentElement.lang, tail, css, faces,
          after: !!(late && t && (late.compareDocumentPosition(t) & Node.DOCUMENT_POSITION_FOLLOWING)),
          wrapWB: cs('zhWrap').wordBreak, wrapLB: cs('zhWrap').lineBreak,
          side: (document.getElementById('app') || document.body).innerText.slice(0, 1500)};
}"""
NOPIXEL = r"""async (h2t) => { pixelFontApply(false); await new Promise(r => setTimeout(r, 200));
  const b = getComputedStyle(document.body).fontFamily, h = document.createElement('h2'); h.textContent = h2t; document.body.appendChild(h);
  const hf = getComputedStyle(h).fontFamily; h.remove(); pixelFontApply(true); return {body: b, h2: hf}; }"""
ROSTER = r"""async () => { UI.view = 'roster'; render(); await new Promise(r => setTimeout(r, 600));
  const h = document.getElementById('rbHost'); if(!h || !h.shadowRoot) return null;
  const st = h.shadowRoot.getElementById('i18nCss'), bub = h.shadowRoot.querySelector('.bub');
  return {css: st ? st.textContent : '', bub: bub ? getComputedStyle(bub).wordBreak : null}; }"""


def crisp(png):
    """12px 줄의 픽셀 — 흰 바탕 · 검은 글자에서 사이 색(번짐) 비율"""
    from PIL import Image
    import io
    im = Image.open(io.BytesIO(png)).convert('L')
    px = im.tobytes()
    ink = sum(1 for v in px if v < 128)
    mid = sum(1 for v in px if 24 < v < 232)
    return ink, mid


def pub_check(br, fails):
    """중국어 공개 — 시험 빌드를 로컬 http 로 (공개 전이면 머리 스크립트의 Z · T 만 바꿔 흉내)"""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import check_i18n as C
    html = C.build(True, 'zh-pub-check')
    m = re.search(r'var P=(true|false),J=(true|false),Z=(true|false),T=(true|false),', html)
    if not m:
        fails.append('공개: 머리 스크립트의 P · J · Z · T 를 못 찾았다'); return
    if m.group(1) != 'true':
        fails.append('공개: config.json public 이 꺼져 있다'); return
    real = m.group(3) == 'true' and m.group(4) == 'true'
    html = html.replace(m.group(0), 'var P=true,J=%s,Z=true,T=true,' % m.group(2), 1)
    srv, url, port = C.serve(html)
    st = "() => [I18N.lang, document.documentElement.lang, localStorage.getItem('hs_lang'), !!I18N.pubZh, !!I18N.pubZhT]"
    lpj = "() => [...document.querySelectorAll('[data-lang]')].map(b => b.dataset.lang + ':' + b.getAttribute('aria-pressed') + ':' + b.textContent)"
    ja_pub = m.group(2) == 'true'
    ALL = ['ko:false:한국어', 'en:false:English'] + (['ja:false:日本語'] if ja_pub else []) + ['zh-Hans:false:简体中文', 'zh-Hant:false:繁體中文']

    def reloaded(pg):
        pg.wait_for_function("() => typeof S !== 'undefined' && S && Array.isArray(S.students) && S.students.length > 0 && !document.getElementById('bootLoader')",
                             polling=250, timeout=60000)
        pg.wait_for_timeout(200)

    def page(locale, query='', init=None):
        c = br.new_context(viewport={'width': 1440, 'height': 900}, locale=locale)
        c.route(re.compile(r'^https?://(?!127\.0\.0\.1:%d/)' % port), lambda r: r.abort())
        c.add_init_script(C.INIT_JS)
        if init:
            c.add_init_script(init)
        pg = c.new_page()
        pg.goto(url + query, wait_until='commit')
        reloaded(pg)
        return c, pg

    try:
        got = {}
        for loc, want in (('zh-CN', 'zh-Hans'), ('zh-SG', 'zh-Hans'), ('zh', 'zh-Hans'), ('zh-TW', 'zh-Hant'), ('zh-HK', 'zh-Hant'), ('zh-MO', 'zh-Hant'),
                          ('ja-JP', 'ja' if ja_pub else 'en'), ('ko-KR', 'ko'), ('en-US', 'en')):
            c, pg = page(loc); r = pg.evaluate(st); c.close()
            got[loc] = r[0]
            if r[0] != want or r[1] != want or r[2] is not None or not (r[3] and r[4]):
                fails.append('공개: %s 브라우저 · 새 방문 → %s (기대 %s)' % (loc, r, want))
        for q, want in (('?lang=zh', 'zh-Hans'), ('?lang=zh-cn', 'zh-Hans'), ('?lang=zh-Hans', 'zh-Hans'), ('?lang=zh-tw', 'zh-Hant'), ('?lang=zh-HK', 'zh-Hant'), ('?lang=zh-Hant', 'zh-Hant')):
            c, pg = page('en-US', q); r = pg.evaluate(st); c.close()
            if r[0] != want:
                fails.append('공개: %s → %s (기대 %s)' % (q, r, want))
        c, pg = page('ko-KR')
        pg.evaluate("() => { __hsReset(9); closeModal(); newScenarioStart('전환 학원'); closeModal(); UI.view = 'opt'; render(); }")
        lp = pg.evaluate(lpj)
        if lp != ['auto:true:자동'] + ALL:
            fails.append('공개: 한국어 설정의 언어 칸 %s' % lp)
        for k, auto in (('zh-Hant', '自動'), ('zh-Hans', '自动')):
            with pg.expect_navigation(timeout=30000):
                pg.click('[data-lang="%s"]' % k)
            reloaded(pg)
            z2 = pg.evaluate("() => [location.search, I18N.lang, localStorage.getItem('hs_lang'), S.acadName]")
            if z2[:3] != ['', k, k]:
                fails.append('공개: %s 를 누른 뒤 %s' % (k, z2))
            pg.evaluate("() => { closeModal(); UI.view = 'opt'; render(); }")
            lp2 = pg.evaluate(lpj)
            exp = ['auto:false:' + auto] + [x.replace(k + ':false:', k + ':true:') for x in ALL]
            if lp2 != exp:
                fails.append('공개: %s 설정의 언어 칸 %s' % (k, lp2))
        c.close()
        was_en = ('if(!sessionStorage.getItem("__old")){localStorage.setItem("heroacademy_v1", %s);localStorage.setItem("hs_lang0","1");localStorage.setItem("hs_lang0j","1");sessionStorage.setItem("__old","1")}'
                  % json.dumps(json.dumps({"v": 1})))
        res = []
        for loc, want in (('zh-CN', 'zh-Hans'), ('zh-TW', 'zh-Hant')):
            c, pg = page(loc, init=was_en)
            z3 = pg.evaluate(st)
            if z3[:3] != ['en', 'en', 'en']:
                fails.append('공개: 영어로 하던 %s 브라우저 — 영어로 기억하지 않았다 %s' % (loc, z3))
            pg.evaluate("() => { closeModal(); UI.view = 'opt'; render(); }")
            with pg.expect_navigation(timeout=30000):
                pg.click('[data-lang=auto]')
            reloaded(pg)
            z4 = pg.evaluate(st)
            if z4[:3] != [want, want, None]:
                fails.append('공개: 자동을 고른 뒤 %s 브라우저를 따르지 않는다 %s' % (loc, z4))
            c.close()
            res.append('%s %s → 자동 %s' % (loc, z3[0], z4[0]))
        print('공개%s — 브라우저 %s · ?lang=zh · zh-tw · 언어 칸 %d개 · 영어로 하던 사람 %s'
              % ('' if real else '(흉내 — config.json 은 아직 공개 전)', ' '.join('%s→%s' % kv for kv in got.items()), len(lp), ' · '.join(res)))
    finally:
        srv.shutdown()


def main():
    if not os.path.exists(PAGE):
        sys.exit('heroschool.html 이 없다 — hs.py build 먼저')
    fails = []
    with sync_playwright() as p:
        br = p.chromium.launch()
        for lang in ('zh-Hans', 'zh-Hant', 'ko', 'en', 'ja'):
            ctx = br.new_context(viewport={'width': 1440, 'height': 900}, locale=LOCALE.get(lang, 'ko-KR'))
            ctx.route(re.compile(r'^https?://'), lambda r: r.abort())
            pg = ctx.new_page()
            errs = []
            pg.on('pageerror', lambda e: errs.append('pageerror: ' + str(e)[:200]))
            pg.on('console', lambda m: errs.append(m.text[:200]) if m.type == 'error' and 'Failed to load resource' not in m.text else None)
            pg.goto('file://' + PAGE + ('?lang=' + lang if lang != 'ko' else ''), wait_until='commit')
            pg.wait_for_function("() => typeof S !== 'undefined' && S && Array.isArray(S.students) && S.students.length > 0"
                                 " && !document.getElementById('bootLoader')", polling=250, timeout=40000)
            pg.evaluate("() => { try { audOver(null); } catch(e) {} closeModal(); UI.view = 'home'; render(); }")
            pg.wait_for_timeout(300)
            L = LANG.get(lang, LANG['zh-Hans'])
            r = pg.evaluate(PROBE, L)
            lang_faces = [f for f in r['faces'] if f[2] != 'U+0-10FFFF']

            def need(cond, msg):
                if not cond:
                    fails.append('%s: %s' % (lang, msg))
            if lang in LANG:
                need(r['lang'] == lang, 'html lang %r' % r['lang'])
                need(r['tail'] == [L['fonts']] and r['after'], '글꼴 덧규칙 %s · lateFonts 뒤 %s' % (r['tail'], r['after']))
                need(r['css'] == [L['css']], '화면 CSS %s (기대 %s)' % (r['css'], L['css']))
                need(sorted(f[0] for f in lang_faces) == ['HsBombaram21', 'Mulmaru', 'Mulmaru Mono'], '글꼴 자리 %s' % [f[0] for f in lang_faces])
                need(all(f[1] == 'loaded' for f in lang_faces), '받지 못한 글꼴 %s' % [f[:2] for f in lang_faces if f[1] != 'loaded'])
                need(all(w in r['side'] for w in L['menu']), '메뉴 · 위쪽 칸에 %s 이(가) 없다' % (L['menu'],))
                need(r['wrapWB'] == 'normal' and r['wrapLB'] == 'strict', 'keep-all → normal · strict 아님 (%s · %s)' % (r['wrapWB'], r['wrapLB']))
                ink, mid = crisp(pg.locator('#zhPx').screenshot())
                need(ink > 50 and mid <= ink * 0.02, '12px 글자가 번진다 (글자 픽셀 %d · 사이 색 %d)' % (ink, mid))
                n = pg.evaluate(NOPIXEL, L['h2'])
                need(n['body'].startswith(L['sans']) and n['h2'].startswith(L['serif']), '도트 폰트를 껐을 때 %s' % n)
                rb = pg.evaluate(ROSTER)
                need(rb is not None and 'word-break:normal' in rb['css'] and rb['bub'] == 'normal', '학생 명부 책 %s' % (rb and {k: (v[:60] if isinstance(v, str) else v) for k, v in rb.items()}))
                print('%s — 글꼴 %s · 12px 글자 픽셀 %d · 사이 색 %d · 도트 끔 %s / %s' % (
                    lang, ' · '.join('%s %s' % (f[0], f[1]) for f in lang_faces), ink, mid, n['body'].split(',')[0], n['h2'].split(',')[0]))
            else:
                need(r['lang'] == lang, 'html lang %r' % r['lang'])
                need(not any(t in ('i18nZhFonts', 'i18nZhtFonts') for t in r['tail']) and not any(c in ('i18nZhCss', 'i18nZhtCss') for c in r['css']),
                     '중국어 글꼴 · CSS 가 붙었다 (%s · %s)' % (r['tail'], r['css']))
                if lang == 'ja':
                    need(r['tail'] == ['i18nJaFonts'] and r['css'] == ['i18nJaCss'], '일본어 글꼴 · CSS 가 빠졌다 (%s · %s)' % (r['tail'], r['css']))
                    need(r['wrapWB'] == 'normal', '일본어 keep-all → normal 아님 (%s)' % r['wrapWB'])
                else:
                    need(not lang_faces and not r['tail'], '다른 언어 글꼴이 붙었다 %s' % [f[0] for f in lang_faces])
                    need(r['wrapWB'] == 'keep-all', 'keep-all 이 바뀌었다 (%s)' % r['wrapWB'])
                    need(r['css'] == (['i18nCss'] if lang == 'en' else []), '화면 CSS %s' % r['css'])
                print('%s — 중국어 글꼴 · CSS 없음%s' % ({'ko': '한국어', 'en': '영어', 'ja': '일본어'}[lang], ' · 일본어 글꼴 · CSS 그대로' if lang == 'ja' else ' · keep-all 그대로'))
            for e in errs:
                fails.append('%s: %s' % (lang, e))
            ctx.close()
        pub_check(br, fails)
        br.close()
    if fails:
        print('\n실패 %d' % len(fails))
        for f in fails:
            print('  ' + f)
        sys.exit(1)
    print('\n통과 — 간체 · 번체 글꼴 · CSS 는 그 언어에서만 붙고, 한국어 · 영어 · 일본어는 그대로 · 공개하면 중국어 브라우저가 간체 · 번체로')


if __name__ == '__main__':
    main()
