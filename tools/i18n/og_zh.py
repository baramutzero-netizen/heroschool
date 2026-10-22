"""중국어판 공유 미리보기 (1022) — 간체 · 번체(대만) 링크를 채팅 · SNS 에 붙였을 때 뜨는 중국어 제목 · 설명 · 그림. og_ja.py 의 중국어 짝.

    python3 tools/i18n/og_zh.py            (저장소 맨 위에서 · Playwright + 크로미움 · 빌드한 heroschool.html 이 있어야 한다)

· site/og-zh-hans.png · site/og-zh-hant.png — 1200×630. 영어 · 일본어 그림과 같은 모양 (og_en.py 의 틀 · 직업 · 스킬 수 세기).
  글꼴은 Noto Sans CJK SC · TC (리눅스 글꼴 — 다른 PC 에서 돌리면 비슷한 고딕으로 바뀐다).
· zh-hans/index.html · zh-hant/index.html — 중국어 공유 링크(저장소 맨 위 /zh-hans/ · /zh-hant/). 크롤러는 이 쪽의 중국어 og 태그를 읽고,
  사람은 site/?lang=zh-Hans · site/?lang=zh-Hant 로 넘어간다. 제목은 그 언어 표(zh-Hans.json · zh-Hant.json)의 게임 제목.
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import og_en as E

ROOT = E.ROOT
LANGS = {
    'zh-Hans': {'dir': 'zh-hans', 'locale': 'zh_CN', 'png': 'og-zh-hans.png', 'cjk': '"Noto Sans CJK SC","Noto Sans SC"',
                'sys': 'system-ui,"PingFang SC","Microsoft YaHei",sans-serif',
                'desc': '成为勇者学院的大师，花三年培养学生的网页学院经营模拟游戏。每周日程、远征、三人一组的ATB战斗、春秋两季大赛。',
                'title': '勇者学院养成记', 'sub': '学院倒闭了',
                'lines': ('勇者学院经营模拟——用三年时间培养英雄的雏鸟。', '每周日程、远征、三人一组的ATB战斗、春秋两季大赛。'),
                'tags': ('职业 %d种', '技能 %d种', 'ATB战斗', '自动存档'),
                'opening': '——正在打开游戏…', 'open': '立即打开'},
    'zh-Hant': {'dir': 'zh-hant', 'locale': 'zh_TW', 'png': 'og-zh-hant.png', 'cjk': '"Noto Sans CJK TC","Noto Sans TC"',
                'sys': 'system-ui,"PingFang TC","Microsoft JhengHei",sans-serif',
                'desc': '成為勇者學院的大師，花三年培養學生的網頁學院經營模擬遊戲。每週日程、遠征、三人一組的ATB戰鬥、春秋兩季大賽。',
                'title': '勇者學院養成記', 'sub': '學院倒閉了',
                'lines': ('勇者學院經營模擬——用三年時間培養英雄的雛鳥。', '每週日程、遠征、三人一組的ATB戰鬥、春秋兩季大賽。'),
                'tags': ('職業 %d種', '技能 %d種', 'ATB戰鬥', '自動存檔'),
                'opening': '——正在開啟遊戲…', 'open': '立即開啟'},
}


def card(C):
    return (E.CARD.replace('<html lang="en">', '<html lang="%s">' % C['code'])
            .replace('font-family:"Noto Sans CJK KR","Noto Sans KR",', 'font-family:%s,' % C['cjk'])
            .replace('letter-spacing:-.01em', 'letter-spacing:.04em'))


def stub(C):
    s = (E.STUB.replace('<html lang="en">', '<html lang="%s">' % C['code'])
         .replace('content="en_US"', 'content="%s"' % C['locale'])
         .replace('../site/og-en.png', '../site/' + C['png'])
         .replace('?lang=en', '?lang=' + C['code'])
         .replace('font-family:system-ui,"Segoe UI",sans-serif', 'font-family:' + C['sys'])
         .replace('<!-- 영어 공유 링크 (tools/i18n/og_en.py 가 만든다) — 미리보기는 이 쪽의 영어 og 태그 · 열면 영어판 게임으로 -->',
                  '<!-- 중국어(%s) 공유 링크 (tools/i18n/og_zh.py 가 만든다) — 미리보기는 이 쪽의 중국어 og 태그 · 열면 중국어판 게임으로 -->' % C['code'])
         .replace('</b> — opening the game…<br><br>', '</b>%s<br><br>' % C['opening'])
         .replace('>Open now</a>', '>%s</a>' % C['open']))
    return s


def render(C, jobs, skills, out):
    from playwright.sync_api import sync_playwright
    t = C['tags']
    tags = [t[0] % jobs, t[1] % skills, t[2], t[3]]
    esc = E.esc
    html = (card(C).replace('@TITLE@', esc(C['title'])).replace('@SUB@', esc(C['sub']))
            .replace('@L1@', esc(C['lines'][0])).replace('@L2@', esc(C['lines'][1]))
            .replace('@TAGS@', ''.join('<span class="t">%s</span>' % esc(x) for x in tags)))
    with sync_playwright() as p:
        br = p.chromium.launch()
        pg = br.new_page(viewport={'width': 1200, 'height': 630}, device_scale_factor=1)
        pg.set_content(html, wait_until='load')
        wide = pg.evaluate("() => [...document.querySelectorAll('h1,h2,p,.row')].map(e => Math.ceil(e.scrollWidth)).reduce((a, b) => Math.max(a, b), 0)")
        if wide > 1200 - 88 * 2:
            sys.exit('%s: 글이 카드보다 넓다 (%dpx) — 글을 줄인다' % (C['png'], wide))
        pg.screenshot(path=out, type='png')
        br.close()


def main():
    jobs, skills = E.counts()
    for code, C in LANGS.items():
        C = dict(C, code=code)
        tab = json.load(open(os.path.join(HERE, code + '.json'), encoding='utf-8'))
        title = tab.get(E.TITLE_KO) or '%s——%s' % (C['title'], C['sub'])
        out = os.path.join(ROOT, 'site', C['png'])
        render(C, jobs, skills, out)
        print('site/%s — 직업 %d · 스킬 %d' % (C['png'], jobs, skills))
        os.makedirs(os.path.join(ROOT, C['dir']), exist_ok=True)
        s = (stub(C).replace('@TITLE@', E.esc(title)).replace('@DESC@', E.esc(C['desc'])).replace('@FAVICON@', E.FAVICON)
             .replace('@SHORT@', E.esc(title.split('——')[0])))
        if '?lang=en' in s or 'og-en' in s:
            sys.exit('%s/index.html: 영어 주소가 남았다' % C['dir'])
        with open(os.path.join(ROOT, C['dir'], 'index.html'), 'w', encoding='utf-8', newline='\n') as f:
            f.write(s)
        print('%s/index.html — %s' % (C['dir'], title))


if __name__ == '__main__':
    main()
