/* One still image per effect. Routing is independent of character sprite sheets. */
const STYLISH_SKILL_FX = {
  assets: {
    trail: "assets/skill-fx/paladin/trail-particles.png?v=1",
    impact: "assets/skill-fx/paladin/impact.png?v=1",
    shield: "assets/skill-fx/paladin/shield.png?v=1",
    beam: "assets/skill-fx/paladin/beam-particles.png?v=1"
  },
  casters: {paladin: ["trail"]},
  targets: {pa_b: ["impact"], pa_1: ["shield"], pa_2: ["beam"], pa_u: ["beam", "shield"]}
};
function stylishSkillFxPlan(job, skillId){
  return {caster: STYLISH_SKILL_FX.casters[job] || [], target: STYLISH_SKILL_FX.targets[skillId] || []};
}
function stylishSkillFxPreload(){
  Object.values(STYLISH_SKILL_FX.assets).forEach(src=>{const img=new Image(); img.src=src;});
}
function stylishSkillFxShow(stage, caster, targets, job, skillId, side, active){
  const plan=stylishSkillFxPlan(job, skillId), entries=[];
  const layer=document.createElement("div");
  layer.className="stylish-skill-fx"; layer.setAttribute("aria-hidden","true");
  layer.style.cssText="position:absolute;inset:0;pointer-events:none;overflow:hidden;z-index:325";
  const add=(el, kind)=>{
    if(!el) return;
    const img=document.createElement("img"); img.src=STYLISH_SKILL_FX.assets[kind];
    img.dataset.effect=kind; img.dataset.target=el.dataset.uid; img.alt="";
    img.style.cssText="position:absolute;max-width:none;image-rendering:auto;object-fit:fill;pointer-events:none";
    img.style.opacity=kind==="shield" ? ".58" : kind==="beam" ? ".72" : ".9";
    if(kind==="trail" && side==="B") img.style.transform="scaleX(-1)";
    layer.append(img); entries.push({el,kind,img});
  };
  plan.caster.forEach(kind=>add(caster,kind));
  [...new Set(targets)].forEach(el=>plan.target.forEach(kind=>add(el,kind)));
  if(!entries.length) return ()=>{};
  stage.append(layer);
  let raf=0, disposed=false;
  const stop=()=>{disposed=true;cancelAnimationFrame(raf);layer.remove();};
  const update=()=>{
    if(disposed || !stage.isConnected || !active()){stop();return;}
    const sr=stage.getBoundingClientRect(), sx=stage.clientWidth/sr.width, sy=stage.clientHeight/sr.height;
    const boundary=stage.querySelector(".cam-fx .cb.t");
    const top=boundary ? (boundary.getBoundingClientRect().bottom-sr.top)*sy : stage.clientHeight*.24;
    const lower=stage.querySelector(".cam-fx .cb.b");
    const bottom=lower ? (lower.getBoundingClientRect().top-sr.top)*sy : stage.clientHeight*.86;
    layer.style.clipPath=`inset(${top}px 0 ${Math.max(0,stage.clientHeight-bottom)}px 0)`;
    entries.forEach(({el,kind,img})=>{
      const sprite=el.querySelector(".spr-anchor") || el.querySelector(".sprwrap") || el;
      const r=sprite.getBoundingClientRect(), h=r.height*sy, w=r.width*sx;
      const cx=(r.left+r.width/2-sr.left)*sx, cy=(r.top-sr.top)*sy+h*.55;
      let width=h*1.05, height=width, x=cx-width/2, y=cy-height/2;
      if(kind==="trail") {width=h*1.35;height=width;x=cx-width/2+(side==="B"?-1:1)*w*.12;y=cy-height*.82;}
      if(kind==="shield") {width=h*.88;height=width;x=cx-width/2;y=cy-height/2;}
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
