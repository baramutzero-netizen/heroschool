/* Weekly scenes are immutable presentation records. Playback never runs training. */
function reportRecord(day, tr, bonus, phase, before, members, status, logStart, extra){
  if(!UI.wrun) return;
  const groups = {};
  members.forEach(s=>{
    const fac = extra?.facility || (phase==="pm" ? FOCUS_FAC[s.focus] : status[s.id]==="rest" ? "infirm" : tr.fac) || "gym";
    (groups[fac] ||= []).push(s);
  });
  const scenes = UI.wrun.scenes ||= [];
  Object.entries(groups).forEach(([facility, group])=> scenes.push({
    day, season:UI.wrun.startPhase || S.phase, training:tr.n, trainingId:tr.id, color:cardColor(UI.wrun.days?.[day] || tr.id).c, bonus, phase, facility,
    logs:DAYLOG.slice(logStart), reward:extra?.reward || "",
    students:group.map(s=>{
      const old=before[s.id], changes=[];
      if(old){
        MENTAL.forEach(m=>{
          if(m.k==="pot")return;
          const from=Math.round(old.ment[m.k]), to=Math.round(s.ment[m.k]), d=to-from;
          if(d) changes.push({label:m.n,from,to,value:d,kind:d>0?"gain":"loss"});
        });
        const cond=Math.round(s.cond)-Math.round(old.cond);
        if(cond)changes.push({label:"컨디션",from:Math.round(old.cond),to:Math.round(s.cond),value:cond,kind:cond>0?"heal":"loss"});
        const xp=Math.round(s.totalExp||0)-Math.round(old.exp);
        if(xp)changes.push({label:"경험",from:Math.round(old.exp),to:Math.round(s.totalExp||0),value:xp,kind:"exp"});
      }
      return {id:s.id,name:s.name,job:s.job,palette:sprPalOf(s),focus:s.focus,condition:{from:Math.round(old?.cond ?? s.cond),to:Math.round(s.cond)},
        state:status[s.id] || (phase==="pm"?"focus":"returned"),changes};
    })
  }));
}

// All rooms use the same 3:1 viewport. Only the vertical crop origin differs.
const REPORT_LAYOUTS = {
  library:{crop:.235, slots:[[12,79],[45,42],[63,47],[79,73],[88,84]]},
  gym:{crop:.255, slots:[[14,75],[34,48],[52,29],[77,81],[90,84]]},
  arena:{crop:.215, slots:[[20,65],[46,25],[72,57],[80,69],[89,81]]},
  hall:{crop:0, slots:[[53,42],[67.5,57],[82.3,71],[41.2,66],[55.8,78]]},
  chapel:{crop:.255, slots:[[12,76],[20,63],[27,52],[73,52],[80,63],[88,76]]},
  infirm:{crop:.195, slots:[[17,63],[36,42],[66,51]]},
  beach:{crop:0, capacity:5, slots:[[19,75],[35,54],[51,80],[67,55],[83,78],[19,48],[35,80],[51,51],[67,81],[83,51]]}
};
function reportBeachPositions(){
  // Presentation-only randomness; never consume the simulation's random stream.
  const slots=REPORT_LAYOUTS.beach.slots, keys=crypto.getRandomValues(new Uint32Array(slots.length));
  const candidates=slots.map((slot,i)=>({slot,key:keys[i]})).sort((a,b)=>a.key-b.key), chosen=[];
  for(const {slot} of candidates){
    // One position per column keeps sprites and growth labels from overlapping.
    if(chosen.every(p=>Math.abs(p[0]-slot[0])>=12))chosen.push(slot);
    if(chosen.length===REPORT_LAYOUTS.beach.capacity)break;
  }
  return chosen;
}
// Keep full records for the text report, but never tour every focus/rest facility.
function reportScenesForPlayback(records){
  const out=[];
  [...new Set(records.map(s=>s.day))].sort((a,b)=>a-b).forEach(day=>{
    let daily=records.filter(s=>s.day===day);
    // Merge summer training/rest groups into one beach per phase, without changing gains.
    const summer=daily.filter(s=>s.season==="summer" && s.phase!=="exped");
    if(summer.length){
      daily=daily.filter(s=>!summer.includes(s));
      for(const phase of ["am","pm"]){
        const group=summer.filter(s=>s.phase===phase);
        if(group.length)daily.push({...group[0],facility:"beach",
          students:group.flatMap(s=>s.students.map(x=>({...x,trainingFacility:s.facility}))) });
      }
    }
    const morning=daily.filter(s=>s.phase!=="pm"), afternoon=daily.filter(s=>s.phase==="pm");
    const choose=list=>list.slice().sort((a,b)=>b.students.length-a.students.length)[0];
    const am=morning.find(s=>s.phase==="exped") || choose(morning.filter(s=>s.students.some(x=>x.state!=="rest"))) || choose(morning);
    const pm=choose(afternoon);
    if(am)out.push(am);
    if(pm)out.push(pm);
  });
  return out;
}

function reportSceneShell(records, dlg){
  const scenes=reportScenesForPlayback(records);
  if(!scenes.length)return dlg.length ? `<div class="daylog">${dlg.map(x=>`<div class="on dlline ${x.k}">${x.t}</div>`).join("")}</div>` : "";
  return `<section class="dr-player" aria-label="요일별 경과 보고">
    <nav class="dr-days" aria-label="요일 선택">${DAY_N.slice(0,5).map((n,d)=>{
      const list=scenes.filter(s=>s.day===d), first=list[0];
      return `<button type="button" data-dr-day="${d}" style="--day-color:${first?.color||cardColor(first?.trainingId).c}" ${!first?"disabled":""}><span>${n}요일 <i></i></span><strong>${esc(first?.training||"기록 없음")}</strong>${first?.bonus?`<em>+${Math.round(first.bonus*100)}%</em>`:""}</button>`;
    }).join("")}</nav>
    <div class="dr-stage" id="drStage"><img class="dr-room" id="drRoom" alt="" draggable="false">
      <div class="dr-top"><div><span class="dr-eyebrow">오늘의 학원</span><h3 id="drFacility"></h3><span id="drActivity"></span></div><span class="dr-chain" id="drChain"></span></div>
      <div id="drStudents"></div><div class="dr-bottom"><span id="drSceneCount"></span><span>학생을 누르면 성장 내역을 볼 수 있어요</span></div>
    </div>
    <nav class="dr-phases" id="drPhases" aria-label="훈련 장면 선택"></nav>
    <div class="dr-result" aria-live="polite"><div><b id="drResultTitle"></b><span id="drResultHint"></span></div><div id="drResultChips"></div></div>
    <div class="dr-controls"><div><button class="btn sm" id="drPlay">일시정지</button><button class="btn sm" id="drPrev" aria-label="이전 장면">‹</button><button class="btn sm" id="drNext" aria-label="다음 장면">›</button>${[1,2,6].map(n=>`<button class="btn sm" data-dr-speed="${n}">×${n}</button>`).join("")}<button class="btn sm" id="dlSkip">한 번에 보기</button></div><span id="drProgress"></span></div>
    <details class="dr-details" id="drDetail"><summary>이 장면의 전체 학생 · 성장 내역</summary><div id="drDetailBody"></div></details>
    <div id="drFullLog" hidden><h3>주간 전체 기록</h3><div class="daylog">${dlg.map(x=>`<div class="on ${x.k==="gap"?"dlgap":"dlline "+x.k}">${x.t}</div>`).join("")}</div></div>
  </section>`;
}

function reportPlayerStop(){
  if(UI._reportPlayer){UI._reportPlayer.dispose();UI._reportPlayer=null;}
  if(UI._dlT){clearTimeout(UI._dlT);UI._dlT=null;}
}
function reportConditionColor(value){return value<=39?"critical":value<=69?"tired":"healthy";}
function reportStatQueue(students){
  const queue=[];
  if(students.some(s=>s.condition && s.condition.to>s.condition.from))
    queue.push({condition:true,recovery:true,from:0,to:1});
  students.forEach((student,index)=>{
    const condition=student.condition;
    if(condition && condition.to<condition.from)queue.push({index,condition:true,...condition});
    student.changes.filter(c=>c.label!=="컨디션" && c.kind!=="exp" && c.label!=="경험" && Number.isInteger(c.from) && Number.isInteger(c.to) && c.from!==c.to)
      .forEach(change=>queue.push({index,...change}));
  });
  return queue;
}
function reportSceneBind(records){
  const scenes=reportScenesForPlayback(records);
  if(!scenes.length || !$("#drStage"))return;
  const root=$("#modalRoot"), reduced=matchMedia("(prefers-reduced-motion: reduce)").matches;
  root.querySelector(".modal").classList.add("dr-modal");
  const confirm=$("#repOk"), oldConfirmRow=confirm?.parentElement;
  if(confirm){
    confirm.classList.add("sm");
    $("#dlSkip").insertAdjacentElement("afterend",confirm);
    if(oldConfirmRow && !oldConfirmRow.children.length)oldConfirmRow.remove();
  }
  let at=0, speed=[1,2,6].includes(PREF.reportSpeed)?PREF.reportSpeed:2, paused=reduced, full=false, elapsed=0, last=performance.now(), timer=null, disposed=false;
  let duration=2400, queue=[], displayed=[], lastSound=-1;
  const stepMs=450, leadMs=250, riseMs=900/0.7, cardMs=400+riseMs, fadeMs=100, fadeDelayMs=cardMs-fadeMs;
  const statAudio=new Audio(REPORT_STATUP);
  const recoveryAudio=new Audio(REPORT_RECOVERY);
  const reportAudio=[statAudio,recoveryAudio];
  reportAudio.forEach(audio=>audio.preload="auto");
  function silence(){reportAudio.forEach(audio=>{audio.pause();audio.currentTime=0;});}
  const placements=new Map();
  const phaseName=s=>s.phase==="exped"?"오전 원정":s.phase==="pm"?"오후 집중":s.students.every(x=>x.state==="rest")?(s.facility==="beach"?"오전 일광욕":"오전 휴식"):"오전 훈련";
  const chip=c=>`<span class="dr-chip ${c.kind}">${esc(c.label)} ${c.value>0?"+":""}${c.value}</span>`;
  const stateName=s=>s.state==="failed"?"실패 · 성과 25%":s.state==="rest"?"휴식":s.state==="focus"?"집중 훈련":s.state==="returned"?"원정 귀환":"훈련 완료";
  const player={dispose(){disposed=true;clearInterval(timer);silence();reportAudio.forEach(audio=>{audio.removeAttribute("src");audio.load();});},get index(){return at;},get paused(){return paused;}};
  UI._reportPlayer=player;
  function sync(){
    $("#drPlay").textContent=at===scenes.length-1&&elapsed>=duration?"다시 보기":paused?"재생":"일시정지";
    $("#drPrev").disabled=at===0;$("#drNext").disabled=at===scenes.length-1;
    root.querySelectorAll("[data-dr-speed]").forEach(b=>{b.classList.toggle("primary",+b.dataset.drSpeed===speed);b.setAttribute("aria-pressed",String(+b.dataset.drSpeed===speed));});
    $("#drStage").classList.toggle("paused",paused);
    if(paused)silence();
    root.querySelectorAll("#drStudents canvas").forEach(c=>{if(paused && +c.dataset.m!==SPR_M.down)c.dataset.still="1";else delete c.dataset.still;});
  }
  function details(id){
    const s=scenes[at];
    $("#drDetailBody").innerHTML=s.students.map(x=>`<div class="dr-student-row ${id===x.id?"selected":""}" data-dr-id="${esc(String(x.id))}"><b>${esc(x.name)}</b>${roleTag(x.job)}<small>${stateName(x)}</small><div>${x.changes.map(chip).join("")||"별도 성장 기록 없음"}</div></div>`).join("");
    if(s.reward)$("#drDetailBody").insertAdjacentHTML("afterbegin",`<p>${esc(s.reward)}</p>`);
    if(id){paused=true;sync();$("#drDetail").open=true;const row=Array.from(root.querySelectorAll(".dr-student-row")).find(el=>el.dataset.drId===String(id));row?.scrollIntoView({block:"nearest",behavior:reduced?"instant":"smooth"});}
  }
  function draw(){
    const s=scenes[at], day=scenes.filter(x=>x.day===s.day), offset=(s.day*3)%Math.max(1,s.students.length);
    const layout=REPORT_LAYOUTS[s.facility] || REPORT_LAYOUTS.gym;
    const visible=s.students.slice(offset).concat(s.students.slice(0,offset)).slice(0,layout.capacity || layout.slots.length);
    displayed=visible;queue=reportStatQueue(visible);lastSound=-1;silence();
    duration=Math.max(2400,leadMs+queue.length*stepMs+cardMs);
    const source=REPORT_ROOMS[s.facility];
    if($("#drRoom").getAttribute("src")!==source)$("#drRoom").src=source;
    const facilityName=s.facility==="beach"?"해수욕장":FACILITIES[s.facility]?.n||"학원";
    $("#drRoom").alt=s.facility==="beach"?"여름 해수욕장 모래사장":`${facilityName} 실내`;
    $("#drStage").dataset.phase=s.phase;
    $("#drStage").dataset.facility=s.facility;
    $("#drStage").style.setProperty("--crop-top",`${-layout.crop*312.5}%`);
    $("#drStage").style.setProperty("--sprite-unit",`${layout.scale || 1050}px`);
    $("#drFacility").textContent=facilityName;
    $("#drActivity").textContent=`${DAY_N[s.day]}요일 · ${phaseName(s)}${s.phase==="pm"?"":" · "+s.training}`;
    $("#drChain").textContent=s.bonus?`+${Math.round(s.bonus*100)}% 체인`:"";
    $("#drChain").hidden=!s.bonus;
    root.querySelectorAll("[data-dr-day]").forEach(b=>{const d=+b.dataset.drDay;b.classList.toggle("current",d===s.day);b.classList.toggle("done",d<s.day);b.setAttribute("aria-current",d===s.day?"step":"false");b.querySelector("i").textContent=d<s.day?"✓":"";});
    $("#drPhases").innerHTML=day.map(x=>`<button class="${x===s?"active":""}" data-dr-scene="${scenes.indexOf(x)}" aria-pressed="${x===s}">${phaseName(x)}${day.length>2?" · "+(FACILITIES[x.facility]?.n||""):""}</button>`).join("");
    root.querySelectorAll("[data-dr-scene]").forEach(b=>b.onclick=()=>seek(+b.dataset.drScene));
    if(s.facility==="beach" && !placements.has(s))placements.set(s,reportBeachPositions());
    const pos=placements.get(s) || layout.slots;
    $("#drStudents").innerHTML=visible.map((x,i)=>{
      const studying=s.facility==="hall" && !!REPORT_STUDY[x.job];
      const resting=s.facility==="infirm" || (s.facility==="beach" && x.state==="rest");
      const motion=resting?"down":x.state==="rest"?"idle":x.state==="failed"?"hit":["gym","hall","arena"].includes(x.trainingFacility || s.facility)?"attack":"idle";
      const cond=x.condition?.from ?? 100;
      return `<button class="dr-student ${studying?"studying":""} ${resting?"resting":""} ${pos[i][1]<48?"low-bubble":""}" data-dr-student="${i}" style="left:${pos[i][0]}%;top:${pos[i][1]}%;z-index:${Math.round(pos[i][1])}" aria-label="${esc(x.name)} 성장 내역"><span class="dr-shadow"></span><span class="dr-avatar">${studying?`<span class="dr-study-sprite" data-study-job="${x.job}" style="background-image:url(${REPORT_STUDY[x.job]})"></span>`:sprHTML(x.job,motion,1,{p:x.palette,flip:resting?i!==2:i%2===1,t0:resting?0:performance.now()})}</span><span class="dr-name">${esc(x.name)}</span><span class="dr-condition ${reportConditionColor(cond)}" role="meter" aria-label="컨디션" aria-valuemin="0" aria-valuemax="100" aria-valuenow="${cond}"><span class="dr-condition-fill" style="width:${clamp(cond,0,100)}%"></span><span class="dr-condition-number">${cond}</span></span><span class="dr-bubbles" hidden></span></button>`;
    }).join("");
    if(s.facility==="hall"){
      $("#drStudents").insertAdjacentHTML("beforeend",pos.slice(visible.length).map(p=>`<div class="dr-student studying empty-seat" aria-hidden="true" style="left:${p[0]}%;top:${p[1]}%;z-index:${Math.round(p[1])}"><span class="dr-avatar"><span class="dr-study-sprite empty" style="background-image:url(${REPORT_STUDY.empty})"></span></span></div>`).join(""));
    }
    root.querySelectorAll("[data-dr-student]").forEach(b=>b.onclick=()=>details(visible[+b.dataset.drStudent].id));
    $("#drSceneCount").textContent=`${visible.length}명 표시${s.students.length>visible.length?` · 시설 참여 ${s.students.length}명`:""}`;
    $("#drResultTitle").textContent=`${DAY_N[s.day]}요일 · ${s.phase==="pm"?"개인 집중 훈련":s.training}`;
    const fail=s.students.filter(x=>x.state==="failed").length;
    $("#drResultHint").textContent=`${phaseName(s)} · ${s.students.length}명${fail?` · 실패 ${fail}명`:""}`;
    const totals={};s.students.forEach(x=>x.changes.forEach(c=>{totals[c.label]=(totals[c.label]||0)+c.value;}));
    $("#drResultChips").innerHTML=s.reward?`<span>${esc(s.reward)}</span>`:Object.entries(totals).map(([label,value])=>chip({label:`${label} 합계`,value:Math.round(value*10)/10,kind:value<0?"loss":label==="컨디션"?"heal":"gain"})).join("")||`<span class="hint">오늘의 기록을 차곡차곡 쌓았어요.</span>`;
    details();sync();timeline(false);progress();
  }
  function timeline(sound){
    const n=Math.floor((elapsed-leadMs)/stepMs);
    root.querySelectorAll(".dr-study-sprite[data-study-job]").forEach((el,i)=>{
      const frame=reduced?0:Math.floor(elapsed/360+i*.7)%4;
      el.style.backgroundPosition=`${frame*100/3}% 0`;el.dataset.frame=frame;
    });
    root.querySelectorAll(".dr-bubbles").forEach(el=>{el.hidden=true;el.innerHTML="";});
    displayed.forEach((student,index)=>{
      const cond=student.condition;if(!cond)return;
      const qi=queue.findIndex(e=>e.condition && (cond.to>cond.from?e.recovery:e.index===index));
      const fraction=qi<0?1:clamp((elapsed-leadMs-qi*stepMs)/stepMs,0,1);
      const value=Math.round(cond.from+(cond.to-cond.from)*fraction);
      const bar=root.querySelector(`[data-dr-student="${index}"] .dr-condition`);
      bar.className=`dr-condition ${reportConditionColor(value)}`;bar.setAttribute("aria-valuenow",String(value));
      bar.title=`컨디션 ${cond.from} → ${cond.to}`;
      bar.querySelector(".dr-condition-fill").style.width=`${clamp(value,0,100)}%`;
      bar.querySelector(".dr-condition-number").textContent=value;
    });
    const bounds=$("#drStage").getBoundingClientRect();
    for(let q=Math.max(0,n-Math.ceil(cardMs/stepMs));q<=Math.min(n,queue.length-1);q++){
      const event=queue[q], age=elapsed-leadMs-q*stepMs;
      if(event.condition || age<0 || age>=cardMs)continue;
      const popup=root.querySelector(`[data-dr-student="${event.index}"] .dr-bubbles`);
      popup.hidden=false;popup.style.marginLeft="0px";popup.style.marginTop="0px";
      const positive=event.to>event.from;
      popup.insertAdjacentHTML("beforeend",`<span class="dr-stat-card ${positive?"up":"down"}" data-stat-event="${q}"><span class="dr-stat-label">${esc(event.label)}</span><span class="dr-stat-from">${mentalGradeHTML(event.from)}${event.from}</span><span class="dr-stat-arrow">→</span><b class="dr-stat-to">${mentalGradeHTML(event.to)}${event.to}</b></span>`);
      const card=popup.lastElementChild, rect=card.getBoundingClientRect();
      const dx=Math.max(0,bounds.left+4-rect.left)-Math.max(0,rect.right-bounds.right+4);
      const baseY=Math.max(0,bounds.top+4-rect.top);
      const rise=Math.min((rect.height+3)*2,Math.max(0,rect.top+baseY-bounds.top-2));
      card.style.opacity=1-clamp((age-fadeDelayMs)/fadeMs,0,1);
      card.style.transform=`translate(calc(-50% + ${dx}px),${baseY-(reduced?0:rise*Math.min(age/riseMs,1))}px)`;
    }
    const event=queue[n];
    if(sound && n!==lastSound){
      lastSound=n;
      if(event && event.to>event.from && sfxGain()>0){
        const audio=event.condition?recoveryAudio:statAudio;
        audio.pause();audio.currentTime=0;audio.volume=sfxGain();audio.play().catch(()=>{});
      }
    }
  }
  function progress(){const s=scenes[at], list=scenes.filter(x=>x.day===s.day), local=list.indexOf(s);const p=(local+Math.min(1,elapsed/duration))/list.length;root.querySelector(`[data-dr-day="${s.day}"]`).style.setProperty("--progress",`${p*100}%`);$("#drProgress").textContent=`${at+1} / ${scenes.length} 장면`;}
  function seek(index){at=Math.max(0,Math.min(scenes.length-1,index));elapsed=0;last=performance.now();root.querySelectorAll("[data-dr-day]").forEach(b=>b.style.removeProperty("--progress"));draw();}
  $("#drPlay").onclick=()=>{if(elapsed>=duration&&at===scenes.length-1){seek(0);paused=false;}else paused=!paused;last=performance.now();sync();};
  $("#drPrev").onclick=()=>seek(at-1);$("#drNext").onclick=()=>seek(at+1);
  root.querySelectorAll("[data-dr-day]").forEach(b=>b.onclick=()=>{const i=scenes.findIndex(s=>s.day===+b.dataset.drDay);if(i>=0)seek(i);});
  root.querySelectorAll("[data-dr-speed]").forEach(b=>b.onclick=()=>{speed=+b.dataset.drSpeed;PREF.reportSpeed=speed;prefSave();sync();});
  $("#dlSkip").onclick=()=>{full=!full;paused=true;$("#drFullLog").hidden=!full;$("#dlSkip").textContent=full?"전체 기록 접기":"한 번에 보기";sync();if(full)$("#drFullLog").scrollIntoView({block:"start",behavior:reduced?"instant":"smooth"});};
  $("#drDetail").addEventListener("toggle",()=>{if($("#drDetail").open){paused=true;sync();}});
  timer=setInterval(()=>{const now=performance.now(),dt=Math.min(now-last,60);last=now;if(disposed||paused||document.hidden){if(document.hidden)silence();return;}if(!$("#drStage")){reportPlayerStop();return;}elapsed+=dt*speed;timeline(true);if(elapsed>=duration){if(at<scenes.length-1){seek(at+1);return;}elapsed=duration;paused=true;sync();}progress();},30);
  draw();
}
