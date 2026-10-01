const {chromium}=require('playwright');
const assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({channel:'msedge',headless:true});
 for(const file of ['heroschool.html','site/index.html']){
  const page=await browser.newPage({viewport:{width:1400,height:900}}),errors=[];
  page.on('pageerror',e=>errors.push(e.message));
  await page.route('**/*',r=>/^https?:/.test(r.request().url())?r.abort():r.continue());
  await page.goto('file:///D:/heroschool/'+file);
  await page.waitForFunction(()=>SPR_READY);await page.locator('#bootLoader').waitFor({state:'hidden'});
  assert.equal(await page.evaluate(()=>JOBS.wizard.skills.find(s=>s.id==='wz_u').name),'중력 반전');
  for(const [skill,side,job,count,cancel] of [
   ['wz_b','A','wizard',3],['wz_1','A','wizard',3],['wz_2','A','wizard',3],['wz_u','A','wizard',3],
   ['wz_1','B','wizard',3],['wz_2','B','wizard',5],['wz_u','B','wizard',5,true],
   ['wz_u','A','paladin',1],['pa_1','A','wizard',3]
  ]){
   if(process.env.WIZARD_FX_SKILLS && !process.env.WIZARD_FX_SKILLS.split(',').includes(skill))continue;
   await page.evaluate(({skill,side,job,count})=>{
    closeModal();PREF.battleCam='stylish';
    const team=()=>Array.from({length:count},(_,i)=>newStudent(1,'B',i?['paladin','priest'][i%2]:job));
    const res=runBattle(team(),team(),{}),own=side==='A'?res.A:res.B,foes=side==='A'?res.B:res.A;
    const initial=JSON.parse(JSON.stringify(res.frames[0])),call=JSON.parse(JSON.stringify(initial));
    const sk=Object.values(JOBS).flatMap(j=>j.skills||[]).find(s=>s.id===skill);
    const targets=skill==='pa_1'?[own[0]]:skill==='wz_b'?[foes[0]]:foes;
    call.cls='';call.actor=own[0].uid;call.call={name:sk.name,kind:sk.kind,pers:'plain'};
    call.fx={skillId:skill,n:sk.fx,e:sk.el,t:targets.map(u=>u.uid)};call.units.forEach(u=>u.atb=1);
    const end=JSON.parse(JSON.stringify(call));delete end.call;delete end.fx;end.pop=[];
    res.frames=[initial,call,end];openBattle(res,{field:'dummy',titleA:'마법사',titleB:'스킬 대상'},()=>{});
   },{skill,side,job,count});
   await page.waitForSelector('.stylish-skill-fx img');await page.waitForTimeout(80);
   const fx=await page.locator('.stylish-skill-fx img,.stylish-group-fx img').evaluateAll(images=>images.map(i=>({kind:i.dataset.effect,loaded:i.complete&&i.naturalWidth>0,targets:i.dataset.targets,layer:i.parentElement.className})));
   assert(fx.every(i=>i.loaded),'all assets must load');
   assert.equal(fx.filter(i=>i.kind==='wizardCircles').length,job==='wizard'?1:0);
   if(job==='paladin')assert(fx.some(i=>i.kind==='trail'));
   if(skill==='wz_1')assert.equal(fx.filter(i=>i.kind==='fireExplosion').length,count);
   if(skill==='pa_1')assert(fx.some(i=>i.kind==='shield'));
   for(const kind of skill==='wz_2'?['blizzardBack','blizzardFront']:skill==='wz_u'?['gravityBeam','gravityCircle']:[]){
    const matches=fx.filter(i=>i.kind===kind);assert.equal(matches.length,1);
    assert.equal(matches[0].targets.split(',').length,count);
    assert.equal(matches[0].layer,['blizzardFront','gravityBeam'].includes(kind)?'stylish-skill-fx':'stylish-group-fx');
   }
   if(skill==='wz_2'||skill==='wz_u'){
    const kind=skill==='wz_u'?'gravityBeam':'blizzardBack';
    const gap=await page.locator(`[data-effect="${kind}"]`).evaluate(i=>i.getBoundingClientRect().top-document.querySelector('.cam-fx .cb.t').getBoundingClientRect().bottom);
    assert(gap<=0&&gap>-8,'effect must meet the upper boundary');
   }
   if(file==='heroschool.html')await page.screenshot({path:`D:/heroschool/assets/skill-fx/wizard/skill-${skill}-${side}-${job}.png`});
   if(cancel)await page.locator('#bPlay').click();
   await page.waitForSelector('.stylish-skill-fx',{state:'detached'});
   assert.equal(await page.locator('.stylish-group-fx').count(),0);
   await page.waitForTimeout(650);console.log(file,skill,side,job,count,'PASS');
  }
  assert.deepEqual(errors,[]);await page.close();
 }
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
