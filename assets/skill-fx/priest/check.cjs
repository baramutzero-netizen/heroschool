const {chromium}=require('playwright');const assert=require('node:assert/strict');
(async()=>{const browser=await chromium.launch({channel:'msedge',headless:true});
for(const file of ['heroschool.html','site/index.html']){
 const page=await browser.newPage({viewport:{width:1400,height:900}}),errors=[];page.on('pageerror',e=>{errors.push(e.message);console.error(e.message)});
 await page.route('**/*',r=>/^https?:/.test(r.request().url())?r.abort():r.continue());
 await page.goto('file:///D:/heroschool/'+file);await page.waitForFunction(()=>SPR_READY);await page.locator('#bootLoader').waitFor({state:'hidden'});
 for(const [skill,side,job,cancel] of [['pr_b','A','priest'],['pr_1','A','priest'],['pr_2','A','priest'],['pr_u','A','priest'],['pr_u','B','priest',true],['pr_u','A','paladin']]){
  await page.evaluate(({skill,side,job})=>{
   closeModal();PREF.battleCam='stylish';
   const team=()=>[job,'paladin','priest'].map(j=>newStudent(1,'B',j));
   const res=runBattle(team(),team(),{}),own=side==='A'?res.A:res.B,foes=side==='A'?res.B:res.A;
   const initial=JSON.parse(JSON.stringify(res.frames[0])),call=JSON.parse(JSON.stringify(initial));
   const sk=JOBS.priest.skills.find(s=>s.id===skill),targets=skill==='pr_b'?[foes[0]]:skill==='pr_1'?[own[1]]:own;
   call.cls='';call.actor=own[0].uid;call.call={name:sk.name,kind:sk.kind,pers:'plain'};
   call.fx={skillId:skill,n:sk.fx,e:sk.el,t:targets.map(u=>u.uid)};
   
   call.units.forEach(u=>u.atb=1);
   if(skill==='pr_u'){
    window.revivedUid=own[1].uid;
    const k=[...res.A,...res.B].findIndex(u=>u.uid===own[1].uid);
    initial.units[k].alive=false;initial.units[k].hp=0;
    call.units[k].alive=false;call.units[k].hp=0;
   }
   const end=JSON.parse(JSON.stringify(call));
   if(skill==='pr_u'){
    const k=[...res.A,...res.B].findIndex(u=>u.uid===own[1].uid);
    end.units[k].alive=true;end.units[k].hp=80;
   }delete end.call;delete end.fx;
   end.pop=(call.fx.shots||call.fx.t).map(u=>({u,k:skill==='pr_b'?'dmg':'heal',v:80}));res.frames=[initial,call,end];
   openBattle(res,{field:'dummy',titleA:'프리스트',titleB:'스킬 대상'},()=>{});
   window.shotsSeen=[];window.watchShots=()=>{
    const visible=[...document.querySelectorAll('[data-shot]')].filter(i=>getComputedStyle(i).visibility==='visible');
    for(const i of visible)if(!shotsSeen.includes(+i.dataset.shot))shotsSeen.push(+i.dataset.shot);
    if(document.querySelector('.bf-stage'))window.shotsWatch=requestAnimationFrame(watchShots);
   };watchShots();
  },{skill,side,job});
  await page.waitForSelector('.stylish-skill-fx img');await page.waitForTimeout(70);
  const r=await page.evaluate(()=>({filter:document.querySelector('.bf-stage').style.filter,fx:[...document.querySelectorAll('.stylish-skill-fx img,.stylish-group-fx img')].map(i=>({kind:i.dataset.effect,behind:i.parentElement.className,loaded:i.complete&&i.naturalWidth>0}))}));
  assert(r.fx.every(i=>i.loaded));
  if(skill==='pr_u') assert.equal(await page.evaluate(()=>document.querySelector(`.bf-unit[data-uid="${window.revivedUid}"]`).classList.contains('dead')),false);
  assert.equal(r.fx.filter(i=>['impact','greaterHeal','blessing','revival'].includes(i.kind)).length,['pr_2','pr_u'].includes(skill)?3:1);
  assert.equal(r.filter.includes('invert(1)'),false);
  if(job==='priest')assert(r.fx.some(i=>i.kind==='holyEssence'));
  if(job==='paladin')assert(r.fx.some(i=>i.kind==='trail'));
  if(file==='heroschool.html')await page.screenshot({path:`D:/heroschool/assets/skill-fx/priest/skill-${skill}-${side}-${job}.png`});
  if(cancel)await page.locator('#bPlay').click();
  await page.waitForSelector('.stylish-skill-fx',{state:'detached'});
  
  assert.equal(await page.evaluate(()=>document.querySelector('.bf-stage').style.filter),'');
  await page.evaluate(()=>cancelAnimationFrame(window.shotsWatch));await page.waitForTimeout(650);console.log(file,skill,side,job,'PASS');
 }
 assert.deepEqual(errors,[]);await page.close();
}await browser.close();})().catch(e=>{console.error(e);process.exit(1)});
