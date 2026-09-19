"""Analyze legacy art into editable regions; Aseprite performs pixel extraction.

Connected regions, not equal-width rectangles, own their pixels. The manifest
records fixed import anchors/scales; runtime never auto-centers a bounding box.
"""
from pathlib import Path
import json
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

HERE = Path(__file__).resolve().parent
JOBS = ['archer','bard','darkpriest','druid','enchanter','forcemage','gunner','monk','ninja','paladin','priest','rogue','spellsword','sword','timemage','wizard']
MOTIONS = ['idle','attack','hit','down','win']
CHOICES = [[0,1,2,3],[0,1,2,3,4,5],[0,1,5],[0,1,3,4,5],[0,1,2,4]]

def runs(mask, ox=0, oy=0):
    out=[]
    for y,row in enumerate(mask):
        edges=np.flatnonzero(np.diff(np.r_[False,row,False].astype(np.int8)))
        for x0,x1 in edges.reshape(-1,2): out.append([y+oy,int(x0)+ox,int(x1)+ox])
    return out

def regions(a):
    labels,n=ndi.label(a[:,:,3]>=128,np.ones((3,3)))
    sizes=np.bincount(labels.ravel())
    objs=ndi.find_objects(labels)
    found=[]
    for i,s in enumerate(objs):
        if s is None or sizes[i+1]<1500: continue
        ys,xs=np.where(labels==i+1)
        found.append(dict(label=i+1,size=int(sizes[i+1]),box=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],cx=float(np.median(xs)),cy=float(np.median(ys))))
    return labels,found

def make():
    output={'version':3,'canvas':[256,256],'pivot':[128,170],'logicalSize':[128,128],'margin':16,'jobs':{}}
    for job in JOBS:
        path=HERE/'source-v3'/f'{job}.png'
        a=np.array(Image.open(path).convert('RGBA')); h,w=a.shape[:2]
        labels,found=regions(a)
        groups={}
        # Row bands classify an entire connected region, never slice its pixels.
        bounds=np.array([0,.225,.439,.645,.817,1])*h
        for reg in found:
            row=int(np.clip(np.searchsorted(bounds,reg['cy'],side='right')-1,0,4))
            col=int(np.clip(reg['cx']/(w/6),0,5))
            key=(row,col)
            if key not in groups or reg['size']>groups[key]['size']: groups[key]=reg
        idle=groups[(0,0)]; scale=96/(idle['box'][3]-idle['box'][1])
        # Existing painterly recolor palette is untouched by the import.
        frames=[]
        for r,choice in enumerate(CHOICES):
            for f,c in enumerate(choice):
                source=path; img=a; lab=labels
                reg=groups.get((r,c))
                override=r==1 and c in (3,4) and job in ('priest','darkpriest')
                if override:
                    source=HERE/'source-v3'/f'{job}-attack.png'
                    img=np.array(Image.open(source).convert('RGBA'))
                    lab,rr=regions(img); reg=max(rr,key=lambda q:q['size'])
                if reg is None: raise ValueError(f'Missing pose {job}/{r}/{c}')
                mask=lab==reg['label']
                # Retain disconnected details only close to this region, never
                # another full character or distant leftovers from adjacent cells.
                nearby=ndi.binary_dilation(mask,iterations=4)
                extras=np.unique(lab[nearby & ~mask]); counts=np.bincount(lab.ravel())
                for v in extras:
                    if v and counts[v]<500: mask|=lab==v
                yy,xx=np.where(mask); box=[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)]
                foot_y=box[3]-1
                # Import-time foot anchor uses the lower body, excluding bright FX.
                lower=mask & (np.indices(mask.shape)[0]>=box[1]+.82*(box[3]-box[1]))
                rgb=img[:,:,:3].astype(float); mx=rgb.max(2); mn=rgb.min(2)
                vivid=(mx>170)&((mx-mn)>100)
                feet=lower & ~vivid
                fy,fx=np.where(feet)
                if len(fx): foot_y=int(np.quantile(fy,.99)); root_x=float(np.median(fx))
                else: root_x=(box[0]+box[2])/2
                if r==3: root_x=(c+.5)*w/6 # falling extends from the standing root
                if job=='rogue' and r==1 and c in (2,3):
                    root_x=(c+.5)*w/6; foot_y=int(.423*h) # effect-only frames retain world height
                frame_scale=scale
                if override: frame_scale=96/(box[3]-box[1])
                # A single repaired-pose normalization is recorded explicitly;
                # no runtime fitting or frame-by-frame rescaling occurs.
                frames.append({'motion':MOTIONS[r],'frame':f,'sourcePose':c,'source':source.relative_to(HERE).as_posix(),'box':box,'anchor':[round(root_x,3),foot_y],'scale':frame_scale,'duration':[180,90,100,140,180][r],'runs':runs(mask[box[1]:box[3],box[0]:box[2]],box[0],box[1])})
        output['jobs'][job]={'scale':scale,'frames':frames}
        print(job,len(frames))
    (HERE/'frames-v3'/'import.json').write_text(json.dumps(output,separators=(',',':')),encoding='utf8')

if __name__=='__main__': make()
