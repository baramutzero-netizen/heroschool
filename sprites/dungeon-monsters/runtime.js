/* Additional expedition encounters; original guardians remain final bosses. */
const DUNGEON_MONSTERS = {
  d1:['mon_wood','mon_target'],
  d2:['mon_sentry','mon_foghound','mon_lantern'],
  d3:['mon_bellcrab','mon_clockcrow','mon_choir'],
  d4:['mon_saltcrab','mon_jelly','mon_diver'],
  d5:['mon_oath','mon_scribe','mon_blade']
};
function dungeonMonsterSkill(id,name,type,target,power,extra={}){
  return {id,name,type,target,power,proc:.22,dur:0,fx:'burst',el:'phys',...extra};
}
const DUNGEON_MONSTER_SPEC = [
  ['mon_wood','mon_dummy','목검 훈련병','관절 달린 목제 인형. 정해진 검술과 방어 자세를 반복한다.',{hp:.68,atk:.78,def:.85,spd:1.05},[
    ['목검 내려치기','dmg','enemy_front',.9,{kind:'basic',proc:1,fx:'slash'}],
    ['연습 삼연격','dmg_multi','enemy_front',.36,{hits:3,fx:'slash',txt:'전열 한 명을 목검으로 세 번 타격한다'}],
    ['방패 자세','buff','self',.22,{stat:'def',dur:2,fx:'aura',el:'buff',txt:'2턴 동안 자신의 방어력을 높인다'}],
    ['검술 종합 시험','ult_single','enemy_front',1.8,{kind:'ult',proc:1,fx:'slash',txt:'훈련한 검술을 모아 전열 한 명을 공격한다'}]
  ]],
  ['mon_target','mon_dummy','마력 표적구','수련생의 조준을 교정하던 부유식 표적. 빗나간 마력을 되돌려 쏜다.',{hp:.62,atk:.82,def:.7,spd:1.22},[
    ['표적 광선','dmg','enemy_rand',.9,{kind:'basic',proc:1,el:'arcane'}],
    ['마력 산탄','dmg_aoe','enemy_all',.55,{el:'arcane',txt:'흩어진 마력으로 적 전체를 타격한다'}],
    ['궤도 변경','buff','self',.18,{stat:'spd',dur:2,fx:'aura',el:'buff',txt:'회전 궤도를 바꿔 자신의 속도를 높인다'}],
    ['과충전 조준','ult_single','enemy_rand',1.9,{kind:'ult',proc:1,el:'arcane',txt:'한 대상에게 충전된 마력탄을 발사한다'}]
  ]],
  ['mon_sentry','mon_wraith','안개 창병','성문을 지키라는 마지막 명령에 묶인 녹슨 갑옷.',{hp:.78,atk:.85,def:1.1,spd:.92},[
    ['녹슨 창끝','dmg','enemy_front',1,{kind:'basic',proc:1,fx:'slash'}],
    ['성문 밀어내기','slow','enemy_front',.2,{dur:2,fx:'aura',el:'debuff',txt:'전열의 행동 게이지를 20% 밀고 속도를 늦춘다'}],
    ['안개 방패','shield','self',.45,{dur:2,scale:'def',fx:'aura',el:'frost',txt:'자신에게 방어력 기반 보호막을 만든다'}],
    ['끝나지 않은 경계','ult_single','enemy_front',2.1,{kind:'ult',proc:1,fx:'slash',txt:'성문을 침범한 전열을 강하게 찌른다'}]
  ]],
  ['mon_foghound','mon_wraith','안개 사냥개','무너진 성벽 사이에서 길 잃은 이의 체온을 쫓는다.',{hp:.63,atk:.92,def:.65,spd:1.24},[
    ['서리 송곳니','dmg','enemy_rand',.95,{kind:'basic',proc:1,fx:'slash',el:'frost'}],
    ['온기 추적','drain','enemy_low',.9,{drain:.4,el:'frost',txt:'체력이 낮은 적을 물어 피해의 40%를 흡수한다'}],
    ['안개 질주','buff','self',.23,{stat:'spd',dur:2,fx:'aura',el:'buff',txt:'2턴 동안 자신의 속도를 높인다'}],
    ['백무의 사냥','ult_single','enemy_low',2.15,{kind:'ult',proc:1,fx:'slash',el:'frost',txt:'약해진 적을 향해 안개 속에서 뛰쳐나온다'}]
  ]],
  ['mon_lantern','mon_wraith','길 잃은 등불','귀환로처럼 보이는 불빛으로 여행자를 성 안쪽에 가둔다.',{hp:.7,atk:.8,def:.8,spd:1.05},[
    ['도깨비불','dmg','enemy_rand',.9,{kind:'basic',proc:1,el:'dark'}],
    ['거짓 이정표','debuff','enemy_all',.12,{stat:'acc',dur:2,fx:'aura',el:'debuff',txt:'적 전체의 명중률을 12%p 낮춘다'}],
    ['혼불 흡수','drain','enemy_low',.85,{drain:.6,el:'dark',txt:'약해진 적의 기운을 흡수한다'}],
    ['귀로 없는 밤','ult_aoe','enemy_all',1.45,{kind:'ult',proc:1,el:'dark',noBreak:true,txt:'길을 잃게 하는 혼불이 적 전체를 덮친다'}]
  ]],
  ['mon_bellcrab','mon_gargoyle','금 간 종게','떨어진 종에 다리가 돋아났다. 금속 껍질 속에서 종추가 흔들린다.',{hp:.8,atk:.84,def:1.08,spd:.9},[
    ['종추 박치기','dmg','enemy_front',1,{kind:'basic',proc:1}],
    ['깨진 울림','dmg_aoe','enemy_all',.65,{txt:'금 간 종의 진동으로 적 전체를 공격한다'}],
    ['청동 껍질','buff','self',.3,{stat:'def',dur:3,fx:'aura',el:'buff',txt:'3턴 동안 방어력을 30% 높인다'}],
    ['낙종 충돌','ult_single','enemy_front',2.25,{kind:'ult',proc:1,txt:'종의 무게를 실어 전열에 충돌한다'}]
  ]],
  ['mon_clockcrow','mon_gargoyle','태엽 까마귀','멈춘 시계를 고치던 기계 새. 톱니바퀴를 훔쳐 둥지를 만든다.',{hp:.62,atk:.88,def:.66,spd:1.35},[
    ['강철 부리','dmg','enemy_rand',.9,{kind:'basic',proc:1,fx:'slash'}],
    ['톱니 깃털','dmg_multi','enemy_rand',.43,{hits:3,fx:'slash',txt:'금속 깃털로 한 적을 세 번 공격한다'}],
    ['태엽 되감기','haste','self',.25,{dur:2,fx:'aura',el:'buff',txt:'자신의 행동 게이지를 25% 올리고 가속한다'}],
    ['분침 급강하','ult_single','enemy_low',2.2,{kind:'ult',proc:1,fx:'slash',txt:'약해진 적에게 시곗바늘처럼 떨어진다'}]
  ]],
  ['mon_choir','mon_gargoyle','종탑 성가석','성가대석의 돌조각에 마지막 노래가 남았다.',{hp:.75,atk:.86,def:.93,spd:.98},[
    ['돌의 메아리','dmg','enemy_rand',.95,{kind:'basic',proc:1,el:'arcane'}],
    ['불협 종소리','debuff','enemy_all',.17,{stat:'atk',dur:2,fx:'aura',el:'debuff',txt:'적 전체의 공격력을 17% 낮춘다'}],
    ['공명 장벽','shield','self',.65,{scale:'def',dur:2,fx:'aura',el:'arcane',txt:'공명으로 자신에게 보호막을 두른다'}],
    ['무너진 성가','ult_aoe','enemy_all',1.65,{kind:'ult',proc:1,el:'arcane',noBreak:true,txt:'돌에 남은 합창으로 적 전체를 타격한다'}]
  ]],
  ['mon_saltcrab','mon_brine','염정 소라게','소금 결정으로 껍질을 키우는 균열의 갑각류.',{hp:.84,atk:.82,def:1.18,spd:.78},[
    ['염석 집게','dmg','enemy_front',1,{kind:'basic',proc:1}],
    ['소금 껍질','shield','self',.8,{scale:'def',dur:3,fx:'aura',el:'frost',txt:'소금 결정을 굳혀 자신을 보호한다'}],
    ['결정 파쇄','debuff','enemy_front',.2,{stat:'def',dur:2,fx:'aura',el:'debuff',txt:'날카로운 결정으로 전열의 방어력을 낮춘다'}],
    ['백염 압착','ult_single','enemy_front',2.3,{kind:'ult',proc:1,txt:'거대한 소금 집게로 전열을 압박한다'}]
  ]],
  ['mon_jelly','mon_brine','심해 염수해파리','상처에 스미는 염수를 품고 균열 위를 떠돈다.',{hp:.67,atk:.82,def:.68,spd:1.08},[
    ['촉수 쏘기','dmg','enemy_rand',.9,{kind:'basic',proc:1,el:'poison'}],
    ['염독 주입','dot','enemy_rand',.65,{dur:2,el:'poison',txt:'한 적을 공격하고 2턴 동안 염독 피해를 준다'}],
    ['끈적한 염수','slow','enemy_rand',.22,{dur:2,fx:'aura',el:'frost',txt:'한 적의 행동 게이지와 속도를 낮춘다'}],
    ['심해 발광','ult_aoe','enemy_all',1.55,{kind:'ult',proc:1,el:'poison',noBreak:true,txt:'심해의 빛과 염수로 적 전체를 타격한다'}]
  ]],
  ['mon_diver','mon_brine','침몰한 잠수병','바다에 버려진 잠수갑주. 안에는 사람 대신 균열의 물이 흐른다.',{hp:.78,atk:.94,def:1.02,spd:.92},[
    ['부식된 삼지창','dmg','enemy_front',1,{kind:'basic',proc:1,fx:'slash'}],
    ['부식 염수','debuff','enemy_all',.16,{stat:'def',dur:2,fx:'aura',el:'debuff',txt:'적 전체의 방어력을 16% 낮춘다'}],
    ['해저 압력','slow','enemy_front',.25,{dur:2,fx:'aura',el:'frost',txt:'전열의 행동을 해저 압력으로 늦춘다'}],
    ['균열 관통','ult_single','enemy_front',2.5,{kind:'ult',proc:1,fx:'slash',txt:'삼지창을 내질러 전열에 큰 피해를 준다'}]
  ]],
  ['mon_oath','mon_guardian','맹세의 방패병','용사의 이름을 잊었어도 무덤을 지킨다는 맹세는 남아 있다.',{hp:.85,atk:.8,def:1.18,spd:.86},[
    ['묘비 방패','dmg','enemy_front',.95,{kind:'basic',proc:1}],
    ['불멸의 맹세','buff','self',.3,{stat:'def',dur:3,fx:'aura',el:'holy',txt:'맹세를 되새겨 자신의 방어력을 높인다'}],
    ['묘역 수호','shield','self',.75,{scale:'def',dur:3,fx:'aura',el:'holy',txt:'무덤의 인장으로 자신에게 보호막을 만든다'}],
    ['맹세의 심판','ult_single','enemy_front',2.45,{kind:'ult',proc:1,el:'holy',txt:'방패에 새긴 맹세로 전열을 심판한다'}]
  ]],
  ['mon_scribe','mon_guardian','묘실 기록관','죽은 용사의 행적을 끝없이 기록하는 이름 없는 혼.',{hp:.7,atk:.83,def:.78,spd:1.04},[
    ['추도 문장','dmg','enemy_rand',.9,{kind:'basic',proc:1,el:'dark'}],
    ['이름의 봉인','debuff','enemy_all',.18,{stat:'atk',dur:2,fx:'aura',el:'debuff',txt:'이름을 기록해 적 전체의 공격력을 낮춘다'}],
    ['생명의 잉크','drain','enemy_low',1,{drain:.6,el:'dark',txt:'약해진 적의 생명을 잉크 삼아 흡수한다'}],
    ['마지막 장','ult_drain','enemy_all',1.6,{kind:'ult',proc:1,drain:.25,el:'dark',txt:'적 전체의 생명을 거두고 일부를 흡수한다'}]
  ]],
  ['mon_blade','mon_guardian','유검의 잔영','주인을 잃은 검이 마지막 결투의 궤적을 반복한다.',{hp:.65,atk:1.0,def:.65,spd:1.2},[
    ['잔영 베기','dmg','enemy_rand',1,{kind:'basic',proc:1,fx:'slash',el:'arcane'}],
    ['파편 연무','dmg_multi','enemy_rand',.48,{hits:3,fx:'slash',el:'arcane',txt:'검의 파편으로 한 적을 세 번 벤다'}],
    ['잊힌 검로','buff','self',.2,{stat:'atk',dur:2,fx:'aura',el:'buff',txt:'과거의 검로를 되살려 공격력을 높인다'}],
    ['영웅의 마지막 일격','ult_single','enemy_low',2.65,{kind:'ult',proc:1,fx:'slash',el:'arcane',txt:'체력이 낮은 적에게 마지막 검격을 날린다'}]
  ]]
];
for(const [key,parent,name,desc,scale,skills] of DUNGEON_MONSTER_SPEC){
  const template=JOBS[parent],base={...template.base},grow={...template.grow};
  for(const [stat,mul] of Object.entries(scale)){base[stat]*=mul;if(grow[stat]!=null)grow[stat]*=mul;}
  JOBS[key]={...template,name,desc,base,grow,encounter:true,skills:skills.map(([n,t,target,p,extra],i)=>dungeonMonsterSkill(`${key}_${i}`,n,t,target,p,{txt:n,...extra}))};
  SFX_JOB[key]=skills[0][4].el && skills[0][4].el!=='phys'?'magic':skills[0][4].fx==='slash'?'weapon':'punch';
}
function dungeonMonsterKey(dg,sec){
  const pool=DUNGEON_MONSTERS[dg.id];
  return sec>=dg.secs || !pool?.length ? dg.mon : pool[(Math.max(1,sec)-1)%pool.length];
}
