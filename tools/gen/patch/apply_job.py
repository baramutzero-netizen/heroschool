"""의뢰 바꾸기 (1006) — game.html 에 몇 번을 돌려도 같은 결과 (이미 바뀐 곳은 건너뛴다).

    python3 apply_job.py <game.html>          (apply_sched.py 가 끝에 같이 부른다)

· 이번 주 의뢰를 주를 시작하기 전에 정해 둔다 (weekJobPlan · S.jobWk) — 주가 끝나면 다음 주 의뢰를 바로 정하고, 세이브에 남는다.
  스케줄 화면(두루마리 의뢰 쪽지 · 예전 화면의 개인 행동 칸 · 학생 화면의 개인 행동 고르기)에 의뢰 이름 · 오르고 내리는 멘탈리티를 미리 보인다.
· 의뢰 등급은 의뢰처마다 따로 — 누적은 의뢰처별 jobN, 등급은 S.jobG[의뢰처]. 예전에는 여섯 곳이 누적 하나(S.jobCount · S.jobGrade)를 같이 썼다.
  옛 세이브는 그때 공용 등급을 모든 의뢰처의 바닥으로 남긴다 (jobGMap — 처음 읽을 때 한 번)."""
import sys

def sub1(src, old, new, done_mark):
    if done_mark in src: return src
    if old not in src: raise RuntimeError("자리를 못 찾았다: " + old[:90])
    if src.count(old) != 1: raise RuntimeError("자리가 여러 곳이다: " + old[:90])
    return src.replace(old, new, 1)


def apply(src):
    # ── 의뢰처별 등급 ──
    old = '''function jobCount(){ return Math.max(0, S.jobCount|0); }
function jobGradeIdx(){ return clamp(S.jobGrade|0, 0, JOB_GRADES.length-1); }
function jobGrade(){ return JOB_GRADES[jobGradeIdx()]; }
function jobUp(){ return jobGrade().up * FOCUS_G / FOCUS_COND; }
function jobDown(){ return jobGrade().down * FOCUS_G / FOCUS_COND; }
function tryJobGrade(){
  let g = jobGradeIdx(), up = 0;
  while(g+1 < JOB_GRADES.length && jobCount() >= JOB_GRADES[g+1].min){ g++; up++; }
  if(!up) return;
  S.jobGrade = g;
  const max = g === JOB_GRADES.length-1;
  logE(`<b>의뢰 등급 상승</b> — 누적 ${fmt(jobCount())}회. 의뢰 보수 <b style="color:var(--brass)">${fmt(jobPay())} G/일</b>${max? " (최대 등급)" : ""}`, "big");
  queueCeremony({type:"jobgrade", grade:g, max, year:S.year, phase:S.phase, week:S.week+1, count:jobCount()});
}'''
    new = '''/* 의뢰 등급은 의뢰처마다 따로 (1006) — 누적은 그 의뢰를 학생 한 명이 하루 마칠 때마다 1회(jobN), 등급은 S.jobG[의뢰처].
   예전에는 여섯 곳이 누적 하나(S.jobCount · S.jobGrade)를 같이 썼다 — 옛 세이브는 그때 등급을 모든 의뢰처의 바닥으로 남긴다.
   k 를 빼면 이번 주 의뢰 (weekJobPlan) */
function jobGMap(){
  if(!S.jobG){
    const g0 = clamp(S.jobGrade|0, 0, JOB_GRADES.length-1);
    S.jobG = {}; JOB_LIST.forEach(J=> S.jobG[J.k] = g0);
  }
  return S.jobG;
}
function jobKey(k){ return k || (weekJobPlan() || JOB_LIST[0]).k; }
function jobCount(k){ return jobN(jobKey(k)); }
function jobGradeIdx(k){ return clamp(jobGMap()[jobKey(k)]|0, 0, JOB_GRADES.length-1); }
function jobGrade(k){ return JOB_GRADES[jobGradeIdx(k)]; }
function jobUp(k){ return jobGrade(k).up * FOCUS_G / FOCUS_COND; }
function jobDown(k){ return jobGrade(k).down * FOCUS_G / FOCUS_COND; }
function tryJobGrade(){
  JOB_LIST.forEach(J=>{
    let g = jobGradeIdx(J.k), up = 0;
    while(g+1 < JOB_GRADES.length && jobN(J.k) >= JOB_GRADES[g+1].min){ g++; up++; }
    if(!up) return;
    jobGMap()[J.k] = g;
    const max = g === JOB_GRADES.length-1;
    logE(`<b>의뢰 등급 상승 · ${esc(J.n)}</b> — 누적 ${fmt(jobN(J.k))}회. 보수 <b style="color:var(--brass)">${fmt(jobPay(J.k))} G/일</b>${max? " (최대 등급)" : ""}`, "big");
    queueCeremony({type:"jobgrade", k:J.k, grade:g, max, year:S.year, phase:S.phase, week:S.week+1, count:jobN(J.k)});
  });
}'''
    src = sub1(src, old, new, 'function jobGMap(){')
    old = '''function jobGradeCeremony(c){
  const G = JOB_GRADES[c.grade] || jobGrade();
  return `<div class="cerhead">
      <div class="eyebrow">${yrName(c.year)} ${(PHASES[c.phase]||PHASES.spring).n} ${c.week}주를 마치고 · 누적 의뢰 ${fmt(c.count)}회</div>
      <h2 style="font-size:24px;margin-top:2px">의뢰 등급 상승</h2>'''
    new = '''function jobGradeCeremony(c){
  const J = c.k ? jobDef(c.k) : null, G = JOB_GRADES[c.grade] || jobGrade(c.k);   // 1006 — 의뢰처마다 (옛 팝업은 c.k 가 없다)
  return `<div class="cerhead">
      <div class="eyebrow">${yrName(c.year)} ${(PHASES[c.phase]||PHASES.spring).n} ${c.week}주를 마치고 · ${J? `${esc(J.n)} 누적` : "누적 의뢰"} ${fmt(c.count)}회</div>
      <h2 style="font-size:24px;margin-top:2px">${J? `${esc(J.n)} — ` : ""}의뢰 등급 상승</h2>'''
    src = sub1(src, old, new, 'const J = c.k ? jobDef(c.k) : null, G = JOB_GRADES[c.grade]')
    src = sub1(src, 'function jobPay(){ return jobGrade().pay; }', 'function jobPay(k){ return jobGrade(k).pay; }', 'function jobPay(k){')
    # ── 이번 주 의뢰를 미리 ──
    old = '''/* 이번 주 의뢰 — 처음 의뢰가 나온 순간 정한다. 배경은 시설 배경 중 하나 (보여주기용이라 게임 난수는 쓰지 않는다)
   처음 의뢰를 하는 여섯 주 (1003) — 아직 한 번도 해 보지 않은 의뢰처에서만 고른다. 의뢰처 수만큼이라 여섯 곳을 한 번씩 다 돈 뒤로는 무작위.
   '해 봤다' 는 의뢰처별 누적(jobN)이 1 이상 — 그 주에 아무도 못 했으면 다음에도 새 의뢰처로 남는다 */
const JOB_FRESH_WEEKS = JOB_LIST.length;
function weekJob(day){
  const R = UI.wrun;
  if(!R) return JOB_LIST[0];
  if(!R.job){
    const tried = JOB_LIST.filter(j=> jobN(j.k) > 0).length;
    const fresh = tried < JOB_FRESH_WEEKS ? JOB_LIST.filter(j=> jobN(j.k) === 0) : [];
    R.job = pick(fresh.length ? fresh : JOB_LIST).k; R.jobDay = day;
    R.jobFac = "job_" + R.job;
  }
  return jobDef(R.job);
}'''
    new = '''/* 이번 주 의뢰 (1006) — 주를 시작하기 전에 정해 둔다. 스케줄 화면에 미리 보이고(의뢰 쪽지 · 개인 행동), 세이브에 남아 다시 열어도 같다.
   주가 끝나면(weekRunEnd) 다음 주 의뢰를 바로 정한다. 계절 마무리 주(S.week = 그 계절 주 수)에는 의뢰가 없다.
   처음 의뢰를 하는 여섯 주 (1003) — 아직 한 번도 해 보지 않은 의뢰처에서만 고른다. 의뢰처 수만큼이라 여섯 곳을 한 번씩 다 돈 뒤로는 무작위.
   '해 봤다' 는 의뢰처별 누적(jobN)이 1 이상 — 그 주에 아무도 못 했으면 다음에도 새 의뢰처로 남는다 */
const JOB_FRESH_WEEKS = JOB_LIST.length;
function weekJobPlan(){
  if(!S || !jobOpen() || !PHASES[S.phase] || S.week >= PHASES[S.phase].weeks) return null;
  const at = `${S.year}-${S.phase}-${S.week}`;
  if(!S.jobWk || S.jobWk.at !== at || !JOB_LIST.some(j=> j.k === S.jobWk.k)){
    const tried = JOB_LIST.filter(j=> jobN(j.k) > 0).length;
    const fresh = tried < JOB_FRESH_WEEKS ? JOB_LIST.filter(j=> jobN(j.k) === 0) : [];
    S.jobWk = {at, k:pick(fresh.length ? fresh : JOB_LIST).k};
    try{ localStorage.setItem(SAVE_KEY, JSON.stringify(S)); }catch(e){}   // 정하자마자 남긴다 — 다시 열어 의뢰를 바꿀 수 없게
  }
  return jobDef(S.jobWk.k);
}
function weekJob(day){
  const R = UI.wrun, J = weekJobPlan() || JOB_LIST[0];
  if(!R) return J;
  if(!R.job){ R.job = J.k; R.jobDay = day; R.jobFac = "job_" + R.job; }   // 주간 보고 — 처음 의뢰가 나온 날에 의뢰 소개
  return jobDef(R.job);
}'''
    src = sub1(src, old, new, 'function weekJobPlan(){')
    old = '''  trainStudent(st, {id:"job", n:J.n, fac:null, cond:0, gains:{[J.up]:jobUp()}}, true, {noExp:true, noRecover:true});
  st.ment[J.down] = Math.max(1, (st.ment[J.down]||0) - 2.4*jobDown()*rnd(.7,1.35));
  S.jobCount = jobCount() + 1;
  (S.jobN = S.jobN || {})[J.k] = jobN(J.k) + 1;
  setCond(st, st.cond - JOB_COND);
  const g0 = S.gold; addGold(jobPay());'''
    new = '''  trainStudent(st, {id:"job", n:J.n, fac:null, cond:0, gains:{[J.up]:jobUp(J.k)}}, true, {noExp:true, noRecover:true});
  st.ment[J.down] = Math.max(1, (st.ment[J.down]||0) - 2.4*jobDown(J.k)*rnd(.7,1.35));
  S.jobCount = (S.jobCount|0) + 1;                   // 모든 의뢰를 합친 누적 (기록용 · 1006 부터 등급은 의뢰처별 jobN)
  (S.jobN = S.jobN || {})[J.k] = jobN(J.k) + 1;
  setCond(st, st.cond - JOB_COND);
  const g0 = S.gold; addGold(jobPay(J.k));'''
    src = sub1(src, old, new, 'gains:{[J.up]:jobUp(J.k)}')
    # 주가 끝나면 다음 주 의뢰를 정해 두고 저장한다
    old = '''  const finish = ()=>{
    tryMarkTut();
    levelReport(S.students.map(s=>({s:s, n:s._up||0})));'''
    new = '''  const finish = ()=>{
    try{ weekJobPlan(); }catch(e){}                 // 다음 주 의뢰 — 미리 정해 둔다 (1006)
    tryMarkTut();
    levelReport(S.students.map(s=>({s:s, n:s._up||0})));'''
    src = sub1(src, old, new, 'try{ weekJobPlan(); }catch(e){}')
    # 주간 보고의 의뢰 소개 (숨긴 줄)
    src = sub1(src, '컨디션 -${JOB_COND}/일 · 보수 ${fmt(jobPay())} G/일</div></div></div>', '컨디션 -${JOB_COND}/일 · 보수 ${fmt(jobPay(J.k))} G/일</div></div></div>', '보수 ${fmt(jobPay(J.k))} G/일</div></div></div>')
    # 학생 화면 — 개인 행동 고르기
    src = sub1(src, 'k==="job"? `보수 ${fmt(jobPay())}G/일 · 컨디션 -${JOB_COND}/일` : ACT[k].d}</option>',
               'k==="job"? `${esc((weekJobPlan()||{n:"의뢰"}).n)} · 보수 ${fmt(jobPay())}G/일 · 컨디션 -${JOB_COND}/일` : ACT[k].d}</option>',
               '${esc((weekJobPlan()||{n:"의뢰"}).n)} · 보수')
    src = sub1(src, ': actShown(s)==="job"? `그 주의 의뢰를 오후에 수행한다. 멘탈리티 하나가 조금 오르고 하나는 내린다.`',
               ': actShown(s)==="job"? ((J)=> J? `이번 주 의뢰 <b>${esc(J.n)}</b> — 오후에 수행한다 · <b style="color:var(--ok)">${mentName(J.up)} ▲</b> · <b style="color:var(--bad)">${mentName(J.down)} ▼</b>` : `그 주의 의뢰를 오후에 수행한다.`)(weekJobPlan())',
               '이번 주 의뢰 <b>${esc(J.n)}</b> — 오후에 수행한다')
    # 예전 화면 — 행동별 요약(숨긴 칸)
    old = ': `그 주 처음 나온 의뢰를 수행 · 보수 ${fmt(jobPay())} G/일 · 컨디션 -${JOB_COND}/일 · 멘탈리티 하나 소폭 증가, 하나 하락 · 의뢰 ${jobGradeIdx()+1}등급 (누적 ${fmt(jobCount())}회${jobGradeIdx()+1<JOB_GRADES.length? ` · 다음 등급 ${fmt(JOB_GRADES[jobGradeIdx()+1].min)}회` : " · 최대"})`;'
    new = ': ((J)=> `이번 주 의뢰 ${esc(J.n)} · 보수 ${fmt(jobPay(J.k))} G/일 · 컨디션 -${JOB_COND}/일 · ${mentName(J.up)} ▲ · ${mentName(J.down)} ▼ · ${jobGradeIdx(J.k)+1}등급 (누적 ${fmt(jobN(J.k))}회${jobGradeIdx(J.k)+1<JOB_GRADES.length? ` · 다음 등급 ${fmt(JOB_GRADES[jobGradeIdx(J.k)+1].min)}회` : " · 최대"})`)(weekJobPlan() || JOB_LIST[0]);'
    src = sub1(src, old, new, ': ((J)=> `이번 주 의뢰 ${esc(J.n)} · 보수')
    # 예전 화면 — 개인 행동 칸 위에 이번 주 의뢰
    old = '''    ${(()=>{ const hurt=S.students.filter(isInjured); if(!hurt.length) return "";'''
    new = '''    ${(()=>{ const J = weekJobPlan(); if(!J) return "";   // 이번 주 의뢰 (1006) — 주를 시작하기 전에 정해 둔다
      const g = jobGradeIdx(J.k), nx = JOB_GRADES[g+1];
      return `<div class="opt" style="cursor:default;border-color:var(--brass);margin-bottom:10px">
        <div class="on" style="color:var(--brass)">이번 주 의뢰 · ${esc(J.n)}<span class="price" style="color:var(--brass)">${g+1}등급 · ${fmt(jobPay(J.k))} G/일</span></div>
        <div class="od">${esc(J.who)} — <b style="color:var(--ok)">${mentName(J.up)} ▲</b> · <b style="color:var(--bad)">${mentName(J.down)} ▼</b> · 컨디션 -${JOB_COND}/일</div>
        <div class="od" style="color:var(--dim)">누적 ${fmt(jobN(J.k))}${nx? ` / ${fmt(nx.min)}회` : "회 · 최대 등급"} — 의뢰처마다 따로 쌓인다</div></div>`; })()}
''' + old
    src = sub1(src, old, new, '// 이번 주 의뢰 (1006) — 주를 시작하기 전에 정해 둔다\n')
    # 안내 13 — 의뢰
    old = '["보수와 멘탈리티 변화", `의뢰 하루마다 컨디션이 ${JOB_COND} 줄고 보수 ${fmt(jobPay())} G를 받아요. 의뢰처에 따라 멘탈리티 하나는 오르고 하나는 내려가요.`],["반복할수록 커지는 보너스", `누적 ${fmt(JOB_GRADES[1].min)}회 · ${fmt(JOB_GRADES[2].min)}회를 넘기면 의뢰 등급이 올라 보수가 하루 ${fmt(JOB_GRADES[1].pay)} G · ${fmt(JOB_GRADES[2].pay)} G로 늘어요.'
    new = '["보수와 멘탈리티 변화", `의뢰 하루마다 컨디션이 ${JOB_COND} 줄고 보수(처음 ${fmt(JOB_GRADES[0].pay)} G)를 받아요. 이번 주 의뢰는 주를 시작하기 전에 정해져서, 진행 화면에서 오르는 멘탈리티와 내리는 멘탈리티를 미리 볼 수 있어요.`],["반복할수록 커지는 보너스", `의뢰처마다 누적 ${fmt(JOB_GRADES[1].min)}회 · ${fmt(JOB_GRADES[2].min)}회를 넘기면 그 의뢰의 등급이 올라 보수가 하루 ${fmt(JOB_GRADES[1].pay)} G · ${fmt(JOB_GRADES[2].pay)} G로 늘어요. 누적은 의뢰처마다 따로 쌓여요.'
    src = sub1(src, old, new, '이번 주 의뢰는 주를 시작하기 전에 정해져서')
    old = '''      const gi=jobGradeIdx();
      const cl=JOB_LIST.map(J=>{ const n=jobN(J.k), lv=jobEvLv(J.k), done=lv>=JOB_EV_AT.length;
        return `<div class="tg-client${done?" done":""}"><span class="tg-cface">${jobFaceHTML(J)}</span><b>${esc(J.n)}</b><small>${done?"단골":`${fmt(n)} / ${fmt(JOB_EV_AT[lv])}회`}</small></div>`; }).join("");
      const gr=JOB_GRADES.map((G,i)=>`<span class="${i===gi?"on":""}"><b>${i+1}등급</b>${i?`누적 ${fmt(G.min)}회`:"처음"}<em>${fmt(G.pay)} G/일</em></span>`).join(`<i aria-hidden="true">→</i>`);
      return `<div class="tg-caption">의뢰처 여섯 곳 · 지금까지 도운 횟수</div><div class="tg-clients">${cl}</div><p class="tg-caption">${JOB_EV_AT[0]}회 · ${JOB_EV_AT[1]}회를 채운 의뢰처는 의뢰인이 보답해요. 새 상점이나 식단이 열리고, 값이 싸지기도 해요.</p><div class="tg-grade">${gr}</div><p class="tg-caption">의뢰 등급 · 지금 누적 ${fmt(jobCount())}회</p>`; }'''
    new = '''      const cl=JOB_LIST.map(J=>{ const n=jobN(J.k), lv=jobEvLv(J.k), done=lv>=JOB_EV_AT.length;   // 1006 — 등급도 의뢰처마다
        return `<div class="tg-client${done?" done":""}"><span class="tg-cface">${jobFaceHTML(J)}</span><b>${esc(J.n)}</b><small>${jobGradeIdx(J.k)+1}등급 · ${done?"단골":`${fmt(n)} / ${fmt(JOB_EV_AT[lv])}회`}</small></div>`; }).join("");
      const gr=JOB_GRADES.map((G,i)=>`<span><b>${i+1}등급</b>${i?`누적 ${fmt(G.min)}회`:"처음"}<em>${fmt(G.pay)} G/일</em></span>`).join(`<i aria-hidden="true">→</i>`);
      return `<div class="tg-caption">의뢰처 여섯 곳 · 지금 등급과 도운 횟수</div><div class="tg-clients">${cl}</div><p class="tg-caption">${JOB_EV_AT[0]}회 · ${JOB_EV_AT[1]}회를 채운 의뢰처는 의뢰인이 보답해요. 새 상점이나 식단이 열리고, 값이 싸지기도 해요.</p><div class="tg-grade">${gr}</div><p class="tg-caption">의뢰 등급 · 의뢰처마다 따로 쌓여요</p>`; }'''
    src = sub1(src, old, new, '<p class="tg-caption">의뢰 등급 · 의뢰처마다 따로 쌓여요</p>')
    return src


if __name__ == "__main__":
    path = sys.argv[1]
    raw = open(path, encoding="utf-8", newline="").read()
    crlf = "\r\n" in raw
    src = apply(raw.replace("\r\n", "\n"))
    if crlf: src = src.replace("\n", "\r\n")
    open(path, "w", encoding="utf-8", newline="").write(src)
    print("job applied", len(raw), "->", len(src))
