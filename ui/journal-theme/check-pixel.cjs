const {chromium}=require('playwright');const assert=require('assert');
(async()=>{
 const b=await chromium.launch({channel:'msedge',headless:true});
 for(const width of [1440,390]){
  const p=await b.newPage({viewport:{width,height:1000}}),errors=[];
  p.on('pageerror',e=>errors.push(e.message));
  await p.goto('file:///D:/heroschool/heroschool.html');
  await p.waitForFunction(()=>typeof PREF!=='undefined'&&typeof newGame==='function');
  await p.evaluate(()=>{newGame('테마 확인 학원');bootLoaderDone();closeModal();document.querySelector('#titleScreen')?.remove();UI.view='opt';render();});
  const picker=p.locator('[data-ui-concept-choice="journal-pixel"]');
  await picker.click();
  assert.equal(await p.evaluate(()=>document.documentElement.dataset.uiConcept),'journal');
  assert.equal(await p.evaluate(()=>JSON.parse(localStorage.getItem(PREF_KEY)).uiConcept),'journal-pixel');
  await p.screenshot({path:`D:/heroschool/ui/journal-theme/pixel-settings-${width}.png`,fullPage:true});
  for(const view of ['home','roster','plan','facil']){
   await p.evaluate(v=>{UI.view=v;render();},view);
   const overflow=await p.evaluate(()=>document.documentElement.scrollWidth>innerWidth+2);
   assert(!overflow,`${width} ${view} horizontal overflow`);
   await p.screenshot({path:`D:/heroschool/ui/journal-theme/pixel-${view}-${width}.png`,fullPage:true});
  }
  await p.reload();await p.waitForFunction(()=>typeof PREF!=='undefined');
  assert.equal(await p.evaluate(()=>document.documentElement.dataset.uiConcept),'journal');
  await p.evaluate(()=>{UI.view='opt';if(!S)newGame('테마 확인');render();});
  await p.locator('[data-ui-concept-choice="default"]').evaluate(el=>el.click());
  assert.equal(await p.evaluate(()=>document.documentElement.dataset.uiConcept),'default');
  assert.deepEqual(errors,[]);await p.close();
 }
 await b.close();console.log('Desktop/mobile theme switch, persistence, reset and overflow checks passed');
})().catch(e=>{console.error(e);process.exit(1)});
