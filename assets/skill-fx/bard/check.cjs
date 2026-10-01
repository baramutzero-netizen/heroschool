const {chromium}=require('playwright');const assert=require('node:assert/strict');
(async()=>{const browser=await chromium.launch({channel:'msedge',headless:true});
for(const file of ['heroschool.html','site/index.html']){
 const page=await browser.newPage({viewport:{width:1400,height:900}}),errors=[];page.on('pageerror',e=>{errors.push(e.message);console.error(e.message)});
 await page.route('**/*',r=>/^https?:/.test(r.request().url())?r.abort():r.continue());
 await page.goto('file:///D:/heroschool/'+file);await page.waitForFunction(()=>SPR_READY);await page.locator('#bootLoader').waitFor({state:'hidden'});
 for(const [skill,side,job,cancel] of [['bd_b','A','bard'],['bd_1','A','bard'],['bd_2','A','bard'],['bd_u','A','bard'],['bd_u','B','bard',true],['bd_u','A','paladin']]){
  await page.evaluate(({skill,side,job})=>{
   closeModal();PREF.battleCam='stylish';
   const team=()=>[job,'paladin','priest'].map(j=>newStudent(1,'B',j));
   const res=runBattle(team(),team(),{}),own=side==='A'?res.A:res.B,foes=side==='A'?res.B:res.A;
   const initial=JSON.parse(JSON.stringify(res.frames[0])),call=JSON.parse(JSON.stringify(initial));
   const sk=JOBS.bard.skills.find(s=>s.id===skill),targets=skill==='bd_b'?[foes[0]]:skill==='bd_2'?foes:own;
   call.cls='';call.actor=own[0].uid;call.call={name:sk.name,kind:sk.kind,pers:'plain'};
   call.fx={skillId:skill,n:sk.fx,e:sk.el,t:targets.map(u=>u.uid)};
   
   call.units.forEach(u=>u.atb=1);
   const end=JSON.parse(JSON.stringify(call));delete end.call;delete end.fx;
   end.pop=[];res.frames=[initial,call,end];
   openBattle(res,{field:'dummy',titleA:'바드',titleB:'스킬 대상'},()=>{});
   window.shotsSeen=[];window.watchShots=()=>{
    const visible=[...document.querySelectorAll('[data-shot]')].filter(i=>getComputedStyle(i).visibility==='visible');
    for(const i of visible)if(!shotsSeen.includes(+i.dataset.shot))shotsSeen.push(+i.dataset.shot);
    if(document.querySelector('.bf-stage'))window.shotsWatch=requestAnimationFrame(watchShots);
   };watchShots();
  },{skill,side,job});
  await page.waitForSelector('.stylish-skill-fx img');await page.waitForTimeout(70);
  const r=await page.evaluate(()=>({filter:document.querySelector('.bf-stage').style.filter,fx:[...document.querySelectorAll('.stylish-skill-fx img,.stylish-group-fx img')].map(i=>({kind:i.dataset.effect,behind:i.parentElement.className,loaded:i.complete&&i.naturalWidth>0}))}));
  assert(r.fx.every(i=>i.loaded));
  if(skill==='bd_1')assert.equal(r.fx.filter(i=>i.kind==='shadowStep').length,3);
  if(skill==='bd_2')assert.equal(r.fx.filter(i=>i.kind==='dissonance').length,3);
  if(skill==='bd_u'){
   assert.equal(r.fx.filter(i=>i.kind==='spotlight').length,3);
   assert(r.fx.filter(i=>i.kind==='ensemble').length>=1);
   const ratios=await page.locator('[data-effect="ensemble"]').evaluateAll(images=>images.map(i=>({display:parseFloat(i.style.width)/parseFloat(i.style.height),original:i.naturalWidth/i.naturalHeight})));
   assert(ratios.every(r=>Math.abs(r.display-r.original)<.001),'musical notes must preserve aspect ratio');
   assert.equal(r.fx.find(i=>i.kind==='ensemble').behind,'stylish-skill-fx');
  }
  if(job==='bard')assert(r.fx.some(i=>i.kind==='bardMelody'));
  assert.equal(r.filter.includes('invert(1)'),false);
  if(job==='paladin')assert(r.fx.some(i=>i.kind==='trail'));
  if(file==='heroschool.html')await page.screenshot({path:`D:/heroschool/assets/skill-fx/bard/skill-${skill}-${side}-${job}.png`});
  if(cancel)await page.locator('#bPlay').click();
  await page.waitForSelector('.stylish-skill-fx',{state:'detached'});
  
  assert.equal(await page.evaluate(()=>document.querySelector('.bf-stage').style.filter),'');
  await page.evaluate(()=>cancelAnimationFrame(window.shotsWatch));await page.waitForTimeout(650);console.log(file,skill,side,job,'PASS');
 }
 assert.deepEqual(errors,[]);await page.close();
}await browser.close();})().catch(e=>{console.error(e);process.exit(1)});
