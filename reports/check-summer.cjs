const {chromium}=require('playwright'),assert=require('assert'),path=require('path');
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'msedge'}),page=await browser.newPage({viewport:{width:1280,height:900}}),errors=[];
 page.on('pageerror',e=>errors.push(e.message));
 await page.goto('http://127.0.0.1:18765/reports/preview.html?season=summer');
 await page.waitForFunction(()=>!document.querySelector('#restart').disabled);
 const f=page.frames().find(f=>f!==page.mainFrame());
 await f.waitForFunction(()=>document.querySelector('#drRoom').complete&&document.querySelector('#drRoom').naturalWidth);
 assert.equal(await f.locator('#drFacility').textContent(),'해수욕장');
 await f.locator('[data-dr-scene="1"]').click();
 assert.equal(await f.locator('#drFacility').textContent(),'해수욕장');
 await f.locator('[data-dr-day="0"]').click();
 await f.locator('#drStage').screenshot({path:path.join(__dirname,'shot_summer_training.png')});
 const trainingSize=await f.locator('#drStage').boundingBox();
 await page.locator('#sunbath').click();await page.waitForTimeout(120);
 assert.equal(await f.locator('#drFacility').textContent(),'해수욕장');
 assert(await f.evaluate(()=>[...document.querySelectorAll('#drStudents canvas')].every(c=>+c.dataset.m===SPR_M.down&&c.__f===sprN(SPR_KEYS[+c.dataset.j],SPR_M.down)-1)));
 await f.locator('#drStage').screenshot({path:path.join(__dirname,'shot_summer_rest.png')});
 assert.equal((await f.locator('#drStage').boundingBox()).height,trainingSize.height);
 const result=await f.evaluate(()=>{
   closeModal();S.phase='summer';S.students.forEach((s,i)=>{s.cond=100;s.injured=0;s.focus=i===0?'rest':i%2?'genius':'team';});
   const snap=snapStudents();UI.wrun={startPhase:'summer',scenes:[]};DAYLOG=[];dayRun(TR.spar,0,0);
   const raw=UI.wrun.scenes;UI.wrun=null;const before=JSON.stringify(raw),state=JSON.stringify(S);
   const selected=reportScenesForPlayback(raw);
   if(selected.length!==2 || selected.some(s=>s.facility!=='beach'))throw Error('Summer morning/focus grouping');
   if(selected[0].students.length!==S.students.length||!selected[0].students.some(s=>s.state==='rest'))throw Error('Missing partial rest');
   for(const phase of ['am','pm']){
    const ids=raw.filter(s=>s.phase===phase).flatMap(s=>s.students.map(x=>x.id)).sort();
    if(JSON.stringify(ids)!==JSON.stringify(selected.find(s=>s.phase===phase).students.map(x=>x.id).sort()))throw Error('Dropped student');
   }
   S.phase='fall';if(reportScenesForPlayback(raw).some(s=>s.facility!=='beach'))throw Error('Season boundary');S.phase='summer';
   const normal=reportScenesForPlayback(raw.map(s=>({...s,season:'spring'})));if(normal.some(s=>s.facility==='beach'))throw Error('Spring beach leak');
   const expedition={...raw[0],phase:'exped',facility:'arena',reward:'원정 귀환'};
   if(reportScenesForPlayback([expedition])[0].facility!=='arena')throw Error('Expedition changed');
   showReport({snap,startWeek:0,ranTo:1,startPhase:'summer',startYear:1,acts:[{n:'대련'}],scenes:raw,daylog:DAYLOG,gold:0,fame:0,relics:0});
   if(!UI._reportPlayer.paused)document.querySelector('#drPlay').click();
   if(document.querySelectorAll('.resting').length!==1)throw Error('Partial sunbathing pose');
   if(JSON.stringify(raw)!==before||JSON.stringify(S)!==state)throw Error('Presentation mutated results');
   return {rawScenes:raw.length,displayScenes:selected.length,partialRest:true,seasonBoundary:true};
 });
 await page.setViewportSize({width:390,height:844});
 await page.screenshot({path:path.join(__dirname,'shot_summer_mobile.png')});
 assert(await f.evaluate(()=>document.querySelector('.modal').scrollWidth<=document.querySelector('.modal').clientWidth+2));
 assert.deepEqual(errors,[]);console.log(JSON.stringify({...result,errors}));await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
