"""영어판 공유 미리보기 (1010 · 5단계) — 링크를 채팅 · SNS 에 붙였을 때 뜨는 영어 제목 · 설명 · 그림.

    python3 tools/i18n/og_en.py            (저장소 맨 위에서 · Playwright + 크로미움 · 빌드한 heroschool.html 이 있어야 한다)

· site/og-en.png — 1200×630. 한국어 site/og.png 와 같은 모양(검은 바탕 · 황동 방패 · 제목 · 설명 두 줄 · 꼬리표 넷 · 아래 띠).
  직업 · 스킬 수는 게임에서 센다 (몬스터 직업 제외 · 스킬은 기본기 · 스킬 둘 · 필살 — 한국어 그림의 '스킬 48종'과 같은 셈).
  글꼴은 Noto Sans CJK (한국어 og.png 를 만든 것과 같은 리눅스 글꼴) — 다른 PC 에서 돌리면 비슷한 고딕으로 바뀐다.
· en/index.html — 영어 공유 링크(저장소 맨 위 /en/). 크롤러는 이 쪽의 영어 og 태그를 읽고, 사람은 site/?lang=en 으로 넘어간다.
  (게임 페이지 site/index.html 하나로는 미리보기 문구를 언어마다 다르게 할 수 없다 — 미리보기는 스크립트를 돌리지 않는다)
  맨 위 index.html(→ site/) 과 같은 방식이고, 그림 주소도 같은 상대 주소다.
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HERE = os.path.dirname(os.path.abspath(__file__))

TITLE_KO = '용사 학원 키우기 — 학원이 망했다'
DESC = ('Become the Master of a hero academy and raise students over three years in this web management sim. '
        'Weekly schedules, expeditions, 3-on-3 ATB battles, and spring and fall tournaments.')
CARD_TITLE, CARD_SUB = 'My Hero’s Academy', 'The Academy Went Under'
CARD_LINES = ('An academy management sim — raise hero students for three years.',
              'Weekly schedules, expeditions, 3-on-3 ATB battles, seasonal tournaments.')
FAVICON = ("data:image/svg+xml,"
           "%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 40 40'%3E"
           "%3Cpath d='M20 2 L35 7 V20 C35 29 28 35 20 38 C12 35 5 29 5 20 V7 Z' fill='%2313141b' stroke='%23c8a24a' stroke-width='2.4'/%3E"
           "%3Cpath d='M20 10 V30 M14 15 L20 12 L26 15 M13 21 H27' fill='none' stroke='%23c8a24a' stroke-width='2.2'/%3E%3C/svg%3E")

CARD = """<!doctype html><html lang="en"><head><meta charset="utf-8"><style>
*{box-sizing:border-box;margin:0}
body{width:1200px;height:630px;background:#13141b;color:#e8e7f0;
  font-family:"Noto Sans CJK KR","Noto Sans KR","Segoe UI","Helvetica Neue",Arial,sans-serif;
  display:flex;flex-direction:column;justify-content:center;padding:64px 88px 70px;position:relative;overflow:hidden}
.glow{position:absolute;inset:-40% -10% auto auto;width:760px;height:760px;border-radius:50%;
  background:radial-gradient(circle,rgba(200,162,74,.16),transparent 62%)}
svg{width:96px;height:96px;flex:none}
h1{font-size:82px;font-weight:700;letter-spacing:-.01em;line-height:1.08;margin:24px 0 2px}
h2{font-size:34px;font-weight:500;color:#c8a24a;margin:0 0 20px}
p{font-size:28px;color:#9c9eb4;line-height:1.55;white-space:nowrap}
.row{display:flex;gap:10px;margin-top:30px}
.t{border:1px solid #333747;border-radius:4px;padding:7px 18px;font-size:22px;color:#c8a24a}
.bar{position:absolute;left:0;right:0;bottom:0;height:7px;background:linear-gradient(90deg,#c8a24a,#8a86ec 55%,transparent)}
</style></head><body>
<div class="glow"></div>
<svg viewBox="0 0 40 40"><path d="M20 2 L35 7 V20 C35 29 28 35 20 38 C12 35 5 29 5 20 V7 Z" fill="none" stroke="#c8a24a" stroke-width="1.6"/><path d="M20 10 V30 M14 15 L20 12 L26 15 M13 21 H27" fill="none" stroke="#c8a24a" stroke-width="1.4"/></svg>
<h1>@TITLE@</h1><h2>@SUB@</h2>
<p>@L1@<br>@L2@</p>
<div class="row">@TAGS@</div>
<div class="bar"></div></body></html>"""

STUB = """<!doctype html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>@TITLE@</title>
<meta name="description" content="@DESC@">
<meta name="theme-color" content="#13141b">
<link rel="icon" href="@FAVICON@">
<meta property="og:type" content="website">
<meta property="og:locale" content="en_US">
<meta property="og:title" content="@TITLE@">
<meta property="og:description" content="@DESC@">
<meta property="og:image" content="../site/og-en.png">
<meta name="twitter:card" content="summary_large_image">
<meta http-equiv="refresh" content="0; url=../site/?lang=en">
<style>
  :root{color-scheme:dark}
  body{margin:0;min-height:100vh;display:flex;align-items:center;justify-content:center;
    background:#13141b;color:#e8e4dc;font-family:system-ui,"Segoe UI",sans-serif;text-align:center}
  a{color:#c8a24a}
</style>
</head>
<body>
  <!-- 영어 공유 링크 (tools/i18n/og_en.py 가 만든다) — 미리보기는 이 쪽의 영어 og 태그 · 열면 영어판 게임으로 -->
  <p><b>@SHORT@</b> — opening the game…<br><br><a href="../site/?lang=en">Open now</a></p>
  <script>location.replace("../site/?lang=en" + location.hash);</script>
</body></html>
"""


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')


def counts():
    """게임에서 직업 · 스킬 수 (몬스터 직업 제외)"""
    from playwright.sync_api import sync_playwright
    page = os.path.join(ROOT, 'heroschool.html')
    with sync_playwright() as p:
        br = p.chromium.launch()
        c = br.new_context(locale='ko-KR')
        c.route(re.compile(r'^https?://'), lambda r: r.abort())
        pg = c.new_page()
        pg.goto('file://' + page + '?lang=ko', wait_until='commit')
        pg.wait_for_function("() => typeof JOBS !== 'undefined' && typeof JOB_KEYS !== 'undefined'", timeout=60000)
        n = pg.evaluate("() => { const pl = JOB_KEYS.filter(k => JOBS[k] && !JOBS[k].mon);"
                        " return [pl.length, pl.reduce((a, k) => a + (JOBS[k].skills || []).length, 0)]; }")
        br.close()
    return n


def render(jobs, skills, out):
    from playwright.sync_api import sync_playwright
    tags = ['%d Classes' % jobs, '%d Skills' % skills, 'ATB Battles', 'Auto-Save']
    html = (CARD.replace('@TITLE@', esc(CARD_TITLE)).replace('@SUB@', esc(CARD_SUB))
            .replace('@L1@', esc(CARD_LINES[0])).replace('@L2@', esc(CARD_LINES[1]))
            .replace('@TAGS@', ''.join('<span class="t">%s</span>' % esc(t) for t in tags)))
    with sync_playwright() as p:
        br = p.chromium.launch()
        pg = br.new_page(viewport={'width': 1200, 'height': 630}, device_scale_factor=1)
        pg.set_content(html, wait_until='load')
        wide = pg.evaluate("() => [...document.querySelectorAll('h1,h2,p,.row')].map(e => Math.ceil(e.scrollWidth)).reduce((a, b) => Math.max(a, b), 0)")
        if wide > 1200 - 88 * 2:
            sys.exit('og-en.png: 글이 카드보다 넓다 (%dpx) — 글을 줄인다' % wide)
        pg.screenshot(path=out, type='png')
        br.close()


def main():
    en = json.load(open(os.path.join(HERE, 'en.json'), encoding='utf-8'))
    title = en.get(TITLE_KO) or "My Hero's Academy - The Academy Went Under"
    jobs, skills = counts()
    out = os.path.join(ROOT, 'site', 'og-en.png')
    render(jobs, skills, out)
    print('site/og-en.png — 직업 %d · 스킬 %d' % (jobs, skills))
    os.makedirs(os.path.join(ROOT, 'en'), exist_ok=True)
    stub = (STUB.replace('@TITLE@', esc(title)).replace('@DESC@', esc(DESC)).replace('@FAVICON@', FAVICON)
            .replace('@SHORT@', esc(title.split(' - ')[0])))
    with open(os.path.join(ROOT, 'en', 'index.html'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(stub)
    print('en/index.html — %s' % title)


if __name__ == '__main__':
    main()
