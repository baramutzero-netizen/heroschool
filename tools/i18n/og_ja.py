"""일본어판 공유 미리보기 (1014) — 링크를 채팅 · SNS 에 붙였을 때 뜨는 일본어 제목 · 설명 · 그림. og_en.py 의 일본어 짝.

    python3 tools/i18n/og_ja.py            (저장소 맨 위에서 · Playwright + 크로미움 · 빌드한 heroschool.html 이 있어야 한다)

· site/og-ja.png — 1200×630. 영어 site/og-en.png 와 같은 모양 (그림 틀 · 직업 · 스킬 수 세기는 og_en.py 의 것을 그대로 쓴다).
  글꼴은 Noto Sans CJK JP (일본어 글자 모양 — 한국어 · 영어 그림의 KR 과 같은 집안) — 다른 PC 에서 돌리면 비슷한 고딕으로 바뀐다.
· ja/index.html — 일본어 공유 링크(저장소 맨 위 /ja/). 크롤러는 이 쪽의 일본어 og 태그를 읽고, 사람은 site/?lang=ja 로 넘어간다.
  제목은 일본어 표(ja.json)의 게임 제목. 말은 ja/GUIDE.md 의 용어집(遠征 · 大会 · マスター …)을 따른다.
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import og_en as E

ROOT = E.ROOT
TITLE_KO = E.TITLE_KO
DESC = ('勇者学園のマスターとなり、生徒を3年間育てるWeb学園経営シミュレーション。'
        '週ごとのスケジュール、遠征、3人1組のATBバトル、春と秋の大会。')
CARD_TITLE, CARD_SUB = 'わが英雄のアカデミー', '学園がつぶれた'
CARD_LINES = ('勇者学園の経営シミュレーション ― 英雄の卵を3年間育てよう。',
              '週ごとのスケジュール、遠征、3人1組のATBバトル、春と秋の大会。')
TAGS = ('職業 %d種', 'スキル %d種', 'ATBバトル', 'オートセーブ')

CARD = (E.CARD.replace('<html lang="en">', '<html lang="ja">')
        .replace('font-family:"Noto Sans CJK KR","Noto Sans KR",', 'font-family:"Noto Sans CJK JP","Noto Sans JP",')
        .replace('letter-spacing:-.01em', 'letter-spacing:.02em'))

STUB = (E.STUB.replace('<html lang="en">', '<html lang="ja">')
        .replace('content="en_US"', 'content="ja_JP"')
        .replace('../site/og-en.png', '../site/og-ja.png')
        .replace('?lang=en', '?lang=ja')
        .replace('font-family:system-ui,"Segoe UI",sans-serif', 'font-family:system-ui,"Hiragino Sans","Yu Gothic UI","Meiryo",sans-serif')
        .replace('<!-- 영어 공유 링크 (tools/i18n/og_en.py 가 만든다) — 미리보기는 이 쪽의 영어 og 태그 · 열면 영어판 게임으로 -->',
                 '<!-- 일본어 공유 링크 (tools/i18n/og_ja.py 가 만든다) — 미리보기는 이 쪽의 일본어 og 태그 · 열면 일본어판 게임으로 -->')
        .replace('</b> — opening the game…<br><br>', '</b> ― ゲームを開いています…<br><br>')
        .replace('>Open now</a>', '>今すぐ開く</a>'))


def render(jobs, skills, out):
    from playwright.sync_api import sync_playwright
    tags = [TAGS[0] % jobs, TAGS[1] % skills, TAGS[2], TAGS[3]]
    esc = E.esc
    html = (CARD.replace('@TITLE@', esc(CARD_TITLE)).replace('@SUB@', esc(CARD_SUB))
            .replace('@L1@', esc(CARD_LINES[0])).replace('@L2@', esc(CARD_LINES[1]))
            .replace('@TAGS@', ''.join('<span class="t">%s</span>' % esc(t) for t in tags)))
    with sync_playwright() as p:
        br = p.chromium.launch()
        pg = br.new_page(viewport={'width': 1200, 'height': 630}, device_scale_factor=1)
        pg.set_content(html, wait_until='load')
        wide = pg.evaluate("() => [...document.querySelectorAll('h1,h2,p,.row')].map(e => Math.ceil(e.scrollWidth)).reduce((a, b) => Math.max(a, b), 0)")
        if wide > 1200 - 88 * 2:
            sys.exit('og-ja.png: 글이 카드보다 넓다 (%dpx) — 글을 줄인다' % wide)
        pg.screenshot(path=out, type='png')
        br.close()


def main():
    ja = json.load(open(os.path.join(HERE, 'ja.json'), encoding='utf-8'))
    title = ja.get(TITLE_KO) or '%s ― %s' % (CARD_TITLE, CARD_SUB)
    jobs, skills = E.counts()
    out = os.path.join(ROOT, 'site', 'og-ja.png')
    render(jobs, skills, out)
    print('site/og-ja.png — 職業 %d · スキル %d' % (jobs, skills))
    os.makedirs(os.path.join(ROOT, 'ja'), exist_ok=True)
    stub = (STUB.replace('@TITLE@', E.esc(title)).replace('@DESC@', E.esc(DESC)).replace('@FAVICON@', E.FAVICON)
            .replace('@SHORT@', E.esc(title.split(' ― ')[0])))
    if '?lang=en' in stub or 'og-en' in stub:
        sys.exit('ja/index.html: 영어 주소가 남았다')
    with open(os.path.join(ROOT, 'ja', 'index.html'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(stub)
    print('ja/index.html — %s' % title)


if __name__ == '__main__':
    main()
