const {chromium}=require('playwright');
const {pathToFileURL}=require('url');
const path=require('path'),assert=require('assert');
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'msedge'});
 const page=await browser.newPage({viewport:{width:1280,height:1100}}),errors=[];
 page.on('pageerror',e=>errors.push(e.message));
 await page.goto(pathToFileURL(path.resolve(__dirname,'../heroschool.html')).href);
 await page.waitForFunction(()=>typeof SPR_READY!=='undefined'&&SPR_READY);
 const data=await page.evaluate(()=>{
   newGame('새봄 용사 학원');closeModal();UI.ceremonies=[];UI.pendingTour=null;
   S.students=['ninja','druid','paladin','bard','wizard','priest'].map((j,i)=>{
    const s=newStudent(1,'B',j);s.name=['라비','포레나','요엘','세레나','아르젠','에스텔'][i];s.focus=i===5?'rest':i%2?'team':'genius';s.cond=90;return s;
   });
   S.students[4].injured=1; // guarantees one failed morning without changing the RNG.
   const snap=snapStudents();RUN={expeds:[]};DAYLOG=[];UI.wrun={scenes:[]};
   ['tact','basic','form','medit','rest'].forEach((id,i)=>{dayRun(TR[id],i===1?.25:0,i);dlog('','gap');});
   const scenes=UI.wrun.scenes;UI.wrun=null;
   if(scenes.length<5)throw Error('Missing scenes');
   if(!scenes.some(s=>s.students.some(x=>x.state==='failed')))throw Error('Missing failure');
   if(scenes.filter(s=>s.phase==='pm').some(s=>s.students.some(x=>FOCUS_FAC[x.focus]!==s.facility)))throw Error('Wrong focus facility');
   const playback=reportScenesForPlayback(scenes);
   for(let day=0;day<5;day++){
    const selected=playback.filter(s=>s.day===day);
    if(selected.filter(s=>s.phase==='am').length!==1||selected.filter(s=>s.phase==='pm').length!==Number(scenes.some(s=>s.day===day&&s.phase==='pm')))throw Error('Unexpected facility count per phase');
   }
   if(playback[0].facility!=='library')throw Error('Partial rest replaced morning training');
   for(const st of S.students){
    const got=scenes.flatMap(s=>s.students).filter(s=>s.id===st.id).flatMap(s=>s.changes).filter(c=>c.label==='컨디션').reduce((n,c)=>n+c.value,0);
    if(Math.abs(got-(st.cond-snap.find(x=>x.id===st.id).cond))>.3)throw Error('Condition drift');
   }
   window.testReport={snap,startWeek:0,ranTo:1,startPhase:'spring',startYear:1,acts:['tact','basic','form','medit','rest'].map(id=>({n:TR[id].n})),scenes,daylog:DAYLOG.slice(),gold:0,fame:0,relics:0};
   window.testState=JSON.stringify(S);showReport(testReport);
   return {scenes:scenes.length,facilities:[...new Set(scenes.map(s=>s.facility))]};
 });
 await page.locator('#drPlay').click();
 await page.waitForFunction(()=>document.querySelector('#drRoom').complete&&document.querySelector('#drRoom').naturalWidth>0);
 await page.locator('.dr-stage').screenshot({path:path.join(__dirname,'shot_room.png')});
 await page.evaluate(()=>document.querySelector('.modal').scrollTop=0);
 await page.screenshot({path:path.join(__dirname,'shot_report_desktop.png'),fullPage:true});
 const rect=await page.locator('#drStage').boundingBox();assert(Math.abs(rect.width/rect.height-3)<.03);
 assert(await page.evaluate(()=>CSS.supports('transform','scale(calc(100cqw / 800px))')),'Sprite responsive scale unsupported');
 await page.locator('[data-dr-day="1"]').click();
 assert((await page.locator('#drChain').textContent()).includes('25%'));
 const first=await page.evaluate(()=>UI._reportPlayer.index);
 await page.waitForTimeout(300);assert.equal(await page.evaluate(()=>UI._reportPlayer.index),first);
 await page.locator('[data-dr-speed="6"]').click();await page.locator('#drPlay').click();
 await page.waitForFunction(first=>UI._reportPlayer.index>first,first,{timeout:20000});
 await page.locator('#drPlay').click();await page.locator('[data-dr-day="4"]').click();
 assert.equal(await page.locator('#drFacility').textContent(),'의무실');
 assert.equal(await page.locator('.dr-student').count(),3,'Infirmary bed capacity');
 await page.waitForTimeout(100);
 assert(await page.evaluate(()=>[...document.querySelectorAll('#drStudents canvas')].every(c=>+c.dataset.m===SPR_M.down && c.__f===sprN(SPR_KEYS[+c.dataset.j],SPR_M.down)-1)),'Infirmary must keep lying frame when paused');
 await page.locator('[data-dr-student="0"]').click();assert(await page.locator('#drDetail').getAttribute('open')!==null);
 await page.locator('#dlSkip').click();assert(await page.locator('#drFullLog').isVisible());
 assert(await page.evaluate(()=>testState===JSON.stringify(S)),'Playback mutated game state');
 await page.evaluate(()=>{closeModal();if(UI._reportPlayer)throw Error('Leaked player');showReport(testReport);document.querySelector('#drPlay').click();});
 await page.setViewportSize({width:390,height:844});
 await page.screenshot({path:path.join(__dirname,'shot_report_mobile.png'),fullPage:true});
 assert(await page.evaluate(()=>document.querySelector('.modal').scrollWidth<=document.querySelector('.modal').clientWidth+2),'Mobile overflow');
 await page.setViewportSize({width:1280,height:900});
 const crops=[];
 for(const facility of ['library','gym','arena','hall','chapel','infirm']){
  await page.evaluate(facility=>{
   const scene=JSON.parse(JSON.stringify(testReport.scenes.find(s=>s.facility===facility)));
   // Fill every station to inspect the maximum density, including all three beds.
   const source=testReport.scenes.flatMap(s=>s.students), unique=[...new Map(source.map(s=>[s.id,s])).values()];
   scene.students=JSON.parse(JSON.stringify(unique.slice(0,REPORT_LAYOUTS[facility].slots.length)));
   if(facility==='infirm')scene.students.forEach(s=>{s.state='rest';s.changes=[{label:'컨디션',value:4,kind:'heal'}];});
   showReport({...testReport,scenes:[scene]});if(!UI._reportPlayer.paused)document.querySelector('#drPlay').click();
  },facility);
  await page.waitForFunction(()=>document.querySelector('#drRoom').complete&&document.querySelector('#drRoom').naturalWidth);
  await page.waitForTimeout(100);
  crops.push(await page.locator('#drStage').boundingBox());
  await page.locator('#drStage').screenshot({path:path.join(__dirname,`shot_crop_${facility}.png`)});
 }
 assert(crops.every(r=>r.width===crops[0].width && r.height===crops[0].height),'Facility crop dimensions differ');
 await page.evaluate(()=>{
   closeModal();UI.wrun={scenes:[]};const member=S.students[0];
   reportRecord(0,TR.exped,0,'exped',{},[member],{},0,{facility:'arena',reward:'원정 · 3/3구간 · 유물 1개'});
   const scenes=UI.wrun.scenes;if(scenes[0].students[0].changes.length)throw Error('Invented expedition growth');
   UI.wrun=null;showReport({...testReport,scenes});closeModal();
   showReport({...testReport,scenes:[]});if(!document.querySelector('.daylog'))throw Error('Legacy log unavailable');closeModal();
   newGame('주간 진행 검수');S.master.pts=0;UI.skipRestWarn=true;UI.ceremonies=[];UI.pendingTour=null;
   S.students.forEach(s=>{s.focus='genius';s.cond=100;});
   S.slots=['tact','tact','basic','medit','rest'].map(t=>({t}));
   weekRunGo(false);
   if(S.week!==1||!document.querySelector('#drStage'))throw Error('Weekly runner did not open scene report');
   if(UI.wrun)throw Error('Weekly runner not completed');closeModal();
 });
 assert.deepEqual(errors,[]);console.log(JSON.stringify({...data,checks:'actual deltas, focus facilities, failures, seek, pause, speed, rest, details, full log, read-only playback, cleanup, mobile, expedition, legacy report',errors}));
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
