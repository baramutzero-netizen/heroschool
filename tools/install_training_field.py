from pathlib import Path
p=Path('D:/heroschool/game.html')
s=p.read_text(encoding='utf-8')
s=s.replace('학원 지하 수련장','학원 전투 연습장')
needle='function alignDemonField(){'
config='''/* Independent compositions and walkable-ground start for each orientation.
   Add other fields here when both original paintings are ready. */
const FIELD_VARIANTS = {
  dummy: {
    landscape:{src:"assets/battle-fields/training/landscape.png?v=1",aspect:2,ground:.31},
    portrait:{src:"assets/battle-fields/training/portrait.png?v=1",aspect:9/16,ground:.20}
  }
};
function battleFieldVariant(key,width,height){
  const orientation=width/Math.max(1,height)<1.2?'portrait':'landscape';
  const field=FIELD_VARIANTS[key];
  return field ? {...field[orientation],orientation} : null;
}
'''
assert needle in s
s=s.replace(needle,config+needle,1)
needle='  const m=modal.getBoundingClientRect(),r=stage.getBoundingClientRect();'
replacement=needle+'''
  const variant=battleFieldVariant(modal.dataset.fk,stage.clientWidth,stage.clientHeight);
  if(variant){
    modal.dataset.fieldOrientation=variant.orientation;
    modal.style.setProperty('--btf',`url('${variant.src}')`);
    modal.style.setProperty('--demon-shift','0px');
    const sw=stage.clientWidth,sh=stage.clientHeight;
    let top=sh;
    stage.querySelectorAll('.bf-slot').forEach(el=>{const b=el.getBoundingClientRect();if(b.height)top=Math.min(top,b.top-r.top-18);});
    const G=Math.max(0,top),g=variant.ground,A=variant.aspect;
    const H=Math.max(sh,sw/A,(sh-G)/(1-g));
    const y=Math.min(0,G-g*H);
    stage.style.setProperty('--field-left','0px');
    stage.style.setProperty('--field-top','0px');
    stage.style.setProperty('--field-width',sw+'px');
    stage.style.setProperty('--field-height',sh+'px');
    stage.style.setProperty('--field-clip','0px');
    stage.style.setProperty('--field-size',`${H*A}px ${H}px`);
    stage.style.setProperty('--field-pos',`center ${y}px`);
    return;
  }
'''
assert needle in s
s=s.replace(needle,replacement,1)
p.write_text(s,encoding='utf-8')
