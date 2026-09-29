"""Connect illustrated student portraits. Run assets/student-portraits-v2/export.lua in Aseprite first."""
from pathlib import Path
import hashlib, json, re
root=Path(__file__).resolve().parents[1]
game=root/'game.html'
text=game.read_text(encoding='utf-8')
match=re.search(r'const FACE_IMG=(\{.*?\});',text)
paths={}
for job in json.loads(match.group(1)):
    asset=root/'assets/student-portraits-v2'/f'{job}-512.png'
    digest=hashlib.sha1(asset.read_bytes()).hexdigest()[:8]
    paths[job]=asset.relative_to(root).as_posix()+'?v='+digest
text=text[:match.start()]+'const FACE_IMG='+json.dumps(paths,separators=(',',':'))+';'+text[match.end():]
text=text.replace('.facebox img{display:block;width:100%;height:100%;object-fit:cover;object-position:50% 40%}', '.facebox img{display:block;width:100%;height:100%;object-fit:contain;object-position:center;image-rendering:auto}')
game.write_text(text,encoding='utf-8')
print('Connected',len(paths),'illustrated student portraits')
