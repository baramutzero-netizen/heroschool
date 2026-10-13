"""화면 모드 시험 (1013) — 기기마다 넓은 화면 · 좁은 화면이 맞게 갈리는지 (맨 앞 스크립트 UISCALE · 안내 ROTATE).

    python3 tools/check_modes.py [--shots 폴더]      (저장소 맨 위 · 빌드 뒤에 · Playwright + 크로미움 · 4분쯤)

규칙 (game.html 의 scalePanel 위 주석): 배치는 게임이 보는 폭만 본다 — 1100 이상이면 넓은 화면(오른쪽 사이드 · 책상 · 마을 지도 · 두루마리 ·
명부 책 · 가로 전투), 그보다 좁으면 좁은 화면(위쪽 탭 · 640 이하는 폰 메뉴 · 세로 전투). 그 폭을 기기마다 맞춘다.
1. PC (?scale=user — 자동화여도 사람처럼 틀이 된다)
   · 1440×900 → 틀 ×1 · 넓은 화면 / 900×600 → ×0.818 · 틀 안 1100×733 · 넓은 화면 / 600×800 → ×1 · 좁은 화면 · 세로 전투
   · 한 창을 1440 → 900 → 600 → 1280 으로 바꾸면 다시 불러오지 않고 배율 · 모드가 바뀐다
   · 1280×800 에서 설정 '화면 크기' 150% → 틀 안 853 → 좁은 화면 · 자동 → 다시 넓은 화면 (진짜 마우스)
   · 900×600: 진짜 마우스로 스케줄 카드를 끌어 칸에 넣는다 (끌리는 카드가 포인터에 붙는다) · 봄 신인전 출전 → 락커룸 창 → 쿼터뷰 전투
   · ?scale=off · 자동화(주소에 scale 없음) → 틀 없이 (다른 시험은 예전처럼 창 크기 그대로)
2. 태블릿 흉내 (iPad 810×1080 · 터치): 세로 → viewport width=1100 · 넓은 화면 · '가로로 돌리면' 알림 · 사이드 스케줄 단추 탭 · 쿼터뷰 전투 /
   1080×810 으로 돌리면 그대로 1100 / iPad Air 가로 1180×820 → device-width / 화면 나누기(창 500) → device-width · 좁은 화면
3. 폰 흉내 (iPhone 13 · 터치): 세로 → 좁은 화면 · 덮개 없음 / 가로 844×390 → '세로로 돌려 주세요' 덮개 / 가로에서 전투 창 → 덮개 숨김 · 세로 전투 /
   전투가 끝나 창이 닫히면 다시 덮개 / 세로로 → 덮개 없음 / 영어(?lang=en) 덮개 글에 한글 없음
바깥 주소는 전부 막는다 — 서버에는 아무것도 쓰지 않는다.
"""
import argparse, asyncio, json, os, re, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(ROOT, 'heroschool.html')
URL = 'file://' + PAGE
FAILS = []
SHOTS = None
READY = "() => typeof S !== 'undefined' && S && Array.isArray(S.students) && S.students.length > 0 && !document.getElementById('bootLoader')"
HOME = "() => { try { audOver(null); } catch (e) {} closeModal(); UI.ceremonies = []; S.tutSeen = S.tutSeen || {}; S.tutSeen['8'] = true; UI.view = 'home'; render(); }"
INFO = """() => { const ra = document.getElementById('rotateAsk');
  return {iw: innerWidth, ih: innerHeight, town: townMode(), orient: bfOrient(), kind: HS_SCALE.kind, framed: !!HS_SCALE.framed, k: HS_SCALE.k,
    vp: (document.querySelector('meta[name=viewport]') || {}).content || '', rot: !!(ra && !ra.hidden),
    side: getComputedStyle(document.getElementById('app')).display === 'grid'}; }"""
# 봄 신인전 — 팀을 채우고 출전 화면까지 (락커룸 시험과 같은 준비)
TOUR = r"""() => {
  function fillTeams(){
    teamsOf().forEach(t=>{
      const taken = new Set();
      teamsOf().forEach(x=>{ if(x!==t) formSlots(x.form).forEach(k=>{ if(x.slots[k]) taken.add(x.slots[k]); }); });
      const pool = S.students.filter(x=> !taken.has(x.id)).sort((a,b)=> power(b)-power(a));
      t.slots = {}; formSlots(t.form).forEach((k,i)=>{ if(pool[i]) t.slots[k] = pool[i].id; });
    });
  }
  while(S.students.length < 9) S.students.push(newStudent(1, "B"));
  fillTeams();
  closeModal(); UI.ceremonies = []; UI.tour = null; UI.pendingTour = null; LKW.auto = null;
  startSpringTour();
  const t = UI.tour; t._prepOpen = true; t.stage = "entry";
  t.entryTeams = ['A','B','C'].filter(n=> teamFull(teamByName(n))).slice(0, tourNeedTeams(t));
  UI.pendingTour = true;
  renderTournament();
  return !!document.querySelector('#tEntry');
}"""
BATTLE = "() => ({stage: !!document.querySelector('#modalRoot .bf-stage'), quarter: !!document.querySelector('.tournament-quarter'), orient: bfOrient()})"
DRAG_INFO = r"""() => {
  const c = document.querySelector('.sk-paper .sk-card[data-card]'), s = document.querySelector('.sk-paper [data-slot]');
  if(!c || !s) return null;
  const a = c.getBoundingClientRect(), b = s.getBoundingClientRect();
  return {card: [a.x + a.width/2, a.y + a.height/2], slot: [b.x + b.width/2, b.y + b.height/2], filled: (S.slots||[]).filter(Boolean).length};
}"""
GHOST = "() => { const g = document.querySelector('.sk-ghost'); if(!g) return null; const r = g.getBoundingClientRect(); return [r.x + r.width/2, r.y + r.height/2]; }"


def ok(cond, msg, extra=None):
    print(('  ok  ' if cond else '  FAIL') + ' ' + msg + ('' if extra is None else ' · ' + json.dumps(extra, ensure_ascii=False)))
    if not cond:
        FAILS.append(msg)


async def shot(pg, name):
    if SHOTS:
        await pg.screenshot(path=os.path.join(SHOTS, name + '.png'))


async def new_page(b, **kw):
    c = await b.new_context(locale='ko-KR', **kw)
    await c.route(re.compile(r'^https?://'), lambda r: r.abort())
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
                    if await f.evaluate(READY):
                        await f.evaluate(HOME)
                        await pg.wait_for_timeout(300)
                        return f
                except Exception:
                    pass
        await pg.wait_for_timeout(300)
    return None


async def main_game(pg, timeout=60):
    """틀 없이 맨 위 창에서 게임이 떴는지 (뜨면 홈으로)"""
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            if await pg.evaluate(READY):
                await pg.evaluate(HOME)
                await pg.wait_for_timeout(300)
                return True
        except Exception:
            pass
        await pg.wait_for_timeout(300)
    return False


async def until(ev, js, timeout=15):
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            if await ev(js):
                return True
        except Exception:
            pass
        await asyncio.sleep(0.2)
    return False


async def host_k(pg):
    return await pg.evaluate("() => window.HS_SCALE ? HS_SCALE.k : null")


async def click_in(pg, fr, sel):
    """틀 안 요소를 진짜 마우스로 — 틀 좌표 = 게임 좌표 × k (iframe 은 왼쪽 위 0,0 · transform-origin 0 0)"""
    k = await host_k(pg)
    r = await fr.evaluate("(s) => { const e = document.querySelector(s); if (!e) return null; e.scrollIntoView({block: 'center'}); const r = e.getBoundingClientRect(); return [r.left, r.top, r.width, r.height]; }", sel)
    if not r:
        return False
    await pg.mouse.click((r[0] + r[2] / 2) * k, (r[1] + r[3] / 2) * k)
    return True


async def tour_battle(ev, pg, tag):
    """봄 신인전 출전 → 락커룸 창(같이 뜬다) → 말없이 시작 → 전투. 반환: 락커룸이 떴나 · 전투 정보"""
    await ev(TOUR)
    await pg.wait_for_timeout(300)
    await ev("() => document.querySelector('#tEntry').click()")
    lk = await until(ev, "() => typeof LKW !== 'undefined' && LKW.phase === 'choose' && !LKW.typing")
    await pg.wait_for_timeout(400)
    await shot(pg, tag + '_locker')
    await ev("() => lkwClose('start')")
    st = await until(ev, "() => !!document.querySelector('#modalRoot .bf-stage')")
    await pg.wait_for_timeout(3500)
    await shot(pg, tag + '_battle')
    info = await ev(BATTLE)
    info['opened'] = st
    return lk, info


async def end_battle(ev, pg):
    """결과로 건너뛰기 → 결과 확정 (전투 창이 닫힌다)"""
    for _ in range(2):
        await until(ev, "() => !!document.querySelector('#bDone')", 10)
        await pg.wait_for_timeout(400)
        await ev("() => { const b = document.querySelector('#bDone'); if (b) b.click(); }")
        await pg.wait_for_timeout(900)
    return await until(ev, "() => !document.querySelector('#modalRoot .bf-stage')", 10)


async def test_pc(b):
    print('[PC — 화면 크기 틀 · ?scale=user]')
    for w, h, k, inner, wide in [(1440, 900, 1.0, 1440, True), (900, 600, 0.818, 1100, True), (600, 800, 1.0, 600, False)]:
        c, pg, errs = await new_page(b, viewport={'width': w, 'height': h})
        await pg.goto(URL + '?scale=user', wait_until='commit')
        fr = await game_frame(pg)
        ok(fr is not None, f'{w}×{h} 틀 안 게임이 뜬다')
        if not fr:
            await c.close(); continue
        I = await fr.evaluate(INFO)
        ok(abs(I['k'] - k) < 1e-6 and abs(I['iw'] - inner) <= 1 and I['town'] == wide and I['side'] == wide and I['kind'] == 'pc' and I['framed']
           and I['orient'] == ('landscape' if wide else 'portrait'),
           f'{w}×{h} → 틀 ×{k} · 틀 안 폭 {inner} · {"넓은" if wide else "좁은"} 화면 · {"가로" if wide else "세로"} 전투', I)
        await shot(pg, f'pc{w}_home')
        if w == 900:
            # 진짜 마우스로 스케줄 카드 끌기 — 끌리는 카드(유령)가 포인터에 붙고, 칸에 들어간다
            await fr.evaluate("() => { PREF.schedScroll = true; S.actUnlock = true; S.jobUnlock = true; closeModal(); UI.tour = null; UI.pendingTour = null; UI.view = 'plan'; render(); window.scrollTo(0, 0); }")
            await pg.wait_for_timeout(1500)
            d = await fr.evaluate(DRAG_INFO)
            if not d:
                ok(False, '900×600 스케줄 카드 · 칸이 보인다')
            else:
                to = lambda x, y: (x * k, y * k)
                cx, cy = to(*d['card']); sx, sy = to(*d['slot'])
                await pg.mouse.move(cx, cy); await pg.mouse.down()
                for i in range(1, 13):
                    await pg.mouse.move(cx + (sx - cx) * i / 12, cy + (sy - cy) * i / 12)
                    await pg.wait_for_timeout(30)
                g = await fr.evaluate(GHOST)
                await pg.mouse.up(); await pg.wait_for_timeout(500)
                await fr.evaluate("() => { try { DRAG.block = false; } catch (e) {} }")    # 끌고 난 뒤 첫 click 을 막는 표시 — 다음 단추가 막히지 않게
                after = await fr.evaluate("() => (S.slots||[]).filter(Boolean).length")
                off = None
                if g:
                    gx, gy = to(*g); off = round(((gx - sx) ** 2 + (gy - sy) ** 2) ** .5, 1)
                ok(off is not None and off <= 2 and after > d['filled'], '900×600 진짜 마우스로 스케줄 카드 끌기 — 유령이 포인터에 붙고 칸에 들어간다',
                   {'ghost_off_px': off, 'filled': [d['filled'], after]})
            await shot(pg, 'pc900_plan')
            lk, B = await tour_battle(fr.evaluate, pg, 'pc900')
            ok(lk and B['opened'] and B['quarter'] and B['orient'] == 'landscape', '900×600 봄 신인전 출전 → 락커룸 창 → 쿼터뷰 전투', {'locker': lk, **B})
        if w == 600:
            lk, B = await tour_battle(fr.evaluate, pg, 'pc600')
            ok(lk and B['opened'] and not B['quarter'] and B['orient'] == 'portrait', '600×800 봄 신인전 → 락커룸 창 → 세로 전투', {'locker': lk, **B})
        real = [e for e in errs if 'favicon' not in e]
        ok(not real, f'{w}×{h} 오류 없음', real[:4])
        await c.close()

    print('[PC — 한 창에서 크기 바꾸기 · 설정 화면 크기]')
    c, pg, errs = await new_page(b, viewport={'width': 1440, 'height': 900})
    await pg.goto(URL + '?scale=user', wait_until='commit')
    fr = await game_frame(pg)
    if fr:
        await fr.evaluate("() => { window.__mark = 7; }")
        for (w, h, k, inner, wide) in [(900, 600, 0.818, 1100, True), (600, 800, 1.0, 600, False), (1280, 800, 1.0, 1280, True)]:
            await pg.set_viewport_size({'width': w, 'height': h}); await pg.wait_for_timeout(900)
            I = await fr.evaluate("() => ({k: HS_SCALE.k, iw: innerWidth, town: townMode(), side: getComputedStyle(document.getElementById('app')).display === 'grid', orient: bfOrient(), mark: window.__mark})")
            hk = await host_k(pg)
            ok(abs(I['k'] - k) < 1e-6 and abs(hk - k) < 1e-6 and abs(I['iw'] - inner) <= 1 and I['town'] == wide and I['side'] == wide and I['mark'] == 7,
               f'창 {w}×{h} 로 바꾸면 ×{k} · {"넓은" if wide else "좁은"} 화면 (다시 불러오지 않음)', I)
            await shot(pg, f'pc_resize_{w}')
        # 설정 '화면 크기' — 150% 면 틀 안 853 → 좁은 화면, 자동이면 다시 넓은 화면
        await fr.evaluate("() => { closeModal(); UI.view = 'opt'; render(); window.scrollTo(0, 0); }"); await pg.wait_for_timeout(600)
        for v, k, wide in [('150', 1.5, False), ('auto', 1.0, True)]:
            await click_in(pg, fr, f'[data-uiscale="{v}"]'); await pg.wait_for_timeout(900)
            I = await fr.evaluate("() => ({k: HS_SCALE.k, iw: innerWidth, town: townMode(), side: getComputedStyle(document.getElementById('app')).display === 'grid', pref: localStorage.getItem('hs_scale')})")
            ok(abs(I['k'] - k) < 1e-6 and I['town'] == wide and I['side'] == wide and I['pref'] == v, f'1280×800 화면 크기 {v} → ×{k} · {"넓은" if wide else "좁은"} 화면', I)
            await shot(pg, f'pc_scale_{v}')
        real = [e for e in errs if 'favicon' not in e]
        ok(not real, '크기 바꾸기 · 설정 오류 없음', real[:4])
    else:
        ok(False, '1440×900 틀 안 게임이 뜬다')
    await c.close()

    print('[PC — 틀 없이]')
    for q, name in [('?scale=off', '?scale=off'), ('', '자동화 · 주소에 scale 없음')]:
        c, pg, errs = await new_page(b, viewport={'width': 900, 'height': 600})
        await pg.goto(URL + q, wait_until='commit')
        up = await main_game(pg)
        I = await pg.evaluate("() => ({frames: document.querySelectorAll('iframe#hsFrame').length, host: !!HS_SCALE.host, iw: innerWidth, town: townMode()})") if up else {}
        ok(up and I['frames'] == 0 and not I['host'] and I['iw'] == 900 and not I['town'], f'900×600 {name} → 틀 없이 창 그대로 (좁은 화면)', I)
        await c.close()


async def test_tablet(b, p):
    print('[태블릿 흉내 — iPad 810×1080 · 터치]')
    ipad = dict(p.devices['iPad (gen 7)'])
    c, pg, errs = await new_page(b, **ipad)
    await pg.goto(URL, wait_until='commit')
    up = await main_game(pg)
    ok(up, '태블릿 게임이 뜬다')
    if up:
        I = await pg.evaluate(INFO)
        ok(I['kind'] == 'tablet' and I['vp'] == 'width=1100' and I['iw'] == 1100 and I['town'] and I['side'] and I['orient'] == 'landscape' and not I['rot'],
           '세로 810×1080 → viewport width=1100 · 넓은 화면 · 가로 전투', I)
        seen = []
        for _ in range(40):
            tx = await pg.evaluate("() => (document.querySelector('#toastRoot .toast') || {}).textContent || ''")
            if tx and tx not in seen:
                seen.append(tx)
            if any('가로로 돌리면' in t for t in seen):
                break
            await pg.wait_for_timeout(250)
        ok(any('가로로 돌리면' in t for t in seen), "세로로 들면 '가로로 돌리면 더 크게 보인다' 알림", seen)
        await shot(pg, 'ipad_portrait')
        await pg.tap('#sideSched'); await pg.wait_for_timeout(1200)
        ok(await pg.evaluate("() => UI.view") == 'plan', '사이드 스케줄 단추를 탭 → 스케줄 (줄인 화면에서 터치 자리)')
        await pg.evaluate(HOME)
        lk, B = await tour_battle(pg.evaluate, pg, 'ipad_portrait')
        ok(lk and B['opened'] and B['quarter'] and B['orient'] == 'landscape', '세로 태블릿 봄 신인전 → 락커룸 창 → 쿼터뷰 전투', {'locker': lk, **B})
        await end_battle(pg.evaluate, pg)
        await pg.set_viewport_size({'width': 1080, 'height': 810}); await pg.wait_for_timeout(900)
        I = await pg.evaluate(INFO)
        ok(I['vp'] == 'width=1100' and I['iw'] == 1100 and I['town'] and I['side'], '가로 1080×810 으로 돌리면 그대로 1100 · 넓은 화면', I)
        await shot(pg, 'ipad_landscape')
        real = [e for e in errs if 'favicon' not in e]
        ok(not real, 'iPad 오류 없음', real[:4])
    await c.close()
    for name, vw, vh, sw, sh, want_vp, want_iw, wide in [('iPad Air 가로 1180×820', 1180, 820, 1180, 820, 'width=device-width,initial-scale=1', 1180, True),
                                                         ('화면 나누기 — 창 500 (화면 810×1080)', 500, 1080, 810, 1080, 'width=device-width,initial-scale=1', 500, False)]:
        kw = dict(p.devices['iPad (gen 7)']); kw['viewport'] = {'width': vw, 'height': vh}; kw['screen'] = {'width': sw, 'height': sh}
        c, pg, errs = await new_page(b, **kw)
        await pg.goto(URL, wait_until='commit')
        up = await main_game(pg)
        I = await pg.evaluate(INFO) if up else {}
        ok(up and I['kind'] == 'tablet' and I['vp'] == want_vp and I['iw'] == want_iw and I['town'] == wide and I['side'] == wide,
           f'{name} → {want_vp.split(",")[0]} · {"넓은" if wide else "좁은"} 화면', I)
        await c.close()


async def test_phone(b, p):
    print('[폰 흉내 — iPhone 13 · 터치]')
    c, pg, errs = await new_page(b, **dict(p.devices['iPhone 13']))
    await pg.goto(URL, wait_until='commit')
    up = await main_game(pg)
    ok(up, '폰 게임이 뜬다')
    if up:
        I = await pg.evaluate(INFO)
        ok(I['kind'] == 'phone' and not I['town'] and not I['side'] and not I['rot'] and I['vp'].startswith('width=device-width') and I['orient'] == 'portrait',
           '세로 390 → 좁은 화면 · 덮개 없음 · viewport 그대로', I)
        await pg.set_viewport_size({'width': 844, 'height': 390}); await pg.wait_for_timeout(900)
        I = await pg.evaluate(INFO)
        txt = await pg.evaluate("() => (document.getElementById('rotateAsk') || {}).innerText || ''")
        ok(I['rot'] and not I['town'] and '세로로 돌려' in txt, "가로 844×390 → '세로로 돌려 주세요' 덮개", {**I, 'text': txt[:40]})
        await shot(pg, 'phone_landscape')
        lk, B = await tour_battle(pg.evaluate, pg, 'phone_landscape')
        I = await pg.evaluate(INFO)
        ok(lk and B['opened'] and not B['quarter'] and B['orient'] == 'portrait' and not I['rot'], '가로에서 전투 창 → 덮개 숨김 · 세로 전투', {'locker': lk, **B, 'rot': I['rot']})
        closed = await end_battle(pg.evaluate, pg)
        await pg.wait_for_timeout(500)
        I = await pg.evaluate(INFO)
        ok(closed and I['rot'], '전투가 끝나 창이 닫히면 다시 덮개', {'closed': closed, 'rot': I['rot']})
        await pg.set_viewport_size({'width': 390, 'height': 844}); await pg.wait_for_timeout(900)
        I = await pg.evaluate(INFO)
        ok(not I['rot'], '세로로 돌리면 덮개 없음', I)
        real = [e for e in errs if 'favicon' not in e]
        ok(not real, '폰 오류 없음', real[:4])
    await c.close()
    # 영어 덮개
    c, pg, errs = await new_page(b, **dict(p.devices['iPhone 13']))
    await pg.goto(URL + '?lang=en', wait_until='commit')
    up = await main_game(pg)
    await pg.set_viewport_size({'width': 844, 'height': 390}); await pg.wait_for_timeout(900)   # 흉내에서는 창 크기를 바꿔야 기기 방향(screen.orientation)도 돈다
    txt = await pg.evaluate("() => (document.getElementById('rotateAsk') || {}).innerText || ''") if up else ''
    ok(up and txt.strip() and not re.search('[가-힣]', txt), '영어판 덮개 — 한글 없음', txt.strip()[:80])
    await shot(pg, 'phone_landscape_en')
    await c.close()


async def main():
    global SHOTS
    ap = argparse.ArgumentParser()
    ap.add_argument('--shots', help='화면을 찍어 둘 폴더')
    o = ap.parse_args()
    if o.shots:
        SHOTS = o.shots; os.makedirs(SHOTS, exist_ok=True)
    from playwright.async_api import async_playwright
    if not os.path.exists(PAGE):
        print('heroschool.html 이 없다 — 빌드 먼저'); sys.exit(2)
    t0 = time.time()
    async with async_playwright() as p:
        b = await p.chromium.launch()
        await test_pc(b)
        await test_tablet(b, p)
        await test_phone(b, p)
        await b.close()
    print()
    if FAILS:
        print('실패 %d — %s' % (len(FAILS), ' / '.join(FAILS))); sys.exit(1)
    print('통과 — 화면 모드 (%d초)' % (time.time() - t0))


if __name__ == '__main__':
    asyncio.run(main())
