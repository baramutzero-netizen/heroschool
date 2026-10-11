"""화면 크기 자동 맞춤(UISCALE · 1011) 시험 — 큰 화면 PC 에서 게임을 iframe 틀에 넣어 통째로 키우는 것.

    python3 tools/check_scale.py      (저장소 맨 위 · 빌드 뒤에 · Playwright + 크로미움)

1. file:// 2560×1300 ?scale=auto → 틀(문서는 iframe 하나뿐 · 틀 쪽 게임은 돌지 않는다) · 게임은 iframe 안에서 1714×870 창 ·
   devicePixelRatio ×k · 탭 제목이 게임 것
2. 진짜 마우스로 (틀 좌표 = 게임 좌표 × k): 사이드 스케줄 단추 → 스케줄 · 깃펜 집기 → 잉크 → 서명 긋기 → 진행 ·
   마을 사람 → 팝업 · 휠 스크롤 · 키보드(명부 책 Esc) · 창 크기를 바꾸면 다시 맞춤
3. 설정 '화면 크기' 150% → 틀이 ×1.5 로 다시 맞춘다 · 100% → ×1 · 자동 → 다시 ×1.494 (고른 값은 hs_scale)
4. 언어 바꾸기 · 새 버전 불러오기 → 틀째로 다시 불러온다 (시험용 ?scale= 은 그대로)
5. ?scale=user (자동화여도 사람처럼): 2560×1300 은 틀 · 1440×900 은 틀 없이(×1.03) · hs_scale=100 이면 틀 없이 ·
   폰(터치) · iPad 는 틀 없이 · 주소에 scale 이 없으면(자동화) 늘 틀 없이 — 다른 시험은 예전 그대로 돈다
6. http:// (같은 출처)에서도 1 과 같게
바깥 주소(firebase · 글꼴 등)는 전부 막는다 — 서버에는 아무것도 쓰지 않는다.
"""
import asyncio, json, os, re, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(ROOT, 'heroschool.html')
PORT = 8766
FAILS = []


def ok(cond, msg, extra=None):
    print(('  ok  ' if cond else '  FAIL') + ' ' + msg + ('' if extra is None else ' · ' + json.dumps(extra, ensure_ascii=False)))
    if not cond:
        FAILS.append(msg)


async def new_page(b, w, h, **kw):
    from playwright.async_api import async_playwright  # noqa: F401 (형태만)
    init = kw.pop('init', None)
    c = await b.new_context(viewport={'width': w, 'height': h}, locale='ko-KR', **kw)
    await c.route(re.compile(r'^https?://(?!127\.0\.0\.1)'), lambda r: r.abort())
    if init:
        await c.add_init_script(init)
    pg = await c.new_page()
    errs = []
    pg.on('pageerror', lambda e: errs.append('pageerror: ' + str(e)[:200]))
    pg.on('console', lambda m: errs.append('console: ' + m.text[:200]) if m.type == 'error' and 'Failed to load resource' not in m.text else None)
    return c, pg, errs


async def game_frame(pg, timeout=60):
    """틀 안 게임(주소에 hsf=)이 다 떴을 때의 frame — 없으면 None"""
    t0 = time.time()
    while time.time() - t0 < timeout:
        for f in pg.frames:
            if 'hsf=' in f.url:
                try:
                    if await f.evaluate("() => typeof S !== 'undefined' && S && Array.isArray(S.students) && S.students.length > 0 && !document.getElementById('bootLoader')"):
                        await f.evaluate("() => { try { audOver(null); } catch (e) {} closeModal(); UI.ceremonies = []; UI.view = 'home'; render(); }")
                        await pg.wait_for_timeout(300)
                        return f
                except Exception:
                    pass
        await pg.wait_for_timeout(300)
    return None


async def main_game(pg, timeout=60):
    """틀 없이 맨 위 창에서 게임이 떴는지"""
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            if await pg.evaluate("() => typeof S !== 'undefined' && S && Array.isArray(S.students) && S.students.length > 0 && !document.getElementById('bootLoader')"):
                return True
        except Exception:
            pass
        await pg.wait_for_timeout(300)
    return False


async def host_k(pg):
    return await pg.evaluate("() => window.HS_SCALE ? HS_SCALE.k : null")


async def click(pg, fr, sel, dx=0.5, dy=0.5):
    """게임 안 요소를 진짜 마우스로 — 틀 좌표 = 게임 좌표 × k (iframe 은 왼쪽 위 0,0 · transform-origin 0 0)"""
    k = await host_k(pg)
    r = await fr.evaluate("(s) => { const e = document.querySelector(s); if (!e) return null; const r = e.getBoundingClientRect(); return [r.left, r.top, r.width, r.height]; }", sel)
    if not r:
        return False
    await pg.mouse.click((r[0] + r[2] * dx) * k, (r[1] + r[3] * dy) * k)
    return True


async def test_host(b, base_url, label):
    print(f'[{label}] 2560×1300 ?scale=auto')
    c, pg, errs = await new_page(b, 2560, 1300)
    await pg.goto(base_url + '?scale=auto', wait_until='commit')
    fr = await game_frame(pg)
    ok(fr is not None, '틀 안 게임이 뜬다')
    if not fr:
        await c.close(); return
    H = await pg.evaluate("() => ({iframes: document.querySelectorAll('iframe').length, app: !!document.getElementById('app'), S: typeof S, host: !!(window.HS_SCALE && HS_SCALE.host), k: HS_SCALE.k, title: document.title, tf: document.getElementById('hsFrame').style.transform, w: document.getElementById('hsFrame').style.width})")
    ok(H['iframes'] == 1 and not H['app'] and H['S'] == 'undefined' and H['host'], '틀 쪽은 iframe 하나뿐 · 게임은 돌지 않는다', H)
    ok(abs(H['k'] - 1.494) < 1e-6, '자동 배율 ×1.494 (min(2560/1280, 1300/870))', H['k'])
    F = await fr.evaluate("() => ({w: innerWidth, h: innerHeight, dpr: devicePixelRatio, dpr0: HS_SCALE.dpr0(), framed: HS_SCALE.framed, host: HS_SCALE.host, cls: document.documentElement.classList.contains('hs-framed'), title: document.title, url: location.search})")
    ok(abs(F['w'] - 2560 / 1.494) <= 1.5 and abs(F['h'] - 1300 / 1.494) <= 1.5, '게임 창 1714×870', [F['w'], F['h']])
    ok(abs(F['dpr'] - 1.494) < 1e-6 and F['dpr0'] == 1 and F['framed'] and F['host'] and F['cls'], 'devicePixelRatio ×k · 틀과 인사', F)
    await pg.wait_for_timeout(300)
    ok(H['title'] == F['title'] or (await pg.evaluate('() => document.title')) == F['title'], '탭 제목 = 게임 제목', [await pg.evaluate('() => document.title'), F['title']])
    if label == 'http':
        same = await pg.evaluate("() => { try { return document.getElementById('hsFrame').contentDocument.title; } catch (e) { return 'X'; } }")
        ok(same == F['title'], '같은 출처 — 틀이 게임 문서를 읽을 수 있다', same)
    # 2. 진짜 마우스
    await fr.evaluate("() => { PREF.schedScroll = true; S.actUnlock = true; S.jobUnlock = true; UI.view = 'home'; render(); }")
    await pg.wait_for_timeout(500)
    await click(pg, fr, '#app>.topbar .side-sched')
    for _ in range(30):
        await pg.wait_for_timeout(200)
        if await fr.evaluate("() => UI.view === 'plan' && !!document.querySelector('#view .skstage')"):
            break
    ok(await fr.evaluate("() => UI.view") == 'plan', '사이드 스케줄 단추(진짜 마우스) → 스케줄')
    await pg.wait_for_timeout(1200)
    await fr.evaluate("() => { delete PREF.sign; autoFillSlots(); render(); window.__went = false; window.__go0 = SK.go; SK.go = () => { window.__went = true; }; }")
    await pg.wait_for_timeout(400)
    k = await host_k(pg)
    G = await fr.evaluate("""() => { const q = document.querySelector('#view .sk-quill').getBoundingClientRect(), st = document.querySelector('#view .skstage').getBoundingClientRect(),
        c = document.querySelector('#view .sk-sig').getBoundingClientRect(), ink = SCHED_GEO.ink, s = SK.s;
        return {q: [q.left + 10, q.bottom - 10], ink: [st.left + (ink.x * 2 + ink.w) * s, st.top + (ink.y * 2 + ink.h) * s], c: [c.left, c.top, c.width, c.height]}; }""")
    m = pg.mouse
    await m.move(G['q'][0] * k, G['q'][1] * k); await m.down(); await pg.wait_for_timeout(80)
    await m.move(G['ink'][0] * k, G['ink'][1] * k, steps=8); await pg.wait_for_timeout(80); await m.up()
    held = await fr.evaluate("() => [!!SK.held, SK.ink]")
    cx, cy = G['c'][0] + 10, G['c'][1] + 8
    await m.move(cx * k, cy * k, steps=6); await m.down()
    for i in range(1, 31):
        await m.move((cx + i * 5) * k, (cy + (i % 6) * 6) * k)
    await m.up()
    for _ in range(40):
        await pg.wait_for_timeout(100)
        if await fr.evaluate("() => window.__went"):
            break
    S2 = await fr.evaluate("() => { SK.go = window.__go0; return {went: window.__went, sign: PREF.sign ? [PREF.sign.w, PREF.sign.h] : null}; }")
    ok(held[0] and held[1] > 0 and S2['went'] and S2['sign'] == [107, 33], '깃펜 집기 → 잉크 → 서명 긋기 → 진행 (진짜 마우스)', {'held': held, **S2})
    await fr.evaluate("() => { UI.view = 'facil'; UI.facTab = null; S.shopUnlock = true; render(); }")
    await pg.wait_for_timeout(600)
    await click(pg, fr, '#view .townnpc[data-factab]')
    await pg.wait_for_timeout(500)
    ok(await fr.evaluate("() => !!document.querySelector('#view .townpop')"), '마을 사람(진짜 마우스) → 팝업')
    await fr.evaluate("() => { UI.facTab = null; UI.view = 'opt'; render(); window.scrollTo(0, 0); }")
    await pg.wait_for_timeout(500)
    tall = await fr.evaluate("() => document.documentElement.scrollHeight > innerHeight + 50")
    await m.move(1000, 700); await m.wheel(0, 600); await pg.wait_for_timeout(500)
    sy = await fr.evaluate("() => scrollY")
    ok((not tall) or sy > 0, '휠 스크롤이 게임 안으로', {'tall': tall, 'scrollY': sy})
    # 3. 설정 '화면 크기'
    await fr.evaluate("() => { UI.view = 'opt'; render(); window.scrollTo(0, 0); }")
    await pg.wait_for_timeout(500)
    ok(await fr.evaluate("() => document.querySelectorAll('[data-uiscale]').length") == 6, "설정에 '화면 크기' 칸 (단추 6)")
    for v, kk in [('150', 1.5), ('100', 1.0), ('auto', 1.494)]:
        await fr.evaluate("(v) => document.querySelector(`[data-uiscale=\"${v}\"]`).scrollIntoView({block: 'center'})", v)
        await pg.wait_for_timeout(200)
        await click(pg, fr, f'[data-uiscale="{v}"]')
        await pg.wait_for_timeout(700)
        R = await pg.evaluate("() => ({k: HS_SCALE.k, tf: document.getElementById('hsFrame').style.transform, pref: localStorage.getItem('hs_scale')})")
        Fk = await fr.evaluate("() => ({k: HS_SCALE.k, w: innerWidth, pressed: (document.querySelector('[data-uiscale][aria-pressed=\"true\"]') || {}).dataset.uiscale, now: (document.querySelector('[data-uiscale]').closest('.optrow').querySelector('.optlab b.num') || {}).textContent})")
        ok(abs(R['k'] - kk) < 1e-6 and abs(Fk['k'] - kk) < 1e-6 and R['pref'] == v and Fk['pressed'] == v and abs(Fk['w'] - 2560 / kk) <= 1.5,
           f"화면 크기 {v} → 틀 ×{kk}", {**R, **Fk})
    # 키보드 — 틀이 게임에 초점을 넘긴다 (학생 명부 책을 Esc 로 닫기)
    await fr.evaluate("() => { UI.view = 'roster'; render(); }"); await pg.wait_for_timeout(900)
    BOOK = "() => { const h = document.getElementById('rbHost'); return !!h && h.style.display !== 'none'; }"   # RB 는 블록 안 const — 화면으로 본다
    opened = await fr.evaluate(BOOK)
    await pg.keyboard.press('Escape'); await pg.wait_for_timeout(500)
    closed = not await fr.evaluate(BOOK)
    ok(opened and closed, '키보드가 게임으로 (명부 책 Esc)', {'opened': opened, 'closed': closed})
    # 창 크기를 바꾸면 틀이 다시 맞춘다
    await pg.set_viewport_size({'width': 1920, 'height': 1070}); await pg.wait_for_timeout(600)
    R = await pg.evaluate("() => HS_SCALE.k"); Fw = await fr.evaluate("() => [innerWidth, innerHeight, HS_SCALE.k]")
    ok(abs(R - 1.229) < 1e-6 and abs(Fw[0] - 1920 / 1.229) <= 1.5 and abs(Fw[2] - 1.229) < 1e-6, '창 1920×1070 으로 줄이면 ×1.229', {'host': R, 'frame': Fw})
    await pg.set_viewport_size({'width': 2560, 'height': 1300}); await pg.wait_for_timeout(600)
    # 4. 언어 바꾸기 · 새 버전 → 틀째로
    await fr.evaluate("() => langSwitch('en')")
    await pg.wait_for_timeout(800)
    fr = await game_frame(pg)
    L = await pg.evaluate("() => ({url: location.search, host: !!(window.HS_SCALE && HS_SCALE.host), title: document.title})") if fr else {}
    lang = await fr.evaluate("() => (typeof I18N !== 'undefined' && I18N.lang) || 'ko'") if fr else None
    ok(fr is not None and L.get('host') and 'scale=auto' in L.get('url', '') and lang == 'en', '언어 바꾸기(영어) → 틀째로 다시 · 영어', {**L, 'lang': lang})
    if fr:
        await pg.wait_for_timeout(500)
        t_en = await pg.evaluate('() => document.title')
        ok(not re.search('[가-힣]', t_en), '영어판 탭 제목', t_en)
        await fr.evaluate("() => { localStorage.removeItem('hs_lang'); VER.srv = {build: 'TESTV', ts: 0, rules: 0}; verReload(); }")
        await pg.wait_for_timeout(800)
        fr = await game_frame(pg)
        V = await pg.evaluate("() => ({url: location.search, host: !!(window.HS_SCALE && HS_SCALE.host)})") if fr else {}
        furl = fr.url if fr else ''
        ok(fr is not None and V.get('host') and 'v=TESTV' in V.get('url', '') and 'scale=auto' in V.get('url', '') and 'v=TESTV' in furl and 'hsf=' in furl,
           '새 버전 불러오기 → 틀째로 (?v=)', {**V, 'frame': furl[-60:]})
    real = [e for e in errs if 'favicon' not in e]
    ok(not real, '오류 없음', real[:5])
    await c.close()


async def test_user(b):
    print('[사람처럼 판단 · ?scale=user]')
    cases = [
        ('2560×1300 → 틀', dict(w=2560, h=1300), '?scale=user', True),
        ('1440×900 → 틀 없이 (×1.03)', dict(w=1440, h=900), '?scale=user', False),
        ('hs_scale=100 → 틀 없이', dict(w=2560, h=1300, init="try { localStorage.setItem('hs_scale', '100'); } catch (e) {}"), '?scale=user', False),
        ('hs_scale=150 → 1440×900 도 틀 ×1.5', dict(w=1440, h=900, init="try { localStorage.setItem('hs_scale', '150'); } catch (e) {}"), '?scale=user', True),
        ('폰(터치) → 틀 없이', dict(w=390, h=844, is_mobile=True, has_touch=True, device_scale_factor=2), '?scale=user', False),
        ('iPad → 틀 없이', dict(w=1366, h=1024, user_agent='Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'), '?scale=user', False),
        ('자동화 · 주소에 scale 없음 → 틀 없이', dict(w=2560, h=1300), '', False),
    ]
    for name, kw, q, want in cases:
        w, h = kw.pop('w'), kw.pop('h')
        c, pg, errs = await new_page(b, w, h, **kw)
        await pg.goto('file://' + PAGE + q, wait_until='commit')
        if want:
            fr = await game_frame(pg)
            k = await host_k(pg) if fr else None
            ok(fr is not None, name, {'k': k})
        else:
            up = await main_game(pg)
            st = await pg.evaluate("() => ({iframes: document.querySelectorAll('iframe#hsFrame').length, host: !!(window.HS_SCALE && HS_SCALE.host)})")
            ok(up and st['iframes'] == 0 and not st['host'], name, st)
        await c.close()


async def main():
    from playwright.async_api import async_playwright
    if not os.path.exists(PAGE):
        print('heroschool.html 이 없다 — 빌드 먼저'); sys.exit(2)
    srv = subprocess.Popen([sys.executable, '-m', 'http.server', str(PORT), '--bind', '127.0.0.1'], cwd=ROOT,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    t0 = time.time()
    try:
        time.sleep(0.8)
        async with async_playwright() as p:
            b = await p.chromium.launch()
            await test_host(b, 'file://' + PAGE, 'file')
            await test_user(b)
            await test_host(b, f'http://127.0.0.1:{PORT}/heroschool.html', 'http')
            await b.close()
    finally:
        srv.terminate()
    print()
    if FAILS:
        print('실패 %d — %s' % (len(FAILS), ' / '.join(FAILS))); sys.exit(1)
    print('통과 — 화면 크기 틀 (%d초)' % (time.time() - t0))


if __name__ == '__main__':
    asyncio.run(main())
