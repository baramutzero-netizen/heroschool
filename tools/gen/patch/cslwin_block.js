/* CSLWIN_START — 상담창 (1008 · apply_cslwin.py) ─ 상담 메뉴를 누르면 뜨는 창. mockups/counsel-window 목업을 게임에 옮겼다
   흐름: 학생이 책상 뒤로 들어온다 → 학생을 누르면 고민을 털어놓는다(지침 무시는 마스터가 먼저 묻는다) → 답변 구름 셋 중 하나를 고른다
   → 학생의 대답 · 효과 → 넘어가기(다음 학생) / 마치기(창이 닫힌다). 지침을 무시한 학생이 먼저, 그다음 고민 상담 대기열 차례로.
   · 답을 고르는 순간 게임에 반영한다 (answerCounsel · answerDefy 의 win 모드 — 화면을 다시 그리지 않고 결과를 돌려준다).
     연출 중에 창을 닫아도 결과는 남는다. 창을 닫으면 화면을 다시 그린다 (메뉴 숫자 등)
   · 무대 560 × 360 = 1배 280 × 180 도트를 2배로. CSL_ART.bg 배경(강당 뒷벽을 흐리게) · CSL_ART.front 책상 + 소품(상담 책상 배치판의 배치를 구운 것)
   · 학생 — 전투 idle 도트 네 장(학생마다 머리색 치환 · sprCellCv)을 128 칸으로 잘라 전투처럼 #111 테두리를 둘러 쓴다.
     크기 · 자리는 직업마다 (CSL_SPR — 상담 책상 배치판의 학생 도트, 기본 2배의 0.95배). 도트가 없으면 얼굴 그림
   · 학생 말 상자 머리 — 이름 · 성격 (직업은 그림으로 보여서 뺐다)
   · 좁은 화면(창을 0.8배보다 줄여야 할 때) — 무대만 폭에 맞춰 줄이고 학생 말 · 답변 구름은 무대 아래로 (글자는 그대로)
   · 키: 스페이스 · 엔터로 넘기기(글자가 찍히는 중이면 바로 끝까지) · 1 · 2 · 3 으로 구름 고르기 · Esc 닫기
   · 소리 (SFX.csl_*) — 학생을 누를 때 · 답변 구름을 고를 때 · 반응 성공 / 실패(학생의 대답이 다 찍히고 효과 숫자가 뜰 때) ·
     학생 / 마스터의 말이 한 글자씩 찍힐 때마다(cwBlip — 빈칸 · 말줄임표 …… 에서는 울리지 않는다). 학생 · 마스터의 말은 같은 빠르기(CSLW_CPS)
   · 상담 기록은 일지의 '상담 기록' 서브탭 (viewCslLog) */
const CSL_ART = __CSL_ART__;
/* 학생 도트 — 직업마다 크기 s(게임 화면 2배 = 1) · 자리 x, y(무대 1배로 옮기는 양). 상담 책상 배치판의 '학생 도트'(배치 JSON 의 sprites)를 apply_cslwin 이 넣는다 */
const CSL_SPR = __CSL_SPR__;
const CSL_SPR_DEF = {s:.95, x:0, y:0};
/* 학생이 들어오는 모습 — 성격마다 */
const CSL_ENTER = {intro:"쭈뼛거리며 들어와 책상 앞에 섰다.", hot:"성큼성큼 들어와 책상 앞에 섰다.", stone:"조용히 들어와 책상 앞에 섰다.",
  dilig:"꾸벅 인사하고 책상 앞에 섰다.", tsun:"팔짱을 낀 채 책상 앞에 섰다.", lively:"문을 벌컥 열고 들어와 손을 흔들었다.",
  boast:"당당한 걸음으로 들어와 책상 앞에 섰다.", plain:"할 말이 있는 듯 책상 앞에 섰다.", genius:"느긋하게 들어와 책상 앞에 섰다."};
const CSL_DEFY_ENTER = {intro:"머뭇거리며", hot:"씩씩하게", stone:"담담한 얼굴로", dilig:"고개를 숙인 채", tsun:"시선을 피한 채",
  lively:"멋쩍게 웃으며", boast:"가슴을 펴고", plain:"조금 멋쩍은 얼굴로", genius:"태연한 얼굴로"};
/* 답변 구름 자리 (무대 560 × 360 · 책상 윗변 y 232) · 제자리 원을 그리는 주기 */
const CSLW_POS = [{l:10, t:26, od:"6.8s", odl:"-1.2s"}, {l:4, t:140, od:"7.6s", odl:"-4.1s"}, {r:6, t:150, od:"6.2s", odl:"-2.7s"}];
const CSLW = {run:0, el:null, list:[], i:0, cur:null, phase:"", typing:null, skipAt:0, spr:{}, popTop:92, popX:280, compact:false, fitKey:""};
const CSLW_CPS = 32;                                             // 학생 · 마스터의 말이 찍히는 빠르기 (글자 / 초)
const CSLW_SFX = ["csl_tap", "csl_pick", "csl_ok", "csl_ng", "csl_stu", "csl_mst"];
const CW_QUIET = /[\s….‥]/;                                       // 이 글자가 찍힐 때는 소리를 내지 않는다 (빈칸 · 말줄임표)
function cwq(s){ return CSLW.el ? CSLW.el.querySelector(s) : null; }
function cwLive(run){ return !!CSLW.el && run === CSLW.run; }
function cwWait(ms){ return new Promise(r=> setTimeout(r, ms)); }
function cwNow(){ return (typeof performance !== "undefined") ? performance.now() : Date.now(); }
function cwSkipped(){ return cwNow() - (CSLW.skipAt||0) < 350; }   // 글자를 끝까지 넘긴 그 누르기로는 다음 단계로 가지 않는다
/* 글자마다 울리는 소리 — 한 목소리: 앞 글자의 소리는 짧게 잦아들며 끊고 새로 (sfxPlay 의 55ms 막기 · 동시 8개 제한을 비켜 간다).
   <audio> 로 울릴 때(file:// 등)는 45ms 보다 촘촘하면 건너뛴다 */
const CW_BLIP = {src:null, g:null, at:0};
function cwBlip(key){
  const t = SFX[key]; if(!t) return;
  try{
    const gain = sfxGain(); if(gain <= 0) return;
    const v = (t.v == null ? 1 : t.v);
    if(AWEB === false || ASBAD[t.f] || !audCtx()){
      const now = cwNow(); if(now - CW_BLIP.at < 45) return;
      CW_BLIP.at = now; sfxHtml(t, gain * v); return;
    }
    const ctx = ACTX, buf = ASBUF[t.f];
    if(!buf){ sfxLoad(t.f); return; }                             // 아직 못 받았다 — 받는 대로 다음 글자부터
    if(ctx.state === "suspended") ctx.resume().catch(()=>{});
    if(!ASG){ ASG = ctx.createGain(); ASG.connect(ctx.destination); }
    ASG.gain.value = gain;
    const now = ctx.currentTime;
    if(CW_BLIP.src){ try{ CW_BLIP.g.gain.setTargetAtTime(0, now, .008); CW_BLIP.src.stop(now + .04); }catch(e){} }
    const src = ctx.createBufferSource(), vg = ctx.createGain();
    src.buffer = buf; vg.gain.value = v;
    src.connect(vg); vg.connect(ASG); src.start(now);
    CW_BLIP.src = src; CW_BLIP.g = vg;
    src.onended = ()=>{ if(CW_BLIP.src === src){ CW_BLIP.src = CW_BLIP.g = null; } };
  }catch(e){}
}
/* 글자를 한 자씩 — 누르면 바로 끝까지. voice — 글자마다 울릴 소리 (SFX 이름 · 없으면 조용히) */
function cwType(el, html, cps, voice){
  return new Promise(res=>{
    if(CSLW.typing) CSLW.typing();
    if(!el){ res(); return; }
    const tmp = document.createElement("div"); tmp.innerHTML = html;
    const full = tmp.innerHTML, plain = tmp.textContent;
    let n = 0, id = 0;
    const done = ()=>{ clearInterval(id); if(CSLW.typing === done) CSLW.typing = null; el.innerHTML = full; res(); };
    el.textContent = "";
    if(!plain.length){ done(); return; }
    id = setInterval(()=>{
      n++; el.textContent = plain.slice(0, n);
      if(voice && !CW_QUIET.test(plain.charAt(n - 1))) cwBlip(voice);
      if(n >= plain.length) done();
    }, Math.max(8, 1000/(cps||CSLW_CPS)));
    CSLW.typing = done;
  });
}
/* 이번에 들을 상담 — 지침 무시 먼저, 그다음 고민 상담 */
function cslwList(){
  const L = [], has = id=> (S.students||[]).some(x=> x.id===id);
  defyState().pend.forEach(p=>{ if(p && has(p.sid)) L.push({kind:"defy", sid:p.sid}); });
  counselState().queue.forEach(q=>{ if(q && has(q.sid) && counselOf(q.cid)) L.push({kind:"worry", sid:q.sid, cid:q.cid}); });
  return L;
}
/* 한 건의 글 — 그때의 게임 상태에서 만든다 (대사는 성격마다 · masterQ 는 대사 함수가 맡는다) */
function cslwSess(e){
  const st = (S.students||[]).find(x=> x.id===e.sid); if(!st) return null;
  const pk = (st.pers && PERSONA[st.pers]) ? st.pers : "plain";
  const base = {e, kind:e.kind, st, pk, name:dnH(st), pers:personaOf(st).n};
  if(e.kind === "defy"){
    const p = defyState().pend.find(x=> x && x.sid===e.sid); if(!p) return null;
    const key = p.from + ">" + p.to, R = DEFY_REPLY[key] || DEFY_REPLY["train>rest"];
    const order = (Array.isArray(p.order) && p.order.length===3) ? p.order : [0,1,2];
    return Object.assign(base, {tag:"지침", title:`행동 지침 무시 — ${actName(p.from)} 대신 ${actName(p.to)}${(p.n|0)>1? ` · ${p.n}주째` : ""}`,
      enter:`${dnH(st)}${iga(st.name)} 이번 주 지침과 다르게 움직였다. ${CSL_DEFY_ENTER[pk] || CSL_DEFY_ENTER.plain} 책상 앞에 섰다.`,
      ask: esc(defyFill(DEFY_ASK[key] || "", p)), q: esc(defyFill(defyLine(st, key), p)), reveal: !!p.reveal,
      opts: order.map(i=> ({i, t:R[i] || "", hit:(DEFY_FIT[i]||[]).includes(pk)}))});
  }
  const q = counselState().queue.find(x=> x && x.sid===e.sid && x.cid===e.cid), c = counselOf(e.cid);
  if(!q || !c) return null;
  const order = (Array.isArray(q.order) && q.order.length===3) ? q.order : [0,1,2];
  return Object.assign(base, {tag:"고민", title:c.t, enter:`${dnH(st)}${iga(st.name)} ${CSL_ENTER[pk] || CSL_ENTER.plain}`,
    q: esc(cslQ(c, st)), reveal: !!q.reveal, opts: order.map(i=> ({i, t:c.o[i].t, hit:(c.o[i].f||[]).includes(pk)}))});
}
function cslwHtml(){
  return `<div class="cw-ov"><div class="cw-fit"><div class="cw-in">
  <div class="cw-win closed" role="dialog" aria-modal="true" aria-label="상담실" tabindex="-1">
    <div class="cw-head">
      <div class="cw-tab title"><span class="cw-k">상담실</span><span class="cw-tt"></span></div>
      <div class="cw-hr"><div class="cw-tab left">남은 상담 <b class="cw-ln">0</b></div><button type="button" class="cw-x" aria-label="상담실 닫기" title="닫기 (Esc)">×</button></div>
    </div>
    <div class="cw-mid">
      <div class="cw-stage"><div class="cw-scene">
        <div class="cw-bg" style="background-image:url(${CSL_ART.bg})"></div>
        <div class="cw-stu"><div class="cw-spr"></div><img class="cw-face" alt="" draggable="false"><div class="cw-hit"></div></div>
        <div class="cw-dots" aria-hidden="true">…</div>
        <div class="cw-front" style="background-image:url(${CSL_ART.front})"></div>
      </div></div>
      <div class="cw-over"><div class="cw-say"><div class="cw-sn"></div><div class="cw-st"></div></div><div class="cw-clouds"></div></div>
    </div>
    <div class="cw-box"><div class="cw-who"></div><div class="cw-bt"></div><div class="cw-more" aria-hidden="true">▼</div><button type="button" class="cw-next">넘어가기 ▶</button></div>
  </div></div></div></div>`;
}
function cslwOpen(){
  const root = $("#modalRoot");
  if(!root || root.firstChild || CSLW.el) return;              // 다른 창이 떠 있으면 열지 않는다
  if(typeof dragCfg === "function") dragCfg(root, null);
  const run = ++CSLW.run;
  CSLW.list = cslwList(); CSLW.i = 0; CSLW.cur = null; CSLW.phase = ""; CSLW.typing = null; CSLW.fitKey = "";
  root.innerHTML = cslwHtml();
  CSLW.el = root.firstElementChild;
  modalLockSync();
  try{ const a = document.activeElement; if(a && a !== document.body && a.blur) a.blur(); }catch(e){}
  cwq(".cw-x").onclick = ()=> cslwClose();
  try{ if(AWEB !== false && sfxGain() > 0 && audCtx()) CSLW_SFX.forEach(k=> SFX[k] && sfxLoad(SFX[k].f)); }catch(e){}   // 소리를 미리 받아 둔다 — 첫 글자부터 울리게
  CSLW.key = e=> cslwKey(e);
  CSLW.rs = ()=> cslwFit();
  CSLW.pd = e=>{                                                 // 글자가 찍히는 중에 글 · 무대를 누르면 바로 끝까지
    if(!CSLW.typing) return;
    const t = e.target; if(!t || !t.closest || t.closest(".cw-x")) return;
    if(t.closest(".cw-say,.cw-box,.cw-stage")){ CSLW.typing(); CSLW.skipAt = cwNow(); }
  };
  document.addEventListener("keydown", CSLW.key, true);
  window.addEventListener("resize", CSLW.rs);
  CSLW.el.addEventListener("pointerdown", CSLW.pd, true);
  cslwFit();
  requestAnimationFrame(()=> requestAnimationFrame(()=>{
    if(!cwLive(run)) return;
    CSLW.el.classList.add("on");
    const w = cwq(".cw-win"); w.classList.remove("closed");
    try{ w.focus({preventScroll:true}); }catch(e){}
  }));
  const font = (document.fonts && document.fonts.load) ? document.fonts.load('12px "Mulmaru"').catch(()=>{}) : Promise.resolve();
  Promise.race([font, cwWait(1500)]).then(()=>{
    if(!cwLive(run)) return;
    cslwFit();
    if(CSLW.list.length) setTimeout(()=>{ if(cwLive(run)) cslwEnter(run); }, 250);
    else cslwEmpty(run);
  });
}
function cslwClose(done){
  const el = CSLW.el; if(!el) return;
  CSLW.run++;
  if(CSLW.typing) CSLW.typing();
  document.removeEventListener("keydown", CSLW.key, true);
  window.removeEventListener("resize", CSLW.rs);
  el.removeEventListener("pointerdown", CSLW.pd, true);
  CSLW.el = null; CSLW.cur = null; CSLW.phase = ""; CSLW.list = [];
  el.classList.remove("on");
  const w = el.querySelector(".cw-win"); if(w){ w.classList.remove("beat"); w.classList.add("closed"); }
  render();
  if(done) toast("찾아온 학생들의 이야기를 모두 들었다.");
  setTimeout(()=>{ const r = $("#modalRoot"); if(r && r.firstElementChild === el) closeModal(); }, 420);
}
function cslwKey(e){
  if(!CSLW.el) return;
  if(e.key === "Escape"){ e.preventDefault(); e.stopPropagation(); cslwClose(); return; }
  if(CSLW.phase === "choose" && /^[1-3]$/.test(e.key)){                 // 1 · 2 · 3 — 그 구름으로 답한다
    const c = cwq(".cw-clouds").children[+e.key - 1];
    if(c && c.classList.contains("on") && !e.repeat){ e.preventDefault(); e.stopPropagation(); cslwChoose(+e.key - 1); }
    return;
  }
  if(e.key !== " " && e.key !== "Enter") return;
  const t = e.target, btn = t && t.closest ? t.closest(".cw-win button") : null;
  if(btn && (btn.classList.contains("cw-x") || (btn.classList.contains("on") && !btn.classList.contains("off")))){   // 초점이 있는 단추는 그 단추가 눌린다
    if(CSLW.typing){ e.preventDefault(); CSLW.typing(); }
    return;
  }
  e.preventDefault(); e.stopPropagation();
  if(e.repeat) return;
  if(CSLW.typing){ CSLW.typing(); return; }
  const ph = CSLW.phase;
  if(ph === "enter"){ const s = cwq(".cw-stu"); if(s && s.onclick) s.onclick(); }
  else if(ph === "ask"){ const b = cwq(".cw-box"); if(b && b.onclick) b.onclick(); }
  else if(ph === "result" || ph === "empty"){ const n = cwq(".cw-next"); if(n && n.classList.contains("on") && n.onclick) n.onclick(); }
}
function cwFocus(){ const w = cwq(".cw-win"); if(w) try{ w.focus({preventScroll:true}); }catch(e){} }   // 쓴 단추(숨긴 단추)에 초점이 남지 않게
function cslwHead(s){
  const k = cwq(".cw-k"); if(!k) return;
  k.textContent = s ? s.tag : "상담실";
  cwq(".cw-tt").textContent = s ? s.title : "";
  cwq(".cw-ln").textContent = s ? String(CSLW.list.length - CSLW.i) : "0";
  cwq(".cw-tab.title").title = s ? `${s.tag} — ${s.title}` : "상담실";
}
function cslwReset(){
  const box = cwq(".cw-box");
  cwq(".cw-say").classList.remove("on"); cwq(".cw-st").innerHTML = ""; cwq(".cw-clouds").innerHTML = "";
  cwq(".cw-who").textContent = ""; cwq(".cw-bt").innerHTML = "";
  const n = cwq(".cw-next"); n.classList.remove("on"); n.onclick = null;
  cwq(".cw-more").classList.remove("on"); cwq(".cw-dots").classList.remove("on");
  box.onclick = null; box.classList.remove("ask");
  cwq(".cw-win").classList.remove("beat");
}
/* 찾아온 학생이 없다 */
function cslwEmpty(run){
  CSLW.phase = "empty";
  cslwHead(null); cslwReset();
  cwType(cwq(".cw-bt"), `지금은 찾아온 학생이 없다. 한 주를 보내면 누군가 문을 두드릴 수 있다.\n<span class="cw-dim">${cslProbLine()}</span>`, 60).then(()=>{
    if(!cwLive(run)) return;
    const n = cwq(".cw-next"); n.textContent = "닫기 ▶"; n.classList.add("on"); n.onclick = ()=> cslwClose();
  });
}
function cslProbLine(){
  return `지도력 — 맞지 않아도 설득 ${Math.round(cslLeadP()*100)}% · 정보력 — 통할 말 파악 ${Math.round(cslInfoP()*100)}% · 호소력 — 상승폭 2배 ${Math.round(cslNetP()*100)}%${
    cslFacLv()? ` (상담실 Lv.${cslFacLv()} 보정 포함)` : ""}`;
}
function cslwSkip(run){                                          // 그 사이 사라진 상담 — 건너뛴다
  if(!cwLive(run)) return;
  if(CSLW.i < CSLW.list.length - 1){ CSLW.i++; cslwEnter(run); return; }
  if(CSLW.cur) cslwClose(); else cslwEmpty(run);
}
/* 1 · 학생이 책상 뒤로 들어온다 */
async function cslwEnter(run){
  if(!cwLive(run)) return;
  const e = CSLW.list[CSLW.i], s = e ? cslwSess(e) : null;
  if(!s) return cslwSkip(run);
  CSLW.cur = s; CSLW.phase = "load";
  cslwHead(s); cslwReset();
  if(CSLW.compact) CSLW.el.scrollTop = 0;
  const stu = cwq(".cw-stu");
  stu.onclick = null; stu.classList.remove("in", "click");
  const look = await cslwLook(s.st, run); if(!cwLive(run)) return;
  cslwSetLook(look, s.st);
  CSLW.phase = "enter";
  stu.classList.remove("out"); void stu.offsetWidth; stu.classList.add("in");
  await cwWait(650); if(!cwLive(run)) return;
  await cwType(cwq(".cw-bt"), s.enter, 40); if(!cwLive(run)) return;
  cwq(".cw-bt").insertAdjacentHTML("beforeend", `\n<span class="cw-hint">학생을 눌러 이야기를 듣는다.</span>`);
  cwq(".cw-dots").classList.add("on");
  stu.classList.add("click");
  stu.onclick = ()=>{
    if(CSLW.phase !== "enter" || !cwLive(run) || cwSkipped()) return;
    stu.onclick = null; stu.classList.remove("click"); cwq(".cw-dots").classList.remove("on");
    sfxPlay("csl_tap");
    (s.kind === "defy" ? cslwAsk : cslwTalk)(run);
  };
}
/* 지침 무시 — 마스터가 먼저 묻는다 */
async function cslwAsk(run){
  const s = CSLW.cur; CSLW.phase = "ask";
  cwq(".cw-who").textContent = "마스터";
  await cwType(cwq(".cw-bt"), s.ask, CSLW_CPS, "csl_mst"); if(!cwLive(run)) return;
  const box = cwq(".cw-box");
  cwq(".cw-more").classList.add("on"); box.classList.add("ask");
  box.onclick = ()=>{
    if(CSLW.phase !== "ask" || !cwLive(run) || cwSkipped()) return;
    box.onclick = null; box.classList.remove("ask"); cwq(".cw-more").classList.remove("on");
    cslwTalk(run);
  };
}
/* 2 · 고민을 털어놓고, 답변 구름 셋이 차례로 */
async function cslwTalk(run){
  const s = CSLW.cur; CSLW.phase = "talk";
  cwq(".cw-who").textContent = ""; cwq(".cw-bt").innerHTML = "";
  cwq(".cw-sn").innerHTML = `${s.name} <i>${esc(s.pers)}</i>`;   // 이름 · 성격 (직업은 그림으로 보인다)
  cwq(".cw-say").classList.add("on");
  await cwType(cwq(".cw-st"), s.q, CSLW_CPS, "csl_stu"); if(!cwLive(run)) return;
  await cwWait(250); if(!cwLive(run)) return;
  CSLW.phase = "choose";
  cslwClouds(s, false);
  for(const c of [...cwq(".cw-clouds").children]){ c.classList.add("on"); await cwWait(220); if(!cwLive(run) || CSLW.phase !== "choose") return; }
  cwq(".cw-bt").innerHTML = `<span class="cw-hint">어떻게 답할까.</span>${(s.reveal && s.opts.some(o=> o.hit))?
    `\n<span class="cw-brass">정보력으로 ${s.name}에게 통할 말을 파악했다 — 금빛 구름.</span>` : ""}`;
  cwq(".cw-win").classList.add("beat");
  if(CSLW.compact){ const c = cwq(".cw-clouds"); if(c && c.scrollIntoView) c.scrollIntoView({block:"nearest", behavior:"smooth"}); }
}
function cslwClouds(s, show){
  const box = cwq(".cw-clouds"); if(!box) return;
  box.innerHTML = "";
  s.opts.forEach((o, k)=>{
    const p = CSLW_POS[k] || CSLW_POS[0];
    const b = document.createElement("button"); b.type = "button"; b.className = "cw-cloud" + (show ? " on" : "");
    if(!CSLW.compact){ if(p.l != null) b.style.left = p.l + "px"; else b.style.right = p.r + "px"; b.style.top = p.t + "px"; }
    b.innerHTML = `<span class="cw-orb" style="--od:${p.od};--odl:${p.odl}"><span class="cw-art"></span><span class="cw-txt"></span></span>`;
    b.querySelector(".cw-txt").textContent = o.t;
    box.appendChild(b);
    const sp = !!(s.reveal && o.hit);
    const w = CSLW.compact ? Math.max(120, Math.round(b.offsetWidth/2)*2) : 196;
    const h = Math.max(70, Math.round(b.querySelector(".cw-txt").offsetHeight/2)*2);
    b.querySelector(".cw-orb").style.height = h + "px";
    b.querySelector(".cw-art").style.backgroundImage = `url(${cslwCloudArt(w, h, sp)})`;
    if(sp) b.setAttribute("aria-label", o.t + " — 정보력으로 파악한 통할 말");
    b.onclick = ()=> cslwChoose(k);
  });
}
/* 3 · 고른 답 — 이 순간 게임에 반영하고, 마스터의 말 · 학생은 고민 중 */
async function cslwChoose(k){
  const s = CSLW.cur, run = CSLW.run;
  if(!s || CSLW.phase !== "choose" || !CSLW.el || cwSkipped()) return;
  const o = s.opts[k]; if(!o) return;
  CSLW.phase = "answer"; cwFocus();
  let res = null;
  try{ res = cslwApply(s, o.i); }
  catch(err){ if(typeof errPush === "function") errPush("counsel", err.message, err.stack); }
  if(!res){ toast("이 상담은 더 이어 갈 수 없다."); cslwClose(); return; }
  s.res = res;
  sfxPlay("csl_pick");
  cwq(".cw-win").classList.remove("beat");
  [...cwq(".cw-clouds").children].forEach((c, j)=>{ c.classList.add("off", j === k ? "pick" : "gone"); });
  setTimeout(()=>{ if(cwLive(run) && CSLW.cur === s){ const cl = cwq(".cw-clouds"); if(cl) cl.innerHTML = ""; } }, 520);   // 사라진 구름 자리를 비운다 (좁은 화면)
  cwq(".cw-who").textContent = "마스터";
  await cwType(cwq(".cw-bt"), `“${esc(o.t)}”`, CSLW_CPS, "csl_mst"); if(!cwLive(run)) return;
  cwq(".cw-st").innerHTML = `<span class="cw-think"><i>…</i><i>…</i><i>…</i></span>`;
  await cwWait(1500); if(!cwLive(run)) return;
  cslwResult(run);
}
function cslwApply(s, oi){
  if(s.kind === "defy"){
    const pi = defyState().pend.findIndex(p=> p && p.sid===s.e.sid);
    return pi < 0 ? null : answerDefy(pi, oi, true);
  }
  const qi = counselState().queue.findIndex(q=> q && q.sid===s.e.sid && q.cid===s.e.cid);
  return qi < 0 ? null : answerCounsel(qi, oi, true);
}
/* 4 · 학생의 대답 · 효과 (오른 수치가 머리 위로) */
async function cslwResult(run){
  const s = CSLW.cur, r = s.res; CSLW.phase = "reply";
  await cwType(cwq(".cw-st"), esc(r.say || ""), 30, "csl_stu"); if(!cwLive(run)) return;
  sfxPlay(r.ok ? "csl_ok" : "csl_ng");                           // 반응 성공 · 실패 — 효과 숫자와 함께
  cslwPops(r);
  cwq(".cw-who").textContent = "";
  await cwType(cwq(".cw-bt"), cslwFx(s, r), 60); if(!cwLive(run)) return;
  CSLW.phase = "result";
  const last = CSLW.i >= CSLW.list.length - 1, n = cwq(".cw-next");
  n.textContent = last ? "마치기 ▶" : "넘어가기 ▶";
  n.classList.add("on"); n.onclick = ()=> cslwNext(run);
  if(CSLW.compact){ const b = cwq(".cw-box"); if(b && b.scrollIntoView) b.scrollIntoView({block:"nearest", behavior:"smooth"}); }
}
function cslwFx(s, r){
  const L = [], defy = s.kind === "defy";
  if(r.r) L.push(`<span class="cw-dim">${esc(r.r)}</span>`);
  if(r.ok){
    let t = r.fit ? (defy ? "마음에 닿았다!" : "도움이 된 듯하다!")
      : `<span class="cw-lead">${r.byLead ? "성격에 맞는 말은 아니었지만, 지도력으로 설득했다." : "신뢰가 운명 단계라 무슨 말이든 닿았다."}</span>`;
    if(r.gain) t += ` ${esc(r.gain.n)}${iga(r.gain.n)} ${r.gain.d} 올랐다.`;
    if(r.dbl) t += ` <span class="cw-lead">호소력으로 상승폭 2배!</span>`;
    if(r.cond) t += ` 컨디션이 ${r.cond} 회복됐다.`;
    if(r.capped) t += ` 멘탈리티는 모두 한계라 더 오르지 않았다.`;
    if(r.trustUp) t += ` 신뢰가 깊어졌다.`;
    L.push(r.fit ? `<span class="cw-ok">${t}</span>` : t);
  } else {
    L.push(`<span class="cw-bad">아직 납득하지 못한 표정이다.${r.trustDown ? " 신뢰가 조금 떨어졌다." : ""}</span>`);
  }
  if(r.band) L.push(`<span class="cw-brass">${s.name}${gwa(s.st.name)}의 관계가 ${esc(r.band)} 단계가 되었다.</span>`);
  if(defy) L.push(r.ok ? "앞으로 한동안은 지침을 잘 따를 것 같다." : "일단은 지침을 따를 것 같다.");
  return L.join("\n");
}
function cslwPops(r){
  const sc = cwq(".cw-scene"); if(!sc) return;
  const fx = [], run = CSLW.run;
  if(r.gain) fx.push([`${r.gain.n} +${r.gain.d}${r.dbl ? " (2배)" : ""}`, ""]);
  if(r.cond) fx.push([`컨디션 +${r.cond}`, "cond"]);
  if(r.trustUp) fx.push(["신뢰 증가", "trust"]);
  else if(r.trustDown) fx.push(["신뢰 감소", "down"]);
  fx.forEach((f, j)=> setTimeout(()=>{
    if(!cwLive(run)) return;
    const p = document.createElement("div"); p.className = "cw-pop" + (f[1] ? " " + f[1] : "");
    p.textContent = f[0]; p.style.left = CSLW.popX + "px"; p.style.top = (CSLW.popTop + j*30) + "px";
    sc.appendChild(p); setTimeout(()=> p.remove(), 2100);
  }, j*260));
}
/* 넘어가기 — 학생이 나가고 다음 학생이 들어온다. 마지막이면 창이 닫힌다 */
async function cslwNext(run){
  if(!cwLive(run) || CSLW.phase !== "result" || cwSkipped()) return;
  CSLW.phase = "next"; cwFocus();
  const n = cwq(".cw-next"); n.classList.remove("on"); n.onclick = null;
  cwq(".cw-clouds").innerHTML = ""; cwq(".cw-say").classList.remove("on");
  const stu = cwq(".cw-stu"); stu.classList.remove("in"); stu.classList.add("out");
  if(CSLW.i >= CSLW.list.length - 1){
    await cwWait(500); if(!cwLive(run)) return;
    cslwClose(true); return;
  }
  cwq(".cw-tab.title").classList.add("fade");
  await cwWait(550); if(!cwLive(run)) return;
  CSLW.i++;
  cwq(".cw-tab.title").classList.remove("fade");
  cslwEnter(run);
}
/* 학생 그림 — 전투 idle 도트 네 장 (128 칸 · 칸의 x 64 · y 56 부터) + #111 테두리. 학생(직업 · 머리색)마다 한 번 굽는다 */
function cslwSprUrl(st){
  if(!st || !sprHas(st.job) || !SPR_READY || SPR_IDX[st.job] == null) return null;
  const ji = SPR_IDX[st.job], pi = sprPalOf(st), key = ji + "|" + pi;
  if(CSLW.spr[key]) return CSLW.spr[key];
  const W = 128, n = Math.max(1, sprN(st.job, 0));
  const cv = document.createElement("canvas"); cv.width = W*4; cv.height = W;
  const g = cv.getContext("2d", {willReadFrequently:true}); g.imageSmoothingEnabled = false;
  for(let f = 0; f < 4; f++){
    const cell = sprCellCv(ji, pi, 0, f % n);
    if(!cell) return null;                                       // 시트가 아직 안 읽혔다 — 조금 뒤에 다시
    g.drawImage(cell, 64, 56, W, W, f*W, 0, W, W);
  }
  // 테두리 — 그림 둘레를 8방향으로 한 칸 넓힌 자리를 #111 로 (전투의 SVG 필터와 같은 모양). 장끼리는 넘지 않는다
  const w4 = W*4, im = g.getImageData(0, 0, w4, W), d = im.data, m = new Uint8Array(w4*W);
  for(let i = 0; i < m.length; i++) m[i] = d[i*4+3] > 0 ? 1 : 0;
  for(let y = 0; y < W; y++) for(let x = 0; x < w4; x++){
    const i = y*w4 + x; if(m[i]) continue;
    const x0 = x - x % W; let on = 0;
    for(let dy = -1; dy <= 1 && !on; dy++){
      const yy = y + dy; if(yy < 0 || yy >= W) continue;
      for(let dx = -1; dx <= 1; dx++){ const xx = x + dx; if(xx >= x0 && xx < x0 + W && m[yy*w4 + xx]){ on = 1; break; } }
    }
    if(on){ d[i*4] = 17; d[i*4+1] = 17; d[i*4+2] = 17; d[i*4+3] = 255; }
  }
  g.putImageData(im, 0, 0);
  const top = new Int16Array(W).fill(W);                         // 칸 x 마다 가장 위 그림 줄 (네 장 합 · 테두리 포함) — 머리 위 말줄임 자리
  for(let f = 0; f < 4; f++) for(let x = 0; x < W; x++) for(let y = 0; y < top[x]; y++){ if(d[(y*w4 + f*W + x)*4 + 3] > 0){ top[x] = y; break; } }
  return (CSLW.spr[key] = {url: cv.toDataURL(), top});
}
async function cslwLook(st, run){
  for(let t = 0; t < 30 && sprHas(st.job); t++){                // 도트 시트를 기다린다 (최대 3초)
    const u = cslwSprUrl(st); if(u) return {spr:u.url, top:u.top};
    await cwWait(100); if(!cwLive(run)) return {};
  }
  return faceHas(st.job) ? {face:FACE_IMG[st.job]} : {};
}
function cslwTune(job){                                          // 직업의 크기 · 자리 — 없거나 이상하면 기본값
  const t = (CSL_SPR && CSL_SPR[job]) || {}, n = (v, d, lo, hi)=> (typeof v === "number" && isFinite(v)) ? clamp(v, lo, hi) : d;
  return {s: n(t.s, CSL_SPR_DEF.s, .5, 1.6), x: n(t.x, CSL_SPR_DEF.x, -60, 60), y: n(t.y, CSL_SPR_DEF.y, -60, 60)};
}
function cslwSetLook(L, st){
  const sc = cwq(".cw-scene"); if(!sc) return;
  const face = !L.spr && !!L.face, spr = cwq(".cw-spr"), hit = cwq(".cw-hit"), dots = cwq(".cw-dots");
  const box = (el, l, t, w, h)=>{ el.style.left = l + "px"; el.style.top = t + "px"; el.style.width = Math.max(0, w) + "px"; el.style.height = Math.max(0, h) + "px"; };
  sc.classList.toggle("face", face);
  spr.style.backgroundImage = L.spr ? `url(${L.spr})` : "";
  const img = cwq(".cw-face"); if(face) img.src = L.face; else img.removeAttribute("src");
  if(face || !L.spr){                                              // 얼굴 그림 (또는 그림 없음) — 예전 자리 그대로
    box(hit, 162, 58, 236, 174); dots.style.left = "300px"; dots.style.top = "50px"; CSLW.popTop = 80; CSLW.popX = 280; return;
  }
  // 무대 2배 — 128 칸(무대 152 ~ 408 · 60 ~ 316)을 발끝(280, 288)을 축으로 s 배 하고 (2x, 2y) 옮긴다
  const T = cslwTune(st && st.job), X = 2*T.x, Y = 2*T.y, k = T.s;
  spr.style.scale = String(k); spr.style.translate = `${X}px ${Y}px`;
  const L0 = 280 + k*(152 - 280) + X, R0 = 280 + k*(408 - 280) + X, T0 = 288 + k*(60 - 288) + Y;
  box(hit, Math.round(L0), Math.round(T0), Math.round(R0 - L0), Math.round(232 - T0));   // 누르는 자리 — 책상 윗변까지
  // 머리 꼭대기 — 가운데(칸 x 64)부터 말줄임 오른쪽 끝(무대 340)까지에서 가장 위 그림 줄. 띠를 못 읽었으면 칸 y 69 즈음
  let cy = 13;
  if(L.top){ let m = 128; for(let x = 64, b = Math.min(127, Math.ceil(64 + 60/(2*k))); x <= b; x++) m = Math.min(m, L.top[x]); if(m < 128) cy = m; }
  const head = 288 + Y + 2*k*(cy - 114);
  dots.style.left = Math.round(300 + X) + "px"; dots.style.top = Math.round(head - 32) + "px";   // 꼬리 끝이 머리에 살짝 닿게
  CSLW.popTop = Math.round(head - 16); CSLW.popX = Math.round(280 + X);
}
/* 도트 구름 — 캔버스로 굽는다 (2px 도트 · 글 길이에 맞춰 높이가 바뀐다). special = 금빛 */
function cslwCloudArt(wc, hc, special){
  const P = 2, w = Math.round(wc/P), h = Math.round(hc/P);
  const r = Math.max(5, Math.min(8, Math.floor(h/4)));
  const m = new Uint8Array(w*h), x0 = r+2, y0 = r+2, x1 = w-r-3, y1 = h-r-3;
  const C = [];
  const stepX = Math.max(5, Math.round(r*1.45)), stepY = Math.max(5, Math.round(r*1.3));
  let k = 0;
  for(let x = x0; x <= x1; x += stepX){ C.push([x, y0, r - (k%3===1?1:0)]); C.push([Math.min(x1, x + (stepX>>1)), y1, r - (k%2)]); k++; }   // 아래 줄 마지막 혹이 그림 밖으로 나가 테두리가 잘리지 않게
  C.push([x1, y0, r]); C.push([x1, y1, r]);
  for(let y = y0 + stepY; y < y1; y += stepY){ C.push([x0, y, r]); C.push([x1, y, r - 1]); }
  for(let y = 0; y < h; y++) for(let x = 0; x < w; x++){
    let inside = (x>=x0 && x<=x1 && y>=y0 && y<=y1);
    for(let j = 0; !inside && j < C.length; j++){ const c = C[j], dx = x-c[0], dy = y-c[1]; if(dx*dx+dy*dy <= c[2]*c[2] + c[2]) inside = true; }
    m[y*w+x] = inside ? 1 : 0;
  }
  const at = (x,y)=> (x<0||y<0||x>=w||y>=h) ? 0 : m[y*w+x];
  const cv = document.createElement("canvas"); cv.width = w; cv.height = h;
  const g = cv.getContext("2d"), img = g.createImageData(w, h), d = img.data;
  const put = (x,y,c)=>{ const i=(y*w+x)*4; d[i]=c[0]; d[i+1]=c[1]; d[i+2]=c[2]; d[i+3]=c[3]; };
  const FILL = special ? [255,226,128,255] : [255,248,232,255];
  const HI   = special ? [255,246,200,255] : [255,255,255,255];
  const LO   = special ? [232,184,72,255]  : [236,222,196,255];
  const OUT  = [74,53,36,255], GLOW = special ? [255,196,40,255] : [232,194,91,255];
  for(let y = 0; y < h; y++) for(let x = 0; x < w; x++){
    if(at(x,y)){ put(x, y, (!at(x,y-1) || !at(x-1,y)) ? HI : (!at(x,y+1) || !at(x+1,y)) ? LO : FILL); continue; }
    if(at(x-1,y)||at(x+1,y)||at(x,y-1)||at(x,y+1)){ put(x, y, OUT); continue; }
    if(at(x-2,y)||at(x+2,y)||at(x,y-2)||at(x,y+2)||at(x-1,y-1)||at(x+1,y-1)||at(x-1,y+1)||at(x+1,y+1)) put(x, y, GLOW);
  }
  if(special){   // 반짝이 몇 점
    [[x0+3,y0+2],[x1-4,y0+4],[x0+8,y1-2],[x1-9,y1-3]].forEach(([x,y])=>{
      if(at(x,y)){ put(x,y,[255,255,255,255]); if(at(x+1,y)) put(x+1,y,[255,250,220,255]); if(at(x,y+1)) put(x,y+1,[255,250,220,255]); }
    });
  }
  g.putImageData(img, 0, 0);
  return cv.toDataURL();
}
/* 화면에 맞추기 — 넉넉하면 창을 통째로 (최대 1배), 0.8배보다 줄여야 하면 좁은 화면 배치 */
function cslwFit(){
  const ov = CSLW.el; if(!ov) return;
  const win = ov.querySelector(".cw-win"), fit = ov.querySelector(".cw-fit"), inn = ov.querySelector(".cw-in"),
        stage = ov.querySelector(".cw-stage"), scene = ov.querySelector(".cw-scene");
  const vw = document.documentElement.clientWidth || window.innerWidth, vh = window.innerHeight;
  win.classList.remove("compact", "wide"); win.style.width = ""; stage.style.width = stage.style.height = ""; scene.style.transform = ""; inn.style.transform = "";
  const W = 592, H = win.offsetHeight + 4;                       // 그림자 4px 까지
  const s = Math.min(1, (vw - 16) / W, (vh - 16) / H);
  CSLW.compact = s < .8;
  let key = "d";
  if(!CSLW.compact){
    if(s < 1) inn.style.transform = `scale(${s})`;
    fit.style.width = Math.floor(W * s) + "px"; fit.style.height = Math.floor(H * s) + "px";
  } else {
    const ww = Math.max(260, Math.min(588, vw - 16)), inner = ww - 4 - 16 - 4;   // 창 테두리 · 안쪽 여백 · 무대 테두리
    const ss = Math.min(1, inner / 560, Math.max(.36, vh * .46 / 360));
    win.classList.add("compact"); win.classList.toggle("wide", inner >= 480); win.style.width = ww + "px";
    stage.style.width = Math.round(560 * ss + 4) + "px"; stage.style.height = Math.round(360 * ss + 4) + "px";
    scene.style.transform = `scale(${ss})`;
    fit.style.width = (ww + 4) + "px"; fit.style.height = "";
    key = "c" + ww;
  }
  if(key !== CSLW.fitKey){
    const was = CSLW.fitKey; CSLW.fitKey = key;
    if(was && CSLW.phase === "choose" && CSLW.cur) cslwClouds(CSLW.cur, true);   // 배치가 바뀌면 구름을 다시
  }
}
/* 상담 확률 (상담 화면 · 상담 기록) */
function cslProbHtml(){
  return `<div class="cslprob">
        <span>지도력 ${cslLead()} — 맞지 않아도 설득 <b>${Math.round(cslLeadP()*100)}%</b></span>
        <span>정보력 ${cslInfo()} — 통할 말 파악 <b>${Math.round(cslInfoP()*100)}%</b></span>
        <span>호소력 ${cslNet()} — 상승폭 2배 <b>${Math.round(cslNetP()*100)}%</b></span>
        ${cslFacLv()? `<span style="color:var(--brass)">상담실 Lv.${cslFacLv()} 보정 포함</span>`:""}
      </div>`;
}
/* 상담 화면 — 상담은 창으로 한다 (메뉴의 상담을 누르면 창이 뜬다). 이 화면은 직접 들어왔을 때의 안내 */
function viewCounsel(){
  const n = cslwList().length;
  return `<section class="panel">
    <div class="panel-h"><h2>상담실</h2><span class="hint">${yrName(S.year)}${n? ` · <b style="color:var(--brass)">찾아온 학생 ${n}명</b>` : ""}</span></div>
    <p style="font-size:13px;color:var(--muted);margin:0 0 12px">${n? "학생이 할 말이 있다고 찾아와 있다." : "지금은 찾아온 학생이 없다. 한 주를 보내면 누군가 문을 두드릴 수 있다."} 지난 상담은 일지의 <b>상담 기록</b>에서 본다.</p>
    ${cslProbHtml()}
    <div class="btnrow" style="margin-top:14px"><button class="btn primary" data-cslw>상담실 열기</button><button class="btn" data-cslrec>상담 기록</button></div>
  </section>`;
}
/* 일지 › 상담 기록 — 올해의 지침 무시 상담 · 고민 상담 (예전 상담 탭 아래쪽 그대로) */
function viewCslLog(){
  const C = counselState(), log = C.done.slice().reverse(), dr = defyRecords(), n = cslwList().length;
  const dn2 = defyState().log.filter(d=> (d.year|0)===(S.year|0)).length;
  return `<section class="panel">
    <div class="panel-h"><h2>올해의 상담 기록</h2><span class="hint">${yrName(S.year)} · 고민 상담 ${C.done.length}회${dn2? ` · 지침 무시 상담 ${dn2}회` : ""}</span></div>
    ${(log.length || dr)? `<div class="grid2">${dr}${log.map(cslRecHtml).join("")}</div>` : `<div class="empty">아직 올해 상담 기록이 없다.</div>`}
    ${cslProbHtml()}
    <div class="btnrow" style="margin-top:14px"><button class="btn${n? " primary" : ""}" data-cslw>상담실 열기${n? ` · 찾아온 학생 ${n}명` : ""}</button></div>
  </section>`;
}
function cslRecHtml(d){
      const c = counselOf(d.cid); if(!c) return "";
      return `<div class="opt" style="cursor:default;border-color:${d.fit?"var(--ok)":"var(--line)"}">
        <div class="on">${esc(d.name)} <span class="tag" style="color:var(--brass);border-color:var(--brass)">${PERSONA[d.pers]?PERSONA[d.pers].n:"평범"}</span>
          <span class="price">${PHASES[d.phase]?PHASES[d.phase].n:""} ${d.week}주</span></div>
        <div class="od" style="color:var(--dim)">${esc(c.t)}</div>
        <div class="od"><b style="color:var(--brass)">마스터</b> “${esc(c.o[d.oi].t)}”</div>
        ${d.reply? `<div class="od"><b>${esc(d.name)}</b> “${esc(d.reply)}”</div>` : ""}
        <div class="od" style="color:var(--${d.fit?"ok":"dim"})">${esc(d.react || (d.fit? c.o[d.oi].r : "표정이 풀리지 않았다. 다른 말이 필요했던 모양이다."))}</div>
        ${d.byLead? `<div class="od" style="color:var(--brass)">성격에 맞는 말은 아니었지만, 지도력으로 설득했다</div>`:""}
        ${d.byTrust? `<div class="od" style="color:var(--brass)">신뢰가 운명 단계라 무슨 말이든 닿았다</div>`:""}
        ${d.gain? `<div class="od" style="color:var(--brass)">${d.gain.n} +${d.gain.d}${d.dbl? ` <span style="color:var(--ok)">— 호소력으로 상승폭 2배</span>`:""}</div>`:""}
        ${d.capped? `<div class="od" style="color:var(--dim)">더 오를 항목이 없다 — 멘탈리티가 모두 한계다. 신뢰만 깊어졌다</div>`:""}
      </div>`;
}
/* CSLWIN_END */
