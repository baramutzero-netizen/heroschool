from pathlib import Path
from PIL import Image
from scipy import ndimage
import numpy as np
from fontTools.ttLib import TTFont
p=Path(__file__).resolve().parent
im=Image.open(p/'ornaments/source.png').convert('RGBA');a=np.array(im);labels,n=ndimage.label(a[:,:,3]>0);counts=np.bincount(labels.ravel());counts[0]=0
ids=np.argsort(counts)[-9:];centers=np.array(ndimage.center_of_mass(a[:,:,3]>0,labels,ids));order=sorted(range(9),key=lambda k:(round(centers[k,0]/(im.height/3)-.5),centers[k,1]));ids=ids[order];centers=centers[order]
cs=np.array(ndimage.center_of_mass(a[:,:,3]>0,labels,np.arange(1,n+1)));assign=np.zeros(n+1,dtype=int);assign[1:]=np.argmin(((cs[:,None,:]-centers[None,:,:])**2).sum(axis=2),axis=1)+1
for i,name in enumerate(['crest','leaf','purse','weight','books','target','swords','cup','map']):
 b=a.copy();b[:,:,3]=np.where(assign[labels]==i+1,b[:,:,3],0);x=Image.fromarray(b);x=x.crop(x.getbbox());x.thumbnail((240,240),Image.Resampling.LANCZOS);x.save(p/f'ornaments/{name}.webp',lossless=True)
x=Image.open(p/'ornaments/letter-source.png').convert('RGBA');x=x.crop(x.getbbox());x.thumbnail((420,420),Image.Resampling.LANCZOS);x.save(p/'ornaments/letter.webp',quality=90)
for name in ['NanumPenScript','NanumBrushScript']:
 f=TTFont(p/f'fonts/{name}-Regular.ttf');f.flavor='woff2';f.save(p/f'fonts/{name}.woff2')
print('Packed nine separate transparent ornaments, letter, two local fonts')
