from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np
from scipy import ndimage
import json,re,base64,io
root=Path(__file__).resolve().parents[2]; out=Path(__file__).resolve().parent
pools=[['wood','target'],['sentry','foghound','lantern'],['bellcrab','clockcrow','choir'],['saltcrab','jelly','diver'],['oath','scribe','blade']]
gallery=Image.new('RGB',(768,5*280),'#e4dfd5'); draw=ImageDraw.Draw(gallery)
assets={}
for row,keys in enumerate(pools):
 a=np.array(Image.open(out/f'd{row+1}-source.png').convert('RGBA')); labels,n=ndimage.label(a[:,:,3]>0); counts=np.bincount(labels.ravel());counts[0]=0
 main=np.argsort(counts)[-len(keys):]; centers=np.array(ndimage.center_of_mass(a[:,:,3]>0,labels,main)); order=np.argsort(centers[:,1]); main=main[order];centers=centers[order]
 # Assign disconnected sparks to nearest complete body, never cut at cell boundaries.
 allcent=np.array(ndimage.center_of_mass(a[:,:,3]>0,labels,np.arange(1,n+1)))
 assign=np.zeros(n+1,dtype=int);assign[1:]=np.argmin(((allcent[:,None,:]-centers[None,:,:])**2).sum(axis=2),axis=1)+1
 for col,key in enumerate(keys):
  b=a.copy();b[:,:,3]=np.where(assign[labels]==col+1,b[:,:,3],0);im=Image.fromarray(b);im=im.crop(im.getbbox());im.thumbnail((220,220),Image.Resampling.LANCZOS)
  canvas=Image.new('RGBA',(256,256));canvas.alpha_composite(im,((256-im.width)//2,236-im.height));name='mon_'+key;canvas.save(out/f'{name}.png')
  bio=io.BytesIO();canvas.save(bio,format='WEBP',lossless=True);assets[name]={'w':256,'h':256,'k':1,'src':'data:image/webp;base64,'+base64.b64encode(bio.getvalue()).decode()}
  gallery.paste(canvas,(col*256,row*280),canvas);draw.text((col*256+12,row*280+256),name,fill='#302d35')
gallery.save(out/'overview.jpg',quality=92)
game=root/'game.html';s=game.read_text(encoding='utf-8');m=re.search(r'const MON_IMG=(\{[^\n]+\});',s);assert m
mon=json.loads(m[1]);mon.update(assets);packed='const MON_IMG='+json.dumps(mon,separators=(',',':'))+';';s=s[:m.start()]+packed+s[m.end():]
(root/'sprites/mon.js').write_text(packed+'\n',encoding='utf-8')
runtime='/* DUNGEON_ENCOUNTERS_START */\n'+(out/'runtime.js').read_text(encoding='utf-8')+'\n/* DUNGEON_ENCOUNTERS_END */\n'
if '/* DUNGEON_ENCOUNTERS_START */' in s:s=re.sub(r'/\* DUNGEON_ENCOUNTERS_START \*/.*?/\* DUNGEON_ENCOUNTERS_END \*/\n',lambda _:runtime,s,flags=re.S)
else:s=s.replace('function genMonster(dg, sec){',runtime+'function genMonster(dg, sec){')
s=s.replace('const key = dg.mon, J = JOBS[key];','const key = dungeonMonsterKey(dg, sec), J = JOBS[key];')
# Exact spelling of original declaration is verified after packing.
s=s.replace('${esc(JOBS[d.mon].name)} 연전 ${d.secs}회','구간 적 ${(DUNGEON_MONSTERS[d.id]||[]).length}종 · 마지막: ${esc(JOBS[d.mon].name)} · ${d.secs}구간')
game.write_text(s,encoding='utf-8');print('Packed 14 monsters; originals retained:',len(mon))
