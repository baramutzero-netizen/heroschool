const {chromium}=require('playwright');
const fs=require('fs');
const root='D:/heroschool';
(async()=>{
 const browser=await chromium.launch({channel:'msedge',headless:true});
 for(const file of ['heroschool.html','site/index.html']){
  const page=await browser.newPage({viewport:{width:390,height:844},deviceScaleFactor:2});
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  // No online registrations or chat traffic during isolated UI checks.
  await page.route('**/*',route=>/^https?:/.test(route.request().url())?route.abort():route.continue());
  await page.goto('file:///'+root+'/'+file);
  await page.locator('#bootLoader').waitFor({state:'hidden'});
  await page.evaluate(()=>{newGame('안내 검증');closeModal();UI.ceremonies=[];});
  for(const theme of ['default','journal'])for(const width of [320,390,1200]){
   await page.setViewportSize({width,height:844});
   await page.evaluate(t=>document.documentElement.dataset.uiConcept=t,theme);
   for(let k=1;k<=12;k++){
    await page.evaluate(k=>tutOnePage(String(k)),k);
    const result=await page.locator('.tg-guide').evaluate(el=>({overflow:el.scrollWidth>el.clientWidth+1,font:parseFloat(getComputedStyle(el.querySelector('.tg-step p')).fontSize),old:!!document.querySelector('.tutwrap'),title:el.querySelector('h2').textContent}));
    if(result.overflow)await page.screenshot({path:root+'/ui/tutorial/overflow.png'});if(result.overflow||result.font<16||result.old)throw Error(JSON.stringify({file,theme,width,k,result}));
    const button=page.locator('#tutOk');await button.scrollIntoViewIfNeeded();
    if((await button.boundingBox()).height<44)throw Error('small touch target');
    if(file==='heroschool.html'&&width===390&&[1,2,10,12].includes(k))await page.screenshot({path:`${root}/ui/tutorial/check-${theme}-${k}.png`});
    await button.click();
   }
  }
  await page.evaluate(()=>{window.__tutDone=0;showTutorial(0,{start:true,after:()=>window.__tutDone++});});
  for(let i=0;i<3;i++)await page.locator('#tutNext').click();
  if(await page.evaluate(()=>window.__tutDone)!==1)throw Error('intro callback');
  await page.evaluate(()=>{showModal('<p id="under-tutorial">기존 팝업</p>');tutOverPage('12',()=>window.__tutDone++);});
  await page.locator('[data-tutok]').click();
  if(!await page.locator('#under-tutorial').isVisible()||await page.evaluate(()=>window.__tutDone)!==2)throw Error('overlay callback');
  await page.evaluate(()=>{closeModal();showTutorial(0);});
  const keys=await page.evaluate(()=>tutPages());if(keys.length!==12)throw Error('replay keys');
  await page.locator('#tutNext').click();await page.locator('#tutPrev').click();
  if(await page.locator('.tg-guide').getAttribute('data-guide')!=='1')throw Error('navigation');
  if(file==='heroschool.html'){
   await page.setViewportSize({width:390,height:844});
   await page.evaluate(()=>{closeModal();document.documentElement.dataset.uiConcept='journal';document.body.insertAdjacentHTML('beforeend','<main id="tutorialExport"></main>');for(const e of document.body.children)if(e.id!=='tutorialExport')e.style.display='none';document.body.style.cssText='margin:0;padding:0;background:#ede1c6';});
   fs.mkdirSync(root+'/assets/tutorial-v2',{recursive:true});
   const titles=[];
   for(let k=1;k<=12;k++){
    await page.evaluate(k=>{document.querySelector('#tutorialExport').innerHTML=tutGuideHTML(k);},k);
    await page.waitForFunction(()=>[...document.querySelectorAll('#tutorialExport img')].every(im=>im.complete&&im.naturalWidth>0));
    titles.push(await page.locator('.tg-guide h2').textContent());
    await page.locator('.tg-guide').screenshot({path:`${root}/assets/tutorial-v2/${String(k).padStart(2,'0')}.png`});
   }
   fs.writeFileSync(root+'/assets/tutorial-v2/titles.json',JSON.stringify(titles,null,2));
  }
  if(errors.length)throw Error(errors.join('\n'));
  console.log(file,': 12 topics × 3 widths × 2 themes; intro/replay/overlay callbacks OK');
  await page.close();
 }
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});

