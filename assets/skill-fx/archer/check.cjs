const {chromium}=require('playwright');const assert=require('node:assert/strict');
(async()=>{const browser=await chromium.launch({channel:'msedge',headless:true});
for(const file of ['heroschool.html','site/index.html']){
 const page=await browser.newPage({viewport:{width:1400,height:900}}),errors=[];page.on('pageerror',e=>{errors.push(e.message);console.error(e.message)});
 await page.route('**/*',r=>/^https?:/.test(r.request().url())?r.abort():r.continue());
 await page.goto('file:///D:/heroschool/'+file);await page.waitForFunction(()=>SPR_READY);await page.locator('#bootLoader').waitFor({state:'hidden'});
 for(const [skill,side,job,cancel] of [['ar_b','A','archer'],['ar_1','A','archer'],['ar_2','A','archer'],['ar_u','A','archer'],['ar_1','B','archer'],['ar_u','B','archer',true],['ar_u','A','paladin']]){
  await page.evaluate(({skill,side,job})=>{
   closeModal();PREF.battleCam='stylish';
   const team=()=>[job,'paladin','priest'].map(j=>newStudent(1,'B',j));
   const res=runBattle(team(),team(),{}),own=side==='A'?res.A:res.B,foes=side==='A'?res.B:res.A;
   const initial=JSON.parse(JSON.stringify(res.frames[0])),call=JSON.parse(JSON.stringify(initial));
   const sk=JOBS.archer.skills.find(s=>s.id===skill),targets=skill==='ar_2'?[own[0]]:skill==='ar_1'?foes:[foes[0]];
   call.cls='';call.actor=own[0].uid;call.call={name:sk.name,kind:sk.kind,pers:'plain'};
   call.fx={skillId:skill,n:sk.fx,e:sk.el,t:targets.map(u=>u.uid)};
   
   call.units.forEach(u=>u.atb=1);
   const end=JSON.parse(JSON.stringify(call));delete end.call;delete end.fx;
   end.pop=[];res.frames=[initial,call,end];
   openBattle(res,{field:'dummy',titleA:'아처',titleB:'스킬 대상'},()=>{});
   window.shotsSeen=[];window.watchShots=()=>{
    const visible=[...document.querySelectorAll('[data-shot]')].filter(i=>getComputedStyle(i).visibility==='visible');
    for(const i of visible)if(!shotsSeen.includes(+i.dataset.shot))shotsSeen.push(+i.dataset.shot);
    if(document.querySelector('.bf-stage'))window.shotsWatch=requestAnimationFrame(watchShots);
   };watchShots();
  },{skill,side,job});
  await page.waitForSelector('.stylish-skill-fx img');await page.waitForTimeout(70);
  const r=await page.evaluate(()=>({filter:document.querySelector('.bf-stage').style.filter,fx:[...document.querySelectorAll('.stylish-skill-fx img,.stylish-group-fx img')].map(i=>({kind:i.dataset.effect,behind:i.parentElement.className,loaded:i.complete&&i.naturalWidth>0}))}));
  assert(r.fx.every(i=>i.loaded));
  if(skill==='ar_1'){
   assert.equal(r.fx.filter(i=>i.kind==='greenPierce').length,1);
   const tip=await page.locator('[data-effect="greenPierce"]').evaluate((i,side)=>{
    const beam=i.getBoundingClientRect(),stage=document.querySelector('.bf-stage').getBoundingClientRect();
    return side==='B'?beam.right-beam.width*.75<stage.left:beam.left+beam.width*.75>stage.right;
   },side);
   assert(tip,'the entire arrowhead must stay outside the stage');
  }
  if(skill==='ar_2')assert.equal(r.fx.filter(i=>i.kind==='hawkEye').length,1);
  if(skill==='ar_u'){
   assert.equal(r.fx.filter(i=>i.kind==='meteorRain').length,1);
   assert.equal(await page.locator('.bf-unit.cam-in').count(),2);
   assert(await page.locator('[data-effect="meteorRain"]').evaluate(i=>!!i.dataset.target && !i.dataset.targets));
   const distance=await page.locator('[data-effect="meteorRain"]').evaluate(i=>i.getBoundingClientRect().top-document.querySelector('.cam-fx .cb.t').getBoundingClientRect().bottom);
   assert(distance<=0 && distance>-8,'rain must extend above upper boundary');
   const geometry=await page.locator('[data-effect="meteorRain"]').evaluate(i=>({bottom:i.getBoundingClientRect().bottom,boundary:document.querySelector('.cam-fx .cb.b').getBoundingClientRect().top,transform:i.style.transform}));
   assert(geometry.bottom>=geometry.boundary);
   assert.equal(geometry.transform,side==='B'?'scaleX(-1)':'');
   assert(await page.locator('.stylish-group-fx [data-effect="meteorRain"]').count());
   assert(await page.locator('.stylish-skill-fx [data-effect="meteorFront"]').count());
   assert(await page.locator('.stylish-skill-fx [data-effect="meteorImpact"]').count());
   assert(await page.locator('.stylish-group-fx [data-effect="meteorShade"]').count());
  }
  if(job==='archer')assert(r.fx.some(i=>i.kind==='archerWind'));
  assert.equal(r.filter.includes('invert(1)'),false);
  if(job==='paladin')assert(r.fx.some(i=>i.kind==='trail'));
  if(file==='heroschool.html')await page.screenshot({path:`D:/heroschool/assets/skill-fx/archer/skill-${skill}-${side}-${job}.png`});
  if(cancel)await page.locator('#bPlay').click();
  await page.waitForSelector('.stylish-skill-fx',{state:'detached'});
  assert.equal(await page.locator('[data-effect="meteorShade"]').count(),0);
  
  assert.equal(await page.evaluate(()=>document.querySelector('.bf-stage').style.filter),'');
  await page.evaluate(()=>cancelAnimationFrame(window.shotsWatch));await page.waitForTimeout(650);console.log(file,skill,side,job,'PASS');
 }
 assert.deepEqual(errors,[]);await page.close();
}await browser.close();})().catch(e=>{console.error(e);process.exit(1)});
