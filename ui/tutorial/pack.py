"""Sync the editable responsive tutorial sources into game.html, then run wrap.py/wrap_site.py."""
from pathlib import Path
import re
root=Path(__file__).resolve().parents[2]
p=root/'game.html';s=p.read_text(encoding='utf-8')
for tag,file in [('STYLE','style.css'),('RUNTIME','runtime.js')]:
    body=(Path(__file__).parent/file).read_text(encoding='utf-8')
    pattern=r'(/\* TUTORIAL_RESPONSIVE_'+tag+r'_START \*/).*?(/\* TUTORIAL_RESPONSIVE_'+tag+r'_END \*/)'
    s,n=re.subn(pattern,lambda m:m[1]+'\n'+body+'\n'+m[2],s,flags=re.S)
    assert n==1,tag
p.write_text(s,encoding='utf-8')
print('Responsive tutorial sources synced')
