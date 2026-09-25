import datetime, re
src=open('game.html',encoding='utf-8').read()
from build_guard import validate_game_source
validate_game_source(src)
STAMP=datetime.datetime.now().strftime('%m%d-%H%M')
src=re.sub(r'const BUILD = "[^"]*";', 'const BUILD = "%s";' % STAMP, src, count=1)
NOW=datetime.datetime.now()
TS=int(NOW.timestamp()*1000)
src=re.sub(r'const BUILD_TS = \d+;', 'const BUILD_TS = %d;' % TS, src, count=1)
RULES=int(re.search(r'const RULES_VER = (\d+);', src).group(1))
i=src.index('<div id="app">')
head=src[:i]; body=src[i:]
from build_boot import boot_split
head, body, tail = boot_split(head, body)   # 첫 접속 로딩 화면 · 글꼴은 맨 뒤로
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
<meta property="og:title" content="용사 학원 키우기 — 학원이 망했다">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="og.png">
<meta name="twitter:card" content="summary_large_image">
<style>:root{{color-scheme:light dark}}body{{margin:0}}img{{max-width:100%}}[hidden]{{display:none!important}}</style>
{head}</head>
<body>
{body}
{tail}
</body></html>'''
open('site/index.html','w',encoding='utf-8').write(out)
# 새 버전 알림 — 게임이 켤 때 · 30분마다 이 파일을 읽어 자기 빌드와 견준다. index.html 과 같이 올려야 한다.
# msg 에 한 줄 적어 두면 알림 띠에 같이 뜬다 (예: "마왕 대항전 보상 조정").
import json
json.dump({"build":STAMP, "ts":TS, "rules":RULES, "msg":""}, open('site/version.json','w',encoding='utf-8'), ensure_ascii=False)
print('site/index.html', len(out), 'build', STAMP, 'rules', RULES, '+ site/version.json')
