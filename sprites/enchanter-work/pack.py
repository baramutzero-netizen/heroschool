"""Embed the native Aseprite export as a dedicated enchanter atlas."""
from pathlib import Path
import base64,json,re
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
names=['idle','attack','hit','down','win','weed','scrub','dust','carry','meditate','read']
durations=[180,100,100,180,180,220,200,220,180,400,300]
meta=[[{'rect':[c*256,r*256,256,256],'duration':durations[r]} for c in range(4)] for r in range(11)]
data='data:image/png;base64,'+base64.b64encode((HERE/'enchanter-complete.png').read_bytes()).decode()
code='/* ENCHANTER_POLISH_START */\nSPR_X_IMG.enchanter='+json.dumps(data)+';\nSPR_JOB.enchanter='+json.dumps([4]*11)+';\nSPR_META.enchanter='+json.dumps(meta,separators=(',',':'))+';\n/* ENCHANTER_POLISH_END */'
p=ROOT/'game.html';s=p.read_text(encoding='utf-8')
if '/* ENCHANTER_POLISH_START */' in s:s=re.sub(r'/\* ENCHANTER_POLISH_START \*/.*?/\* ENCHANTER_POLISH_END \*/',lambda _:code,s,flags=re.S)
else:s=s.replace('const SPR_XB = {};',code+'\nconst SPR_XB = {};')
s=re.sub(r'const SPR_M\s*= \{[^\n]+', 'const SPR_M = '+json.dumps(dict(zip(names,range(11))))+';',s,count=1)
s=re.sub(r'const SPR_MS\s*= \[[^\n]+', 'const SPR_MS = '+json.dumps(durations)+';',s,count=1)
s=re.sub(r'const SPR_LOOP\s*= \[[^\n]+', 'const SPR_LOOP = [1,0,0,0,1,1,1,1,1,1,1];',s,count=1)
p.write_text(s,encoding='utf-8')
(HERE/'enchanter-complete.json').write_text(json.dumps({'cell':256,'pivot':[128,170],'motions':dict(zip(names,meta))},indent=2),encoding='utf-8')
print('Enchanter: 5 combat + 6 work motions embedded')
