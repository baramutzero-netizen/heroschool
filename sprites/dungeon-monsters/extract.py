from pathlib import Path
from PIL import Image
import numpy as np
from scipy import ndimage
import shutil
out=Path('sprites/dungeon-monsters'); src=Path('C:/Users/mjkki/.codex/generated_images/01a0a7eb-8edf-7741-964c-cd51a7960b15')
files=['6adbcac0-a024-4515-b107-53378d61ada2','64f00fd5-d955-43b1-b794-28972d984dd9','ef639bac-b804-485b-ae03-a7178aa6c0eb','0c67a64f-86b0-4f22-a090-6c0aef1b4876','fa37c0f4-2e98-4157-b2c5-f5fb3206c51d']
for i,f in enumerate(files,1):
 shutil.copy2(src/f'exec-{f}.png',out/f'd{i}-source.png')
 a=np.array(Image.open(out/f'd{i}-source.png').convert('RGBA')); labels,n=ndimage.label(a[:,:,3]>0); counts=np.bincount(labels.ravel()); counts[0]=0
 ids=np.argsort(counts)[-8:][::-1]
 print(i,a.shape,[(int(k),int(counts[k]),tuple(round(v,1) for v in ndimage.center_of_mass(a[:,:,3]>0,labels,int(k)))) for k in ids])
