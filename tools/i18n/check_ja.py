"""일본어판 준비 시험 (1014) — 빌드한 heroschool.html 을 ?lang=ja · 한국어 · 영어로 띄워 일본어 글꼴 · CSS 가 일본어에서만 붙는지 본다.

    python3 tools/i18n/check_ja.py            (저장소 맨 위 · hs.py build 뒤 · playwright · 바깥 주소는 막는다)

· 일본어 — <html lang="ja"> · 글꼴 덧규칙(#i18nJaFonts)이 lateFonts 뒤 · 물마루 · 물마루 Mono · 봄바람체 자리의 일본어 글꼴이 받아짐 ·
  메뉴 · 위쪽 칸이 일본어 · 12px 일본어 글자가 또렷함(사이 색 없음) · keep-all → normal · line-break strict ·
  도트 폰트를 끄면 IBM Plex Sans JP · Shippori Mincho 가 앞에 · 학생 명부 책(그림자 DOM)의 keep-all 도 normal · 오류 없음
· 한국어 · 영어 — 일본어 글꼴 · CSS 가 없다 (영어는 영어 화면 CSS 그대로)
"""
import os, re, sys
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PAGE = os.path.join(ROOT, 'heroschool.html')
SAMPLE = '強化ポイント123 スキル'

PROBE = r"""async () => {
  const late = document.getElementById('lateFonts'), jaf = document.getElementById('i18nJaFonts');
  const box = document.createElement('div'); box.id = 'jaT';
  box.style.cssText = 'position:fixed;left:0;top:0;z-index:99999;background:#fff;color:#000;padding:4px 6px';
  box.innerHTML = '<div id="jaPx" style="font:12px/20px Mulmaru;white-space:nowrap">__S__</div>'
    + '<div id="jaMono" style="font:12px/20px \'Mulmaru Mono\',Mulmaru;white-space:nowrap">戦闘力 1,808</div>'
    + '<div class="greet boast" id="jaBoast" style="position:static;width:auto">ハハハ！見ておけ！</div>'
    + '<div class="greet" id="jaWrap" style="position:static;width:120px;font:12px/20px Mulmaru">あの…少しお時間いいですか？長くはかかりません。</div>';
  document.body.appendChild(box);
  await new Promise(r => setTimeout(r, 300)); await document.fonts.ready;
  const faces = []; document.fonts.forEach(f => { if(/^(Mulmaru|Mulmaru Mono|HsBombaram21)$/.test(f.family)) faces.push([f.family, f.status, String(f.unicodeRange)]); });
  const cs = id => getComputedStyle(document.getElementById(id));
  return {lang: document.documentElement.lang, jaFonts: !!jaf, after: !!(late && jaf && (late.compareDocumentPosition(jaf) & Node.DOCUMENT_POSITION_FOLLOWING)),
          jaCss: !!document.getElementById('i18nJaCss'), enCss: !!document.getElementById('i18nCss'), faces,
          wrapWB: cs('jaWrap').wordBreak, wrapLB: cs('jaWrap').lineBreak,
          side: (document.getElementById('app') || document.body).innerText.slice(0, 1500)};
}"""
NOPIXEL = r"""async () => { pixelFontApply(false); await new Promise(r => setTimeout(r, 200));
  const b = getComputedStyle(document.body).fontFamily, h = document.createElement('h2'); h.textContent = '春季大会'; document.body.appendChild(h);
  const hf = getComputedStyle(h).fontFamily; h.remove(); pixelFontApply(true); return {body: b, h2: hf}; }"""
ROSTER = r"""async () => { UI.view = 'roster'; render(); await new Promise(r => setTimeout(r, 600));
  const h = document.getElementById('rbHost'); if(!h || !h.shadowRoot) return null;
  const st = h.shadowRoot.getElementById('i18nCss'), bub = h.shadowRoot.querySelector('.bub');
  return {css: st ? st.textContent : '', bub: bub ? getComputedStyle(bub).wordBreak : null}; }"""


def crisp(png):
    """12px 일본어 줄의 픽셀 — 흰 바탕 · 검은 글자에서 사이 색(번짐) 비율"""
    from PIL import Image
    import io
    im = Image.open(io.BytesIO(png)).convert('L')
    px = im.tobytes()
    ink = sum(1 for v in px if v < 128)
    mid = sum(1 for v in px if 24 < v < 232)
    return ink, mid


def main():
    if not os.path.exists(PAGE):
        sys.exit('heroschool.html 이 없다 — hs.py build 먼저')
    fails = []
    with sync_playwright() as p:
        br = p.chromium.launch()
        for lang in ('ja', 'ko', 'en'):
            ctx = br.new_context(viewport={'width': 1440, 'height': 900}, locale='ja-JP' if lang == 'ja' else 'ko-KR')
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
            r = pg.evaluate(PROBE.replace('__S__', SAMPLE))
            ja_faces = [f for f in r['faces'] if f[2] != 'U+0-10FFFF']

            def need(cond, msg):
                if not cond:
                    fails.append('%s: %s' % (lang, msg))
            if lang == 'ja':
                need(r['lang'] == 'ja', 'html lang %r' % r['lang'])
                need(r['jaFonts'] and r['after'], '글꼴 덧규칙이 없거나 lateFonts 앞 (%s · %s)' % (r['jaFonts'], r['after']))
                need(r['jaCss'] and not r['enCss'], '일본어 CSS %s · 영어 CSS %s' % (r['jaCss'], r['enCss']))
                need(sorted(f[0] for f in ja_faces) == ['HsBombaram21', 'Mulmaru', 'Mulmaru Mono'], '일본어 글꼴 자리 %s' % [f[0] for f in ja_faces])
                need(all(f[1] == 'loaded' for f in ja_faces), '받지 못한 일본어 글꼴 %s' % [f[:2] for f in ja_faces if f[1] != 'loaded'])
                need('面談' in r['side'] and '日程' in r['side'], '메뉴 · 위쪽 칸에 일본어 단어가 없다')
                need(r['wrapWB'] == 'normal' and r['wrapLB'] == 'strict', 'keep-all → normal · strict 아님 (%s · %s)' % (r['wrapWB'], r['wrapLB']))
                ink, mid = crisp(pg.locator('#jaPx').screenshot())
                need(ink > 50 and mid <= ink * 0.02, '12px 일본어가 번진다 (글자 픽셀 %d · 사이 색 %d)' % (ink, mid))
                n = pg.evaluate(NOPIXEL)
                need(n['body'].startswith('"IBM Plex Sans JP"') and n['h2'].startswith('"Shippori Mincho"'), '도트 폰트를 껐을 때 %s' % n)
                rb = pg.evaluate(ROSTER)
                need(rb is not None and 'word-break:normal' in rb['css'] and rb['bub'] == 'normal', '학생 명부 책 %s' % (rb and {k: (v[:60] if isinstance(v, str) else v) for k, v in rb.items()}))
                print('일본어 — 글꼴 %s · 12px 글자 픽셀 %d · 사이 색 %d · 도트 끔 %s / %s' % (
                    ' · '.join('%s %s' % (f[0], f[1]) for f in ja_faces), ink, mid, n['body'].split(',')[0], n['h2'].split(',')[0]))
            else:
                need(r['lang'] == lang, 'html lang %r' % r['lang'])
                need(not r['jaFonts'] and not ja_faces and not r['jaCss'], '일본어 글꼴 · CSS 가 붙었다')
                need(r['wrapWB'] == 'keep-all', 'keep-all 이 바뀌었다 (%s)' % r['wrapWB'])
                need(r['enCss'] == (lang == 'en'), '영어 화면 CSS %s' % r['enCss'])
                print('%s — 일본어 글꼴 · CSS 없음 · keep-all 그대로' % ('한국어' if lang == 'ko' else '영어'))
            for e in errs:
                fails.append('%s: %s' % (lang, e))
            ctx.close()
        br.close()
    if fails:
        print('\n실패 %d' % len(fails))
        for f in fails:
            print('  ' + f)
        sys.exit(1)
    print('\n통과 — 일본어 글꼴 · CSS 는 일본어에서만 붙고, 한국어 · 영어는 그대로')


if __name__ == '__main__':
    main()
