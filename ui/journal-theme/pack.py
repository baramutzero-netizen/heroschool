from pathlib import Path
import re
root=Path(__file__).resolve().parents[2]
p=root/'game.html'
s=p.read_text(encoding='utf-8')
block='/* JOURNAL_THEME_START */\n'+(Path(__file__).parent/'theme.css').read_text(encoding='utf-8')+'\n'+(Path(__file__).parent/'pixel.css').read_text(encoding='utf-8')+'\n/* JOURNAL_THEME_END */'
if '/* JOURNAL_THEME_START */' in s:
    s=re.sub(r'/\* JOURNAL_THEME_START \*/.*?/\* JOURNAL_THEME_END \*/',lambda _:block,s,flags=re.S)
else:
    s=s.replace('</style>',block+'\n</style>',1)
s=s.replace('/* JOURNAL_THEME_END */',(Path(__file__).parent/'mint.css').read_text(encoding='utf-8')+'\n/* JOURNAL_THEME_END */',1)
s=s.replace('/* JOURNAL_THEME_END */',(Path(__file__).parent/'riso.css').read_text(encoding='utf-8')+'\n/* JOURNAL_THEME_END */',1)
p.write_text(s,encoding='utf-8')
