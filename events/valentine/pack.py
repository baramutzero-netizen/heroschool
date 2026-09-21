"""Embed the three Valentine illustrations in the standalone game source."""
from pathlib import Path
import base64,json,re
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
assets={}
for n in range(1,4):
    image=Image.open(HERE/f'page-{n}.png').convert('RGB')
    image.thumbnail((1100,734),Image.Resampling.LANCZOS)
    out=HERE/f'page-{n}.webp'
    image.save(out,format='WEBP',quality=88,method=6)
    assets[str(n)]='data:image/webp;base64,'+base64.b64encode(out.read_bytes()).decode()
p=ROOT/'game.html'
s=p.read_text(encoding='utf-8')
start='/* VALENTINE_ART_START */'
end='/* VALENTINE_ART_END */'
block=start+'\nconst VALENTINE_ART = '+json.dumps(assets)+';\n'+end
if start in s:
    s=re.sub(re.escape(start)+r'.*?'+re.escape(end),lambda _:block,s,count=1,flags=re.S)
else:
    s=s.replace('const VALENTINE_WEEK = 4;',block+'\nconst VALENTINE_WEEK = 4;',1)
p.write_text(s,encoding='utf-8')
print('Embedded three Valentine illustrations')
