const {chromium}=require('playwright');
const assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({channel:'msedge',headless:true});
 for(const file of ['heroschool.html','site/index.html']){
  const page=await browser.newPage({viewport:{width:1400,height:900}});
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.route('**/*',r=>/^https?:/.test(r.request().url())?r.abort():r.continue());
  await page.goto('file:///D:/heroschool/'+file);
  await page.waitForFunction(()=>SPR_READY);
  await page.locator('#bootLoader').waitFor({state:'hidden'});
  for(const [job,skill,expected,side] of [['darkpriest','dp_b',2,'A'],['darkpriest','dp_b',2,'B'],['darkpriest','pa_b',2,'A'],['paladin','dp_b',2,'A']]){
   await page.evaluate(({job,skill,side})=>{
    closeModal();newGame('효과 검증');closeModal();PREF.battleCam='stylish';
    const a=[newStudent(1,'B',job)],b=[newStudent(1,'B',side==='B'?job:'paladin')];
    const res=runBattle(a,b,{});
    if(!res.frames.some(f=>f.fx&&f.fx.skillId))throw Error('engine missing skill ID');
    const initial=JSON.parse(JSON.stringify(res.frames[0]));
    const idx=side==='A'?0:1,other=1-idx;
    const actor=res.A.concat(res.B)[idx].uid,target=res.A.concat(res.B)[other].uid;
    const call=JSON.parse(JSON.stringify(initial));
    call.actor=actor;call.call={name:({dp_b:'어둠의 손길',pa_b:'성스러운 일격',pa_1:'수호의 맹세',pa_2:'치유의 빛',pa_u:'성역 선포'})[skill]||skill,kind:'skill',pers:'plain'};
    call.fx={skillId:skill,n:'aura',e:'holy',t:[target]};
    call.units.forEach(u=>u.atb=1);
    const end=JSON.parse(JSON.stringify(call));delete end.call;delete end.fx;
    end.pop=[{u:target,k:'shield',v:120}];
    res.frames=[initial,call,end];
    window.fxTestRes=res;
    openBattle(res,{field:'dummy',titleA:'암흑 사제 효과',titleB:'대상'},()=>{});
   },{job,skill,side});
   await page.waitForSelector('.stylish-skill-fx img',{timeout:10000});
   await page.waitForTimeout(180);
   const result=await page.evaluate(()=>{
    const layer=document.querySelector('.stylish-skill-fx');
    const effects=[...layer.querySelectorAll('img')].map(im=>({kind:im.dataset.effect,mirror:im.style.transform,loaded:im.complete&&im.naturalWidth>0,w:im.clientWidth,h:im.clientHeight,top:im.getBoundingClientRect().top}));
    return {effects,boundary:document.querySelector('.cam-fx .cb.t').getBoundingClientRect().bottom};
   });
   assert.equal(result.effects.length,expected,job+skill);
   assert(result.effects.every(e=>e.loaded&&e.w>0&&e.h>0));
   const beam=result.effects.find(e=>e.kind==='beam');if(beam)assert(Math.abs(beam.top-result.boundary)<2);
   assert.equal(result.effects.some(e=>e.kind==='darkEssence'),job==='darkpriest');
   if(side==='B')assert.equal(result.effects[0].mirror,'scaleX(-1)');
   if(file==='heroschool.html')await page.screenshot({path:`D:/heroschool/assets/skill-fx/darkpriest/test-${job}-${skill}-${side}.png`});
   await page.waitForSelector('.stylish-skill-fx',{state:'detached',timeout:10000});
   console.log(file,job,skill,JSON.stringify(result));
  }
  assert.deepEqual(errors,[]);await page.close();
 }
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
