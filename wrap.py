import datetime, re
src=open('game.html',encoding='utf-8').read()
from build_guard import validate_game_source
validate_game_source(src)
STAMP=datetime.datetime.now().strftime('%m%d-%H%M')
src=re.sub(r'const BUILD = "[^"]*";', 'const BUILD = "%s";' % STAMP, src, count=1)
i=src.index('<div id="app">')
head=src[:i]; body=src[i:]
from build_boot import boot_split
head, body, tail = boot_split(head, body)   # 첫 접속 로딩 화면 · 글꼴은 맨 뒤로
out=f'''<!doctype html>
<html lang="ko"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<style>:root{{color-scheme:light dark}}body{{margin:0}}img{{max-width:100%}}[hidden]{{display:none!important}}</style>
{head}</head>
<body>
{body}
{tail}
</body></html>'''
open('heroschool.html','w',encoding='utf-8').write(out)
print('wrapped', len(out), 'build', STAMP)
