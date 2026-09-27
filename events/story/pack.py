"""이야기 팝업 삽화를 game.html 에 넣는다 (0927)
· 직접 의뢰를 받다 1~4쪽 — sprites/src/mission1~4.png.png
· 라이벌 이야기 1~2쪽 — sprites/src/rivalry1~2.png.png
game.html 이 20MB 한도에 가까워서 가로 900px · WebP 66 으로 줄여 넣는다. 다시 넣을 때는 이 파일만 돌리면 된다."""
from pathlib import Path
import base64, json, re, sys
from PIL import Image
ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
SRC = ROOT/'sprites'/'src'
PAGES = {'guild1':'mission1', 'guild2':'mission2', 'guild3':'mission3', 'guild4':'mission4',
         'rival1':'rivalry1', 'rival2':'rivalry2'}
def build(target):
    assets = {}
    for key, name in PAGES.items():
        im = Image.open(SRC/f'{name}.png.png').convert('RGB')
        im.thumbnail((900, 900), Image.Resampling.LANCZOS)
        out = HERE/f'{name}.webp'
        im.save(out, format='WEBP', quality=66, method=6)
        assets[key] = 'data:image/webp;base64,' + base64.b64encode(out.read_bytes()).decode()
    s = target.read_text(encoding='utf-8')
    start, end = '/* STORY_ART_START */', '/* STORY_ART_END */'
    block = start + '\nconst STORY_ART = ' + json.dumps(assets) + ';\n' + end
    if start in s:
        s = re.sub(re.escape(start) + r'.*?' + re.escape(end), lambda _: block, s, count=1, flags=re.S)
    else:
        anchor = 'const GUILD_WYVERN = 5000'
        if anchor not in s: sys.exit('anchor not found')
        s = s.replace(anchor, block + '\n' + anchor, 1)
    target.write_text(s, encoding='utf-8')
    print('story art embedded', sum(len(v) for v in assets.values()), 'chars')
if __name__ == '__main__':
    build(Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT/'game.html')
