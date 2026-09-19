const {chromium}=require('playwright');
const path=require('path');
const {pathToFileURL}=require('url');
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'msedge'});
 const page=await browser.newPage({viewport:{width:1280,height:900}}),errors=[];
 page.on('pageerror',e=>errors.push(e.message));
 await page.goto(pathToFileURL(path.resolve(__dirname,'../heroschool.html')).href);
 await page.waitForFunction(()=>SPR_READY);
 const result=await page.evaluate(()=>{
  closeModal();
  for(const p of PERSONA_KEYS){const t=battleCallout({name:'쿠나이',pers:p},2).text;
   if(p==='genius'?t.includes('쿠나이'):!t.includes('쿠나이'))throw Error('Persona '+p);
  }
  const jobs=['paladin','monk','sword','wizard','priest','archer'];
  const a=jobs.map(j=>newStudent(1,'B',j)),b=jobs.map(j=>newStudent(1,'B',j));
  const rows=list=>Object.fromEntries(list.map((s,i)=>[s.id,i<3?'front':'back']));
  const bt=runBattle(a,b,{rowsA:rows(a),rowsB:rows(b)});
  if(!bt.frames.some(f=>f.call&&f.call.name))throw Error('No skill metadata');
  window.reviewBattle=bt;
  openBattle(bt,{titleA:'새봄 용사 학원',titleB:'은빛 마법 학원'},()=>{});
  document.querySelector('#bPlay').click();
  return {calls:bt.frames.filter(f=>f.call).length,personas:PERSONA_KEYS.length};
 });
 const check=()=>page.evaluate(()=>{
  const stage=document.querySelector('.bf-stage').getBoundingClientRect();
  const nodes=[...document.querySelectorAll('.bf-unit')];
  if(nodes.length!==12||document.querySelectorAll('.bf-slot').length!==12)throw Error('Formation slots');
  for(const el of nodes){const r=el.getBoundingClientRect();
   if(r.left<stage.left-1||r.right>stage.right+1||r.bottom>stage.bottom+1||r.top<stage.top-1)throw Error('Unit outside field');
   const g=el.querySelector('.bf-gauges').getBoundingClientRect();
   if(el.classList.contains('team-A')?g.x>=r.x+r.width/2:g.x<=r.x+r.width/2)throw Error('Gauge side');
  }
  return nodes.length;
 });
 await check();await page.screenshot({path:path.join(__dirname,'shot_field_desktop.png'),fullPage:true});
 await page.setViewportSize({width:390,height:844});await check();
 await page.screenshot({path:path.join(__dirname,'shot_field_mobile.png'),fullPage:true});
 await page.evaluate(()=>{
  document.querySelector('#bEnd').click();closeModal();
  const a=['paladin','rogue','priest'].map(j=>newStudent(1,'B',j));
  openBattle(runBattle(a,genMonster(DUNGEONS[0],1),{}),{titleB:'학원 지하 수련장'},()=>{});
  document.querySelector('#bPlay').click();
  const el=document.querySelector('.bf-boss');
  if(!el||parseFloat(el.style.left)<60)throw Error('Boss position');
 });
 await page.screenshot({path:path.join(__dirname,'shot_field_boss.png'),fullPage:true});
 if(errors.length)throw Error(errors.join('\n'));
 console.log(JSON.stringify({...result,units:12,slots:12,errors}));await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
