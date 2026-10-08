// 원정 시뮬레이션 (1008) — exped_sim.py 가 게임 페이지에 넣어 돌린다. 게임 상태(S)는 건드리되 저장하지 않는다.
// __sim  — 원정 n번: 권장 레벨(+lvAdd) · 그 무렵 멘탈리티(DG_MENT) · 등급(grade, 기본 B) · 유물 없음 · 컨디션 90 · 스킬 자동 배분
//          sk: "auto" 면 학생처럼 강화 포인트를 임의 강화 방식(skAutoSpend — 세 제안 중 가장 높은 강화)으로 쓴다 (1008).
//          없으면 적과 같은 autoSkMod (레벨/2 번 강화 · 16% 등급 +1)
//          comp: "role" 이면 탱커 + 딜러 + 힐/지원, 아니면 무작위 직업 셋 · form 이면 쐐기진(탱커 전열)
// __duel — 체력 가득한 팀으로 보스 방(kind "boss") 또는 그뉵이용 한 판 승률
window.__simSetup = () => {
  window.logE = ()=>{}; window.levelReport = ()=>{}; window.addRelicToPool = ()=>{}; window.tryEpithet = ()=>null;
  window.addGold = ()=>{}; window.addFame = ()=>{}; window.lvupQueue = ()=>{};
  return {secs: DUNGEONS.map(d=>[d.id, d.secs, d.depth||null]), mobK: Object.assign({}, MOB_K), diff: S.diff||null, items: Object.keys(S.items||{})};
};
const ROLE = j => JOBS[j].role;
/* 스킬 — "auto": 학생처럼 포인트를 임의 강화 방식으로 (skAutoSpend 가 없는 예전 빌드면 autoSkMod) · 그 밖: autoSkMod */
function skSim(st, sk){
  if(sk === "auto" && typeof skAutoSpend === "function"){ st.skMod = {}; st.skOpts = null; skAutoSpend(st); }
  else autoSkMod(st, st.level);
}
function simTeam(comp, mk){
  const ks = JOB_KEYS.slice();
  if(comp === "role"){
    const pickR = r => pick(ks.filter(j=> r.includes(ROLE(j))));
    const t = pickR(["tank"]), h = pickR(["heal","supp"]);
    const d = pick(ks.filter(j=> ROLE(j)==="dps"));
    return [t, d, h].map(mk);
  }
  return shuffle(ks).slice(0,3).map(mk);
}
function simTM(team){
  const order = team.slice().sort((a,b)=> (ROLE(a.job)==="tank"?0:1) - (ROLE(b.job)==="tank"?0:1));
  return {n:"SIM", form:"wedge", slots:{f2:order[0].id, b1:order[1].id, b3:order[2].id}};
}
window.__sim = ({id, n, mobK, cond, comp, form, lvAdd, grade, sk}) => {
  if(mobK != null) MOB_K[id] = mobK;
  const dg = DUNGEONS.find(d=>d.id===id);
  const M = DG_MENT[id];
  const LV = Math.max(1, dg.lv + (lvAdd||0));
  const mk = job => { const st = newStudent(1, grade || "B", job); st.level = 1; st.exp = 0; st.relics = []; st.sp = 0;
    for(let i=1;i<LV;i++) levelUp(st, true);
    MENTAL.forEach(m=>{ if(m.k!=="pot") st.ment[m.k] = M; });
    st.cond = cond || 90; skSim(st, sk); st.eval = 0; st.fame = 0; st.karma = 0; return st; };
  const o = {n, full:0, reached:0, exp:0, gold:0, relics:0, karma:0, cond:0, fame:0, eval:0, battles:0,
             wipe:0, retire:0, stam:0, muscle:0, secWin:[], secTry:[], ms:0};
  const t0 = performance.now();
  for(let i=0;i<n;i++){
    const team = simTeam(comp, mk);
    const c0 = team.map(s=>s.cond);
    const res = runExpedition(dg, team, form ? simTM(team) : null);
    if(res.reached >= dg.secs) o.full++;
    o.reached += res.reached / dg.secs;
    o.exp += res.exp; o.gold += res.gold || 0; o.relics += res.relics.length; o.karma += res.karma || 0;
    o.cond += team.reduce((a,s,j)=> a + (c0[j]-s.cond), 0)/3;
    o.fame += team.reduce((a,s)=> a + (s.fame||0), 0)/3;
    o.eval += team.reduce((a,s)=> a + (s.eval||0), 0)/3;
    o.battles += res.secs.length; o.muscle += res.muscleN||0;
    const st = res.stopped||"";
    if(/전멸/.test(st)) o.wipe++; else if(/리타이어/.test(st)) o.retire++; else if(/지구력/.test(st)) o.stam++;
    res.secs.forEach(x=>{ o.secTry[x.sec-1] = (o.secTry[x.sec-1]||0)+1; if(x.win) o.secWin[x.sec-1] = (o.secWin[x.sec-1]||0)+1; });
  }
  o.ms = Math.round(performance.now()-t0);
  return o;
};
// 한 판 승률 — 보스 방(마지막 구간) 또는 그뉵이용(보스 방을 뺀 구간 무작위), 체력 가득한 팀
window.__duel = ({id, n, lvAdd, kind, mobK, muscleK, grade, sk}) => {
  if(mobK != null) MOB_K[id] = mobK;
  if(muscleK != null) MUSCLE_K[id] = muscleK;
  const dg = DUNGEONS.find(d=>d.id===id);
  const M = DG_MENT[id], LV = Math.max(1, dg.lv + (lvAdd||0));
  const mk = job => { const st = newStudent(1, grade || "B", job); st.level = 1; st.exp = 0; st.relics = []; st.sp = 0;
    for(let i=1;i<LV;i++) levelUp(st, true);
    MENTAL.forEach(m=>{ if(m.k!=="pot") st.ment[m.k] = M; });
    st.cond = 90; skSim(st, sk); return st; };
  let win = 0;
  for(let i=0;i<n;i++){
    const team = simTeam("role", mk), TM = simTM(team);
    const mon = kind === "boss" ? genMonster(dg, dg.secs) : genMuscle(dg, 1 + Math.floor(RNG()*(dg.secs-1)));
    const b = runBattle(team, mon, Object.assign({hpA:{}, rowsB: mon.rows||null, slotsB: mon.slots||null}, teamBattleOpt(TM)));
    if(b.winner === "A") win++;
  }
  return {n, win, rate: win/n};
};
