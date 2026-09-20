import datetime, re
src=open('game.html',encoding='utf-8').read()
from build_guard import validate_game_source
validate_game_source(src)
STAMP=datetime.datetime.now().strftime('%m%d-%H%M')
src=re.sub(r'const BUILD = "[^"]*";', 'const BUILD = "%s";' % STAMP, src, count=1)
i=src.index('<div id="app">')
head=src[:i]; body=src[i:]
favicon=("data:image/svg+xml,"
 "%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 40 40'%3E"
 "%3Cpath d='M20 2 L35 7 V20 C35 29 28 35 20 38 C12 35 5 29 5 20 V7 Z' fill='%2313141b' stroke='%23c8a24a' stroke-width='2.4'/%3E"
 "%3Cpath d='M20 10 V30 M14 15 L20 12 L26 15 M13 21 H27' fill='none' stroke='%23c8a24a' stroke-width='2.2'/%3E%3C/svg%3E")
desc="용사 학원의 마스터가 되어 학생을 3년간 육성하는 웹 운영 시뮬레이션. 주간 스케줄, 원정, 3인 1팀 ATB 전투와 봄·가을 대회."
out=f'''<!doctype html>
<html lang="ko"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="{desc}">
<meta name="theme-color" content="#13141b">
<link rel="icon" href="{favicon}">
<meta property="og:type" content="website">
<meta property="og:title" content="학원이 망했다">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="og.png">
<meta name="twitter:card" content="summary_large_image">
<style>:root{{color-scheme:light dark}}body{{margin:0}}img{{max-width:100%}}[hidden]{{display:none!important}}</style>
{head}</head>
<body>
{body}
</body></html>'''
open('site/index.html','w',encoding='utf-8').write(out)
print('site/index.html', len(out), 'build', STAMP)
