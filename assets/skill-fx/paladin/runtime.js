/* One still image per effect. Routing is independent of character sprite sheets. */
const STYLISH_SKILL_FX = {
  assets: {
    trail: "assets/skill-fx/paladin/trail-particles.png?v=1",
    impact: "assets/skill-fx/paladin/impact.png?v=1",
    shield: "assets/skill-fx/paladin/shield.png?v=1",
    beam: "assets/skill-fx/paladin/beam-particles.png?v=1",
    darkEssence: "assets/skill-fx/darkpriest/essence.png?v=1",
    darkHit: "assets/skill-fx/darkpriest/hit.png?v=1",
    redDrain: "assets/skill-fx/darkpriest/drain.png?v=1",
    curseNail: "assets/skill-fx/darkpriest/nail.png?v=1",
    bloodRitual: "assets/skill-fx/darkpriest/ritual.png?v=1",
    gunMuzzle: "assets/skill-fx/gunner/muzzle.png?v=1",
    gunHit: "assets/skill-fx/gunner/hit.png?v=1",
    gunPierce: "assets/skill-fx/gunner/pierce.png?v=1",
    poisonDagger: "assets/skill-fx/rogue/dagger-embedded.png?v=1",
    shadowStep: "assets/skill-fx/rogue/shadow.png?v=1",
    assassination: "assets/skill-fx/rogue/assassinate.png?v=1",
    holyEssence: "assets/skill-fx/priest/essence.png?v=1",
    greaterHeal: "assets/skill-fx/priest/heal.png?v=1",
    blessing: "assets/skill-fx/priest/blessing.png?v=1",
    revival: "assets/skill-fx/priest/revival.png?v=1",
    bardMelody: "assets/skill-fx/bard/melody.png?v=1",
    dissonance: "assets/skill-fx/bard/dissonance.png?v=1",
    ensemble: "assets/skill-fx/bard/ensemble.png?v=1",
    spotlight: "assets/skill-fx/bard/spotlight.png?v=1",
    ninjaRipple: "assets/skill-fx/ninja/ripple.png?v=1",
    waterSwamp: "assets/skill-fx/ninja/swamp.png?v=1",
    waterDragon: "assets/skill-fx/ninja/dragon.png?v=1",
    fumaWave: "assets/skill-fx/ninja/fuma.png?v=1",
    boundaryWave: "assets/skill-fx/ninja/boundary-wave.png?v=1",
    fumaPassed: "assets/skill-fx/ninja/fuma-water-spin.png?v=1",
    waterFlower: "assets/skill-fx/ninja/water-flower.png?v=1",
    archerWind: "assets/skill-fx/archer/wind.png?v=1",
    greenPierce: "assets/skill-fx/archer/pierce-offscreen.png?v=1",
    hawkEye: "assets/skill-fx/archer/hawk-outline.png?v=1",
    meteorRain: "assets/skill-fx/archer/meteor-perspective-back.svg?v=1",
    meteorFront: "assets/skill-fx/archer/meteor-perspective-front.svg?v=1",
    meteorImpact: "assets/skill-fx/archer/meteor-impact.svg?v=1"
  },
  casters: {paladin: ["trail"], darkpriest: ["darkEssence"], gunner:["gunMuzzle"], priest:["holyEssence"], bard:["bardMelody"], ninja:["ninjaRipple"], archer:["archerWind"]},
  targets: {pa_b: ["impact"], pa_1: ["shield"], pa_2: ["beam"], pa_u: ["beam", "shield"],
    dp_b:["darkHit"], dp_1:["redDrain"], dp_2:["curseNail"], dp_u:["redDrain"],
    gn_b:["gunHit"], gn_1:["gunHit"], gn_2:["gunPierce"], gn_u:["gunPierce"],
    ro_1:["poisonDagger"], ro_2:["shadowStep"], ro_u:["assassination"],
    pr_b:["impact"], pr_1:["greaterHeal"], pr_2:["blessing"], pr_u:["revival"],
    bd_1:["shadowStep"], bd_2:["dissonance"], bd_u:["spotlight"],
    nj_1:["dissonance"], nj_2:["boundaryWave","waterDragon"], nj_u:["fumaPassed","waterFlower"],
    ar_1:[], ar_2:["hawkEye"], ar_u:["meteorRain","meteorFront","meteorImpact"]},
  groups: {dp_u:["bloodRitual"], bd_u:["ensemble"], nj_1:["waterSwamp"], ar_1:["greenPierce"]}
};
function stylishSkillFxPlan(job, skillId){
  return {caster: STYLISH_SKILL_FX.casters[job] || [], target: STYLISH_SKILL_FX.targets[skillId] || [], group: STYLISH_SKILL_FX.groups[skillId] || []};
}
function stylishFormation(actor, allies, enemies, side, skillId){
  const positions=[], mirror=x=>side==="B"?100-x:x;
  const lane=(list,left,right)=>list.forEach((uid,i)=>positions.push({uid,
    x:mirror(list.length===1?(left+right)/2:left+(right-left)*i/(list.length-1)),
    y:list.length>2?(i%2?61:56):58, scale:1.3*Math.max(.62,Math.min(1,2.5/list.length))}));
  if(skillId==="nj_u" && enemies.length===1){lane([actor,...allies],15,25);lane(enemies,43,43);}
  else if(skillId==="ar_1"){lane([actor,...allies],18,30);lane(enemies,50,82);positions.forEach(p=>p.y=58);}
  else if(enemies.length){lane([actor,...allies],18,43);lane(enemies,57,82);}
  else {lane([actor,...allies],28,78);}
  return positions;
}
function stylishSkillFxPreload(){
  Object.values(STYLISH_SKILL_FX.assets).forEach(src=>{const img=new Image(); img.src=src;});
}
function stylishSkillFxShow(stage, caster, targets, job, skillId, side, active, groupTargets=[], timing={}){
  const plan=stylishSkillFxPlan(job, skillId), entries=[];
  const mono=skillId==="gn_u", inverted=skillId==="ro_u", shots=skillId==="gn_1"?(timing.shots||[]):[];
  const started=performance.now(), duration=timing.duration||1500;
  const shotStep=Math.min(duration/Math.max(1,shots.length),duration*.16);
  const layer=document.createElement("div");
  layer.className="stylish-skill-fx"; layer.setAttribute("aria-hidden","true");
  layer.style.cssText="position:absolute;inset:0;pointer-events:none;overflow:hidden;z-index:325";
  const ground=layer.cloneNode();ground.className="stylish-group-fx";ground.style.zIndex="0";
  if(skillId==="ar_u"){
    const shade=document.createElement("div");shade.dataset.effect="meteorShade";
    shade.style.cssText="position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,24,15,.78),rgba(0,31,18,.6));pointer-events:none";
    ground.append(shade);
  }
  const group=[...new Set(skillId==="bd_u"?[caster,...targets]:groupTargets)].filter(Boolean);
  const add=(el, kind)=>{
    if(!el) return;
    const img=document.createElement("img"); img.src=STYLISH_SKILL_FX.assets[kind];
    img.dataset.effect=kind; img.dataset.target=el.dataset.uid; img.alt="";
    img.style.cssText="position:absolute;max-width:none;image-rendering:auto;object-fit:fill;pointer-events:none";
    img.style.opacity=kind==="bloodRitual" ? ".6" : kind==="shield" ? ".58" : kind==="beam" ? ".72" : (kind==="darkEssence"||kind==="holyEssence") ? ".66" : kind==="curseNail" ? ".65" : ".9";
    if(kind==="spotlight") img.style.opacity=".46";
    if(kind==="archerWind") img.style.opacity=".72";
    if(kind==="meteorRain") img.style.opacity=".85";
    if((kind==="meteorRain" || kind==="meteorFront") && side==="B") img.style.transform="scaleX(-1)";
    if(kind==="greenPierce" && side==="B") img.style.transform="scaleX(-1)";
    if(kind==="waterSwamp") img.style.opacity=".64";
    if(kind==="ninjaRipple") img.style.opacity=".8";
    if(kind==="waterDragon") img.style.maskImage="linear-gradient(to right,transparent 0%,black 16%,black 100%)";
    if((kind==="waterDragon"||kind==="fumaWave") && side==="B") img.style.transform="scaleX(-1)";
    if(kind==="waterFlower" && side==="B") img.style.transform="scaleX(-1)";
    if(kind==="bardMelody" && side==="B") img.style.transform="scaleX(-1)";
    if((kind==="trail" || kind==="darkEssence" || kind==="holyEssence" || kind==="redDrain" || kind==="gunMuzzle" || kind==="gunPierce" || kind==="poisonDagger" || kind==="assassination") && side==="B") img.style.transform="scaleX(-1)";
    if(kind==="gunPierce" && mono) img.style.filter="brightness(.08)";
    layer.append(img); entries.push({el,kind,img});
    if(kind==="gunPierce" || kind==="ninjaRipple" || kind==="fumaPassed" || kind==="waterFlower" || kind==="meteorRain") ground.append(img);
    return entries[entries.length-1];
  };
  plan.caster.forEach(kind=>add(caster,kind));
  if(shots.length) shots.forEach((uid,shot)=>{
    const el=targets.find(t=>t.dataset.uid===uid);if(!el)return;
    plan.target.forEach(kind=>{const entry=add(el,kind);entry.shot=shot;entry.img.dataset.shot=shot;});
  });
  else [...new Set(skillId==="bd_u"?[caster,...targets]:targets)].forEach(el=>plan.target.forEach(kind=>add(el,kind)));
  if(group.length) plan.group.forEach(kind=>{
    add(group[0],kind);const entry=entries[entries.length-1];entry.group=group;
    entry.img.dataset.targets=group.map(el=>el.dataset.uid).join(",");
    if(!["ensemble","greenPierce","meteorRain"].includes(kind)) ground.append(entry.img);
  });
  if(!entries.length) return ()=>{};
  // Field background is z=-1; the transformed camera is an auto/0 stacking context.
  // Put the ground effect before that context, below all units, labels and foreground FX.
  stage.insertBefore(ground,stage.querySelector(".bf-cam"));
  stage.append(layer);
  const oldFilter=stage.style.filter;
  if(mono){stage.style.filter=(oldFilter?oldFilter+" ":"")+"grayscale(1) contrast(1.12)";stage.dataset.skillMonochrome=skillId;}
  if(inverted){stage.style.filter=(oldFilter?oldFilter+" ":"")+"invert(1)";stage.dataset.skillInverted=skillId;}
  let raf=0, disposed=false;
  const stop=()=>{disposed=true;cancelAnimationFrame(raf);layer.remove();ground.remove();if(mono||inverted){stage.style.filter=oldFilter;delete stage.dataset.skillMonochrome;delete stage.dataset.skillInverted;}};
  const update=()=>{
    if(disposed || !stage.isConnected || !active()){stop();return;}
    const sr=stage.getBoundingClientRect(), sx=stage.clientWidth/sr.width, sy=stage.clientHeight/sr.height;
    const boundary=stage.querySelector(".cam-fx .cb.t");
    const top=boundary ? (boundary.getBoundingClientRect().bottom-sr.top)*sy : stage.clientHeight*.24;
    const lower=stage.querySelector(".cam-fx .cb.b");
    const bottom=lower ? (lower.getBoundingClientRect().top-sr.top)*sy : stage.clientHeight*.86;
    layer.style.clipPath=`inset(${top}px 0 ${Math.max(0,stage.clientHeight-bottom)}px 0)`;
    ground.style.clipPath=layer.style.clipPath;
    const elapsed=performance.now()-started;
    entries.forEach(({el,kind,img,group,shot})=>{
      if(shot!=null){
        const end=shot===shots.length-1?duration:(shot+.6)*shotStep;
        img.style.visibility=elapsed>=shot*shotStep && elapsed<end?"visible":"hidden";
      }
      if(kind==="gunMuzzle" && shots.length){
        const index=Math.min(shots.length-1,Math.floor(elapsed/shotStep));
        img.style.visibility=index===shots.length-1 || elapsed-index*shotStep<shotStep*.6?"visible":"hidden";
      }
      const sprite=el.querySelector(".spr-anchor") || el.querySelector(".sprwrap") || el;
      const r=sprite.getBoundingClientRect(), h=r.height*sy, w=r.width*sx;
      const cx=(r.left+r.width/2-sr.left)*sx, cy=(r.top-sr.top)*sy+h*.55;
      const throwSize=Math.min(h,Math.max(1,(side==="B"?cx:stage.clientWidth-cx)-12)/3.6);
      let width=h*1.05, height=width, x=cx-width/2, y=cy-height/2;
      if(kind==="archerWind"){width=h*1.12;height=width;x=cx-width/2;y=cy-height*.5;}
      if(kind==="meteorRain" || kind==="meteorFront"){
        width=Math.max(h*4.4,stage.clientWidth*.54);y=top-4;height=Math.max(1,bottom-top+8);
        x=cx-width*(side==="B"?.45:.55);
      }
      if(kind==="meteorImpact"){width=h*.48;height=width;x=cx-width/2;y=(r.top-sr.top)*sy+h*.62-height/2;}
      if(kind==="hawkEye"){
        width=h*.46;height=width;x=cx-width/2;y=(r.top-sr.top)*sy+h*.12-height;
        const speech=el.querySelector(".bf-speech");
        if(speech)y=Math.min(y,(speech.getBoundingClientRect().top-sr.top)*sy-height-6);
        y=Math.max(top+4,y);
      }
      if(kind==="trail") {width=h*1.35;height=width;x=cx-width/2+(side==="B"?-1:1)*w*.12;y=cy-height*.82;}
      if(kind==="shield") {width=h*.88;height=width;x=cx-width/2;y=cy-height/2;}
      if(kind==="darkHit") {width=h*.9;height=width/1.5;x=cx-width*.51;y=cy-height*.58;}
      if(kind==="curseNail") {width=h*.53;height=width/1.2;x=cx-width*.28;y=cy-height*.86;}
      if(kind==="redDrain") {width=h*.95;height=width/1.5;x=cx-width*(side==="B"?.33:.67);y=cy-height*.72;}
      if(kind==="poisonDagger") {width=h*.34;height=width;x=cx-width*(side==="B"?.26:.74);y=(r.top-sr.top)*sy+h*.65-height*.5;}
      if(kind==="shadowStep" || kind==="dissonance") {width=h*1.05;height=width;x=cx-width/2;y=cy-height/2;}
      if(kind==="dissonance") y=(r.top-sr.top)*sy+h*.8-height*.97;
      if(kind==="ninjaRipple") {
        width=h*1.12;height=width/2;x=cx-width/2;y=(r.top-sr.top)*sy+h*.8-height*.5;
      }
      if(kind==="waterDragon" || kind==="boundaryWave") {
        const dir=side==="B"?-1:1, sourceX=cx-dir*h*.95;
        if(kind==="boundaryWave"){
          width=h*1.45;height=width/2;x=sourceX-width/2;y=bottom-height*.98;
        }else{
          const dx=cx-sourceX,dy=cy-bottom;
          width=Math.hypot(dx,dy)/.7;height=width/2;x=sourceX;y=bottom-height/2;
          img.style.transformOrigin="0 50%";
          img.style.transform=`rotate(${Math.atan2(dy,dx)*180/Math.PI}deg)${side==="B"?" scaleY(-1)":""}`;
        }
      }
      if(kind==="fumaPassed") {
        width=throwSize*1.8;height=width;
        const dir=side==="B"?-1:1;
        x=cx+dir*throwSize*2.6-width/2;y=cy-h*.2-height/2;
        img.style.transform=`rotate(${-dir*18}deg) scaleY(.65) rotate(${dir*elapsed*.7}deg)`;
      }
      if(kind==="waterFlower"){
        width=throwSize*1.6;height=width/2;
        x=side==="B"?cx-w*.15-width:cx+w*.15;
        y=(r.top-sr.top)*sy+h*.62-height*.5;
      }
      if(kind==="fumaWave") {width=h*1.25;height=width;x=cx-width/2;y=cy-height*.55;}
      if(kind==="bardMelody") {
        width=h*1.1;height=width*.5;
        x=cx+(side==="B"?-1:1)*w*.24-width*(side==="B"?.9:.1);
        y=(r.top-sr.top)*sy+h*.59-height*.7;
      }
      if(kind==="spotlight") {
        width=h*.88;height=Math.max(1,(r.top-sr.top)*sy+h*.84-top);
        x=cx-width/2;y=top;
      }
      if(kind==="greaterHeal" || kind==="blessing") {width=h; height=h; x=cx-width/2;y=cy-height/2;}
      if(kind==="revival") {
        height=h*1.2;width=height*.5;x=cx-width/2;
        y=(r.top-sr.top)*sy+h*.82-height*.92;
      }
      if(kind==="assassination") {width=h*.8;height=width;x=cx-width*(side==="B"?.84:.16);y=(r.top-sr.top)*sy+h*.56-height*.66;}
      if(kind==="gunHit") {
        width=h*.48;height=width;x=cx-width/2;y=cy-height/2;
        if(shot!=null){x+=([-.06,.05,-.02,.04][shot%4])*h;y+=([-.03,.03,.05,-.05][shot%4])*h;}
      }
      if(kind==="gunMuzzle") {
        width=h*.36;height=width;
        const muzzleX=cx+(side==="B"?-1:1)*w*.32,muzzleY=(r.top-sr.top)*sy+h*.42;
        x=muzzleX-width*(side==="B"?.85:.15);y=muzzleY-height*.5;
      }
      if(kind==="gunPierce") {
        const room=side==="B"?cx:stage.clientWidth-cx;
        width=Math.min(h*1.4,Math.max(20,room-8)/.88);height=width*.5;
        x=cx-width*(side==="B"?.88:.12);y=cy-height*.5;
      }
      if(group){
        const rs=group.map(u=>(u.querySelector(".spr-anchor")||u.querySelector(".sprwrap")||u).getBoundingClientRect());
        const left=Math.min(...rs.map(b=>b.left+b.width*.2)),right=Math.max(...rs.map(b=>b.right-b.width*.2));
        const foot=Math.max(...rs.map(b=>b.top+b.height*.8));
        width=Math.max(h*1.15,(right-left)*sx+h*.35);height=width*.5;
        x=((left+right)/2-sr.left)*sx-width/2;y=(foot-sr.top)*sy-height*.72;
        if(kind==="greenPierce"){
          // Begin just ahead of the first target on the caster-facing side.
          const start=((side==="B"?right:left)-sr.left)*sx+(side==="B"?1:-1)*h*.08;
          // Keep the arrowhead (last 25% of the artwork) beyond either screen edge.
          const visibleLength=side==="B"?start:stage.clientWidth-start;
          width=(visibleLength+32)/.70;height=h*.65;
          x=side==="B"?start-width:start;
          y=(rs.reduce((sum,b)=>sum+b.top+b.height*.57,0)/rs.length-sr.top)*sy-height/2;
        }
        if(kind==="ensemble") {
          // Repeat proportionally scaled phrases instead of stretching the notes.
          const span=width, start=x, ratio=img.naturalWidth/img.naturalHeight || 3;
          const count=Math.max(1,Math.ceil(span/(h*.95*ratio)));
          width=span/(count-(count-1)*.08);height=width/ratio;
          const heads=Math.min(...rs.map(b=>b.top+b.height*.15));
          y=Math.max(top,(heads-sr.top)*sy-height*.9);
          const tiles=img._ensembleTiles||(img._ensembleTiles=[]);
          while(tiles.length<count-1){const tile=img.cloneNode();layer.append(tile);tiles.push(tile);}
          while(tiles.length>count-1)tiles.pop().remove();
          [img,...tiles].forEach((tile,i)=>{
            Object.assign(tile.style,{left:(start+i*width*.92)+"px",top:y+"px",width:width+"px",height:height+"px"});
            tile.style.maskImage=count===1?"none":`linear-gradient(to right,${i?"transparent 0%,black 8%":"black 0%"},${i<count-1?"black 92%,transparent 100%":"black 100%"})`;
          });
        }
      }
      if(kind==="darkEssence" || kind==="holyEssence") {
        // Artwork focus (88%,48%) meets the outstretched staff tip; mirror for side B.
        width=h*1.15;height=width;
        const tipX=cx+(side==="B"?-1:1)*w*.46, tipY=(r.top-sr.top)*sy+h*.38;
        x=tipX-width*(side==="B"?.12:.88);y=tipY-height*.48;
      }
      if(kind==="beam") {
        width=h*.8; height=Math.max(1,((r.top-sr.top)*sy+h*.3-top)/.9);
        x=cx-width/2;y=top;
      }
      Object.assign(img.style,{left:x+"px",top:y+"px",width:width+"px",height:height+"px"});
    });
    raf=requestAnimationFrame(update); // Anchor tracking only; the effect artwork stays on one frame.
  };
  update(); return stop;
}
