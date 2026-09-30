const {chromium}=require('playwright');
const assert=require('node:assert/strict');
(async()=>{const browser=await chromium.launch({channel:'msedge',headless:true});
for(const file of ['heroschool.html','site/index.html']){
 const page=await browser.newPage({viewport:{width:1400,height:900}}),errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.route('**/*',r=>/^https?:/.test(r.request().url())?r.abort():r.continue());
 await page.goto('file:///D:/heroschool/'+file);await page.waitForFunction(()=>SPR_READY);await page.locator('#bootLoader').waitFor({state:'hidden'});
 for(const [skill,side] of [['dp_b','A'],['dp_1','A'],['dp_2','A'],['dp_u','A'],['dp_u','B']]){
  await page.evaluate(({skill,side})=>{
   closeModal();newGame('암흑 효과 검증');closeModal();PREF.battleCam='stylish';
   const team=()=>['darkpriest','paladin','priest'].map(j=>newStudent(1,'B',j));
   const res=runBattle(team(),team(),{}),all=res.A.concat(res.B),own=side==='A'?res.A:res.B,foes=side==='A'?res.B:res.A;
   const initial=JSON.parse(JSON.stringify(res.frames[0])),call=JSON.parse(JSON.stringify(initial));
   const sk=JOBS.darkpriest.skills.find(s=>s.id===skill);
   const targets=(skill==='dp_2'||skill==='dp_u')?foes:[foes[0]],healed=(skill==='dp_1'||skill==='dp_u')?own:[];
   call.cls="";call.actor=own[0].uid;call.call={name:sk.name,kind:sk.kind,pers:'plain'};call.fx={skillId:skill,n:sk.fx,e:sk.el,t:targets.map(u=>u.uid)};
   call.units.forEach(u=>u.atb=1);
   const end=JSON.parse(JSON.stringify(call));delete end.call;delete end.fx;
   end.pop=[...targets.map(u=>({u:u.uid,k:'dmg',v:150})),...healed.map(u=>({u:u.uid,k:'heal',v:50}))];
   res.frames=[initial,call,end];window.fxFixture={actor:own[0].uid,allies:healed.map(u=>u.uid),enemies:targets.map(u=>u.uid)};
   openBattle(res,{field:'dummy',titleA:'암흑 사제',titleB:'스킬 대상'},()=>{});
  },{skill,side});
  await page.waitForSelector('.stylish-skill-fx img');await page.waitForTimeout(200);
  const r=await page.evaluate(()=>{
   const f=window.fxFixture,pos=id=>document.querySelector(`.bf-unit[data-uid="${id}"]`).getBoundingClientRect().x;
   const imgs=[...document.querySelectorAll('.stylish-skill-fx img,.stylish-group-fx img')];
   return {effects:imgs.map(i=>({kind:i.dataset.effect,target:i.dataset.target,targets:i.dataset.targets,loaded:i.complete&&i.naturalWidth>0})),own:[f.actor,...f.allies].map(pos),foes:f.enemies.map(pos),ids:f.enemies};
  });
  assert(r.effects.every(e=>e.loaded));
  assert.equal(r.effects.filter(e=>['darkHit','redDrain','curseNail'].includes(e.kind)).length,r.foes.length);
  assert(r.effects.filter(e=>['darkHit','redDrain','curseNail'].includes(e.kind)).every(e=>r.ids.includes(e.target)));
  if(side==='A')assert(Math.max(...r.own)<Math.min(...r.foes));else assert(Math.min(...r.own)>Math.max(...r.foes),JSON.stringify(r));
  const group=r.effects.filter(e=>e.kind==='bloodRitual');assert.equal(group.length,skill==='dp_u'?1:0);
  if(group.length)assert.deepEqual(group[0].targets.split(',').sort(),r.ids.slice().sort());
  if(file==='heroschool.html')await page.screenshot({path:`D:/heroschool/assets/skill-fx/darkpriest/skill-${skill}-${side}.png`});
  await page.waitForSelector('.stylish-skill-fx',{state:'detached'});assert.equal(await page.locator('.stylish-group-fx').count(),0);
  console.log(file,skill,side,'PASS');
 }
 assert.deepEqual(await page.evaluate(()=>[stylishSkillFxPlan('paladin','dp_u').caster,stylishSkillFxPlan('darkpriest','pa_b').caster]),[['trail'],['darkEssence']]);
 assert.deepEqual(errors,[]);await page.close();
}await browser.close();})().catch(e=>{console.error(e);process.exit(1)});
