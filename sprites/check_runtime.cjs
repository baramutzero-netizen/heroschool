// Run with NODE_PATH pointing at a runtime that provides playwright.
const {chromium}=require('playwright');
const fs=require('fs');
const path=require('path');
const {pathToFileURL}=require('url');
const root=path.resolve(__dirname,'..');
(async()=>{
 const browser=await chromium.launch({headless:true,channel:process.env.SPR_BROWSER||'msedge'});
 const page=await browser.newPage({viewport:{width:1280,height:900}});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto(pathToFileURL(path.join(root,'heroschool.html')).href);
 await page.waitForFunction(()=>typeof SPR_READY!=='undefined'&&SPR_READY);
 const result=await page.evaluate(()=>{
  let count=0;
  for(let j=0;j<SPR_KEYS.length;j++)for(let m=0;m<5;m++){
   const list=SPR_META[SPR_KEYS[j]][m];
   list.forEach((f,i)=>{
    const c=sprCellCv(j,-1,m,i),a=c.getContext('2d').getImageData(0,0,256,256).data;
    let visible=0;
    for(let y=0;y<256;y++)for(let x=0;x<256;x++)if(a[(y*256+x)*4+3]){
     visible++;if(x<16||x>=240||y<16||y>=240)throw Error('Safe margin: '+SPR_KEYS[j]+'/'+m+'/'+i);
    }
    if(!visible)throw Error('Empty composite frame');count++;
   });
   if(sprFrameAt(j,m,0,100,false)!==0)throw Error('First frame');
   if(!SPR_LOOP[m]&&sprFrameAt(j,m,10000,100,false)!==list.length-1)throw Error('Final hold');
  }
  const r=SPR_META.rogue[1][2];
  if(!r.fx)throw Error('Rogue effect frame missing');
  closeModal();
  document.querySelector('#app').innerHTML='<div id="sprite-test" style="padding:40px;display:flex;flex-wrap:wrap;gap:35px">'+SPR_KEYS.map((job,i)=>'<div class="unit" style="width:150px"><div class="sprwrap">'+sprHTML(job,'attack',1,{flip:i%2===1,t0:performance.now(),p:-1})+'</div><div>'+job+'</div></div>').join('')+'</div>';
  return {jobs:SPR_KEYS.length,frames:count,atlas:[SPR_BASE.naturalWidth,SPR_BASE.naturalHeight]};
 });
 await page.waitForTimeout(160);
 await page.screenshot({path:path.join(__dirname,'shot_desktop.png'),fullPage:true});
 await page.setViewportSize({width:390,height:844});
 const mobile=await page.evaluate(()=>{
  const all=[...document.querySelectorAll('#sprite-test .spr')];
  return all.map((el,i)=>{
   const t=new DOMMatrix(getComputedStyle(el).transform),a=el.parentElement;
   if((i%2===1)!==(t.a<0))throw Error('Mobile flip');
   if(getComputedStyle(a).overflow!=='visible')throw Error('Anchor clipping');
   if(Math.abs(new DOMMatrix(getComputedStyle(a).transform).a-.48)>.001)throw Error('Mobile scale');
   return true;
  }).length;
 });
 await page.screenshot({path:path.join(__dirname,'shot_mobile.png'),fullPage:true});
 await page.evaluate(()=>{
  closeModal();
  const a=['priest','rogue','archer'].map(j=>newStudent(1,'B',j));
  const b=['darkpriest','ninja','forcemage'].map(j=>newStudent(1,'B',j));
  openBattle(runBattle(a,b,{}),{},()=>{});
 });
 await page.waitForTimeout(400);
 await page.screenshot({path:path.join(__dirname,'shot_battle_mobile.png'),fullPage:true});
 await page.setViewportSize({width:1280,height:900});
 await page.waitForTimeout(250);
 await page.screenshot({path:path.join(__dirname,'shot_battle_desktop.png'),fullPage:true});
 await page.goto(pathToFileURL(path.join(__dirname,'review.html')).href);
 await page.waitForFunction(()=>typeof SPR_READY!=='undefined'&&SPR_READY);
 await page.setViewportSize({width:1280,height:900});
 await page.locator('#frame').evaluate(el=>{el.value='3';el.dispatchEvent(new Event('input'))});
 await page.waitForTimeout(120);
 await page.screenshot({path:path.join(__dirname,'shot_review.png'),fullPage:true});
 if(errors.length)throw Error(errors.join('\n'));
 console.log(JSON.stringify({...result,mobileSprites:mobile,pageErrors:errors}));
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
