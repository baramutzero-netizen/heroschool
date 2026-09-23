function chronArt(key,cls=''){return `<img class="chron-art ${cls}" src="${CHRONICLE_ART[key]}" alt="" aria-hidden="true" draggable="false">`;}
function chronRule(cls=''){return `<svg class="chron-rule ${cls}" viewBox="0 0 600 16" preserveAspectRatio="none" aria-hidden="true"><path d="M9 10 Q165 5 300 8 T589 7 M14 12 Q280 9 583 10"/><path d="M1 10l5-3 5 3-5 3z M589 7l5-3 5 3-5 3z"/></svg>`;}
function chronHeading(title,cls='',art='leaf'){return `<div class="chron-heading ${cls}">${chronArt(art,'chron-h-'+art)}<h3>${title}</h3>${chronRule()}</div>`;}
function chronTrainingArt(id){const map={basic:'weight',heavy:'weight',spar:'swords',mock:'swords',strike:'target',free:'target',tact:'books',study:'books',form:'books',medit:'leaf',deep:'leaf',rest:'cup',crest:'cup',exped:'map',camp:'target'};return chronArt(map[id]||'books','chron-training-art');}
function viewPlan(){
  const legacy=viewPlanClassic();
  if(!PREF.chronicleTest) return legacy;
  const t=document.createElement('template');t.innerHTML=legacy;
  const take=sel=>{const el=t.content.querySelector(sel);if(el&&sel==='#btnWeek'&&!el.disabled&&S.week<PHASES[S.phase].weeks)el.textContent='이번 주를 기록한다';return el?el.outerHTML:''};
  t.content.querySelectorAll('.handrow [data-card]').forEach(el=>{const c=(S.hand||[]).find(c=>c.u===Number(el.dataset.card));if(c){const tr=TR[c.t]||TR.free;el.title += ' · '+(tr.fx||[]).map(f=>f[0]+' '+(f[2]?'-':'+').repeat(f[1])).join(' · ')+' · '+cardEffLine(tr);}});
  const pages=Math.max(1,Math.ceil(S.students.length/15));
  UI.chroniclePage=clamp(UI.chroniclePage||0,0,pages-1);
  const students=S.students.slice(UI.chroniclePage*15,UI.chroniclePage*15+15);
  const slots=S.slots||[], ph=PHASES[S.phase];
  const days=DAY_N.map((day,i)=>{const c=slots[i],tr=c&&(TR[c.t]||TR.free),col=c&&cardColor(c),mk=c&&markOf(c),chain=chainOf(slots,i);
    return `<div class="dslot chron-day ${c?'filled':''}" data-slot="${i}" style="--day-color:${col?col.c:'#9c8972'}"><b class="chron-weekday">${day}</b>${c?`<div class="chron-entry" draggable="true" data-card="${c.u}" title="클릭하면 손패로 돌아갑니다"><strong>${esc(tr.n)}</strong>${chronTrainingArt(c.t)}<small>${esc(tr.d)}</small></div>`:'<span class="chron-empty">손패를 눌러 넣거나 이곳으로 끌어오세요</span>'}${(mk||chain)?`<span class="chron-tail">${mk?`<span class="chron-mark" style="background:${mk.c}" title="${esc(mk.d)}">${mk.i}</span>`:''}${chain?`<span class="chron-chain">능률 +${Math.round(chain*100)}%</span>`:''}</span>`:''}${chronRule('chron-day-rule')}</div>`}).join('');
  const focusControls=['btnFocusWeak','btnFocusStrong','btnFocusClear','btnRestAll','btnRest40','btnRest70','btnRestInj','btnFocusUndo','btnFocusPrev'];
  return `<section class="chronicle" style="--book-art:url('${CHRONICLE_BOOK}')"><div class="chron-pages"><div class="chron-page chron-left"><header class="chron-masthead">${chronArt('crest','chron-crest')}<div class="chron-title-block"><h2>${esc(S.acadName)} 운영 일지</h2>${chronRule('chron-title-rule')}<div class="chron-daterow"><p class="chron-date">${S.year}년차 · ${ph.n} · ${Math.min(S.week+1,ph.weeks)}주차${chronRule('chron-date-rule')}</p><p class="chron-motto">좋은 용사는<br>하루아침에 만들어지지 않는다.<br><span>— 그리고,</span><br><span>오늘도, 조금 더.</span>${chronArt('leaf')}</p></div></div></header><div class="chron-intro"><p class="chron-note">새로운 한 주가 시작되었다. ${chronArt('leaf')}</p></div><div class="chron-toolbar">${take('#btnAuto')}${take('#btnClearSlots')}${take('#btnRest')}</div>${chronHeading('이번 주의 계획','chron-plan-heading','quill')}<div class="chron-days">${days}</div>${chronHeading('손패 <small>'+((S.hand||[]).length)+'장</small>','chron-hand-heading','ink')}<div class="chron-hand-title">${take('#btnBookUse')}${take('#btnBook2')}</div>${take('.handrow')}<footer>${chronArt('purse','chron-purse')}<span>자금 <b>${fmt(S.gold)} G</b></span></footer></div><div class="chron-page chron-right"><header class="chron-focus-heading">${chronHeading('개인 집중 훈련','','watch')}<p>… 언젠가, 이 아이들이<br>세상을 더 좋은 곳으로 만들기를.</p></header><div class="chron-focus-tools">${focusControls.map(k=>take('#'+k)).join('')}</div><div class="chron-students">${students.map(s=>`<div class="chron-student"><button class="chron-person" data-sid="${esc(s.id)}">${faceHTML(s.job,s.name)}<strong>${esc(s.name)}</strong></button><small>${s.year}학년 · ${esc(JOBS[s.job].name)}</small><div class="chron-condition" title="컨디션 ${Math.round(s.cond)}"><i style="width:${clamp(s.cond,0,100)}%;background:${s.cond<40?'#b54a40':s.cond<70?'#ba8336':'#4d8a65'}"></i><span>${Math.round(s.cond)}</span></div><select data-chron-focus="${esc(s.id)}" aria-label="${esc(s.name)} 집중 목표">${[{k:'free',n:'지정 없음'},...MENTAL.filter(m=>!m.fixed),{k:'rest',n:'휴식'}].map(m=>`<option value="${m.k}" ${s.focus===m.k?'selected':''}>${m.n}</option>`).join('')}</select></div>`).join('')||'<p>아직 등록된 학생이 없습니다.</p>'}</div><div class="chron-pagination"><button data-chron-page="-1" ${UI.chroniclePage===0?'disabled':''}>이전</button><span>${UI.chroniclePage+1} / ${pages} · 전체 ${S.students.length}명</span><button data-chron-page="1" ${UI.chroniclePage+1>=pages?'disabled':''}>다음</button></div><div class="chron-condition-tools">${take('#btnWater2')}</div><div class="chron-seal-wrap">${take('#btnWeek')}</div></div></div>${chronArt('letter','chron-letter')}<nav class="chron-tabs"><button data-chron-nav="plan" aria-current="page">일지</button><button data-chron-nav="roster">학생</button><button data-chron-nav="facil">시설</button></nav></section>`;
}
function bindChronicle(){
  document.querySelectorAll('.chronicle [data-card]').forEach(el=>{el.tabIndex=0;el.setAttribute('role','button');el.onkeydown=e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();el.click();}};});
  const toggle=document.querySelector('#chronicleToggle');
  if(toggle)toggle.onchange=()=>{PREF.chronicleTest=toggle.checked;prefSave();render();};
  document.querySelectorAll('[data-chron-nav]').forEach(b=>b.onclick=()=>{UI.view=b.dataset.chronNav;render()});
  document.querySelectorAll('[data-chron-page]').forEach(b=>b.onclick=()=>{UI.chroniclePage=(UI.chroniclePage||0)+Number(b.dataset.chronPage);render()});
  document.querySelectorAll('[data-chron-focus]').forEach(el=>el.onchange=()=>{const st=S.students.find(s=>s.id===el.dataset.chronFocus);if(st){st.focus=el.value;save();render()}});
  chronAlign();[120,400,1000].forEach(t=>setTimeout(chronAlign,t));
  if(!window.__chronAlignBound){window.__chronAlignBound=true;window.addEventListener('resize',()=>chronAlign());if(document.fonts&&document.fonts.ready)document.fonts.ready.then(()=>chronAlign());}
}
/* 오른쪽 '개인 집중 훈련' 밑줄을 왼쪽 '운영 일지' 밑줄과 같은 높이에 맞춘다 (두 쪽이 나란히 있을 때만) */
function chronAlign(){
  const head=document.querySelector('.chronicle .chron-focus-heading'),a=document.querySelector('.chronicle .chron-title-rule'),b=head&&head.querySelector('.chron-rule');
  if(!head||!a||!b)return;
  const L=document.querySelector('.chronicle .chron-left'),R=document.querySelector('.chronicle .chron-right');
  if(!L||!R||window.innerWidth<=1250||Math.abs(L.getBoundingClientRect().top-R.getBoundingClientRect().top)>40){head.style.marginTop='';return;}   // 제목이 두 줄로 접히는 폭에서는 맞추지 않는다   // 한 줄로 쌓인 폰 화면은 건드리지 않는다
  for(let i=0;i<3;i++){const d=a.getBoundingClientRect().top-b.getBoundingClientRect().top;if(Math.abs(d)<1)break;head.style.marginTop=Math.round((parseFloat(head.style.marginTop)||0)+d)+'px';}
}
function chronicleAdvance(button){
  if(!PREF.chronicleTest){runWithReport();return;}
  if(button.dataset.stamping)return;
  button.dataset.stamping='1';button.disabled=true;button.classList.add('stamped');
  const seal=document.createElement('span');seal.className='chron-seal-imprint';seal.textContent='기록 승인';button.parentElement.append(seal);
  setTimeout(()=>{if(button.isConnected&&UI.view==='plan'&&PREF.chronicleTest){runWithReport();if(button.isConnected){button.disabled=false;delete button.dataset.stamping;}}},window.matchMedia('(prefers-reduced-motion: reduce)').matches?0:450);
}
