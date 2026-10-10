import datetime, re
from split_assets import split_file
src=split_file('game.html')   # 박혀 있는 그림 · 효과음은 assets/ 로 뺀다 (0928)
from build_guard import validate_game_source
validate_game_source(src)
STAMP=datetime.datetime.now().strftime('%m%d-%H%M')
src=re.sub(r'const BUILD = "[^"]*";', 'const BUILD = "%s";' % STAMP, src, count=1)
from build_strip import strip_dev
src = strip_dev(src)   # 배포 빌드에서는 테스트 기능(진행 페이지 테스트 모드 · 애니메이션 테스트)을 뺀다
try:   # 영어판 (1010) — 한국어 글을 번역 함수로 감싼다. 한국어로 띄우면 그대로 · 실패하면 변환 없이 (tools/i18n/i18n_build.py)
    import sys; sys.path.insert(0, 'tools/i18n'); from i18n_build import apply_i18n
    src = apply_i18n(src)
except ImportError:
    print('i18n: tools/i18n 이 없어 한국어만으로 빌드한다')
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
