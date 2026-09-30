const {chromium}=require('playwright');const assert=require('node:assert/strict');
(async()=>{const browser=await chromium.launch({channel:'msedge',headless:true});
for(const file of ['heroschool.html','site/index.html']){
 const page=await browser.newPage({viewport:{width:1400,height:900}}),errors=[];page.on('pageerror',e=>{errors.push(e.message);console.error(e.message)});
 await page.route('**/*',r=>/^https?:/.test(r.request().url())?r.abort():r.continue());
 await page.goto('file:///D:/heroschool/'+file);await page.waitForFunction(()=>SPR_READY);await page.locator('#bootLoader').waitFor({state:'hidden'});
 await page.evaluate(()=>{
  newGame('거너 검증');closeModal();
  let found=false;
  for(let n=0;n<20&&!found;n++){
   const team=()=>['gunner','paladin','priest'].map(j=>newStudent(1,'B',j));
   const r=runBattle(team(),team(),{});
   for(const f of r.frames.filter(f=>f.fx?.skillId==='gn_1')){
    if(!Array.isArray(f.fx.shots)||f.fx.shots.length>4||!f.fx.shots.length)throw Error('invalid engine shot record');
    if(!f.fx.shots.every(id=>f.fx.t.includes(id)))throw Error('missing retarget');found=true;
   }
  }if(!found)throw Error('no engine volley exercised');
 });
 for(const [skill,side,job,cancel] of [['gn_b','A','gunner'],['gn_1','A','gunner'],['gn_2','A','gunner'],['gn_u','A','gunner'],['gn_u','B','gunner',true],['gn_u','A','paladin']]){
  await page.evaluate(({skill,side,job})=>{
   closeModal();PREF.battleCam='stylish';
   const team=()=>[job,'paladin','priest'].map(j=>newStudent(1,'B',j));
   const res=runBattle(team(),team(),{}),own=side==='A'?res.A:res.B,foes=side==='A'?res.B:res.A;
   const initial=JSON.parse(JSON.stringify(res.frames[0])),call=JSON.parse(JSON.stringify(initial));
   const sk=JOBS.gunner.skills.find(s=>s.id===skill),targets=skill==='gn_u'?foes:skill==='gn_1'?foes.slice(0,2):[foes[0]];
   call.cls='';call.actor=own[0].uid;call.call={name:sk.name,kind:sk.kind,pers:'plain'};
   call.fx={skillId:skill,n:sk.fx,e:sk.el,t:targets.map(u=>u.uid)};
   if(skill==='gn_1')call.fx.shots=[foes[0].uid,foes[0].uid,foes[1].uid,foes[1].uid];
   call.units.forEach(u=>u.atb=1);
   const end=JSON.parse(JSON.stringify(call));delete end.call;delete end.fx;
   end.pop=(call.fx.shots||call.fx.t).map(u=>({u,k:'dmg',v:80}));res.frames=[initial,call,end];
   openBattle(res,{field:'dummy',titleA:'거너',titleB:'스킬 대상'},()=>{});
   window.shotsSeen=[];window.watchShots=()=>{
    const visible=[...document.querySelectorAll('[data-shot]')].filter(i=>getComputedStyle(i).visibility==='visible');
    for(const i of visible)if(!shotsSeen.includes(+i.dataset.shot))shotsSeen.push(+i.dataset.shot);
    if(document.querySelector('.bf-stage'))window.shotsWatch=requestAnimationFrame(watchShots);
   };watchShots();
  },{skill,side,job});
  await page.waitForSelector('.stylish-skill-fx img');await page.waitForTimeout(70);
  const r=await page.evaluate(()=>({filter:document.querySelector('.bf-stage').style.filter,fx:[...document.querySelectorAll('.stylish-skill-fx img,.stylish-group-fx img')].map(i=>({kind:i.dataset.effect,behind:i.parentElement.className,loaded:i.complete&&i.naturalWidth>0}))}));
  assert(r.fx.every(i=>i.loaded));assert.equal(r.fx.filter(i=>i.kind==='gunMuzzle').length,job==='gunner'?1:0);
  assert.equal(r.fx.filter(i=>i.kind==='gunHit').length,skill==='gn_1'?4:skill==='gn_b'?1:0);
  assert.equal(r.filter.includes('grayscale(1)'),skill==='gn_u');
  assert(r.fx.filter(i=>i.kind==='gunPierce').every(i=>i.behind==='stylish-group-fx'));
  if(file==='heroschool.html')await page.screenshot({path:`D:/heroschool/assets/skill-fx/gunner/skill-${skill}-${side}-${job}.png`});
  if(cancel)await page.locator('#bPlay').click();
  await page.waitForSelector('.stylish-skill-fx',{state:'detached'});
  if(skill==='gn_1')assert.deepEqual(await page.evaluate(()=>shotsSeen),[0,1,2,3]);
  assert.equal(await page.evaluate(()=>document.querySelector('.bf-stage').style.filter),'');
  await page.evaluate(()=>cancelAnimationFrame(window.shotsWatch));await page.waitForTimeout(650);console.log(file,skill,side,job,'PASS');
 }
 assert.deepEqual(errors,[]);await page.close();
}await browser.close();})().catch(e=>{console.error(e);process.exit(1)});
