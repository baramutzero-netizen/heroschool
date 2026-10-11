/* SCHED_SCROLL_START — 두루마리 스케줄 (1006)
   배치판(Claude outputs/schedule_kit · 배치 JSON)으로 정한 책상 · 두루마리 · 소품 그림(SCHED_ART) 위에 스케줄을 HTML 로 얹는다.
   자리는 두루마리 캔버스(607×466)의 2배 좌표 그대로 — 목업(schedule_mock2)과 같은 숫자. 무대 전체(1544×1008)를 화면 폭에 맞춰 줄인다.
   가로 화면(townMode)에서만 쓰고, 설정에서 끌 수 있다(PREF.schedScroll — 끄면 예전 스케줄 화면).
   결재 — 깃펜을 집어 잉크 단지에 찍은 뒤 결재란 서명줄에 서명한다. 처음 그린 서명은 이 브라우저에 남고(PREF.sign),
   다음부터는 다섯 칸이 차면 결재란도 깃펜처럼 반짝이고, 결재란을 누르면 깃펜이 스스로 잉크를 찍어 그 서명을 쓴다 (1011).
   깃펜을 집어 잉크를 찍고 서명줄을 한 번 누르는 것도 그대로 된다. 새로 그으면 서명이 바뀐다.
   결재란에서 Enter(키보드)를 누르면 (저장된 서명이 없어도) 깃펜이 스스로 잉크를 찍고 서명한다.
   사이드(오른쪽 메뉴판)가 잉크 단지 · 깃펜을 가리면 사이드를 줄인다 — skSideFit (1010). */
const SCHED_ART = /*SCHED_ART*/{};
const SCHED_GEO = /*SCHED_GEO*/{};
const SK_X0 = 42, SK_X1 = 565, SK_YRIB = 54, SK_YDAY = 78, SK_YHANDL = 166, SK_YHAND = 188, SK_YBAND = 280, SK_XL1 = 432, SK_XR0 = 440;
/* 카드 56×82 (1006, 예전 80) — 훈련 이름을 화면 12px 로 키우며 색 머리를 2칸 늘렸다. 손패 줄도 2칸 내렸다 (sched_art 의 M2.CH · HB · Y_RULE2 와 같이) */
const SK_CW = 56, SK_CH = 82, SK_ROW = 10, SK_ROWS = 15;   // 명부 줄 간격 10 — 행동 칸(15×9)이 줄 안에 들어가고 점선 한 줄이 남는다 (1006, 예전 9) · 한 쪽 15명. 줄 폭은 skRowGeo (1011 — 예전 SK_COLW 192)
const SK_ICON = {basic:"dumbbell", heavy:"barbell", spar:"swords", mock:"shield", tact:"book", study:"book", form:"flag", medit:"leaf", deep:"lotus",
  free:"target", strike:"arrow", exped:"map", rest:"cup", crest:"cup", camp:"barbell"};
/* 카드 색 — 진한 쪽부터 다섯 (DT.CARD 와 같다). [0] 글자 그림자 · [2] 바탕 */
const SK_PAL = {red:["7a2a33","a83a46","e0616a","f08f92","f9cfc9"], green:["24603c","368552","54ae70","82c98d","c9eac5"],
  blue:["2a447f","3d62ad","5b87dd","88aaee","cddcf8"], sky:["1a6f80","2a98ad","48c3d8","80d9e6","c8f0f5"],
  gold:["7c5512","a97c22","d9a63c","ecc56a","f9e7b2"], none:["484c55","666b74","8a8f98","b1b5bc","dcdee2"]};
const SK_INK = "#1d2433", SK_INK_LEN = 420;                   // 서명 잉크 색(잉크 단지 색) · 한 번 찍으면 그을 수 있는 길이(서명 캔버스 칸)
/* 기본 서명 — 키보드로 결재하는데 저장된 서명이 없을 때 (목업의 학원장 서명) */
const SK_SIG0 = [[4,15,8,6,11,3,12,9,8,14,6,13,12,10,16,11,18,7,17,12,21,13,24,8,25,13,29,12,31,6,33,3,33,12,36,13,39,9,41,12,44,11,47,8,49,12,53,11,57,9,61,11,66,10],
  [6,16,24,14,44,15,58,12]];
const SK = {s:.78, held:false, ink:0, strokes:[], cur:null, len:0, writing:false, timer:0, busy:false, auto:false, keyOn:null, ro:null};

function schedScrollOn(){ return PREF.schedScroll !== false && typeof townMode === "function" && townMode(); }
function skSpr(name, x, y, cls, attrs, k){                       // x, y = 2배 좌표 · k = 그림 1배의 몇 배로 (기본 2 — 큰 단추의 아이콘은 3, 1011)
  const p = SCHED_GEO.sheet.pos[name]; if(!p) return "";
  k = k || 2;
  const bs = k !== 2 ? `;background-size:${SCHED_GEO.sheet.w*k}px ${SCHED_GEO.sheet.h*k}px` : "";
  return `<i class="sk-spr${cls? " "+cls : ""}" style="left:${x}px;top:${y}px;width:${p[2]*k}px;height:${p[3]*k}px;background-position:${-p[0]*k}px ${-p[1]*k}px${bs}"${attrs||""}></i>`;
}
function skBg(name){ const p = SCHED_GEO.sheet.pos[name]; return p? `background-position:${-p[0]*2}px ${-p[1]*2}px` : ""; }
function skB(id, label, icon, tone, attrs){                     // 종이 꼬리표 단추 — tone 에 lg 가 있으면 큰 단추 (1011 · 글자 18 · 아이콘 3배)
  const lg = /(^|\s)lg(\s|$)/.test(tone || "");
  return `<button type="button" class="skb${icon? " ic" : ""}${tone? " "+tone : ""}"${id? ` id="${id}"` : ""}${attrs||""}>${icon? (lg ? skSpr("mi_"+icon, 8, 4, "", "", 3) : skSpr("mi_"+icon, 6, 2)) : ""}${label}</button>`;
}
function skHasSign(){ return !!(PREF.sign && Array.isArray(PREF.sign.s) && PREF.sign.s.length); }   // 저장된 서명이 있다 (1011)
function skColKey(c){ const k = colOf(c); return SK_PAL[k] ? k : "none"; }
function skCard(c, x, y){                                       // x, y = 카드 왼쪽 위 (1배)
  const tr = TR[c.t] || TR.free, key = skColKey(c), pal = SK_PAL[key], col = cardColor(c), mk = markOf(c);
  const L = clamp(cardLeft(c), 1, CARD_LIFE), eff = cardEffLine(tr), cv = eff.replace(/^[^+\-−]*/, "")   /* 1010 — 영어판: 앞의 이름(컨디션 · Condition)을 떼고 값만 */, good = cv.charAt(0) === "+";
  const cost = cardCostText(c);
  const tip = `${tr.n}${cost? " · "+cardCostTip(c) : ""}${mk? ` — ${mk.i} ${mk.n}: ${mk.d}` : ""} · ${cardLeftText(L)}${L<=1? "" : " 남음"}`;
  const fx = (tr.fx||[]).slice(0, 4).map((f, i)=> `<span class="sk-fx${f[2]? " bad":""}" style="top:${80 + i*14}px">${esc(mentShortOf(f[0]))}<b>${"+".repeat(f[1])}</b></span>`).join("");   // 1011 — 멘탈리티는 줄임말 (영어 Comp. 등)
  const lc = {3:"#3b6b33", 2:"#8a5e1c", 1:"#a3302a"}[Math.min(3, L)] || "#3b6b33";
  return `<div class="sk-card" data-card="${c.u}" draggable="false" role="button" tabindex="0" title="${esc(tip)}" aria-label="${esc(tip)}" style="left:${x*2}px;top:${y*2}px;${skBg("card_"+key)}">`
    + skSpr("ic_" + (SK_ICON[c.t] || "target"), 40, 10, "ic")
    + `<span class="sk-cn" style="text-shadow:var(--o) var(--o) 0 #${pal[0]}">${esc(tr.n)}</span>`
    + (cost? `<span class="sk-cc">${esc(cost)}</span>` : "") + fx
    + `<span class="sk-ck">컨디션<b class="${good? "sk-grn" : "sk-red"}">${esc(cv)}</b></span>`
    + `<span class="sk-life" style="--lc:${lc}">${cardLeftText(L)}</span>`
    + (mk? `<span class="sk-mark" title="${esc(mk.n)} — ${esc(mk.d)}">${esc(mk.i)}</span>` : "")
    + `</div>`;
}
function skRibbon(cx, label, key){
  const pal = key? SK_PAL[key] : ["4a3b2c"];
  return skSpr(key? "rib_"+key : "rib_empty", (cx - 49) * 2, SK_YRIB * 2)
    + `<span class="sk-rib" style="left:${cx*2 - 100}px;top:${SK_YRIB*2 + 4}px;text-shadow:2px 2px 0 #${pal[0]}">${label}</span>`;
}
/* 행동 칸 (1011) — 그림(chip_*) 대신 CSS 로 같은 모양(테두리 · 바탕 · 윗줄 밝게)을 그려 폭을 바꿀 수 있게 했다.
   폭은 CSS 변수 --sk-chipw (한국어 30 · 영어 38 — en_layout.css · 'Train' 이 테두리 안에 들어가게). 글은 칸에 맞춘 짧은 이름(SK_CHIP_N — 영어 의뢰 = Work).
   부상 표시(✚ N주) 자리 폭은 --sk-injw (한국어 36 · 영어 40 — '2wk'). 둘 다 skRoster 가 막대 자리를 정할 때 읽는다 */
const SK_CHIP_N = {train:"훈련", rest:"휴식", job:"의뢰"};
function skCssPx(name, def){ const v = parseFloat(getComputedStyle(document.documentElement).getPropertyValue(name)); return v > 0 ? v : def; }
function skChips(s){
  const k = actUnlocked() ? actShown(s) : (isRestFocus(s) ? "rest" : "train");
  const col = {train:"#3a2a20", rest:"#3b6b33", job:"#8a5e1c"}[k] || "#3a2a20";
  return `<button type="button" class="sk-chip k-${k}" data-sk-act="${esc(s.id)}" ${actUnlocked()? "" : "disabled"} title="${esc(actName(k))} — 누르면 ${actPickKeys().map(actName).join(" → ")}" style="color:${col}"><b>${esc(SK_CHIP_N[k] || actName(k))}</b></button>`;
}
function skTone(v){
  if(v >= COND_HI)  return ["#3b6b33", "#4f8a42", "#86bd6c"];
  if(v >= COND_MID) return ["#9a6410", "#c3922c", "#e6c262"];
  return ["#a3302a", "#b0473a", "#d97a62"];
}
/* 명부 크기 (1006 · 1011) — 남는 자리를 다 쓰도록 한 단 · 두 단 중 더 크게 들어가는 쪽으로, 크기는 2배까지 1/8 단위.
   두 단은 왼쪽 단부터 채운다 (15명이면 8 + 7). 줄 폭이 좁아지는 만큼 컨디션 막대를 줄인다 (SK_BARMIN 까지 · 한 단은 줄이지 않는다).
   한 단이 두 단보다 1/4 이상 작을 때만 두 단으로 — 비슷하면 막대가 긴 한 단이 보기 좋다.
   rsv — 맨 끝 칸 하나를 '변경 취소' 단추 자리로 비워 둔다 (지난주 기록이 있을 때 · 칸은 skRoster 의 slot).
   아래 끝은 그 밑에 놓인 소품(문진) 바로 위까지 (SCHED_GEO.ros_bottom). 줄 안 자리는 2배 좌표 — 이름 60 · 행동 칸 62~(30 · 영어 38) · 부상 그 뒤 4~ · 막대 bx~ */
const SK_BARMIN = 60, SK_BARMAX = 160, SK_RTAIL = 70;            // 막대 폭 (2배) · 막대 뒤(컨디션 값 · 효율 % · 여백)
function skRowGeo(f, cols, bx){                                  // 한 줄 폭 · 막대 폭 (2배 · 명부를 키우기 전)
  const W2 = (SK_XL1 - (SK_X0 + 2)) * 2, room = cols === 2 ? (W2 / f - 12) / 2 : W2 / f;
  const bar = Math.floor(clamp(room - bx - SK_RTAIL, SK_BARMIN, SK_BARMAX) / 2) * 2;
  return {bar, w: bx + bar + SK_RTAIL};
}
function skRosterFit(n, y0, bx, rsv){
  const H = (SCHED_GEO.ros_bottom || 421) - y0, W2 = (SK_XL1 - (SK_X0 + 2)) * 2, q = v=> Math.floor(v * 8) / 8;
  const r = n + (rsv ? 1 : 0), per2 = Math.max(1, Math.ceil(r / 2));
  const f1 = q(Math.min(2, H / (Math.max(1, r) * SK_ROW), W2 / (bx + SK_BARMAX + SK_RTAIL)));
  const f2 = q(Math.min(2, H / (per2 * SK_ROW), W2 / (2 * (bx + SK_BARMIN + SK_RTAIL) + 12)));
  if(r <= 1 || f1 + .25 > f2){ const f = Math.max(.5, f1); return {f, cols:1, per: Math.max(r, Math.floor(H / (SK_ROW * f)))}; }
  return {f: f2, cols:2, per: per2};
}
function skRoster(x0, y0, chips, rsv){
  const all = S.students.slice().sort((a,b)=> a.cond - b.cond);
  const pages = Math.max(1, Math.ceil(all.length / SK_ROWS));
  UI.skPage = clamp(UI.skPage|0, 0, pages - 1);
  const list = all.slice(UI.skPage * SK_ROWS, UI.skPage * SK_ROWS + SK_ROWS);
  const cw = chips ? skCssPx("--sk-chipw", 30) : 0, cx = 62 + cw + 4;   // 행동 칸 폭 (1011 — 영어는 넓다) · 부상 표시(✚) 자리
  const bx = !chips ? 66 : all.some(isInjured) ? cx + skCssPx("--sk-injw", 36) : cx;   // 막대 왼쪽 — 행동 칸 뒤 · 다친 학생이 있으면 부상 표시(✚ N주) 뒤 (한국어 96 · 132)
  const F = skRosterFit(pages > 1 ? SK_ROWS : list.length, y0, bx, rsv);   // 여러 쪽이면 쪽마다 같은 모양 (15명 기준)
  const G = skRowGeo(F.f, F.cols, bx), lines = F.cols === 2 ? F.per * 2 : F.per, pitch = G.w + 12;
  let h = "";
  for(let i = 0; i < lines; i++){
    const col = Math.floor(i / F.per), row = i % F.per, s = list[i];
    const x = col * pitch, y = row * SK_ROW * 2;                   // 명부 안 좌표 (2배) — 명부 전체를 F.f 배로 키운다
    if(!s){ h += `<div class="sk-r empty" style="left:${x}px;top:${y}px"></div>`; continue; }
    const v = Math.round(clamp(s.cond, 0, 100)), [tc, fc, hc] = skTone(v);
    const inj = isInjured(s) ? skSpr("cross", cx, 2) + `<span class="iw" style="left:${cx + 15}px">${injWeeks(s)}주</span>` : "";
    h += `<div class="sk-r${(chips ? actShown(s) === "rest" : isRestFocus(s))? " rest" : ""}" style="left:${x}px;top:${y}px">`
      + `<span class="nm" title="${esc(dn(s))}">${esc(s.name)}</span>${chips? skChips(s) + inj : ""}`
      + `<span class="sk-bar" style="left:${bx}px"><i style="width:${Math.max(0, Math.round((G.bar - 6) / 2 * v / 100)) * 2}px;background:${fc};--hc:${hc}"></i></span>`
      + `<span class="cv" style="left:${bx + G.bar - 18}px;color:${tc}">${v}</span>`
      + `<span style="left:${bx + G.bar + 28}px;color:${tc}">${effPct(s)}%</span></div>`;
  }
  if(F.cols === 2) h += `<i class="sk-div" style="left:${G.w + 4}px;top:0;height:${(F.per * SK_ROW - 1) * 2}px"></i>`;
  /* 맨 끝 빈칸 (종이 2배 좌표 · 밑줄 끝까지) — 변경 취소 단추를 여기 오른쪽 끝에 맞춰 놓는다 */
  const last = lines - 1, sc = Math.floor(last / F.per), sr = last % F.per;
  const slot = rsv && lines > list.length ? {x: x0*2 + sc * pitch * F.f, y: y0*2 + sr * SK_ROW * 2 * F.f, w: (G.w - 14) * F.f, h: SK_ROW * 2 * F.f} : null;
  return {html:`<div class="sk-ros" style="left:${x0*2}px;top:${y0*2}px;--rw:${G.w}px;--bw:${G.bar}px${F.f !== 1? `;transform:scale(${F.f})` : ""}">${h}</div>`, pages, f:F.f, slot};
}
/* 교회 단추 (1011) — 예지의 서(쓰기 · 사기) · 신비한 성수. 개인 행동 줄 오른쪽 끝에 (예전엔 일과 머리 줄 · 명부 머리 줄).
   사기 단추는 바로 옆 예지의 서 단추에 붙어 '구매 · 값'만. 줄이 넘치면 skActFit 이 이름(.nm)을 숨긴다 (아이콘 · 권수 · 값만 — 이름은 title 에)
   — 영어는 거의 늘 · 한국어는 소진일 때쯤. 소진은 '이번 계절 소진' 대신 '소진' (남은 횟수는 title) */
function skChurch(hand){
  const lv2 = churchLv() >= 2, nb = bookCount();
  if(!lv2 && nb <= 0) return "";
  let h = skB("btnBookUse", `<span class="nm">예지의 서${nb>0? " " : ""}</span>${nb>0? `×${nb}` : ""}`, "book", "", (nb>0 && hand.length? "" : " disabled") + ` title="일과를 통째로 새로 뽑는다 — 월~금에 올려둔 카드는 그대로 둔다"`);
  if(lv2){
    const pr = foresightPrice(), bd = churchBought("book"), c = holyWaterCost(), wd = churchBought("water");
    h += skB("btnBook2", `구매 · ${bd? "소진" : fmt(pr)+" G"}`, "", "brass" + (S.gold < pr ? " poor" : ""), (bd? " disabled" : "") + ` title="교회에 가지 않고 바로 산다 · ${esc(churchLeftLabel("book"))}"`);
    h += skB("btnWater2", `<span class="nm">신비한 성수 · </span>${wd? "소진" : fmt(c)+" G"}`, "water", S.gold < c ? "poor" : "", (wd? " disabled" : "") + ` title="교회에 가지 않고 바로 쓴다 · 전 학생 컨디션 +${HOLY_WATER_COND} · ${esc(churchLeftLabel("water"))}"`);
  }
  return `<span class="sk-church">${h}</span>`;
}
/* 글이 넘치는 곳 줄이기 (1011 · 그린 뒤 · 글꼴을 받은 뒤) — 개인 행동 줄: 교회 단추 이름을 숨긴다 ·
   결재란 맨 위 줄('결재' + 비용): 결재란 안쪽(테두리 8 안)을 넘으면 '결재'를 뺀다. 한국어는 거의 그대로 — 영어 글이 길 때 */
function skActFit(){
  const r = document.querySelector("#view .sk-act");
  if(r){ r.classList.remove("tight"); if(r.scrollWidth > r.clientWidth + 1) r.classList.add("tight"); }
  const b = document.querySelector("#view .sk-appr"), t = b && b.querySelector(".top");
  if(t){ b.classList.remove("tight"); if(t.offsetLeft + t.scrollWidth > b.clientWidth - 8) b.classList.add("tight"); }
}
function viewPlanScroll(){
  const G = SCHED_GEO, ph = PHASES[S.phase];
  const slots = S.slots || [], hand = S.hand || [];
  const chains = slots.map((c, i)=> chainOf(slots, i));
  const left = WEEK_DAYS - slots.filter(Boolean).length;
  const endSeason = S.week >= ph.weeks;
  const disabled = (endSeason && UI.pendingTour) || (!endSeason && left > 0);
  const P = [];
  /* 반짝이는 별 (1006) — pts = 그 요소 안 1배 좌표 (skFxUpd 가 빛을 켜면 보인다) */
  const tw = (pts)=> pts.map(([x, y], i)=> `<i class="sk-tw" style="left:${x*2}px;top:${y*2}px;--d:${(i * .55).toFixed(2)}s"></i>`).join("");
  /* ── 머리 ── */
  P.push(`<h2 class="sk-title" style="left:88px;top:44px">${yrName(S.year)} ${ph.n} ${Math.min(S.week+1, ph.weeks)}주 스케줄</h2>`);
  { const wl = Math.max(0, ph.weeks - S.week), due = upkeepTotal() + debtInterest();
    P.push(`<span class="sk-t sk-ink2" style="left:90px;top:74px">${wl? `${wl}주 후` : "계절 종료 시"} 차감 예정 자금: <span class="sk-red">${fmt(due)} G</span>${
      isCampWeek()? `<span class="sk-brass"> · 합숙 — 훈련 ×${CAMP_GAIN} · 컨디션 소모 ×${CAMP_COND}</span>` : ""}</span>`); }
  { const d = dietDef(), open = DIETS.filter(dietOpen).length;
    const dt = `${open>1? "누르면 다음 식단으로 바꾼다 · " : ""}${d.eff? `훈련 효율 +${Math.round(d.eff*100)}% · ` : ""}이번 주 ${fmt(dietCostWeek())} G (${(S.students||[]).length}명)`;
    /* 위 단추 셋은 크게 (1011 — 글자 18 · 높이 36 · 아이콘 3배). 제목(24 · 44~68)과 세로 가운데를 맞춘다 */
    P.push(`<div class="sk-row r" style="right:86px;top:38px;gap:10px">${skB("btnAuto", "자동 배치", "wand", "lg")}${skB("btnDiet", `식단: ${esc(d.n)} (학생 당 ${fmt(dietPrice(d))} G)`, "bowl", "lg", ` title="${esc(dt)}"`)}${skB("btnClearSlots", "전부 비우기", "eraser", "lg")}${
      SHOW_BULKRUN? skB("btnRest", "남은 주 일괄 진행", "", "lg", endSeason? " disabled" : "") : ""}</div>`); }
  /* ── 요일 ── */
  const colw = (SK_X1 - SK_X0) / 5, cxs = [0,1,2,3,4].map(i=> Math.floor(SK_X0 + colw * (i + .5)));
  DAY_N.forEach((d, i)=>{
    const c = slots[i], cx = cxs[i];
    P.push(skRibbon(cx, d + "요일", c ? skColKey(c) : null));
    P.push(`<div class="sk-day" data-slot="${i}" style="left:${(cx - SK_CW/2)*2}px;top:${SK_YDAY*2}px" aria-label="${d}요일${c? " — "+esc((TR[c.t]||TR.free).n) : " — 비었다"}">${
      c ? skCard(c, 0, 0) : `<div class="sk-empty" style="${skBg("slot_empty")}"><b style="top:136px">일과</b><b style="top:152px">배치</b></div>`}</div>`);
  });
  for(let i = 1; i < WEEK_DAYS; i++){
    if(!(chains[i] > 0)) continue;
    const x0 = cxs[i-1] + SK_CW/2 + 1, x1 = cxs[i] - SK_CW/2 - 1, y = SK_YDAY + SK_CH/2;
    P.push(`<i class="sk-chain" style="left:${x0*2}px;top:${(y-3)*2}px;width:${(x1 - x0)*2}px"></i><span class="sk-badge" style="left:${x0 + x1}px;top:${(y+6)*2}px">+${Math.round(chains[i]*100)}%</span>`);
  }
  /* ── 일과 (손패) ── */
  /* 쓰는 법 안내(카드를 끌어 요일 칸에 놓는다 …)는 화면에서 뺐다 — 제목에 마우스를 올리면 보인다 (1006) */
  P.push(`<div class="sk-row" style="left:88px;top:${SK_YHANDL*2}px"><span class="sk-h" title="카드를 끌어 요일 칸에 놓는다 · 누르면 빈 칸으로 · 전날과 같은 색이면 능률이 오른다">일과 ${hand.length}장</span></div>`);
  /* 예지의 서 단추는 개인 행동 줄로 옮겼다 (1011 — skChurch) */
  P.push(`<div class="sk-hand" data-handzone="1" style="left:${(SK_X0-2)*2}px;top:${(SK_YHAND-4)*2}px;width:${(SK_X1 - SK_X0 + 4)*2}px;height:${(SK_CH + 8)*2}px">${
    hand.map((c, j)=> skCard(c, 43 + j * (SK_CW + 2) - (SK_X0 - 2), 4 + (j % 2))).join("")}${hand.length? "" : `<span class="sk-t sk-fade" style="left:20px;top:70px">일과가 비었다.</span>`}</div>`);
  /* ── 아래 띠 왼쪽 — 개인 행동 · 부상 · 컨디션 ── */
  let y = SK_YBAND;
  /* 개인 행동 줄 (1011) — 왼쪽 개인 행동 · 전원 단추, 오른쪽 끝(왼쪽 띠 끝)에 교회 단추(skChurch).
     변경 취소 단추는 명부 맨 끝 빈칸으로 옮겼다 (아래 ros.slot) — 이 줄에 다 넣으면 넘친다. 개인 행동이 열리기 전에는 '컨디션' 머리 줄 오른쪽에 */
  const church = skChurch(hand), actW = (SK_XL1 + 1)*2 - 88;
  const und = actUnlocked() ? focusUndoDiff() : 0, prv = actUnlocked() ? focusPrevDiff() : 0;
  if(actUnlocked()){
    P.push(`<div class="sk-row sk-act" style="left:88px;top:${y*2}px;width:${actW}px;gap:6px"><span class="sk-h" style="margin-right:6px">개인 행동</span>${skB("btnActTrain", "전원 훈련")}${
      skB("btnRestAll", "전원 휴식", "", "", ` title="컨디션과 상관없이 전 학생을 휴식으로 돌린다"`)}${jobOpen()? skB("btnActJob", "전원 의뢰", "", "", (J0=> J0? ` title="이번 주 의뢰 — ${esc(J0.n)}"` : "")(weekJobPlan())) : ""}${church}</div>`);
    y += 17;
    const hurt = S.students.filter(isInjured);
    if(hurt.length){
      const bad = hurt.filter(s=> actShown(s) !== "rest");
      P.push(`<div class="sk-inj" style="left:${SK_X0*2}px;top:${y*2}px;width:${(SK_XL1 - SK_X0 + 1)*2}px">${skSpr("cross", 8, 6)}`
        + `<span class="sk-t" style="left:22px;top:5px"><span class="sk-red">부상 ${hurt.length}명</span>&nbsp; ${hurt.map((h, i)=> `${i? " · " : ""}${esc(h.name)} <span class="sk-red">${injWeeks(h)}주</span>${isRestFocus(h)? ' <span class="sk-grn">휴식 중</span>' : ""}`).join("")}</span>`
        + `<span class="sk-t sk-fade" style="left:22px;top:20px">멘탈리티 50% · 휴식 외 훈련은 실패${bad.length? `<span class="sk-red"> — ${esc(bad.map(h=> h.name).join(", "))} 훈련 중</span>` : ""}</span>`
        + (bad.length? skB("btnRestInj", `휴식 전환 (${bad.length}명)`, "", "bad") : "") + `</div>`);
      y += 25;
    }
  }
  /* 명부 머리 줄 — 안내 글(컨디션 · 낮은 순 · N명 · 행동 칸을 누르면 …)은 화면에서 뺐다 (1006). 행동 칸 안내는 칸에 마우스를 올리면 보인다.
     머리 줄에는 쪽 넘김(16명부터)만 남는다 — 없으면 명부를 그 자리까지 올린다 (1011 — 성수 단추는 개인 행동 줄로) */
  const many = S.students.length > SK_ROWS, rsv = actUnlocked() && !!focusHist()[0];   // 지난주 기록이 있으면 변경 취소 자리를 비워 둔다
  const ros = skRoster(SK_X0 + 2, actUnlocked() ? y + (many ? 16 : 4) : y + 18, actUnlocked(), rsv);
  { const pg = ros.pages > 1 ? `<span class="sk-pager">${skB("", "◀", "", "", ` data-sk-page="-1"${UI.skPage? "" : " disabled"} aria-label="앞 명부"`)}<span class="sk-ink2" style="margin-top:6px">${UI.skPage+1}/${ros.pages}</span>${skB("", "▶", "", "", ` data-sk-page="1"${UI.skPage < ros.pages-1? "" : " disabled"} aria-label="다음 명부"`)}</span>` : "";
    if(actUnlocked()){
      if(pg) P.push(`<div class="sk-row" style="left:80px;top:${y*2 + 6}px">${pg}</div>`);
    } else
      P.push(`<div class="sk-row sk-act" style="left:88px;top:${y*2}px;width:${actW}px;gap:10px"><span class="sk-h">컨디션</span>${pg}${church}</div>`);
  }
  P.push(ros.html);
  /* 변경 취소 (1011) — 명부 맨 끝 빈칸의 오른쪽 끝에. 칸이 단추(24)보다 낮으면 칸 가운데에 걸친다 */
  if(ros.slot && (und || prv)){ const L = ros.slot;
    P.push(`<div class="sk-row r sk-undo" style="right:${Math.round(1214 - L.x - L.w)}px;top:${Math.round(L.y + (L.h - 24) / 2)}px;gap:6px">${
      und? skB("btnFocusUndo", `변경 취소 (${und}명)`, "", "", ` title="지금 바꾼 설정을 취소하고 지난주 배치로 돌아간다"`) : ""}${
      prv? skB("btnFocusPrev", `지난주 변경 취소 (${prv}명)`, "", "", ` title="지난주에 바꾼 설정을 취소하고 지지난주 배치로 돌아간다"`) : ""}</div>`); }
  /* ── 아래 띠 오른쪽 — 의뢰 쪽지(위) · 결재(아래 — 1006 에 자리를 바꿨다) ── */
  /* 결재란 (1006 · 1011) — 맨 위 '결재'와 그 옆에 비용(일과 · 식단) · 그 밑 진행 비용(글자 20 — 예전 24) · 아래쪽 서명 줄과 '학원장'.
     서명 칸(.sk-sig)은 진행 줄 바로 밑부터 서명 줄까지 (예전엔 비용 줄 밑부터 — 1011 에 두 배 가까이 키웠다). 일과가 덜 찼을 때는 글 없이 비워 둔다
     (다섯 칸이 차면 깃펜이 반짝인다 — 저장된 서명이 있으면 결재란도 · skFxUpd) */
  { const A = G.appr, cost = weekCardCost(slots), n = (S.students||[]).length, rest = S.students.filter(s=> !willAttend(s)).length;
    const label = endSeason ? "시즌 마무리" : left > 0 ? `일과 ${left}일치 세팅 필요` : `진행 (${fmt(cost + dietCostWeek())} G 소모)`;
    const big = endSeason || left <= 0 ? label : "";
    const sub = disabled ? (endSeason ? `<span class="sk-fade">대회 준비를 먼저 마친다</span>` : "")
      : endSeason ? `<span class="sk-fade">서명하면 계절을 마무리한다</span>`
      : `<span class="sk-ink2">일과 ${fmt(cost)} G · 식단 ${fmt(dietPrice())} G × ${n}명</span>`;
    const tip = !disabled && !endSeason && rest ? ` title="쉬는 ${rest}명은 일과 비용이 없다"` : "";
    const signed = skHasSign(), lab = "결재";
    const how = disabled ? "" : signed ? "클릭으로 서명" : "깃펜을 잉크에 찍어 서명";   // 1011 — 저장된 서명이 있으면 결재란을 누르기만 하면 된다
    P.push(`<button type="button" id="btnWeek" class="sk-appr${disabled? "" : " ready"}" data-need="${endSeason? 0 : Math.max(0, left)}" style="left:${A.x*2}px;top:${A.y*2}px;${skBg(disabled? "appr_off" : "appr_on")}" ${disabled? "disabled" : ""}${tip} aria-label="결재 — ${esc(label)}${disabled? "" : signed ? " · 누르면 깃펜이 저장된 서명을 쓴다" : " · 깃펜으로 서명한다 (Enter 를 누르면 깃펜이 스스로 서명한다)"}">`
      + `<span class="top"><span class="lab">${lab}</span>${sub}</span>${big? `<span class="big${disabled? " sk-fade" : ""}">${big}</span>` : ""}`
      + `<canvas class="sk-sig" width="107" height="33"></canvas><span class="who">학원장</span><span class="how">${how}</span>`
      + `${tw([[2, 2], [125, 3], [126, 68], [2, 70]])}</button>`); }
  /* 의뢰 쪽지 (1006) — 이번 주 의뢰를 미리 보인다(weekJobPlan — 주를 시작하기 전에 정해 둔다): 의뢰 이름 · 의뢰인 · 보수 ·
     오르는 멘탈리티 ▲ · 내리는 멘탈리티 ▼ · 그 의뢰처의 누적과 등급(의뢰처마다 따로) · 이번 주 맡은 학생. 계절 마무리 주에는 의뢰가 없어 뺀다 */
  { const J = weekJobPlan();
    if(J){
      const L = G.slip, g = jobGradeIdx(J.k), nx = JOB_GRADES[g+1], cnt = jobN(J.k), pay = jobPay(J.k);
      const nj = S.students.filter(s=> actOf(s) === "job").length;
      P.push(`<div class="sk-slip" style="left:${L.x*2}px;top:${L.y*2}px;${skBg("slip")}" title="${esc(J.who)} — “${esc(J.line)}”">`
        + `<div class="hd" style="left:12px;top:10px"><span class="sk-h" style="color:#8a5e1c">${esc(J.n)}</span><span class="gr">${g+1}등급</span></div>`
        + `<span class="sk-fade" style="left:12px;top:38px">${esc(J.who)}</span>`
        + `<span style="left:12px;top:54px"><span class="sk-ink2">보수 </span><span class="sk-brass">${fmt(pay)} G/일</span><span class="sk-ink2"> · 컨디션 </span><span class="sk-red">-${JOB_COND}/일</span></span>`
        + `<span style="left:12px;top:68px"><span class="sk-ink2">${esc(mentShort(J.up))} </span><span class="sk-grn">▲</span><span class="sk-ink2"> · ${esc(mentShort(J.down))} </span><span class="sk-red">▼</span></span>`
        + (nx ? `<span style="left:12px;top:82px"><span class="sk-ink2">누적 </span>${fmt(cnt)} / ${fmt(nx.min)}회</span><span class="bar" style="left:150px;top:84px;width:84px"><i style="width:${Math.round(80 * clamp(cnt / nx.min, 0, 1))}px"></i></span>`
              : `<span style="left:12px;top:82px"><span class="sk-ink2">누적 </span>${fmt(cnt)}회<span class="sk-brass"> · 최대 등급</span></span>`)
        + `<span style="left:12px;top:96px">${nj? `<span class="sk-ink2">이번 주 </span><span class="sk-brass">의뢰 ${nj}명</span><span class="sk-ink2"> · 최대 </span><span class="sk-brass">+${fmt(pay * nj * WEEK_DAYS)} G</span>` : `<span class="sk-fade">이번 주 의뢰를 맡은 학생이 없다</span>`}</span></div>`);
    } }
  /* ── 무대 ── */
  const Q = G.quill, IW = G.inkwell;
  /* 반짝임 (1006) — 다섯 칸이 차면 깃펜(저장된 서명이 있으면 결재란도 — 1011) · 깃펜을 집으면 잉크 단지 · 잉크를 찍으면 결재란 (skFxUpd 가 켠다).
     별 자리 = 그림 1배 좌표 (깃펜: 끝 · 깃 위 · 아래 깃 · 펜촉 / 잉크 단지: 왼쪽 위 모서리 · 금 고리 · 오른쪽 · 왼쪽 아래 / 결재란: 네 귀퉁이 쪽) */
  return `<section class="skwrap" aria-label="${esc(yrName(S.year))} ${ph.n} 스케줄"><div class="skfit"><div class="skstage" style="--sk-sheet:url('${SCHED_ART.sheet}');--sk-ss:${G.sheet.w*2}px ${G.sheet.h*2}px;--sk-chain:url('${SCHED_ART.chain}')">`
    + `<img class="sk-under" src="${SCHED_ART.under}" alt="" draggable="false">`
    + `<div class="sk-paper" style="left:${G.paper.x*2}px;top:${G.paper.y*2}px">${P.join("")}</div>`
    + `<img class="sk-over1" src="${SCHED_ART.over1}" alt="" draggable="false">`
    + (IW? `<div class="sk-inkfx" style="left:${IW.x*2}px;top:${IW.y*2}px;width:${IW.w*2}px;height:${IW.h*2}px"><img src="${SCHED_ART.inkwell}" alt="" draggable="false">${tw([[1, 1], [41, 6], [IW.w - 1, Math.round(IW.h * .55)], [6, IW.h - 9]])}</div>` : "")
    + `<button type="button" class="sk-quill" style="left:${(Q.x - Q.px)*2}px;top:${(Q.y - Q.py)*2}px" aria-label="깃펜 — 집어서 잉크 단지에 찍고 결재란에 서명한다"><img src="${SCHED_ART.quill}" alt="" draggable="false"><i class="tip" style="left:${Q.px*2 - 2}px;top:${Q.py*2 - 4}px"></i>${tw([[Q.w - 9, 5], [56, 12], [22, 35], [Q.px + 2, Q.py - 2]])}</button>`
    + `<img class="sk-over2" src="${SCHED_ART.over2}" alt="" draggable="false">`
    + `<div class="sk-hold" hidden></div>`
    + `</div></div></section>`;
}

/* ── 무대 크기 · 좌표 ── */
function skStage(){ return document.querySelector("#view .skstage"); }
function skFit(){
  const st = skStage(); if(!st) return;
  const w = st.parentElement.clientWidth; if(!w) return;
  SK.s = w / 1544; st.style.setProperty("--sk-s", SK.s.toFixed(5));
}
/* ── 사이드가 잉크 단지 · 깃펜을 가리지 않게 (1010) ──
   가로 화면의 사이드(#app>.topbar)는 화면에 고정이고 무대 오른쪽 위에 얹힌다. 소품(잉크 단지 · 깃펜)은 그 아래 책상 자리라
   화면이 낮으면(14인치 맥북 등) 무대를 아래로 내렸을 때, 창이 좁으면(무대가 작다) 처음부터 사이드가 소품 위로 내려와 잉크를 찍을 수 없었다.
   페이지를 끝까지 내렸을 때 소품의 위쪽을 재서, 사이드가 거기까지 내려오면 ① 'MENU' 글자 ② 스케줄 단추(지금 보는 화면)를 차례로 숨기고
   ③ 그래도 길면 사이드 높이를 줄인다 (안에서 스크롤). 스크롤하는 동안 사이드가 바뀌지 않게 끝까지 내린 자리 하나로 정한다.
   다시 재는 때 — 스케줄을 그릴 때 · 무대 폭이 바뀔 때 · 창 크기가 바뀔 때 · 글꼴을 받았을 때. 다른 화면으로 가면 되돌린다 (skLeave) */
const SK_SIDE_GAP = 6;                                             // 사이드 아래 끝과 소품 사이 (화면 px)
function skSideReset(){
  document.documentElement.classList.remove("sk-side1", "sk-side2");
  const tb = document.querySelector("#app>.topbar"); if(tb) tb.style.removeProperty("max-height");
}
function skSideFit(){
  const st = skStage(), tb = document.querySelector("#app>.topbar"), keep = tb ? tb.scrollTop : 0;
  skSideReset();
  if(!st || !tb || getComputedStyle(tb).position !== "fixed") return;      // 세로 · 좁은 화면 — 사이드가 아니라 위쪽 띠
  const r = st.getBoundingClientRect(), s = r.width / 1544, t = tb.getBoundingClientRect();
  if(!s || !t.height) return;
  const IW = SCHED_GEO.inkwell, Q = SCHED_GEO.quill;
  const zx = Math.min(IW.x, Q.x - Q.px) * 2, zy = Math.min(IW.y, Q.y - Q.py) * 2;   // 소품 자리 왼쪽 · 위 (2배 좌표)
  if(r.left + zx * s >= t.right) return;                                   // 사이드와 옆으로 비켜 있다
  const de = document.documentElement, endY = Math.max(0, de.scrollHeight - innerHeight);
  const room = r.top + scrollY - endY + zy * s - SK_SIDE_GAP - t.top;     // 끝까지 내렸을 때 사이드가 쓸 수 있는 높이
  for(const c of ["sk-side1", "sk-side2"]){ if(tb.scrollHeight <= room) return; de.classList.add(c); }
  if(tb.scrollHeight > room){ tb.style.maxHeight = Math.max(240, Math.floor(room)) + "px"; tb.scrollTop = keep; }   // 다시 그려도 사이드 안 스크롤은 그대로
}
function skPt(e){ const r = skStage().getBoundingClientRect(); return {x:(e.clientX - r.left) / SK.s, y:(e.clientY - r.top) / SK.s}; }
function skInkRect(){ const I = SCHED_GEO.ink; return {x:I.x*2, y:I.y*2, w:I.w*2, h:I.h*2}; }

/* ── 카드 끌기 — 줄인 무대 안에서 유령 카드를 직접 그린다 (기본 끌기 dragCfg 는 무대 밖 body 에 그려서 크기가 어긋난다) ── */
function skDragBind(v){
  v.__dragCfg = null;
  const stage = skStage(); if(!stage) return;
  const paper = stage.querySelector(".sk-paper");
  let st = null;
  const clearHi = ()=> stage.querySelectorAll(".sk-on").forEach(x=> x.classList.remove("sk-on"));
  const target = (e)=>{
    const el = document.elementFromPoint(e.clientX, e.clientY);
    return el && el.closest ? el.closest(".sk-paper [data-slot], .sk-paper [data-handzone]") : null;
  };
  const end = ()=>{ if(st && st.ghost) st.ghost.remove(); if(st && st.el) st.el.classList.remove("sk-lift"); clearHi(); st = null; };
  stage.onpointerdown = (e)=>{
    if(SK.held || SK.busy || (e.button != null && e.button !== 0)) return;
    const el = e.target && e.target.closest ? e.target.closest(".sk-card[data-card]") : null;
    if(!el) return;
    st = {el, u: +el.dataset.card, x: e.clientX, y: e.clientY, started: false, th: e.pointerType === "mouse" ? 6 : 14};
  };
  const move = (e)=>{
    if(!st) return;
    if(!stage.isConnected){ end(); return; }
    if(!st.started){
      if(Math.abs(e.clientX - st.x) + Math.abs(e.clientY - st.y) < st.th) return;
      st.started = true;
      const r = st.el.getBoundingClientRect(), pr = paper.getBoundingClientRect();
      st.gx = (r.left - pr.left) / SK.s; st.gy = (r.top - pr.top) / SK.s;
      const g = st.el.cloneNode(true); g.classList.add("sk-ghost"); g.removeAttribute("data-card"); g.removeAttribute("tabindex");
      g.style.left = st.gx + "px"; g.style.top = st.gy + "px"; paper.appendChild(g); st.ghost = g;
      st.el.classList.add("sk-lift");
    }
    st.ghost.style.left = (st.gx + (e.clientX - st.x) / SK.s) + "px"; st.ghost.style.top = (st.gy + (e.clientY - st.y) / SK.s) + "px";
    clearHi(); const t = target(e); if(t) t.classList.add("sk-on");
    if(e.cancelable) e.preventDefault();
  };
  const up = (e)=>{
    if(!st) return;
    const started = st.started, u = st.u, t = started ? target(e) : null;
    end();
    if(!started) return;
    DRAG.block = true;                                           // 끌고 난 뒤 따라오는 click(빈 칸에 넣기)은 막는다
    if(!t) return;
    if(t.dataset.handzone){ const j = (S.slots||[]).findIndex(c=> c && c.u === u); if(j >= 0){ slotClear(j); save(); render(); } return; }
    slotPut(u, +t.dataset.slot); save(); render();
  };
  if(SK.dragMove) window.removeEventListener("pointermove", SK.dragMove);
  if(SK.dragUp) window.removeEventListener("pointerup", SK.dragUp);
  SK.dragMove = move; SK.dragUp = up;
  window.addEventListener("pointermove", move, {passive:false});
  window.addEventListener("pointerup", up);
}

/* ── 서명 캔버스 ── */
function skSig(){ return document.querySelector("#view .sk-sig"); }
function skSigPt(e){                                             // 화면 좌표 → 서명 캔버스 칸 (밖이면 가장자리로)
  const c = skSig(), r = c.getBoundingClientRect();
  return {x: clamp(Math.floor((e.clientX - r.left) / r.width * c.width), 0, c.width - 1), y: clamp(Math.floor((e.clientY - r.top) / r.height * c.height), 0, c.height - 1)};
}
function skSigToStage(px, py){                                    // 서명 캔버스 칸 → 무대 좌표 (깃펜 펜촉 자리)
  const c = skSig(), r = c.getBoundingClientRect(), sr = skStage().getBoundingClientRect();
  return {x: (r.left + (px + .5) / c.width * r.width - sr.left) / SK.s, y: (r.top + (py + .5) / c.height * r.height - sr.top) / SK.s};
}
function skOverSign(e){                                       // 결재란 어디든 — 그은 자리는 서명줄 안으로 붙인다
  const b = document.querySelector("#view .sk-appr"); if(!b) return false;
  const r = b.getBoundingClientRect();
  return e.clientX >= r.left && e.clientX <= r.right && e.clientY >= r.top && e.clientY <= r.bottom;
}
function skLine(g, x0, y0, x1, y1, a){                          // 도트 선 (Bresenham) — 잉크가 묽어지면 흐리게
  g.fillStyle = SK_INK; g.globalAlpha = a;
  let dx = Math.abs(x1 - x0), sx = x0 < x1 ? 1 : -1, dy = -Math.abs(y1 - y0), sy = y0 < y1 ? 1 : -1, err = dx + dy;
  for(let k = 0; k < 400; k++){
    g.fillRect(x0, y0, 1, 1);
    if(x0 === x1 && y0 === y1) break;
    const e2 = 2 * err; if(e2 >= dy){ err += dy; x0 += sx; } if(e2 <= dx){ err += dx; y0 += sy; }
  }
  g.globalAlpha = 1;
}
function skInkAlpha(){ return SK.ink > .25 ? 1 : SK.ink > 0 ? .45 + SK.ink * 2 : 0; }

/* ── 깃펜 ── */
function skQuill(){ return document.querySelector("#view .sk-quill"); }
function skQuillAt(x, y, held){                                  // x, y = 펜촉 (무대 좌표) — 그림 한 칸(2) 단위로
  const q = skQuill(), Q = SCHED_GEO.quill; if(!q) return;
  const ax = Math.round(x / 2) * 2, ay = Math.round(y / 2) * 2;
  q.style.left = (ax - Q.px*2) + "px"; q.style.top = (ay - Q.py*2) + "px";
  q.classList.toggle("held", !!held);
  SK.nib = {x: ax, y: ay};
}
function skQuillHome(){ const Q = SCHED_GEO.quill; skQuillAt(Q.x*2, Q.y*2, false); }
function skInkUpd(){ const q = skQuill(); if(!q) return; q.classList.toggle("inked", SK.ink > 0); q.style.setProperty("--ink", String(Math.max(.25, Math.min(1, SK.ink * 1.6)))); skFxUpd(); }
/* 반짝임 (1006) — 다음에 할 일을 빛으로 알려 준다: 다섯 칸이 차면 깃펜 → 깃펜을 집으면 잉크 단지 → 잉크를 찍으면 결재란.
   잉크가 떨어지면 다시 잉크 단지가 반짝인다. 저장된 서명이 있으면 다섯 칸이 찼을 때 결재란도 깃펜과 같이 반짝인다 (1011 — 누르면 바로 서명) */
function skFxUpd(){
  const st = skStage(); if(!st) return;
  const rd = skReady(), q = skQuill(), b = $("#btnWeek"), iw = st.querySelector(".sk-inkfx");
  const run = !!(UI && UI.wrun);                                   // 주가 진행 중(경과 보고 · 원정) — 빛도 소리도 없다
  const glint = rd && !run && !SK.held && !SK.busy, inkOn = rd && !run && SK.held && SK.ink <= 0 && !SK.busy;
  if(q) q.classList.toggle("glint", glint);
  if(iw) iw.classList.toggle("on", inkOn);
  if(b){ b.classList.toggle("inked", rd && SK.held && SK.ink > 0); b.classList.toggle("glint", glint && skHasSign()); }
  /* 반짝이는 소리 (1006) — 깃펜이나 잉크 단지가 빛나기 시작할 때 (깃펜 → 잉크 단지로 넘어갈 때는 이어서). 빛이 꺼지면 잦아든다.
     다른 화면에서 스케줄로 넘어왔을 때 일과가 이미 꽉 차 있으면 그때도 울린다 (skLeave 가 SK.fx 를 비운다). 스케줄 안에서 다시 그릴 때는 울리지 않는다 */
  const glow = glint || inkOn, was = !!(SK.fx && SK.fx.glow);
  if(glow && !was) skGlowSnd(true); else if(!glow && was) skGlowSnd(false);
  SK.fx = {glow};
}
/* 두루마리 스케줄이 아닌 화면으로 갈 때 (bindView) — 반짝이는 소리를 끄고, 다음에 스케줄로 돌아오면 처음 연 것처럼. 줄였던 사이드도 되돌린다 (1010) */
function skLeave(){ skGlowSnd(false); SK.fx = null; skSideReset(); }

/* ── 소리 (1006) — 일과 놓기 · 체인 · 서명 (SFX.sk_* · bgm/sched_*.ogg). 효과음 음량을 따른다 ── */
function skSfx(k){ try{ sfxPlay(k); }catch(e){} }
/* slotPut · 자동 배치 뒤 — 새로 놓인 카드가 있으면 놓는 소리, 같은 색끼리 새 고리가 생기면 이어서 체인 소리 */
function slotSfx(pre){
  try{
    const now = S.slots || [], was = pre || [];
    if(!now.some((c, i)=> c && (!was[i] || was[i].u !== c.u))) return;
    skSfx("sk_place");
    const links = L=>{ const o = new Set(); for(let i = 1; i < L.length; i++) if(L[i] && L[i-1] && chainOf(L, i) > 0) o.add(L[i-1].u + ":" + L[i].u); return o; };
    const a = links(was);
    if([...links(now)].some(k=> !a.has(k))) setTimeout(()=> skSfx("sk_chain"), 110);
  }catch(e){}
}
/* 서명 소리 — 펜이 종이 위에서 움직이는 동안만 (멈추고 0.12초 지나면 끈다). 고리 소리를 매번 다른 자리에서 시작한다 */
const SK_SCR = {on:false, t:0, src:null, g:null, el:null};
function skScratch(on){
  let t = null; try{ t = SFX.sk_sign; }catch(e){}
  if(!t) return;
  if(!on){
    clearTimeout(SK_SCR.t);
    if(!SK_SCR.on) return;
    SK_SCR.on = false;
    const src = SK_SCR.src, vg = SK_SCR.g; SK_SCR.src = SK_SCR.g = null;
    if(src && ACTX){ try{ const now = ACTX.currentTime; vg.gain.cancelScheduledValues(now); vg.gain.setValueAtTime(vg.gain.value, now); vg.gain.linearRampToValueAtTime(0, now + .06); src.stop(now + .08); }catch(e){} }
    if(SK_SCR.el){ try{ SK_SCR.el.pause(); }catch(e){} }
    return;
  }
  clearTimeout(SK_SCR.t); SK_SCR.t = setTimeout(()=> skScratch(false), 120);
  if(SK_SCR.on) return;
  try{
    const g = sfxGain(); if(g <= 0) return;
    const v = (t.v == null ? 1 : t.v);
    if(AWEB === false || ASBAD[t.f] || !audCtx()){                // <audio> (file:// 등)
      let el = SK_SCR.el;
      if(!el){ el = SK_SCR.el = new Audio(BGM_DIR + t.f); el.preload = "auto"; el.loop = true; }
      el.volume = clamp(g * v, 0, 1);
      if(el.duration) el.currentTime = Math.random() * el.duration;
      el.play().catch(()=>{});
      SK_SCR.on = true; return;
    }
    const ctx = ACTX, buf = ASBUF[t.f];
    if(!buf){ sfxLoad(t.f); return; }                               // 아직 못 받았다 — 받는 대로 다음 획부터
    if(ctx.state === "suspended") ctx.resume().catch(()=>{});
    if(!ASG){ ASG = ctx.createGain(); ASG.connect(ctx.destination); }
    ASG.gain.value = g;
    const src = ctx.createBufferSource(), vg = ctx.createGain(), now = ctx.currentTime;
    src.buffer = buf; src.loop = true;
    vg.gain.setValueAtTime(0, now); vg.gain.linearRampToValueAtTime(v, now + .03);
    src.connect(vg); vg.connect(ASG); src.start(now, Math.random() * buf.duration);
    SK_SCR.src = src; SK_SCR.g = vg; SK_SCR.on = true;
  }catch(e){}
}
function skSfxPreload(){                                          // 스케줄을 열 때 미리 받아 둔다 — 첫 카드 소리가 늦지 않게
  try{ if(ACTX && AWEB !== false && sfxGain() > 0) ["sk_place", "sk_chain", "sk_sign", "sk_glow"].forEach(k=> SFX[k] && sfxLoad(SFX[k].f)); }catch(e){}
}
/* 반짝이는 소리 (1006, SFX.sk_glow · 13.8초) — 빛나는 동안 한 번 끝까지(되풀이하지 않는다). 빛이 꺼지면 0.4초에 걸쳐 잦아든다.
   아직 소리를 못 받았으면 받는 대로 (그때도 빛나고 있으면) 튼다 */
const SK_GLW = {want:false, on:false, src:null, g:null, el:null, iv:0};
function skGlowSnd(want){
  let t = null; try{ t = SFX.sk_glow; }catch(e){}
  if(!t) return;
  SK_GLW.want = !!want;
  if(!want){
    if(!SK_GLW.on) return;
    SK_GLW.on = false;
    const src = SK_GLW.src, vg = SK_GLW.g; SK_GLW.src = SK_GLW.g = null;
    if(src && ACTX){ try{ const now = ACTX.currentTime; vg.gain.cancelScheduledValues(now); vg.gain.setValueAtTime(vg.gain.value, now); vg.gain.linearRampToValueAtTime(0, now + .4); src.stop(now + .45); }catch(e){} }
    const el = SK_GLW.el;
    if(el && !el.paused){ clearInterval(SK_GLW.iv); SK_GLW.iv = setInterval(()=>{ try{ el.volume = Math.max(0, el.volume - .02); if(el.volume <= .001 || SK_GLW.on){ clearInterval(SK_GLW.iv); if(!SK_GLW.on) el.pause(); } }catch(e){ clearInterval(SK_GLW.iv); } }, 40); }
    return;
  }
  if(SK_GLW.on) return;
  try{
    const g = sfxGain(); if(g <= 0) return;
    const v = (t.v == null ? 1 : t.v);
    if(AWEB === false || ASBAD[t.f] || !audCtx()){                // <audio> (file:// 등)
      let el = SK_GLW.el;
      if(!el){ el = SK_GLW.el = new Audio(BGM_DIR + t.f); el.preload = "auto"; }
      clearInterval(SK_GLW.iv);
      el.volume = clamp(g * v, 0, 1); try{ el.currentTime = 0; }catch(e){}
      el.play().catch(()=>{});
      SK_GLW.on = true; return;
    }
    const ctx = ACTX, buf = ASBUF[t.f];
    if(!buf){ sfxLoad(t.f, ()=>{ if(SK_GLW.want && !SK_GLW.on) skGlowSnd(true); }); return; }
    if(ctx.state === "suspended") ctx.resume().catch(()=>{});
    if(!ASG){ ASG = ctx.createGain(); ASG.connect(ctx.destination); }
    ASG.gain.value = g;
    const src = ctx.createBufferSource(), vg = ctx.createGain(), now = ctx.currentTime;
    src.buffer = buf;
    vg.gain.setValueAtTime(0, now); vg.gain.linearRampToValueAtTime(v, now + .08);
    src.connect(vg); vg.connect(ASG); src.start(now);
    src.onended = ()=>{ if(SK_GLW.src === src){ SK_GLW.src = SK_GLW.g = null; } };
    SK_GLW.src = src; SK_GLW.g = vg; SK_GLW.on = true;
  }catch(e){}
}
function skOverInk(p){ const R = skInkRect(), m = 4; return p.x >= R.x - m && p.x <= R.x + R.w + m && p.y >= R.y - m && p.y <= R.y + R.h + m; }
function skDip(){
  if(SK.dipT && Date.now() - SK.dipT < 350) return;
  SK.dipT = Date.now(); SK.ink = 1; skInkUpd();
  const q = skQuill(); if(q){ q.classList.remove("dip"); void q.offsetWidth; q.classList.add("dip"); }
  const R = skInkRect(), st = skStage(), rp = document.createElement("i");
  rp.className = "sk-ripple"; rp.style.left = (R.x + 4) + "px"; rp.style.top = (R.y + 4) + "px"; rp.style.width = (R.w - 8) + "px"; rp.style.height = (R.h - 8) + "px";
  st.appendChild(rp); setTimeout(()=> rp.remove(), 600);
}
function skHint(msg){ toast(msg); const q = skQuill(); if(q && !SK.held){ q.classList.remove("nudge"); void q.offsetWidth; q.classList.add("nudge"); } }
function skReady(){ const b = $("#btnWeek"); return !!(b && !b.disabled); }
function skPick(e){
  if(SK.busy) return;
  SK.held = true; SK.strokes = []; SK.len = 0; SK.writing = false; clearTimeout(SK.timer);
  const hold = document.querySelector("#view .sk-hold"); if(hold) hold.hidden = false;
  if(e) { const p = skPt(e); skQuillAt(p.x, p.y, true); } else skQuillAt(SK.nib ? SK.nib.x : 0, SK.nib ? SK.nib.y : 0, true);
  if(!SK.keyOn){ SK.keyOn = (ev)=>{ if(ev.key === "Escape" && SK.held && !SK.busy){ ev.preventDefault(); skDrop(); } }; document.addEventListener("keydown", SK.keyOn); }
  skFxUpd();
}
function skDrop(){                                               // 깃펜을 제자리에 내려놓는다 (쓰다 만 서명은 지운다)
  SK.held = false; SK.writing = false; clearTimeout(SK.timer); skScratch(false);
  if(!SK.busy && SK.strokes.length){ const c = skSig(); if(c) c.getContext("2d").clearRect(0, 0, c.width, c.height); SK.strokes = []; SK.len = 0; }
  const hold = document.querySelector("#view .sk-hold"); if(hold) hold.hidden = true;
  if(SK.keyOn){ document.removeEventListener("keydown", SK.keyOn); SK.keyOn = null; }
  skQuillHome(); skFxUpd();
}
function skStrokeStart(e){
  if(!skReady()){ const b = $("#btnWeek"); skDrop(); toast(b && +b.dataset.need > 0 ? "다섯 칸을 모두 채운 뒤에 서명한다." : "지금은 결재할 수 없다."); return; }
  if(SK.ink <= 0){ toast("잉크가 없다 — 깃펜을 잉크 단지에 먼저 찍는다."); return; }
  clearTimeout(SK.timer);
  const p = skSigPt(e); SK.writing = true; SK.cur = [p.x, p.y];
  const g = skSig().getContext("2d"); skLine(g, p.x, p.y, p.x, p.y, skInkAlpha());
}
function skStrokeMove(e){
  const p = skSigPt(e), c = SK.cur, lx = c[c.length - 2], ly = c[c.length - 1];
  if(p.x === lx && p.y === ly) return;
  const d = Math.hypot(p.x - lx, p.y - ly);
  if(SK.ink > 0){ skLine(skSig().getContext("2d"), lx, ly, p.x, p.y, skInkAlpha()); SK.ink = Math.max(0, SK.ink - d / SK_INK_LEN); skInkUpd(); skScratch(true); }
  else if(!SK.dry){ SK.dry = true; skScratch(false); toast("잉크가 떨어졌다 — 잉크 단지에 다시 찍는다."); }
  c.push(p.x, p.y); SK.len += d;
}
function skStrokeEnd(){
  skScratch(false);
  if(!SK.writing) return;
  SK.writing = false; SK.dry = false;
  if(SK.cur && SK.cur.length >= 2) SK.strokes.push(SK.cur);
  SK.cur = null;
  clearTimeout(SK.timer); SK.timer = setTimeout(skFinish, 850);   // 잠깐 쉬면 서명이 끝난 것으로 본다 (획을 여러 번 그어도 된다)
}
function skFinish(){
  if(!SK.held || SK.writing || SK.busy) return;
  const c = skSig(); if(!c) return;
  if(SK.len >= 6 && (SK.ink <= .001 || (SK.nib && skOverInk(SK.nib)))){   // 잉크가 떨어져 다시 찍으러 갔다 — 이어 쓸 시간을 준다
    clearTimeout(SK.timer); SK.timer = setTimeout(skFinish, SK.ink <= .001 ? 2600 : 700); return;
  }
  if(SK.len < 6){                                                // 짧게 콕 — 저장된 서명을 쓴다
    c.getContext("2d").clearRect(0, 0, c.width, c.height);
    if(!PREF.sign || !Array.isArray(PREF.sign.s) || !PREF.sign.s.length){ SK.strokes = []; SK.len = 0; toast("아직 저장된 서명이 없다 — 서명줄에 서명을 그어 남긴다."); return; }
    skReplay(PREF.sign, ()=> skSigned(false));
    return;
  }
  PREF.sign = {v:1, w:c.width, h:c.height, s:SK.strokes.slice(0, 40).map(s=> s.slice(0, 600))};
  prefSave();
  skSigned(true);
}
/* 저장된 서명 → 지금 서명 칸 (1011) — 서명 칸을 위로 키웠다(107×20 → 107×33). 예전 서명은 늘리지 않고 아래(서명 줄)에 붙인다 · 큰 서명만 줄인다 */
function skSigFit(sig, c){
  const sw = sig.w || c.width, sh = sig.h || c.height, k = Math.min(1, c.width / sw, c.height / sh);
  return {k, dy: c.height - Math.round(sh * k)};
}
function skReplay(sig, done){                                    // 저장된 서명을 깃펜이 따라 쓴다
  SK.busy = true;
  const c = skSig(), g = c.getContext("2d"), m = skSigFit(sig, c);
  const strokes = sig.s.map(s=>{ const o = []; for(let i = 0; i + 1 < s.length; i += 2) o.push([Math.round(s[i] * m.k), Math.round(s[i+1] * m.k) + m.dy]); return o; }).filter(s=> s.length);
  let si = 0, pi = 0, acc = 0, last = performance.now();
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches, speed = reduce ? 4000 : 150;   // 칸/초
  const step = (now)=>{
    if(!c.isConnected){ SK.busy = false; skScratch(false); return; }
    acc += (now - last) / 1000 * speed; last = now;
    let drew = false;
    while(acc >= 1 && si < strokes.length){
      const s = strokes[si];
      if(pi === 0){ skLine(g, s[0][0], s[0][1], s[0][0], s[0][1], 1); pi = 1; }
      if(pi < s.length){ const a = s[pi - 1], b = s[pi]; skLine(g, a[0], a[1], b[0], b[1], 1); acc -= Math.max(1, Math.hypot(b[0] - a[0], b[1] - a[1])); pi++; drew = true; }
      if(pi >= s.length){ si++; pi = 0; }
    }
    if(drew) skScratch(true);                                     // 깃펜이 쓰는 동안만 소리
    const cur = strokes[Math.min(si, strokes.length - 1)], pt = cur[Math.max(0, Math.min(pi, cur.length) - 1)] || cur[0];
    const sp = skSigToStage(pt[0], pt[1]); skQuillAt(sp.x, sp.y, true);
    if(si < strokes.length) requestAnimationFrame(step); else { SK.busy = false; skScratch(false); done && done(); }
  };
  requestAnimationFrame(step);
}
function skSigned(fresh){                                         // 서명 끝 — 잉크가 마르는 동안 잠깐 보여 주고 깃펜을 내려놓은 뒤 진행
  SK.busy = true; skScratch(false);
  const b = $("#btnWeek"); if(b) b.classList.add("signed");
  if(fresh) toast("서명을 남겼다 — 다음부터는 결재란을 누르면 이 서명이 써진다.");
  setTimeout(()=>{
    SK.busy = false; SK.held = false; SK.ink = 0;
    const hold = document.querySelector("#view .sk-hold"); if(hold) hold.hidden = true;
    if(SK.keyOn){ document.removeEventListener("keydown", SK.keyOn); SK.keyOn = null; }
    SK.fx = {glow: true};                                         // 결재를 마쳤다 — 깃펜이 제자리로 돌아가도 반짝이는 소리는 내지 않는다 (곧 주가 진행되고 경과 보고가 뜬다)
    skQuillHome(); skInkUpd();                                     // skInkUpd → skFxUpd
    const bw = $("#btnWeek"); if(bw && bw.isConnected && !bw.disabled && SK.go) SK.go(bw);
  }, window.matchMedia("(prefers-reduced-motion: reduce)").matches ? 150 : 550);
}
function skMoveTo(x, y, ms){                                       // 깃펜을 (x, y) 까지 옮긴다 (키보드 서명)
  return new Promise(res=>{
    const a = SK.nib || {x, y}, t0 = performance.now();
    const f = (now)=>{ const k = Math.min(1, (now - t0) / ms), e = k < .5 ? 2*k*k : 1 - Math.pow(-2*k + 2, 2) / 2;
      skQuillAt(a.x + (x - a.x) * e, a.y + (y - a.y) * e, true); if(k < 1 && skQuill()) requestAnimationFrame(f); else res(); };
    requestAnimationFrame(f);
  });
}
async function skAutoSign(){                                      // Enter · 저장된 서명이 있을 때 결재란 누르기 (1011) — 깃펜이 스스로 잉크를 찍고 서명한다
  if(SK.busy || !skReady()) return;
  SK.busy = true;
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches, T = reduce ? 1 : 280;
  SK.busy = false; skPick(null); SK.busy = true;                  // 깃펜을 든 상태로 (busy 인 채로는 skPick 이 바로 돌아간다)
  const R = skInkRect();
  await skMoveTo(R.x + R.w / 2, R.y + R.h / 2, T); skDip(); await new Promise(r=> setTimeout(r, reduce ? 1 : 260));
  const sig = (PREF.sign && Array.isArray(PREF.sign.s) && PREF.sign.s.length) ? PREF.sign : {w:107, h:20, s:SK_SIG0};
  const c = skSig(); if(!c){ SK.busy = false; return; }
  const s0 = sig.s[0], m = skSigFit(sig, c), sp = skSigToStage(Math.round(s0[0]*m.k), Math.round(s0[1]*m.k) + m.dy);
  await skMoveTo(sp.x, sp.y, T);
  skReplay(sig, ()=> skSigned(false));
}
function bindSchedScroll(v){
  const stage = skStage(); if(!stage) return;
  skFit(); skSideFit(); skActFit();
  if(SK.ro) SK.ro.disconnect();
  if(typeof ResizeObserver === "function"){ SK.ro = new ResizeObserver(()=>{ skFit(); skSideFit(); }); SK.ro.observe(stage.parentElement); }
  SK.held = false; SK.busy = false; SK.ink = 0; SK.strokes = []; SK.len = 0; SK.writing = false; clearTimeout(SK.timer); skScratch(false);
  if(SK.keyOn){ document.removeEventListener("keydown", SK.keyOn); SK.keyOn = null; }
  skQuillHome(); skFxUpd(); skSfxPreload();
  skDragBind(v);
  /* 결재 — 원래 단추가 하던 일(진행 · 시즌 마무리)은 서명이 끝난 뒤에 */
  const bw = $("#btnWeek");
  if(bw){
    const orig = bw.onclick;
    SK.go = (b)=>{ if(typeof orig === "function") orig.call(b, {currentTarget:b}); else runWithReport(); };
    bw.onclick = (e)=>{
      if(SK.busy) return;
      if(e && e.detail === 0){ skAutoSign(); return; }               // 키보드 — 깃펜이 스스로
      if(skHasSign()){ skAutoSign(); return; }                      // 저장된 서명이 있으면 바로 (1011)
      skHint("깃펜을 집어 잉크 단지에 찍은 뒤 서명줄에 서명한다.");
    };
  }
  const q = skQuill();
  if(q){
    q.onpointerdown = (e)=>{
      if(SK.busy || (e.button != null && e.button !== 0)) return;
      e.preventDefault(); e.stopPropagation();
      if(SK.held) return;
      skPick(e);
      try{ q.releasePointerCapture(e.pointerId); }catch(x){}          // 터치는 누른 곳(깃펜)이 포인터를 붙잡는다 — 덮개로 넘긴다
      try{ if(hold) hold.setPointerCapture(e.pointerId); }catch(x){}
    };
    q.onclick = (e)=>{ if(e.detail === 0 && !SK.busy){ if(skReady()) skAutoSign(); else toast("다섯 칸을 모두 채운 뒤에 서명한다."); } };
  }
  const hold = stage.querySelector(".sk-hold");
  if(hold){
    hold.onpointermove = (e)=>{
      if(!SK.held || SK.busy) return;
      const p = skPt(e); skQuillAt(p.x, p.y, true);
      if(SK.writing) skStrokeMove(e);
      else if(skOverInk(p)) skDip();
    };
    hold.onpointerdown = (e)=>{
      if(!SK.held || SK.busy) return;
      e.preventDefault();
      const p = skPt(e); skQuillAt(p.x, p.y, true);
      if(skOverInk(p)){ skDip(); return; }
      if(skOverSign(e)){ try{ hold.setPointerCapture(e.pointerId); }catch(x){} skStrokeStart(e); return; }
      if(SK.strokes.length) return;                              // 서명하다가 다른 데를 누른 건 무시
      skDrop();
    };
    hold.onpointerup = (e)=>{ if(SK.writing) skStrokeEnd(); };
    hold.onpointercancel = ()=>{ if(SK.writing) skStrokeEnd(); };
    hold.oncontextmenu = (e)=>{ e.preventDefault(); if(!SK.busy) skDrop(); };
  }
  /* 명부 — 행동 칸을 누르면 훈련 → 휴식 → 의뢰 (임의는 감췄다 — 임의인 학생은 지금 보이는 칸에서 다음으로) */
  v.querySelectorAll("[data-sk-act]").forEach(b=> b.onclick = (e)=>{
    e.stopPropagation();
    const st = S.students.find(s=> String(s.id) === b.dataset.skAct); if(!st) return;
    const L = actPickKeys();
    st.focus = L[(L.indexOf(actShown(st)) + 1) % L.length]; delete st._prevFocus;
    save(); render();
  });
  v.querySelectorAll("[data-sk-page]").forEach(b=> b.onclick = ()=>{ UI.skPage = (UI.skPage|0) + Number(b.dataset.skPage); render(); });
  v.querySelectorAll(".sk-card[data-card]").forEach(el=> el.onkeydown = (e)=>{ if(e.key === "Enter" || e.key === " "){ e.preventDefault(); el.click(); } });
}
/* 가로 ↔ 세로가 바뀌면 스케줄 화면을 다시 그린다 (마을 지도와 같은 기준 · TOWN_MQ 는 아래에서 선언돼 여기서 따로 만든다) */
{ const mq = (typeof matchMedia === "function") ? matchMedia("(min-width:1100px) and (orientation:landscape)") : null;
  const h = ()=>{ if(UI && UI.view === "plan" && S) render(); };
  if(mq){ if(mq.addEventListener) mq.addEventListener("change", h); else if(mq.addListener) mq.addListener(h); } }
/* 창 높이만 바뀌어도(무대 폭은 그대로) · 글꼴을 받아 사이드 높이가 바뀌어도 사이드를 다시 잰다 (1010 — 학원 이름 맞춤 acadNameFit 의 0.15초 뒤) */
{ let t = 0;
  const h = ()=>{ clearTimeout(t); t = setTimeout(()=>{ if(typeof UI !== "undefined" && UI.view === "plan" && skStage()){ skSideFit(); skActFit(); } }, 200); };   // 1011 — 글꼴이 바뀌면 개인 행동 줄 폭도
  addEventListener("resize", h);
  if(document.fonts && document.fonts.addEventListener) document.fonts.addEventListener("loadingdone", h); }
/* SCHED_SCROLL_END */
