const sharp=require('sharp'),fs=require('fs'),path=require('path');
const root=__dirname,generated='C:/Users/mjkki/.codex/generated_images/01a0a7eb-8edf-7741-964c-cd51a7960b15';
const files=['exec-963ae487-cefa-44d5-8c45-4f557d2d796e.png','exec-6a047fda-4081-42b3-87cd-608f700a4086.png','exec-b7a2f9f5-a64a-4d27-b710-e530c0e16f68.png','exec-7a6fcd24-8f2b-4c13-a87d-bc9cdc7882f2.png'];
const groups=require('./groups.json');
(async()=>{for(let g=0;g<4;g++){
const corrected=path.join(root,'uniform-'+g+'-corrected.png');
const uniform=fs.existsSync(corrected)?corrected:path.join(root,'uniform-'+g+'.png');
const source=fs.existsSync(uniform)?uniform:path.join(root,'source-'+g+'.png');if(!fs.existsSync(source))fs.copyFileSync(path.join(generated,files[g]),source);
const meta=await sharp(source).metadata();
for(let row=0;row<4;row++){const layers=[];for(let col=0;col<4;col++){
const left=Math.round(col*meta.width/4),top=Math.round(row*meta.height/4),width=Math.round((col+1)*meta.width/4)-left,height=Math.round((row+1)*meta.height/4)-top;
const input=await sharp(source).extract({left,top,width,height}).resize(256,256).png().toBuffer();layers.push({input,left:col*256,top:0});
}await sharp({create:{width:1024,height:256,channels:4,background:{r:0,g:0,b:0,alpha:0}}}).composite(layers).webp({quality:95,alphaQuality:100}).toFile(path.join(root,groups[g][row]+'.webp'));}}
if(!fs.existsSync(path.join(root,'hall-classroom.png')))fs.copyFileSync(path.join(generated,'exec-498ae252-910a-4c51-a441-c66b580806cf.png'),path.join(root,'hall-classroom.png'));
await sharp(path.join(root,'hall-classroom.png')).resize(1536,512).webp({quality:90}).toFile(path.join(root,'hall.webp'));
if(!fs.existsSync(path.join(root,'empty-source.png')))fs.copyFileSync(path.join(generated,'exec-4be2b450-f8af-4864-a3bb-f35c17bac72c.png'),path.join(root,'empty-source.png'));
const desk=await sharp(path.join(root,fs.existsSync(path.join(root,'empty-uniform.png'))?'empty-uniform.png':'empty-source.png')).trim().resize(188,188,{fit:'inside'}).png().toBuffer();
await sharp({create:{width:256,height:256,channels:4,background:{r:0,g:0,b:0,alpha:0}}}).composite([{input:desk,left:34,top:56}]).webp({quality:95}).toFile(path.join(root,'empty.webp'));
console.log('Prepared 16 four-frame study strips, classroom and empty desk');})();
