/* LKWIN_START — 락커룸 창 (1013 · apply_lkwin.py) ─ 경기 직전 감독의 한마디를 상담창 같은 창으로. mockups/locker-room 목업 그대로
   흐름: 경기 화면에 들어서면 한마디 전일 때 창이 같이 뜬다 — 출전 · 엔트리 확정 · 대진 확정을 눌렀을 때, 전투를 보고 '결과 확정'으로 다음 경기에 왔을 때 (lkwAuto)
   → 출전 학생 3 ~ 5명이 둥글게 모인다 → 구름 넷(기대치 충족 요구 1 · 부담감 완화 1 · 동기부여 2)
   → 고르면 마스터의 말 · 학생들이 가운데로 살짝 다가서고 머리 위에 … (잠시 고민) → 한 명씩 반응: 납득 ~♪ (폴짝) · 못 납득 | | | (어깨가 처지고 어두워진다)
   · 이름표의 기분 ±20 → 글 상자에 통함 · 빗나감 · 신뢰 · 이번 경기 기분 보정 → '경기 시작 ▶' 로 전투
   · '말없이 시작 ▶' — 한마디 없이 바로 전투 · ×(Esc) — 경기 화면으로 (그 화면의 '경기 시작'을 누르면 창이 다시 뜬다. 한마디를 했으면 바로 전투)
   · 경기 화면에는 창을 여는 단추가 없다 (1013 사용자 — '출전을 누르면 한마디 전이면 락커룸이 같이 뜨게'. 예전 '락커룸에서 한마디' 단추 · 안내는 뺐다)
   · '빠르게 결과만' · '남은 경기 한 번에'는 창 없이 (그때까지의 기분 그대로) — 그렇게 넘긴 다음 경기는 창이 저절로 뜨지 않는다 ('경기 시작'에서)
   · 고르는 순간 게임에 반영한다 (lockerSpeak — 기분 · 신뢰 · 일지). 연출 중에 창을 닫아도 결과는 남는다
   · 배경 — 그 경기의 대회 쿼터뷰 지도(TQ_MAPS · tqMapKey — 시내 · 광역 / 예선 · 본선 · 친선전은 그 계절 학원)를 흐리게. 바닥 문장(mx, my)이 허들 바로 뒤
   · 학생 — 상담창과 같은 전투 idle 도트(cslwSprUrl — 머리색 · #111 테두리)를 1.5배. 둥글게 선 원의 먼 쪽 반원: 양 끝이 앞(아래) · 가운데가 뒤(위),
     오른쪽 학생은 좌우를 뒤집어 가운데를 본다. 머리 · 발 자리는 도트에서 잰다 (lkwMeasure)
   · 무대 768 × 432 (1배 384 × 216 의 2배) · 창 796. 좁은 화면(창을 0.8배보다 줄여야 할 때)은 무대만 폭에 맞춰 줄이고 구름 · 이름표는 무대 아래로 (상담창과 같은 방식)
   · 소리 — 상담창 것: 구름을 고를 때 csl_pick · 마스터의 말 csl_mst · 반응 csl_ok / csl_ng
   · 튜토리얼 8(전투 전, 학생들에게 한마디)은 창을 처음 열 때 창 위에
   · 시험 · 점검용: lkwOpen({instant:true, pick:k}) — 기다림 · 글자 찍기 없이 그 단계까지 (pick 을 주면 그 말을 골라 결과까지) */
const LKW_W = 768, LKW_H = 432;
const LKW_K = 1.5;                                               // 학생 도트 배율 — 도트 1칸 = 1.5px (상담창은 2배의 0.95 · 다섯이 모이면 커서 줄였다)
/* 허들 자리 (1.5배 기준) — dx 머리 가운데 · dy 발끝: 무대 (384, 앞줄 발끝) 에서 떨어진 양. m 좌우 뒤집기 · s 다가서는 쪽 (l 오른쪽으로 · r 왼쪽으로) · d 밝기 */
const LKW_SLOTS = {
  1: [{dx:0, dy:-20, m:0, s:"c", d:1}],
  2: [{dx:-56, dy:0, m:0, s:"l", d:1}, {dx:56, dy:0, m:1, s:"r", d:1}],
  3: [{dx:-100, dy:0, m:0, s:"l", d:1}, {dx:0, dy:-40, m:0, s:"c", d:.94}, {dx:100, dy:0, m:1, s:"r", d:1}],
  4: [{dx:-138, dy:0, m:0, s:"l", d:1}, {dx:-50, dy:-32, m:0, s:"l", d:.95}, {dx:50, dy:-32, m:1, s:"r", d:.95}, {dx:138, dy:0, m:1, s:"r", d:1}],
  5: [{dx:-164, dy:0, m:0, s:"l", d:1}, {dx:-86, dy:-26, m:0, s:"l", d:.96}, {dx:0, dy:-50, m:0, s:"c", d:.92}, {dx:86, dy:-26, m:1, s:"r", d:.96}, {dx:164, dy:0, m:1, s:"r", d:1}]
};
function lkwSlots(n){                                            // 여섯 이상(없지만) — 같은 반원을 넓힌다
  if(LKW_SLOTS[n]) return LKW_SLOTS[n];
  const out = [], half = (n - 1) / 2;
  for(let i = 0; i < n; i++){ const k = (i - half) / half; out.push({dx:Math.round(k * 190), dy:Math.round(-50 * (1 - k * k)), m:k > 0 ? 1 : 0, s:k < 0 ? "l" : k > 0 ? "r" : "c", d:1 - .08 * (1 - k * k)}); }
  return out;
}
/* 구름 자리 (무대 기준) · 제자리 원 주기 — 상담창 CSLW_POS 와 같은 식. 양옆 위아래 둘씩 (아래 구름은 같은 쪽 위 구름 바로 밑) */
const LKW_POS = [{l:14, t:12, od:"6.8s", odl:"-1.2s"}, {r:14, t:12, od:"7.4s", odl:"-3.3s"},
                 {l:8, t:118, od:"7.6s", odl:"-4.1s"}, {r:8, t:126, od:"6.2s", odl:"-2.7s"}];
const LKW_CLOUD_W = 188;
const LKW_BG = {zoom:1.4, y:250, pad:28};                        // 쿼터뷰 지도 — 지도 폭 = 무대 폭이 1 · 바닥 문장을 무대 y 250 에
const LKW_SFX = ["csl_pick", "csl_ok", "csl_ng", "csl_mst"];
const LKW = {run:0, el:null, ctx:null, phase:"", typing:null, skipAt:0, compact:false, fitKey:"", meta:new Map(), team:[], instant:false, art:null,
             auto:null};                                         // auto — 다음에 그려질 경기 화면에서 창을 같이 띄울 대회 (lkwAuto · bindLocker 가 한 번 쓰고 지운다)
function lkwq(s){ return LKW.el ? LKW.el.querySelector(s) : null; }
function lkwqa(s){ return LKW.el ? [...LKW.el.querySelectorAll(s)] : []; }
function lkwLive(run){ return !!LKW.el && LKW.el.isConnected && run === LKW.run; }
function lkwWait(ms){ return LKW.instant ? Promise.resolve() : cwWait(ms); }
function lkwLater(run, ms, fn){ if(LKW.instant){ fn(); return; } setTimeout(()=>{ if(lkwLive(run)) fn(); }, ms); }
function lkwSkipped(){ return cwNow() - (LKW.skipAt||0) < 350; }   // 글자를 끝까지 넘긴 그 누르기로는 다음 단계로 가지 않는다
function lkwFocus(){ const w = lkwq(".cw-win"); if(w) try{ w.focus({preventScroll:true}); }catch(e){} }
/* 글자를 한 자씩 — 누르면 바로 끝까지 (상담창 cwType 과 같다 · 상태만 따로) */
function lkwType(el, html, cps, voice){
  return new Promise(res=>{
    if(LKW.typing) LKW.typing();
    if(!el){ res(); return; }
    const tmp = document.createElement("div"); tmp.innerHTML = html;
    const full = tmp.innerHTML, plain = tmp.textContent;
    if(LKW.instant || !plain.length){ el.innerHTML = full; res(); return; }
    let n = 0, id = 0;
    const done = ()=>{ clearInterval(id); if(LKW.typing === done) LKW.typing = null; el.innerHTML = full; res(); };
    el.textContent = "";
    id = setInterval(()=>{
      n++; el.textContent = plain.slice(0, n);
      if(voice && !CW_QUIET.test(plain.charAt(n - 1))) cwBlip(voice);
      if(n >= plain.length) done();
    }, Math.max(8, 1000/(cps||CSLW_CPS)));
    LKW.typing = done;
  });
}

/* ── 경기 화면의 락커룸 칸 (경기 화면 셋 — 가을 대회 · 친선전 · 봄 신인전) ── */
function lockerHtml(L, my){
  const said = (L.said!=null) ? L.offers[L.said] : null;
  const gap = L.foeP - L.myP;
  const tierN = foeTierName(L.tier||0);
  return `<div class="rule"></div>
    <div class="panel-h" style="margin-bottom:8px"><h2 style="font-size:13px">락커룸</h2>
      <span class="hint">전력 우리 <b style="color:var(--text)">${fmt(L.myP)}</b> · 상대 ${L.seen
        ? `<b style="color:var(--text)">${fmt(L.foeP)}</b> ${gap>0? `· <span style="color:var(--bad)">열세</span>` : gap<0? `· <span style="color:var(--ok)">우세</span>` : `· 호각`}`
        : `<b style="color:var(--dim)">파악 못 함</b> <span style="color:var(--dim)">· <span class="lk-pc">${esc(tierN)} 학원은 정보력 ${FOE_INFO_NEED[clamp(L.tier||0,0,PORTAL_TIER)]}에서 확실히 읽힌다</span><span class="lk-mob">정보력 부족</span></span>`}</span></div>
    <div class="lkrow">${(my||[]).map(st=>{
      const v = L.mood[st.id], tone = moodTone(v), r = L.res[st.id], d = v - L.base[st.id];
      return `<div class="lkcard">
        <div class="lkn">${dnH(st)}</div>
        <div class="lkp">${persTag(st)}${roleTag(st.job)}</div>
        <div class="lkm ${tone}">${moodLabel(v)}<span class="num">${v}</span></div>
        <div class="lkb"><i class="${tone}" style="width:${v}%"></i></div>
        <div class="lkf">${v>=MOOD_GOOD? `체력·공격력·방어력·속도 <b style="color:var(--ok)">+${Math.round(MOOD_STAT*100)}%</b>`
          : v<=MOOD_BAD? `체력·공격력·방어력·속도 <b style="color:var(--bad)">-${Math.round(MOOD_STAT*100)}%</b>` : "보정 없음"}</div>
        ${said? `<div class="lkr ${r?"ok":"bad"}">${r? "받아들였다":"통하지 않았다"} ${d>0?"+":""}${d}${
          r? ` · <span style="color:var(--brass)">신뢰 ${trustGainWord(said.type==="motive"?2:1)}</span>`:""}${
          L.conv[st.id]? ` · <span style="color:var(--brass)">호소력</span>`:""}${
          (L.byTrust&&L.byTrust[st.id])? ` · <span style="color:var(--brass)">운명</span>`:""}</div>`:""}
      </div>`; }).join("")}</div>
    ${said
      ? `<div class="opt" style="cursor:default;margin-top:10px;border-color:var(--brass)">
          <div class="od" style="color:var(--text);font-size:13px;margin-top:0">&ldquo;${esc(said.t)}&rdquo;</div></div>`
      : ""}`;
}
/* 경기 화면이 그려질 때 — 이 경기의 락커룸(창이 쓸 것)을 기억해 둔다.
   c = {title, label, foe, field, start} — 창 위 탭 · 상대 이름 · 배경 필드(openBattle 의 field 와 같은 값) · 전투를 여는 함수
   막 넘어온 경기 화면(lkwAuto)이고 한마디 전이면 창을 같이 띄운다 — 다시 그리기 · '빠르게 결과만' 뒤에는 띄우지 않는다 */
function bindLocker(t, L, my, rerender, c){
  LKW.ctx = Object.assign({t, L, my, rerender}, c || {});
  const auto = LKW.auto === t; LKW.auto = null;
  if(auto && L && L.said == null && (my||[]).length && UI.tour === t) lkwOpen();
}
/* 경기 화면으로 넘어가는 단추(출전 · 엔트리 확정 · 대진 확정)와 전투 시작이 부른다 — 다음에 그려질 이 대회의 경기 화면에서 창이 같이 뜬다 */
function lkwAuto(t){ LKW.auto = t || null; }
/* '경기 시작' — 한마디 전이면 락커룸 창부터, 했으면 바로 전투 */
function lkwGate(){
  const c = LKW.ctx;
  if(!c || !c.start) return;
  if(!c.L || c.L.said != null || !(c.my||[]).length || UI.tour !== c.t){ lkwAuto(c.t); c.start(); return; }   // 전투를 보고 나면 다음 경기에서도 창이 같이 뜬다
  lkwOpen();
}

/* ── 창 ── */
function lkwHtml(c){
  return `<div class="cw-fit"><div class="cw-in">
  <div class="cw-win lkw-win closed" role="dialog" aria-modal="true" aria-label="락커룸" tabindex="-1">
    <div class="cw-head">
      <div class="cw-tab title"><span class="cw-k">락커룸</span><span class="lkw-tt"></span></div>
      <div class="cw-hr"><div class="cw-tab lkw-pw"></div><button type="button" class="cw-x" aria-label="락커룸 닫기" title="닫기 (Esc)">×</button></div>
    </div>
    <div class="cw-mid">
      <div class="cw-stage"><div class="lkw-scene"><div class="lkw-bg"></div><div class="lkw-tint"></div><div class="lkw-floor"></div><div class="lkw-team"></div><div class="lkw-fx"></div></div></div>
      <div class="cw-over"><div class="cw-clouds"></div><div class="lkw-plates"></div></div>
    </div>
    <div class="cw-box"><div class="cw-who"></div><div class="cw-bt"></div><div class="cw-more" aria-hidden="true">▼</div><button type="button" class="cw-next"></button></div>
  </div></div></div>`;
}
/* 우세 · 열세 · 호각 (색) */
function lkwStHtml(L){
  return L.myP > L.foeP ? `<span class="cw-ok">우세</span>` : L.myP < L.foeP ? `<span class="cw-bad">열세</span>` : `<span class="cw-brass">호각</span>`;
}
function lkwHead(c){
  const L = c.L, tt = lkwq(".lkw-tt"), pw = lkwq(".lkw-pw");
  const title = [c.title, c.label].filter(Boolean).join(" · ");
  tt.textContent = title; lkwq(".cw-tab.title").title = title;
  pw.innerHTML = L.seen
    ? `전력 우리 <b>${fmt(L.myP)}</b> · 상대 <b>${fmt(L.foeP)}</b> ${lkwStHtml(L)}`
    : `전력 우리 <b>${fmt(L.myP)}</b> · 상대 <b class="cw-dim">???</b> <span class="cw-dim lkw-unk">파악 못 함</span>`;
}
function lkwIntroHtml(c){
  const L = c.L, tierN = esc(foeTierName(L.tier||0)), need = FOE_INFO_NEED[clamp(L.tier||0,0,PORTAL_TIER)];
  const line = c.foe
    ? (L.seen ? `상대는 ${esc(c.foe)}. 전력 우리 <b>${fmt(L.myP)}</b> · 상대 <b>${fmt(L.foeP)}</b> — ${lkwStHtml(L)}.`
              : `상대는 ${esc(c.foe)}. <span class="cw-dim">상대 전력은 파악하지 못했다 — ${tierN} 학원은 정보력 ${need}에서 확실히 읽힌다.</span>`)
    : (L.seen ? `전력 우리 <b>${fmt(L.myP)}</b> · 상대 <b>${fmt(L.foeP)}</b> — ${lkwStHtml(L)}.`
              : `<span class="cw-dim">상대 전력은 파악하지 못했다 — ${tierN} 학원은 정보력 ${need}에서 확실히 읽힌다.</span>`);
  return "경기 직전, 출전할 학생들이 둥글게 모였다." + "\n" + line;
}
/* 쿼터뷰 지도 (없으면 필드 그림) — 다 받으면 나타난다 */
function lkwBg(c, run){
  const el = lkwq(".lkw-bg"); if(!el) return;
  let fk = "";
  try{ fk = battleFieldKey(c.field); }catch(e){}
  const qk = (typeof tqMapKey === "function" && fk) ? tqMapKey(fk) : null, m = qk ? TQ_MAPS[qk] : null;
  let src = "", css = "";
  if(m){
    const B = LKW_BG, w = LKW_W * B.zoom, h = w * 1024 / 1536;     // 지도는 모두 1536 × 1024
    const x = clamp(LKW_W / 2 - m.mx / 1536 * w, LKW_W + B.pad - w, -B.pad), y = clamp(B.y - m.my / 1024 * h, LKW_H + B.pad - h, -B.pad);
    src = "assets/battle-fields/quarter/" + m.src;
    css = `background-size:${w.toFixed(1)}px ${h.toFixed(1)}px;background-position:${(x + B.pad).toFixed(1)}px ${(y + B.pad).toFixed(1)}px`;
  } else if(fk){
    src = fieldOf(fk, false); css = "background-size:cover;background-position:50% 50%";
  }
  if(!src) return;
  const im = new Image();
  im.onload = ()=>{ if(!lkwLive(run)) return; el.style.cssText = `background-image:url("${src}");${css}`; el.classList.add("on"); };
  im.src = src;
}
/* 학생 도트 — 상담창의 cslwSprUrl (128 칸 네 장 · 머리색 · #111 테두리) + 자리 잡기에 쓰는 점을 잰다 (1배 칸 좌표):
   hx 머리 덩어리 가운데(맨 위 줄 아래 6 ~ 46 줄 불투명 화소 x 의 중앙값) · hy 그 둘레 ±12 칸의 맨 위 줄 · fy 발끝(맨 아래 줄) · fx 발 가운데 · l · r 좌우 끝 */
function lkwMeasure(url){
  return new Promise(res=>{
    const im = new Image();
    im.onload = ()=>{
      try{
        const W = 128, cv = document.createElement("canvas"); cv.width = W * 4; cv.height = W;
        const g = cv.getContext("2d", {willReadFrequently:true}); g.drawImage(im, 0, 0);
        const d = g.getImageData(0, 0, W * 4, W).data, u = new Uint8Array(W * W);
        for(let y = 0; y < W; y++) for(let x = 0; x < W * 4; x++) if(d[(y * W * 4 + x) * 4 + 3] > 0) u[y * W + (x % W)] = 1;
        let top0 = W, bot = 0, l = W, r = 0;
        for(let y = 0; y < W; y++) for(let x = 0; x < W; x++) if(u[y * W + x]){ if(y < top0) top0 = y; if(y > bot) bot = y; if(x < l) l = x; if(x > r) r = x; }
        if(top0 >= W){ res(null); return; }
        const med = a=> { a.sort((p, q)=> p - q); return a.length ? a[a.length >> 1] : 64; };
        const hb = []; for(let y = top0 + 6; y < Math.min(W, top0 + 46); y++) for(let x = 0; x < W; x++) if(u[y * W + x]) hb.push(x);
        const hx = med(hb);
        let hy = W; for(let x = Math.max(0, hx - 12); x <= Math.min(W - 1, hx + 12); x++) for(let y = 0; y < hy; y++) if(u[y * W + x]){ hy = y; break; }
        const fb = []; for(let y = Math.max(0, bot - 5); y <= bot; y++) for(let x = 0; x < W; x++) if(u[y * W + x]) fb.push(x);
        res({hx, hy:hy < W ? hy : top0, fy:bot, fx:med(fb), l, r});
      }catch(e){ res(null); }
    };
    im.onerror = ()=> res(null);
    im.src = url;
  });
}
async function lkwMeta(st, run){
  for(let t = 0; t < 30 && sprHas(st.job); t++){                  // 도트 시트를 기다린다 (최대 3초)
    const u = cslwSprUrl(st);
    if(u){
      let m = LKW.meta.get(u.url);
      if(!m){ m = await lkwMeasure(u.url); if(m) LKW.meta.set(u.url, m); }
      if(m) return Object.assign({url:u.url}, m);
      break;
    }
    await cwWait(100); if(!lkwLive(run)) return null;
  }
  return faceHas(st.job) ? {face:FACE_IMG[st.job], hx:64, hy:24, fy:114, fx:64, l:24, r:104} : {hx:64, hy:24, fy:114, fx:64, l:24, r:104};
}
/* 학생 · 이름표를 만든다 (자리는 lkwLayout) */
function lkwTeam(c){
  const team = lkwq(".lkw-team"), plates = lkwq(".lkw-plates"), L = c.L, K = LKW_K, C = 128 * K;
  team.innerHTML = ""; plates.innerHTML = ""; lkwq(".lkw-fx").innerHTML = "";
  const slots = lkwSlots(LKW.team.length);
  LKW.team.forEach((T, i)=>{
    const st = T.st, sl = slots[i], m = !!sl.m;
    T.slot = sl;
    const el = document.createElement("div");
    el.className = `lkw-stu ${sl.s}${m ? " m" : ""}`; el.dataset.i = i;
    el.style.cssText = `width:${C}px;height:${C}px;--ld:${sl.d};--c:${C}px`;
    el.innerHTML = `<div class="lkw-sh"></div><div class="lkw-lean"><div class="lkw-body"><div class="lkw-spr${T.meta.face ? " face" : ""}"></div></div></div><div class="lkw-hit"></div>`;
    const spr = el.querySelector(".lkw-spr");
    if(T.meta.url){ spr.style.backgroundImage = `url(${T.meta.url})`; spr.style.backgroundSize = `${4 * C}px ${C}px`; spr.style.animationDelay = `-${(i * .73 % 2.8).toFixed(2)}s`; }
    else if(T.meta.face) spr.style.backgroundImage = `url(${T.meta.face})`;
    team.appendChild(el);
    const p = document.createElement("div"); p.className = "lkw-plate"; p.dataset.i = i;
    p.innerHTML = `<div class="r1"><span class="pn"></span><span class="pp"></span></div><div class="r2"><span class="ml"></span><span class="mv"></span></div>
      <div class="bar"><i></i><b style="left:${MOOD_BAD}%"></b><b style="left:${MOOD_GOOD}%"></b></div>`;
    p.querySelector(".pn").textContent = st.name; p.querySelector(".pp").textContent = personaOf(st).n;
    plates.appendChild(p);
    lkwPlate(i, L.mood[st.id], false);
  });
  const hiOn = (i, on)=>{ const a = lkwq(`.lkw-stu[data-i="${i}"]`), b = lkwq(`.lkw-plate[data-i="${i}"]`); if(a) a.classList.toggle("hi", on); if(b) b.classList.toggle("hi", on); };
  lkwqa(".lkw-hit, .lkw-plate").forEach(el=>{
    const i = (el.closest(".lkw-stu") || el).dataset.i;
    el.onmouseenter = ()=> hiOn(i, true); el.onmouseleave = ()=> hiOn(i, false);
  });
  lkwLayout();
}
/* 자리 — 학생 · 그림자 · 머리 위 효과 · 이름표(넓은 화면). 화면 배치가 바뀌면 다시 */
function lkwLayout(){
  if(!LKW.el || !LKW.team.length) return;
  const K = LKW_K, C = 128 * K, u = K / 1.5;
  const plates = lkwqa(".lkw-plate"), ph = (!LKW.compact && plates[0]) ? plates[0].offsetHeight || 49 : 0;
  const footY = LKW.compact ? LKW_H - 36 : LKW_H - ph - 5 - 20;  // 앞줄 발끝 — 이름표 위 20px
  const xs = [], ys = [];
  LKW.team.forEach((T, i)=>{
    const M = T.meta, sl = T.slot, m = !!sl.m;
    const sx = Math.round(LKW_W / 2 + sl.dx * u), sy = Math.round(footY + sl.dy * u);
    const hx = m ? C - K * M.hx : K * M.hx, fx = m ? C - K * M.fx : K * M.fx;
    const left = Math.round(sx - hx), top = Math.round(sy - K * (M.fy + 1));
    const bl = m ? C - K * (M.r + 1) : K * M.l, br = m ? C - K * M.l : K * (M.r + 1);
    const el = lkwq(`.lkw-stu[data-i="${i}"]`); if(!el) return;
    el.style.left = left + "px"; el.style.top = top + "px"; el.style.zIndex = String(sy);
    const shw = Math.round(38 * K), sh = el.querySelector(".lkw-sh");
    sh.style.cssText = `left:${Math.round(fx - shw / 2)}px;top:${Math.round(K * (M.fy + 1) - 4 * K - 2)}px;width:${shw}px;height:${Math.round(8 * K)}px`;
    el.querySelector(".lkw-hit").style.cssText = `left:${Math.round(bl + 7 * K)}px;top:${Math.round(K * M.hy + 4 * K)}px;width:${Math.max(0, Math.round(br - bl - 14 * K))}px;height:${Math.max(0, Math.round(K * (M.fy - M.hy) - 4 * K))}px`;
    T.head = {x:sx, y:top + Math.round(K * M.hy), dir:m ? -1 : 1};
    T.foot = {x:Math.round(left + fx), y:sy};
    xs.push(T.foot.x); ys.push(sy);
    lkwqa(`.lkw-fx [data-i="${i}"]`).forEach(fxEl=> lkwFxPlace(fxEl, T));
  });
  const fl = lkwq(".lkw-floor"), x0 = Math.min(...xs), x1 = Math.max(...xs), fw = x1 - x0 + 220, fh = 74, cy = ys.reduce((a, b)=> a + b, 0) / ys.length;
  fl.style.cssText = `left:${Math.round((x0 + x1) / 2 - fw / 2)}px;top:${Math.round(cy - fh / 2 + 4)}px;width:${fw}px;height:${fh}px`;
  if(LKW.compact) return;
  // 이름표 — 발 아래 한 줄. 겹치면 벌리고, 무대 안으로
  const n = plates.length, pw = n >= 5 ? 100 : 112, gap = n >= 5 ? 4 : 6, cs = xs.slice();
  for(let it = 0; it < 40; it++){
    let moved = false;
    for(let i = 0; i < cs.length - 1; i++){ const dd = cs[i + 1] - cs[i] - (pw + gap); if(dd < 0){ cs[i] += dd / 2; cs[i + 1] -= dd / 2; moved = true; } }
    if(!moved) break;
  }
  const lo = 8 + pw / 2 - cs[0], hi = LKW_W - 8 - pw / 2 - cs[cs.length - 1], shift = lo > 0 ? lo : (hi < 0 ? hi : 0);
  plates.forEach((p, i)=>{ p.style.setProperty("--x", Math.round(cs[i] + shift - pw / 2) + "px"); p.style.setProperty("--y", (LKW_H - ph - 5) + "px"); p.style.setProperty("--w", pw + "px"); });
}
function lkwFxPlace(el, T){
  const h = T.head; if(!h) return;
  if(el.classList.contains("lkw-think")){ el.classList.toggle("r", h.dir < 0); el.style.left = (h.dir < 0 ? h.x - 28 : h.x - 8) + "px"; el.style.top = (h.y - 36) + "px"; }
  else if(el.classList.contains("lkw-joy")){ el.style.left = (h.x - 30) + "px"; el.style.top = (h.y - 40) + "px"; }
  else if(el.classList.contains("lkw-gloom")){ el.style.left = (h.x - 11 - h.dir * 18) + "px"; el.style.top = (h.y - 16) + "px"; }
  else if(el.classList.contains("lkw-tag")){ el.style.left = h.x + "px"; el.style.top = (h.y - 62) + "px"; }
}
function lkwPlate(i, v, anim){
  const T = LKW.team[i], p = lkwq(`.lkw-plate[data-i="${i}"]`); if(!T || !p) return;
  const tone = moodTone(v), ml = p.querySelector(".ml"), mv = p.querySelector(".mv"), bar = p.querySelector(".bar i");
  ml.textContent = moodLabel(v); ml.className = "ml " + tone; mv.className = "mv num " + tone;
  bar.className = tone; bar.style.width = clamp(v, 0, 100) + "%";
  p.title = `${T.st.name} · ${personaOf(T.st).n} — ${moodLabel(v)} ${v}`;
  if(!anim || LKW.instant){ mv.textContent = v; return; }
  const from = +mv.textContent || 0, run = LKW.run, n = 8;
  for(let k = 1; k <= n; k++) lkwLater(run, k * 60, ()=>{ mv.textContent = Math.round(from + (v - from) * k / n); });
}
/* 도트 효과 그림 — 1배로 찍고(테두리 1칸) 2배로 본다. ♪ · ♫ · ~ · | | | */
function lkwPix(rows, color, outline){
  const h = rows.length, w = rows[0].length, cw = w + 2, ch = h + 2;
  const cv = document.createElement("canvas"); cv.width = cw; cv.height = ch;
  const g = cv.getContext("2d"), im = g.createImageData(cw, ch), d = im.data;
  const at = (x, y)=> y >= 0 && y < h && x >= 0 && x < w && rows[y][x] !== ".";
  for(let y = 0; y < ch; y++) for(let x = 0; x < cw; x++){
    const sx = x - 1, sy = y - 1; let c = null;
    if(at(sx, sy)) c = color(rows[sy][sx], sx, sy, w, h);
    else if(outline){ for(let dy = -1; dy <= 1 && !c; dy++) for(let dx = -1; dx <= 1; dx++){ if((dx || dy) && at(sx + dx, sy + dy)){ c = outline; break; } } }
    if(c){ const k = (y * cw + x) * 4; d[k] = c[0]; d[k+1] = c[1]; d[k+2] = c[2]; d[k+3] = c[3] == null ? 255 : c[3]; }
  }
  g.putImageData(im, 0, 0);
  return `width:${cw * 2}px;height:${ch * 2}px;background-image:url(${cv.toDataURL()})`;
}
function lkwArt(){
  if(LKW.art) return LKW.art;
  const pal = (main, hi)=> ch=> ch === "o" ? hi : main, top = [52,48,112], bot = [128,134,214];
  return (LKW.art = {
    note: lkwPix(["....#...","....##..","....#.#.","....#..#","....#..#","....#.#.","....#...","....#...","..o##...",".o###...","####....",".##....."], pal([255,138,176], [255,214,229]), [74,36,52]),
    note2: lkwPix(["...########","...########","...#......#","...#......#","...#......#","..o#.....o#",".o##....o##","####...####",".##.....##."], pal([255,210,92], [255,244,196]), [92,62,18]),
    tilde: lkwPix([".##.......","####....##","#..##..##.","....####.."], ()=> [255,170,200], [74,36,52]),
    gloom: lkwPix(["#...#...#","#...#...#","#...#...#","#...#...#","#...#...#","#...#...#","#...#...#","....#...#","....#...#","....#....","....#....","....#...."],
      (c, x, y, w, h)=>{ const k = y / (h - 1); return top.map((v, j)=> Math.round(v + (bot[j] - v) * k)); }, [240,238,255,235])
  });
}
function lkwFx(cls, i, inner){
  const T = LKW.team[i], box = lkwq(".lkw-fx"); if(!T || !box) return null;
  const el = document.createElement("div"); el.className = cls; el.dataset.i = i;
  if(inner) el.innerHTML = inner;
  box.appendChild(el); lkwFxPlace(el, T);
  if(LKW.instant) el.classList.add("on"); else requestAnimationFrame(()=> requestAnimationFrame(()=> el.classList.add("on")));
  return el;
}

/* ── 열기 · 닫기 ── */
function lkwOpen(opt){
  opt = opt || {};
  const c = LKW.ctx, root = $("#modalRoot");
  if(!c || !c.L || !root || !root.firstChild || (LKW.el && LKW.el.isConnected)) return;
  if(LKW.el) lkwDrop();
  const run = ++LKW.run;
  LKW.phase = "load"; LKW.typing = null; LKW.fitKey = ""; LKW.team = []; LKW.instant = !!opt.instant; LKW.skipAt = 0;
  const ov = document.createElement("div"); ov.className = "cw-ov lkw-ov" + (LKW.instant ? " instant" : "");
  ov.innerHTML = lkwHtml(c);
  root.appendChild(ov); LKW.el = ov;
  try{ const a = document.activeElement; if(a && a !== document.body && a.blur) a.blur(); }catch(e){}
  lkwHead(c);
  lkwq(".cw-x").onclick = ()=> lkwClose("back");
  try{ if(AWEB !== false && sfxGain() > 0 && audCtx()) LKW_SFX.forEach(k=> SFX[k] && sfxLoad(SFX[k].f)); }catch(e){}   // 소리를 미리 받아 둔다
  LKW.key = e=> lkwKey(e);
  LKW.rs = ()=> lkwFit();
  LKW.pd = e=>{                                                  // 글자가 찍히는 중에 글 · 무대를 누르면 바로 끝까지
    if(!LKW.typing) return;
    const t = e.target; if(!t || !t.closest || t.closest(".cw-x, .cw-next")) return;
    if(t.closest(".cw-box,.cw-stage")){ LKW.typing(); LKW.skipAt = cwNow(); }
  };
  document.addEventListener("keydown", LKW.key, true);
  window.addEventListener("resize", LKW.rs);
  ov.addEventListener("pointerdown", LKW.pd, true);
  lkwFit();
  lkwBg(c, run);
  const show = ()=>{ if(!lkwLive(run)) return; ov.classList.add("on"); const w = lkwq(".cw-win"); w.classList.remove("closed"); lkwFocus(); };
  if(LKW.instant) show(); else requestAnimationFrame(()=> requestAnimationFrame(show));
  const font = (document.fonts && document.fonts.load) ? document.fonts.load('12px "Mulmaru"').catch(()=>{}) : Promise.resolve();
  const metas = Promise.all((c.my||[]).map(st=> lkwMeta(st, run).then(meta=> ({st, meta}))));
  Promise.all([Promise.race([font, cwWait(1500)]), metas]).then(([_, team])=>{
    if(!lkwLive(run)) return;
    LKW.team = team.filter(T=> T.meta);
    lkwTeam(c); lkwFit();
    const go = ()=>{ if(lkwLive(run)) lkwIntro(run, opt); };
    if(!LKW.instant && typeof tutSeen === "function" && !tutSeen("8")) tutOverPage("8", go);   // 처음 연 락커룸 — 안내 한 장을 창 위에
    else if(LKW.instant) go(); else setTimeout(go, 150);
  });
}
/* 이벤트만 떼어 낸다 (창이 이미 사라졌을 때 — 경기 화면이 다시 그려지는 등) */
function lkwDrop(){
  LKW.run++;
  if(LKW.typing){ const f = LKW.typing; LKW.typing = null; try{ f(); }catch(e){} }
  document.removeEventListener("keydown", LKW.key, true);
  window.removeEventListener("resize", LKW.rs);
  if(LKW.el) LKW.el.removeEventListener("pointerdown", LKW.pd, true);
  LKW.el = null; LKW.phase = ""; LKW.instant = false;
}
/* how — "start": 전투로 (한마디 했든 말없이든) · "back": 경기 화면으로 */
function lkwClose(how){
  const el = LKW.el, c = LKW.ctx; if(!el) return;
  lkwDrop();
  if(how === "start" && c && c.start && UI.tour === c.t){ el.remove(); lkwAuto(c.t); c.start(); return; }   // 전투를 보고 '결과 확정'으로 다음 경기에 오면 창이 같이 뜬다
  el.classList.remove("on");
  const w = el.querySelector(".cw-win"); if(w){ w.classList.remove("beat"); w.classList.add("closed"); }
  setTimeout(()=>{
    el.remove();
    if(c && c.rerender && UI.tour === c.t && c.L && c.L.said != null && $("#modalRoot").firstChild) c.rerender();   // 한마디를 했으면 경기 화면의 락커룸 칸을 새로
  }, 380);
}
function lkwKey(e){
  if(!LKW.el) return;
  if(!LKW.el.isConnected){ lkwDrop(); return; }
  if($("#modalRoot > .tutover")) return;                         // 위에 뜬 튜토리얼 · 확인 창이 먼저
  if(e.key === "Escape"){ e.preventDefault(); e.stopPropagation(); lkwClose("back"); return; }
  if(LKW.phase === "choose" && /^[1-4]$/.test(e.key)){            // 1 ~ 4 — 그 구름으로
    const cl = lkwq(".cw-clouds").children[+e.key - 1];
    if(cl && cl.classList.contains("on") && !e.repeat){ e.preventDefault(); e.stopPropagation(); lkwChoose(+e.key - 1); }
    return;
  }
  if(e.key !== " " && e.key !== "Enter") return;
  const t = e.target, btn = t && t.closest ? t.closest(".lkw-win button") : null;
  if(btn && (btn.classList.contains("cw-x") || (btn.classList.contains("on") && !btn.classList.contains("off")))){   // 초점이 있는 단추는 그 단추가 눌린다
    if(LKW.typing){ e.preventDefault(); LKW.typing(); }
    return;
  }
  e.preventDefault(); e.stopPropagation();
  if(e.repeat) return;
  if(LKW.typing){ LKW.typing(); LKW.skipAt = cwNow(); return; }
  if(LKW.phase === "result"){ const n = lkwq(".cw-next"); if(n && n.classList.contains("on") && n.onclick) n.onclick(); }
}
function lkwNext(label, fn, dim){
  const n = lkwq(".cw-next"); if(!n) return;
  n.textContent = label; n.className = "cw-next on" + (dim ? " dim" : ""); n.onclick = ()=>{ if(!lkwSkipped()) fn(); };
}
function lkwHideNext(){ const n = lkwq(".cw-next"); if(n){ n.className = "cw-next"; n.onclick = null; } }

/* ── 흐름 ── */
/* 1 · 모임 — 학생들이 하나씩 들어와 둥글게 선다 */
async function lkwIntro(run, opt){
  const c = LKW.ctx, L = c.L;
  LKW.phase = "enter";
  lkwqa(".lkw-stu").forEach((el, i)=> lkwLater(run, 150 + i * 110, ()=> el.classList.add("in")));
  lkwqa(".lkw-plate").forEach((el, i)=> lkwLater(run, 420 + i * 90, ()=> el.classList.add("in")));
  await lkwWait(620); if(!lkwLive(run)) return;
  await lkwType(lkwq(".cw-bt"), lkwIntroHtml(c), 40); if(!lkwLive(run)) return;
  await lkwWait(260); if(!lkwLive(run)) return;
  if(L.said != null){ lkwAfter(run); return; }                  // 이미 한마디를 했다 — 반응을 그대로 보여 준다
  /* 2 · 구름 넷이 차례로 */
  LKW.phase = "choose";
  lkwClouds(false);
  for(const cl of [...lkwq(".cw-clouds").children]){ cl.classList.add("on"); await lkwWait(200); if(!lkwLive(run) || LKW.phase !== "choose") return; }   // 다 뜨기 전에 골랐으면 여기서 끝
  lkwq(".cw-bt").insertAdjacentHTML("beforeend", `\n<span class="cw-hint">무슨 말을 해 줄까.</span>`);
  lkwq(".cw-win").classList.add("beat");
  lkwNext("말없이 시작 ▶", ()=> lkwClose("start"), true);
  if(opt && opt.pick != null){ lkwChoose(opt.pick); return; }
  if(LKW.instant){ LKW.instant = false; LKW.el.classList.remove("instant"); }
  if(LKW.compact){ const cl = lkwq(".cw-clouds"); if(cl && cl.scrollIntoView) cl.scrollIntoView({block:"nearest", behavior:"smooth"}); }
}
function lkwClouds(show){
  const box = lkwq(".cw-clouds"), L = LKW.ctx.L; if(!box) return;
  box.innerHTML = "";
  const hs = L.offers.map((o, k)=>{
    const p = LKW_POS[k] || LKW_POS[0];
    const b = document.createElement("button"); b.type = "button"; b.className = "cw-cloud" + (show ? " on" : "");
    if(!LKW.compact){ if(p.l != null) b.style.left = p.l + "px"; else b.style.right = p.r + "px"; }
    b.innerHTML = `<span class="cw-orb" style="--od:${p.od};--odl:${p.odl}"><span class="cw-art"></span><span class="cw-txt"></span></span>`;
    b.querySelector(".cw-txt").textContent = o.t;
    box.appendChild(b);
    const w = LKW.compact ? Math.max(120, Math.round(b.offsetWidth / 2) * 2) : LKW_CLOUD_W;
    const h = Math.max(70, Math.round(b.querySelector(".cw-txt").offsetHeight / 2) * 2);
    b.querySelector(".cw-orb").style.height = h + "px";
    b.querySelector(".cw-art").style.backgroundImage = `url(${cslwCloudArt(w, h, false)})`;
    b.setAttribute("aria-keyshortcuts", String(k + 1));
    b.onclick = ()=> lkwChoose(k);
    return h;
  });
  if(!LKW.compact) [...box.children].forEach((b, k)=>{   // 위 둘은 제자리, 아래 둘은 같은 쪽 위 구름 바로 밑 (글이 길어 구름이 커져도 겹치지 않게)
    const p = LKW_POS[k] || LKW_POS[0];
    b.style.top = (k < 2 ? p.t : Math.max(p.t, LKW_POS[k - 2].t + hs[k - 2] + 10 + (k - 2) * 6)) + "px";
  });
}
/* 3 · 고른 말 — 이 순간 게임에 반영하고(lockerSpeak), 마스터의 말 · 학생들이 잠시 고민 */
async function lkwChoose(k){
  const c = LKW.ctx, L = c && c.L, run = LKW.run;
  if(!L || LKW.phase !== "choose" || !LKW.el || lkwSkipped()) return;
  const o = L.offers[k]; if(!o) return;
  LKW.phase = "speak"; lkwFocus();
  const before = {}; (c.my||[]).forEach(st=> before[st.id] = L.mood[st.id]);
  try{ lockerSpeak(c.t, L, k, c.my); save(); }
  catch(err){ if(typeof errPush === "function") errPush("locker", err.message, err.stack); }
  if(L.said !== k){ lkwClose("back"); return; }
  LKW.before = before;
  sfxPlay("csl_pick");
  lkwHideNext();
  lkwq(".cw-win").classList.remove("beat");
  [...lkwq(".cw-clouds").children].forEach((cl, j)=> cl.classList.add("off", j === k ? "pick" : "gone"));
  lkwLater(run, 520, ()=>{ const cl = lkwq(".cw-clouds"); if(cl) cl.innerHTML = ""; });
  lkwq(".lkw-scene").classList.add("lean");
  lkwq(".cw-who").textContent = "마스터";
  await lkwType(lkwq(".cw-bt"), `“${esc(o.t)}”`, CSLW_CPS, "csl_mst"); if(!lkwLive(run)) return;
  await lkwWait(220); if(!lkwLive(run)) return;
  for(let i = 0; i < LKW.team.length; i++){ lkwFx("lkw-think", i, "<i></i><i></i><i></i>"); await lkwWait(120); if(!lkwLive(run)) return; }
  await lkwWait(1400); if(!lkwLive(run)) return;
  /* 4 · 한 명씩 반응 (차례는 섞어서) */
  LKW.phase = "react";
  const order = LKW.team.map((T, i)=> i);
  for(let i = order.length - 1; i > 0; i--){ const j = Math.floor(Math.random() * (i + 1)); [order[i], order[j]] = [order[j], order[i]]; }   // 연출만 — 게임 난수(RNG)는 쓰지 않는다
  for(const i of order){ lkwReact(i, true); await lkwWait(320); if(!lkwLive(run)) return; }
  await lkwWait(480); if(!lkwLive(run)) return;
  lkwResult(run);
}
function lkwReact(i, sound){
  const T = LKW.team[i], L = LKW.ctx.L; if(!T) return;
  const st = T.st, ok = !!L.res[st.id], el = lkwq(`.lkw-stu[data-i="${i}"]`), th = lkwq(`.lkw-think[data-i="${i}"]`);
  if(th) th.remove();
  if(el) el.classList.add(ok ? "ok" : "no");
  const A = lkwArt();
  if(ok){
    lkwFx("lkw-joy", i, `<i class="jt" style="${A.tilde}"></i><i class="j1" style="${A.note}"></i><i class="j2" style="${A.note2}"></i>`);
    const how = L.conv[st.id] ? "호소력" : (L.byTrust && L.byTrust[st.id]) ? "운명" : "";
    if(how){ const tg = lkwFx("lkw-tag", i); if(tg) tg.textContent = how; }
  } else {
    const g = lkwFx("lkw-gloom", i); if(g) g.style.cssText += ";" + A.gloom;
  }
  const v = L.mood[st.id], v0 = (LKW.before && LKW.before[st.id] != null) ? LKW.before[st.id] : v;
  lkwPlate(i, v, sound);
  if(sound && !LKW.instant){
    sfxPlay(ok ? "csl_ok" : "csl_ng");
    const p = lkwq(`.lkw-plate[data-i="${i}"]`), dv = v - v0;
    if(p && dv){ const q = document.createElement("div"); q.className = "cw-pop" + (dv < 0 ? " down" : ""); q.textContent = (dv > 0 ? "+" : "") + dv; p.appendChild(q); setTimeout(()=> q.remove(), 2100); }
  }
}
/* 5 · 결과 — 고른 말의 종류 · 통함 · 빗나감 · 이번 경기 기분 보정 → 경기 시작 */
function lkwResultHtml(){
  const c = LKW.ctx, L = c.L, o = L.offers[L.said];
  const ok = LKW.team.filter(T=> L.res[T.st.id]), no = LKW.team.filter(T=> !L.res[T.st.id]);
  const nm = T=> esc(T.st.name) + (L.conv[T.st.id] ? ` <span class="cw-lead">(호소력)</span>` : (L.byTrust && L.byTrust[T.st.id]) ? ` <span class="cw-lead">(운명)</span>` : "");
  const pct = Math.round(MOOD_STAT * 100), lines = [];
  if(ok.length) lines.push(`<span class="cw-ok">통함 — ${ok.map(nm).join(", ")}</span> · <span class="cw-brass">신뢰 ${trustGainWord(o.type === "motive" ? 2 : 1)}</span>`);
  if(no.length) lines.push(`<span class="cw-bad">빗나감 — ${no.map(nm).join(", ")}</span>`);
  const g = LKW.team.filter(T=> L.mood[T.st.id] >= MOOD_GOOD).length, b = LKW.team.filter(T=> L.mood[T.st.id] <= MOOD_BAD).length;
  if(g && b) lines.push(`이번 경기 체력·공격력·방어력·속도 — 기분 좋음 ${g}명 <span class="cw-ok">+${pct}%</span> · 기분 나쁨 ${b}명 <span class="cw-bad">-${pct}%</span>`);
  else if(g) lines.push(`이번 경기 체력·공격력·방어력·속도 — 기분 좋음 ${g}명 <span class="cw-ok">+${pct}%</span>`);
  else if(b) lines.push(`이번 경기 체력·공격력·방어력·속도 — 기분 나쁨 ${b}명 <span class="cw-bad">-${pct}%</span>`);
  else lines.push("이번 경기 기분 보정을 받는 학생은 없다.");
  return lines.join("\n");
}
async function lkwResult(run){
  const c = LKW.ctx, L = c.L, ty = SPEECH_TYPE[L.offers[L.said].type];
  LKW.phase = "result";
  lkwq(".cw-who").innerHTML = `${esc(ty.n)} <span class="cw-dim">— ${esc(ty.d)}</span>`;
  await lkwType(lkwq(".cw-bt"), lkwResultHtml(), 60); if(!lkwLive(run)) return;
  if(c.start) lkwNext("경기 시작 ▶", ()=> lkwClose("start"));
  else lkwNext("닫기 ▶", ()=> lkwClose("back"));
  if(LKW.instant){ LKW.instant = false; LKW.el.classList.remove("instant"); }
  if(LKW.compact){ const bx = lkwq(".cw-box"); if(bx && bx.scrollIntoView) bx.scrollIntoView({block:"nearest", behavior:"smooth"}); }
}
/* 이미 한마디를 한 경기 — 반응을 바로 보여 주고 결과 */
function lkwAfter(run){
  const L = LKW.ctx.L;
  LKW.phase = "react";
  lkwq(".lkw-scene").classList.add("lean");
  LKW.team.forEach((T, i)=> lkwReact(i, false));
  lkwq(".cw-who").textContent = "마스터";
  lkwResult(run);
}
/* 화면에 맞추기 — 넉넉하면 창을 통째로 (최대 1배), 0.8배보다 줄여야 하면 좁은 화면 배치 (상담창 cslwFit 과 같다) */
function lkwFit(){
  const ov = LKW.el; if(!ov || !ov.isConnected) return;
  const win = ov.querySelector(".cw-win"), fit = ov.querySelector(".cw-fit"), inn = ov.querySelector(".cw-in"),
        stage = ov.querySelector(".cw-stage"), scene = ov.querySelector(".lkw-scene");
  const vw = document.documentElement.clientWidth || window.innerWidth, vh = window.innerHeight;
  win.classList.remove("compact", "wide"); win.style.width = ""; stage.style.width = stage.style.height = ""; scene.style.transform = ""; inn.style.transform = "";
  const W = 800, H = win.offsetHeight + 4;                         // 그림자 4px 까지
  const s = Math.min(1, (vw - 16) / W, (vh - 16) / H);
  LKW.compact = s < .8;
  let key = "d";
  if(!LKW.compact){
    if(s < 1) inn.style.transform = `scale(${s})`;
    fit.style.width = Math.floor(W * s) + "px"; fit.style.height = Math.floor(H * s) + "px";
  } else {
    const ww = Math.max(260, Math.min(796, vw - 16)), inner = ww - 4 - 16 - 4;   // 창 테두리 · 안쪽 여백 · 무대 테두리
    const ss = Math.min(1, inner / LKW_W, Math.max(.3, vh * .42 / LKW_H));
    win.classList.add("compact"); win.classList.toggle("wide", inner >= 480); win.style.width = ww + "px";
    stage.style.width = Math.round(LKW_W * ss + 4) + "px"; stage.style.height = Math.round(LKW_H * ss + 4) + "px";
    scene.style.transform = `scale(${ss})`;
    fit.style.width = (ww + 4) + "px"; fit.style.height = "";
    key = "c" + ww;
  }
  if(key !== LKW.fitKey){
    const was = LKW.fitKey; LKW.fitKey = key;
    if(was){ lkwLayout(); if(LKW.phase === "choose") lkwClouds(true); }   // 배치가 바뀌면 자리 · 구름을 다시
  }
}
/* LKWIN_END */
