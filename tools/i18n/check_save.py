"""영어판 3단계 시험 (1010) — 세이브 · 서버의 데이터 글(학생 이름 · 이명 · 유물 · 학원 · 진로 · 스킬 이름)이 언어를 따라가는지.

    python3 tools/i18n/check_save.py [--years 3]      (저장소 맨 위 · 빌드 뒤에 · Playwright + 크로미움)

1. 한국어판으로 몇 해 쌓은 세이브를 영어판(?lang=en)에서 연다 → 이름 · 이명 · 유물 · 스킬 · 진로 · 친선전 학원에 한글이 없어야 한다
2. 그걸 영어판에서 저장해 한국어판에서 연다 → 그 칸들이 처음 한국어 세이브와 같아야 한다 (왕복)
3. 영어판으로 쌓은 학원 — 서버로 보낼 묶음(leaguePackUnit · leagueMyPack)은 한국어 원문, 받은 묶음(leagueSane · chatSane)은 영어,
   5인 리그 NPC 학원 문서(l5NpcDoc)는 두 언어에서 똑같아야 한다 (누가 만들어도 같은 한국어 문서)
바깥 주소(firebase · 글꼴 등)는 전부 막는다 — 서버에는 아무것도 쓰지 않는다.
"""
import argparse, asyncio, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, 'tools', 'i18n'))
import check_i18n as C      # INIT_JS (같은 시드 · 같은 시계) · SIM_JS (몇 해 돌리기)

HAN = re.compile('[가-힣]')
PAGE = os.path.join(ROOT, 'heroschool.html')


def fields(S):
    """언어를 따라가야 하는 칸 (일지 · 문장은 쓰인 언어 그대로라 뺀다)"""
    out = {
        'students': [(s.get('name'), s.get('epithet')) for s in S.get('students', [])],
        'grads': [(g.get('name'), g.get('raw'), g.get('epithet'), g.get('career'), g.get('careerD'), g.get('gift'),
                   [r.get('name') for r in g.get('relics', [])]) for g in S.get('graduates', [])],
        'epiUsed': sorted(S.get('epiUsed', [])),
        'epiLog': [(e.get('name'), e.get('title'), e.get('prev'), e.get('crowd')) for e in S.get('epiLog', [])],
        'relics': [(r.get('name'), [a.get('n') for a in r.get('aff', [])]) for r in S.get('relicPool', [])],
        'skills': [(x.get('name'), x.get('from')) for x in S.get('skillPool', [])],
        'friendly': [(x.get('name'), [[m.get('name') for m in t] for t in x.get('teams', [])])
                     for ph in ('spring', 'winter') for x in ((S.get('friendly') or {}).get(ph) or {}).get('offers', [])],
        'mission': [x.get('n') for x in (S.get('mission') or {}).get('done', [])],
        'tour': [r.get('vs') for r in (S.get('lastTour') or {}).get('results', [])],
    }
    return out


def han_left(F):
    bad = []
    def walk(v, p):
        if isinstance(v, (list, tuple)):
            for i, x in enumerate(v): walk(x, p)
        elif isinstance(v, str) and HAN.search(v):
            bad.append((p, v[:40]))
    for k, v in F.items():
        if k in ('tour',):          # 대회 상대 — 기본 조각이 아닌 학원(직접 지은 이름)일 수 있다
            continue
        walk(v, k)
    return bad


PACK_JS = r"""() => {
  const g = S.graduates.find(x=> x.epithet) || S.graduates[0];
  const pk = leaguePackUnit(g);
  S.acadName = "Argent Hero Academy";
  const my = leagueMyPack([], 'wedge').acad;
  const T = leagueSane({acad: "백은 용사 학원", form: "wedge", t: [pk, pk, pk], v: 99, lp: 1000}, "tid1");
  return {grad: [g.raw, g.epithet, g.career], pack: [pk.n, pk.e, pk.c].concat(pk.r.map(r=> r.name)), my,
          sane: T ? [T.acad, T.units[0].name, T.units[0].epithet, T.units[0].career] : null,
          chat: chatSane('k', {t: 'hi', acad: '은여우 학원'}).acad, npc: JSON.stringify(l5NpcDoc(3))};
}"""


async def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--years', type=int, default=3)
    o = ap.parse_args()
    from playwright.async_api import async_playwright
    fails, errs_all = [], []
    async with async_playwright() as p:
        br = await p.chromium.launch()

        async def page(lang, save=None):
            c = await br.new_context(viewport={'width': 1440, 'height': 900})
            await c.route(re.compile(r'^https?://'), lambda r: r.abort())
            await c.add_init_script(C.INIT_JS)
            if save is not None:
                await c.add_init_script('localStorage.setItem("heroacademy_v1", %s);' % json.dumps(json.dumps(save, ensure_ascii=False)))
            pg = await c.new_page()
            pg.on('pageerror', lambda e: errs_all.append('%s: %s' % (lang, str(e)[:200])))
            await pg.goto('file://' + PAGE + '?lang=' + lang, wait_until='commit')
            await pg.wait_for_function("() => typeof S !== 'undefined' && S && S.students && S.students.length && !document.getElementById('bootLoader')",
                                       polling=250, timeout=60000)
            return c, pg

        async def state(pg):
            return json.loads(await pg.evaluate('() => JSON.stringify(S)'))

        # 1 · 2
        c, pg = await page('ko'); r = await pg.evaluate(C.SIM_JS, o.years); ko = await state(pg); await c.close()
        errs_all += ['sim ko: ' + e for e in r['err']]
        c, pg = await page('en', ko); en = await state(pg)
        await pg.evaluate('() => save()'); en_saved = json.loads(await pg.evaluate('() => localStorage.getItem("heroacademy_v1")')); await c.close()
        left = han_left(fields(en))
        print('1. 한국어 세이브 → 영어판 — 학생 %s' % [s[0] for s in fields(en)['students']][:6])
        print('   졸업생 %s' % [g[0] for g in fields(en)['grads']])
        if left: fails.append('영어판에서 한글이 남은 칸 %d: %s' % (len(left), left[:6]))
        c, pg = await page('ko', en_saved); back = await state(pg); await c.close()
        A, B = fields(ko), fields(back)
        diff = [k for k in A if A[k] != B[k]]
        print('2. 영어판 저장 → 한국어판 — 처음과 다른 칸: %s' % (diff or '없음'))
        if diff: fails.append('왕복 뒤 다른 칸: %s' % ['%s: %s → %s' % (k, A[k], B[k]) for k in diff][:3])
        # 3
        c, pg = await page('en'); r = await pg.evaluate(C.SIM_JS, o.years); out = await pg.evaluate(PACK_JS); await c.close()
        errs_all += ['sim en: ' + e for e in r['err']]
        c, pg = await page('ko'); npc_ko = await pg.evaluate('() => JSON.stringify(l5NpcDoc(3))'); await c.close()
        print('3. 서버로: %s · 내 학원 %s | 받은 것: %s · 채팅 %s | NPC 문서 두 언어 같음 %s'
              % (out['pack'][:3], out['my'], out['sane'], out['chat'], out['npc'] == npc_ko))
        if not all(HAN.search(x or '가') for x in out['pack'][:3] if x) or not HAN.search(out['my']):
            fails.append('서버로 보낼 묶음에 영어: %s · %s' % (out['pack'], out['my']))
        if not out['sane'] or any(HAN.search(x or '') for x in out['sane']) or HAN.search(out['chat']):
            fails.append('받은 묶음이 영어가 아니다: %s · %s' % (out['sane'], out['chat']))
        if out['npc'] != npc_ko:
            fails.append('NPC 학원 문서가 언어마다 다르다')
        await br.close()
    if errs_all: fails.append('오류 %d: %s' % (len(errs_all), errs_all[:3]))
    print('\n' + ('통과 — 세이브 · 서버의 데이터 글이 언어를 따라간다' if not fails else '실패:\n  ' + '\n  '.join(fails)))
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(asyncio.run(main()))
