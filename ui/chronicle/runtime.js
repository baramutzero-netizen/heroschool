function chronBookmark(c,i,all){
  const tr=TR[c.t]||TR.free,col=cardColor(c),mk=markOf(c),life=clamp(cardLeft(c),1,CARD_LIFE);
  const tilt=(all&&all.length===9&&i===8)?8:[-4,2,-2,3,-3,1,-1,3,-2][i%9],   // 9장일 때 맨 오른쪽 카드는 오른쪽으로 8도
        rise=[3,12,0,9,3,13,1,9,5][i%9];
  const title=tr.n+' · '+tr.d+' · '+cardLeftText(life)+' · '+cardEffLine(tr)+(mk?' · '+mk.n+': '+mk.d:'');
  return `<div class="card chron-bookmark" draggable="true" data-card="${c.u}" title="${esc(title)}" aria-label="${esc(title)}" style="--cc:${col.c};--mk:${mk?mk.c:'transparent'};--paper:url('${CHRONICLE_ART['bookmark-paper-center']}');--order:${i+1};--tilt:${tilt}deg;--rise:${rise*1.05}px"><svg class="bookmark-thread" viewBox="0 0 60 45" aria-hidden="true"><path d="M51 36 C43 21 28 15 17 12 M49 35 Q55 32 53 37 Q50 40 48 35"/></svg><div class="bookmark-tape" data-life="${life}" aria-hidden="true"><b>${life}주 <small>남음</small></b></div><strong class="bookmark-name">${esc(tr.n)}</strong><p class="bookmark-desc">${esc(tr.d)}</p><div class="bookmark-stats">${fxHtml(tr)}</div><div class="bookmark-effect">${cardEffLine(tr)}</div>${chronTrainingArt(c.t)}${mk?`<span class="bookmark-mark">${mk.i}</span>`:''}</div>`;
}
function chronHand(){
  // Only sort the presentation: preserve inventory order and card identity.
  const cards=(S.hand||[]).slice().sort((a,b)=>(a.w??S.weekSeq??0)-(b.w??S.weekSeq??0)||a.u-b.u);
  return `<svg width="0" height="0" aria-hidden="true" style="position:absolute"><defs><filter id="chron-paper-cutout" color-interpolation-filters="sRGB"><feColorMatrix type="matrix" values="1 0 0 0 0 0 1 0 0 0 0 0 1 0 0 -1 -1 -1 0 3"/><feComponentTransfer><feFuncA type="linear" slope="5"/></feComponentTransfer><feComposite in2="SourceGraphic" operator="in"/></filter></defs></svg><div class="chron-bookmark-stage"><div class="handrow chron-bookmarks" data-handzone="1" style="--fan-gaps:${Math.max(1,cards.length-1)}">${cards.map(chronBookmark).join('')||'<p>책갈피를 모두 이번 주 계획에 기록했습니다.</p>'}</div></div>`;
}
function chronArt(key,cls=''){return `<img class="chron-art ${cls}" src="${CHRONICLE_ART[key]}" alt="" aria-hidden="true" draggable="false">`;}
function chronRule(cls=''){return `<svg class="chron-rule ${cls}" viewBox="0 0 600 16" preserveAspectRatio="none" aria-hidden="true"><path d="M9 10 Q165 5 300 8 T589 7 M14 12 Q280 9 583 10"/><path d="M1 10l5-3 5 3-5 3z M589 7l5-3 5 3-5 3z"/></svg>`;}
function chronHeading(title,cls='',art='leaf'){return `<div class="chron-heading ${cls}">${chronArt(art,'chron-h-'+art)}<h3>${title}</h3>${chronRule()}</div>`;}
function chronTrainingArt(id){const map={basic:'weight',heavy:'weight',spar:'swords',mock:'swords',strike:'target',free:'target',tact:'books',study:'books',form:'books',medit:'leaf',deep:'leaf',rest:'cup',crest:'cup',exped:'map',camp:'target'};return chronArt(map[id]||'books','chron-training-art');}
function viewPlan(){
  const legacy=viewPlanClassic();
  if(!PREF.chronicleTest) return legacy;
  const t=document.createElement('template');t.innerHTML=legacy;
  const take=sel=>{const el=t.content.querySelector(sel);if(el&&sel==='#btnWeek'&&S.week<PHASES[S.phase].weeks){const status=el.disabled?el.textContent:'';el.classList.add('chron-proceed-art');el.setAttribute('aria-label','이번 주를 진행한다');el.title='이번 주를 진행한다';el.innerHTML=chronArt('proceed-button','chron-proceed-paper')+chronArt('wax-stamp','chron-wax-stamp');}return el?el.outerHTML:''};
  /* 손글씨 글자만 보이는 버튼 — 원래 버튼(id·disabled·동작)은 그대로 쓰고 모양과 글자만 바꾼다 */
  const inkLine=sel=>{const el=t.content.querySelector(sel);if(!el)return '';el.className='chron-inkbtn chron-inkline';el.removeAttribute('style');return el.outerHTML};
  const inkBtn=(sel,l1,l2)=>{const el=t.content.querySelector(sel);if(!el)return '';el.className='chron-inkbtn';el.innerHTML=chronArt(sel==='#btnBookUse'?'prophecy-book':'supreme-water','chron-action-icon')+`<span>${l1}</span><small>${l2}</small>`;return el.outerHTML};
  t.content.querySelectorAll('.handrow [data-card]').forEach(el=>{const c=(S.hand||[]).find(c=>c.u===Number(el.dataset.card));if(c){const tr=TR[c.t]||TR.free;el.title += ' · '+(tr.fx||[]).map(f=>f[0]+' '+(f[2]?'-':'+').repeat(f[1])).join(' · ')+' · '+cardEffLine(tr);}});
  const pages=Math.max(1,Math.ceil(S.students.length/15));
  UI.chroniclePage=clamp(UI.chroniclePage||0,0,pages-1);
  const students=S.students.slice(UI.chroniclePage*15,UI.chroniclePage*15+15);
  const slots=S.slots||[], ph=PHASES[S.phase];
  const days=DAY_N.map((day,i)=>{const c=slots[i],tr=c&&(TR[c.t]||TR.free),col=c&&cardColor(c),mk=c&&markOf(c),chain=chainOf(slots,i);
    return `<div class="dslot chron-day ${c?'filled':''}" data-slot="${i}" style="--day-color:${col?col.c:'#9c8972'}"><b class="chron-weekday">${day}</b>${c?`<div class="chron-entry" draggable="true" data-card="${c.u}" title="클릭하면 손패로 돌아갑니다"><strong>${esc(tr.n)}</strong>${chronTrainingArt(c.t)}<small>${esc(tr.d)}</small></div>`:'<span class="chron-empty">무슨 훈련 메뉴를 준비해볼까?</span>'}${(mk||chain)?`<span class="chron-tail">${mk?`<span class="chron-mark" style="background:${mk.c}" title="${esc(mk.d)}">${mk.i}</span>`:''}${chain?`<span class="chron-chain">능률 +${Math.round(chain*100)}%</span>`:''}</span>`:''}${chronRule('chron-day-rule')}</div>`}).join('');
  const focusControls=['btnFocusWeak','btnFocusStrong','btnFocusClear','btnRestAll','btnRest40','btnRest70','btnRestInj','btnFocusUndo','btnFocusPrev'];
  return `<section class="chronicle" style="--book-art:url('${CHRONICLE_BOOK}')"><div class="chron-pages"><div class="chron-page chron-left"><header class="chron-masthead">${chronArt('crest','chron-crest')}<div class="chron-title-block"><h2>${esc(S.acadName)} 운영 일지</h2>${chronRule('chron-title-rule')}<div class="chron-daterow"><p class="chron-date">${S.year}년차 · ${ph.n} · ${Math.min(S.week+1,ph.weeks)}주차${chronRule('chron-date-rule')}</p><p class="chron-motto">좋은 용사는<br>하루아침에 만들어지지 않는다.<br><span>— 그리고,</span><br><span>오늘도, 조금 더.</span>${chronArt('leaf')}</p></div></div></header><div class="chron-intro"><p class="chron-note">새로운 한 주가 시작되었다. ${chronArt('leaf')}</p></div><div class="chron-toolbar">${take('#btnAuto')}${take('#btnClearSlots')}${take('#btnRest')}</div>${chronHeading('이번 주의 계획','chron-plan-heading','quill')}<div class="chron-days">${days}</div>${chronHeading('준비된 훈련 메뉴 <small>'+((S.hand||[]).length)+'장</small>','chron-hand-heading','ink')}<div class="chron-hand-title"></div>${chronHand()}</div><div class="chron-page chron-right"><header class="chron-focus-heading">${chronHeading('개인 집중 훈련','','watch')}<p>… 언젠가, 이 아이들이<br>세상을 더 좋은 곳으로 만들기를.</p></header><div class="chron-focus-tools">${['btnFocusWeak','btnRestAll','btnFocusClear','btnFocusPrev'].map(k=>inkLine('#'+k)).join('')}</div><div class="chron-students">${students.map(s=>`<div class="chron-student chron-st2"><button class="chron-person" data-sid="${esc(s.id)}" title="${esc(s.name)} 상세">${faceHTML(s.job,s.name)}</button><div class="chron-st-id"><strong>${esc(s.name)}</strong>${(()=>{const f=Math.round((1-trainSuccessP(s,false))*100);return `<span class="chron-fail ${f>0?'bad':''}" title="이번 주 훈련이 실패할 확률 — 컨디션 70 이상이면 0%">훈련 실패: <b>${f}%</b></span>`})()}</div><div class="chron-st-focus"><strong>집중</strong><button class="chron-focus-cycle" data-chron-cycle="${esc(s.id)}" title="누를 때마다 다음 목표로 바뀐다" aria-label="${esc(s.name)} 집중 목표 바꾸기 — 지금 ${esc(chronFocusName(s.focus))}"><span>${esc(chronFocusName(s.focus))}</span>${CHRON_CYCLE_ICON}</button></div><div class="chron-condition" title="컨디션 ${Math.round(s.cond)}"><i style="width:${clamp(s.cond,0,100)}%;background:${s.cond<40?'#b54a40':s.cond<70?'#ba8336':'#4d8a65'}"></i><span>${Math.round(s.cond)}</span></div></div>`).join('')||'<p>아직 등록된 학생이 없습니다.</p>'}</div><div class="chron-pagination" ${pages<=1?'hidden':''}><button data-chron-page="-1" ${UI.chroniclePage===0?'disabled':''}>이전</button><span>${UI.chroniclePage+1} / ${pages} · 전체 ${S.students.length}명</span><button data-chron-page="1" ${UI.chroniclePage+1>=pages?'disabled':''}>다음</button></div><div class="chron-condition-tools"></div><footer class="chron-funds">${chronArt('purse','chron-purse')}<span>자금 <b>${fmt(S.gold)} G</b></span></footer><div class="chron-actions">${inkBtn('#btnBookUse',`예지의 서 ×${bookCount()}`,'(훈련 메뉴 교체)')}${inkBtn('#btnWater2','초성수 주문',churchBought('water')?'이번 계절 소진':`컨디션 +${HOLY_WATER_COND} · ${fmt(holyWaterCost())} G`)}</div><div class="chron-seal-wrap">${take('#btnWeek')}</div></div></div>${chronArt('letter','chron-letter')}<nav class="chron-tabs"><button data-chron-nav="plan" aria-current="page">일지</button><button data-chron-nav="roster">학생</button><button data-chron-nav="facil">시설</button></nav></section>`;
}
/* 집중 훈련 목표 — 누를 때마다 없음 → 팀워크 → 적극성 → 침착성 → 정신력 → 지구력 → 천재성 → 휴식 → 없음 */
const CHRON_FOCUS_CYCLE=['free','team','aggr','calm','will','stam','genius','rest'];
function chronFocusName(k){if(!k||k==='free')return '없음';if(k==='rest')return '휴식';const m=MENTAL.find(x=>x.k===k);return m?m.n:'없음';}
const CHRON_CYCLE_ICON='<svg class="chron-cycle-ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M19.5 12a7.5 7.5 0 0 1-12.8 5.3"/><path d="M4.5 12A7.5 7.5 0 0 1 17.3 6.7"/><path d="M17.6 2.8v4.2h-4.2"/><path d="M6.4 21.2v-4.2h4.2"/></svg>';
function bindChronicle(){
  document.querySelectorAll('.chronicle [data-card]').forEach(el=>{el.tabIndex=0;el.setAttribute('role','button');el.onkeydown=e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();el.click();}};});
  const toggle=document.querySelector('#chronicleToggle');
  if(toggle)toggle.onchange=()=>{PREF.chronicleTest=toggle.checked;prefSave();render();};
  document.querySelectorAll('[data-chron-nav]').forEach(b=>b.onclick=()=>{UI.view=b.dataset.chronNav;render()});
  document.querySelectorAll('[data-chron-page]').forEach(b=>b.onclick=()=>{UI.chroniclePage=(UI.chroniclePage||0)+Number(b.dataset.chronPage);render()});
  document.querySelectorAll('[data-chron-cycle]').forEach(b=>b.onclick=e=>{e.stopPropagation();const st=S.students.find(s=>s.id===b.dataset.chronCycle);if(!st)return;const i=CHRON_FOCUS_CYCLE.indexOf(st.focus);st.focus=CHRON_FOCUS_CYCLE[(i+1)%CHRON_FOCUS_CYCLE.length];save();render()});
  document.querySelectorAll('[data-chron-focus]').forEach(el=>el.onchange=()=>{const st=S.students.find(s=>s.id===el.dataset.chronFocus);if(st){st.focus=el.value;save();render()}});
  const bw=document.querySelector('.chronicle #btnWeek');if(bw)bw.addEventListener('pointerdown',e=>{bw._chronPt={x:e.clientX,y:e.clientY,t:Date.now()}});
  chronAlign();[120,400,1000].forEach(t=>setTimeout(chronAlign,t));
  if(!window.__chronAlignBound){window.__chronAlignBound=true;window.addEventListener('resize',()=>chronAlign());if(document.fonts&&document.fonts.ready)document.fonts.ready.then(()=>chronAlign());}
}
/* 오른쪽 '개인 집중 훈련' 밑줄을 왼쪽 '운영 일지' 밑줄과 같은 높이에 맞춘다 (두 쪽이 나란히 있을 때만) */
function chronAlign(){
  const head=document.querySelector('.chronicle .chron-focus-heading'),a=document.querySelector('.chronicle .chron-title-rule'),b=head&&head.querySelector('.chron-rule');
  if(!head||!a||!b)return;
  const L=document.querySelector('.chronicle .chron-left'),R=document.querySelector('.chronicle .chron-right');
  if(!L||!R||Math.abs(L.getBoundingClientRect().top-R.getBoundingClientRect().top)>40){head.style.marginTop='';return;}   // 제목이 두 줄로 접히는 폭에서는 맞추지 않는다   // 한 줄로 쌓인 폰 화면은 건드리지 않는다
  for(let i=0;i<3;i++){const d=a.getBoundingClientRect().top-b.getBoundingClientRect().top;if(Math.abs(d)<1)break;head.style.marginTop=Math.round((parseFloat(head.style.marginTop)||0)+d)+'px';}
}
/* 붉은 인주 도장 — 누른 자리(키보드면 버튼 가운데)에 찍힌다 */
function chronInkStamp(){
  return `<svg viewBox="0 0 120 120" aria-hidden="true"><defs><filter id="chron-ink-rough" x="-10%" y="-10%" width="120%" height="120%"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" seed="7" result="n"/><feDisplacementMap in="SourceGraphic" in2="n" scale="1.6" result="d"/><feTurbulence type="fractalNoise" baseFrequency=".35" numOctaves="3" seed="3" result="m"/><feColorMatrix in="m" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 -1.5 1.95" result="mask"/><feComposite in="d" in2="mask" operator="in"/></filter></defs><g filter="url(#chron-ink-rough)" fill="none" stroke="currentColor"><circle cx="60" cy="60" r="53" stroke-width="5"/><circle cx="60" cy="60" r="44" stroke-width="1.8"/><path d="M22 60h10M88 60h10" stroke-width="2.2"/><g fill="currentColor" stroke="currentColor" stroke-width=".9" stroke-linejoin="round" font-family="Batang,'Nanum Myeongjo',serif" font-weight="900" text-anchor="middle"><text x="60" y="55" font-size="25">기록</text><text x="60" y="82" font-size="25">승인</text><text x="60" y="30" font-size="9" letter-spacing="1.5">★ 이번 주 ★</text><text x="60" y="99" font-size="8.5" letter-spacing="1">${esc(String(S.year||''))}년 ${esc(String(S.week+1))}주차</text></g></g></svg>`;
}
function chronicleAdvance(button){
  if(!PREF.chronicleTest){runWithReport();return;}
  if(button.dataset.stamping)return;
  button.dataset.stamping='1';button.disabled=true;button.classList.add('stamped');
  const wrap=button.parentElement,wr=wrap.getBoundingClientRect(),br=button.getBoundingClientRect(),pt=button._chronPt&&Date.now()-button._chronPt.t<1500?button._chronPt:null;
  const x=(pt?Math.min(br.right,Math.max(br.left,pt.x)):br.left+br.width/2)-wr.left,y=(pt?Math.min(br.bottom,Math.max(br.top,pt.y)):br.top+br.height/2)-wr.top;
  const seal=document.createElement('span');seal.className='chron-ink-stamp';seal.setAttribute('aria-hidden','true');
  seal.style.left=x+'px';seal.style.top=y+'px';seal.style.setProperty('--rot',(-18+Math.random()*14).toFixed(1)+'deg');seal.innerHTML=chronInkStamp();wrap.append(seal);
  setTimeout(()=>{if(button.isConnected&&UI.view==='plan'&&PREF.chronicleTest){runWithReport();if(button.isConnected){button.disabled=false;delete button.dataset.stamping;button.classList.remove('stamped');seal.remove();}}},window.matchMedia('(prefers-reduced-motion: reduce)').matches?250:700);
}
