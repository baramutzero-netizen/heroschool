"""행동 지침 무시 (1008) — 몇 번을 돌려도 같은 결과.

    python3 apply_defy.py <game.html>

· 1년차 봄 8주차부터, 매주 스케줄을 시작할 때 학생마다 확률을 굴려 걸린 학생 중 한 명(한 주에 한 명까지)이
  그 주 개인 행동 지침 대신 다른 행동을 한다 — 훈련 → 휴식 · 의뢰 / 휴식 → 훈련 · 의뢰 / 의뢰 → 훈련 · 휴식
  (의뢰는 열려 있고 여름이 아닐 때만). 그 행동의 컨디션 소모 ×2 · 회복 ×1/2
· 확률(%) = 등급(D 10 ~ S 50) + 신뢰(타인 +20 · 면식 +10 · 관심 0 · 의지 -10 · 유대 -20) + 학원 명성(무명 +20 ~ 초명문 -20)
  + 성격(허세 · 천재적 +10 · 성실 -10). 신뢰 운명 · 상담 뒤 면제 기간 · 부상인 학생은 빠진다
· 주가 끝나면 경과 보고 결산 창에 빨간 글씨 '! 행동 지침을 무시한 학생이 발생했습니다.' · 일지 · 상담 탭에 그 학생 이벤트.
  상담하지 않고 다음 주를 시작하면 그 학생은 무조건 또 무시한다 (그 주의 한 명). 처음 발생하면 상담 안내(튜토리얼 14)
· 상담 — 마스터가 무엇을 안 하고 무엇을 했는지 묻고, 학생은 성격 × 행동에 따라 대답한다. 마스터의 말은 셋 중 하나
  (공감 — 소심 · 평범 · 활발 / 원칙 — 차분 · 성실 · 새침 / 도전 — 열혈 · 허세 · 천재적). 지도력 · 정보력 · 호소력은 고민 상담과 같다.
  맞는 말 — 멘탈리티 · 컨디션 · 신뢰가 오르고 4계절 동안 무시하지 않는다 / 안 맞는 말 — 신뢰가 내리고 2계절 동안 무시하지 않는다"""
import sys

MARK = "function defyWeekStart(R){"

DEFY_JS = r"""/* ============================================================
   행동 지침 무시 (1008)
   1년차 봄 8주차부터 — 매주 스케줄을 시작할 때 학생마다 확률을 굴려, 걸린 학생 중 한 명이 그 주 개인 행동 지침 대신 다른 행동을 한다 (한 주에 한 명까지).
   확률(%) = 등급(D 10 · C 20 · B 30 · A 40 · S 50) + 신뢰(타인 +20 · 면식 +10 · 관심 0 · 의지 -10 · 유대 -20) + 학원 명성(무명 +20 ~ 초명문 -20) + 성격(허세 · 천재적 +10 · 성실 -10)
   빠지는 학생 — 신뢰 운명 단계 · 지침 무시 상담 뒤 면제 기간(성격에 맞는 말 4계절 · 맞지 않는 말 2계절) · 부상
   상담 탭의 이벤트를 하지 않고 다음 주를 시작하면 그 학생이 무조건 또 무시한다 (그 주의 한 명)
   바꾸는 행동 — 훈련 → 휴식 · 의뢰 / 휴식 → 훈련 · 의뢰 / 의뢰 → 훈련 · 휴식 (의뢰는 열려 있고 여름이 아닐 때만). 그 행동의 컨디션 소모 ×2 · 회복 ×1/2
   ============================================================ */
const DEFY_START_WEEK = 8;                                   // 1년차 봄 이 주차부터
const DEFY_GRADE = {D:10, C:20, B:30, A:40, S:50};
const DEFY_TRUST = [20, 10, 0, -10, -20];                    // 신뢰 단계 타인 · 면식 · 관심 · 의지 · 유대 (운명은 무시하지 않는다)
const DEFY_FAME = [20, 10, 0, -10, -20];                     // 학원 명성 무명 · 유명 · 강호 · 명문 · 초명문
const DEFY_PERS = {boast:10, genius:10, dilig:-10};
const DEFY_COST = 2, DEFY_REC = .5;                          // 바꾼 행동의 컨디션 소모 ×2 · 회복 ×1/2
const DEFY_FIT_SEASONS = 4, DEFY_MISS_SEASONS = 2;          // 상담 뒤 지침을 무시하지 않는 기간 — 지금 계절 뒤로 이만큼
const DEFY_FIT_COND = 10;                                    // 성격에 맞는 말 — 컨디션 회복
const DEFY_SUBS = {train:["rest","job"], rest:["train","job"], job:["train","rest"]};
const DEFY_LOG_MAX = 60;
function defyState(){
  if(!S.defy || typeof S.defy !== "object") S.defy = {};
  const D = S.defy;
  if(!Array.isArray(D.pend)) D.pend = [];
  if(!D.imm || typeof D.imm !== "object") D.imm = {};
  if(!Array.isArray(D.log)) D.log = [];
  const ids = new Set((S.students||[]).map(x=> x.id));
  D.pend = D.pend.filter(p=> p && ids.has(p.sid));            // 졸업한 학생의 이벤트는 내린다
  Object.keys(D.imm).forEach(k=>{ if(!ids.has(k)) delete D.imm[k]; });
  return D;
}
function defySeason(){ return (S.year|0)*4 + Math.max(0, PHASE_ORDER.indexOf(S.phase)); }
function defyWeekKey(){ return `${S.year}-${S.phase}-${S.week}`; }
function defyOpen(){ return (S.year|0) > 1 || S.phase !== "spring" || (S.week|0) + 1 >= DEFY_START_WEEK; }
function defyTrustIdx(st){ const v = trustOf(st); return v>=7? 4 : v>=5? 3 : v>=3? 2 : v>=1? 1 : 0; }
/* 이번 주에 지침을 무시할 확률 (0~1) — 신뢰 운명이면 0 */
function defyChance(st){
  if(!st || trustFull(st)) return 0;
  const p = (DEFY_GRADE[st.grade]||0) + DEFY_TRUST[defyTrustIdx(st)]
          + DEFY_FAME[clamp(fameTitleIdx(S.fame|0), 0, DEFY_FAME.length-1)] + (DEFY_PERS[st.pers]||0);
  return clamp(p, 0, 100) / 100;
}
function defySubs(st){ return (DEFY_SUBS[actShown(st)]||[]).filter(k=> k!=="job" || jobOpen()); }
function defyCan(st){ return !!st && actUnlocked() && !isInjured(st) && defySubs(st).length > 0; }
function defyImmune(st){ const u = defyState().imm[st.id]; return u != null && defySeason() <= u; }
function defyPend(st){ return (st && S && S.defy && Array.isArray(S.defy.pend)) ? (S.defy.pend.find(p=> p && p.sid===st.id) || null) : null; }
/* 이번 주에 지침을 무시하는 중인가 — 그렇다면 {from, to} */
function defyNow(st){ const c = S && S.defy && S.defy.cur; return (c && st && c.sid===st.id && c.at===defyWeekKey()) ? c : null; }
function defyCostMul(st, act){ const c = defyNow(st); return (c && c.to===act) ? DEFY_COST : 1; }
function defyRecMul(st){ const c = defyNow(st); return (c && c.to==="rest") ? DEFY_REC : 1; }
/* 주를 시작할 때 — 상담하지 않은 학생이 있으면 그 학생이 무조건, 없으면 확률을 굴려 걸린 학생 중 한 명 */
function defyWeekStart(R){
  const D = defyState();
  D.cur = null;
  if(!R || !defyOpen() || !actUnlocked()) return null;
  let st = null, forced = false;
  const pend = D.pend.map(p=> S.students.find(x=> x.id===p.sid)).filter(defyCan);
  if(pend.length){ st = pick(pend); forced = true; }
  else {
    const hit = S.students.filter(x=> defyCan(x) && !trustFull(x) && !defyImmune(x) && RNG() < defyChance(x));
    if(hit.length) st = pick(hit);
  }
  if(!st) return null;
  const from = actShown(st), to = pick(defySubs(st));
  D.cur = {sid:st.id, from, to, at:defyWeekKey(), forced};
  R.defy = {sid:st.id, from, to, forced};
  return D.cur;
}
/* 주가 끝날 때 — 상담 탭에 이벤트를 건다 (이미 걸려 있으면 이번 일로 고친다). 처음이면 상담 안내 한 장 */
function defyWeekEnd(R){
  const D = defyState(), c = D.cur;
  D.cur = null;
  if(!c || !R || !R.defy) return;
  const st = S.students.find(x=> x.id===c.sid);
  if(!st) return;
  let jk = null;
  if(c.to==="job" || c.from==="job"){ try{ jk = R.job || (weekJobPlan() || JOB_LIST[0]).k; }catch(e){ jk = JOB_LIST[0].k; } }
  let p = defyPend(st);
  if(!p){ p = {sid:st.id, n:0, order:shuffled([0,1,2]), reveal: RNG() < cslInfoP()}; D.pend.push(p); }
  Object.assign(p, {from:c.from, to:c.to, jk, year:S.year, phase:S.phase, week:(R.startWeek|0)+1, forced:!!c.forced, n:(p.n|0)+1});
  dlog(`<b style="color:var(--bad)">! 행동 지침 무시</b> — ${dnH(st)}${eunn(st.name)} 이번 주 개인 행동 지침(<b>${actName(c.from)}</b>) 대신 <b style="color:var(--bad)">${actName(c.to)}</b>${eulr(actName(c.to))} 했다.${c.forced? " 상담하지 않고 넘긴 탓에 또 지침을 무시했다." : ""}`, "bad");
  logE(`<b style="color:var(--bad)">! 행동 지침을 무시한 학생이 발생했습니다.</b> <b>${dnH(st)}</b> — ${actName(c.from)} 대신 <b>${actName(c.to)}</b>. <b style="color:var(--brass)">상담</b> 탭에서 이유를 들어 볼 수 있다. 상담하지 않고 다음 주를 시작하면 또 지침을 무시한다.`, "bad");
  if(!D.first){ D.first = 1; if(!tutSeen("14")) queueCeremony({type:"tut", page:"14"}); }
}
/* ── 상담 ── 마스터가 묻고, 학생이 성격 × (안 한 것 > 한 것)으로 대답한다.
   {who} 의뢰인 · {job} 의뢰 이름 — 뒤에 +이 · +을 · +은 · +와 를 붙이면 조사까지 맞춘다 */
const DEFY_ASK = {
  "train>rest":"이번 주 네 개인 행동 지침은 훈련이었다. 어째서 훈련을 하지 않고 쉬었지?",
  "train>job": "이번 주 네 개인 행동 지침은 훈련이었다. 어째서 훈련을 하지 않고 의뢰를 하러 갔지?",
  "rest>train":"이번 주엔 쉬라고 했다. 어째서 쉬지 않고 훈련을 했지?",
  "rest>job":  "이번 주엔 쉬라고 했다. 어째서 쉬지 않고 의뢰를 하러 갔지?",
  "job>train": "이번 주 네 개인 행동 지침은 의뢰였다. 어째서 의뢰를 하지 않고 훈련을 했지?",
  "job>rest":  "이번 주 네 개인 행동 지침은 의뢰였다. 어째서 의뢰를 하지 않고 쉬었지?"
};
const DEFY_LINES = {
  intro:{
    "train>rest":"……너무 힘들어서…… 쉬었어요…… 죄송해요……",
    "train>job": "그게…… {who}께서 도와 달라고 하셔서…… 거절을 못 했어요……",
    "rest>train":"쉬고 있으면…… 저만 뒤처지는 것 같아서…… 몰래 연습했어요……",
    "rest>job":  "{who}께서 혼자 힘들어 보이셔서…… 말씀도 못 드리고 도와드렸어요……",
    "job>train": "모르는 분들이랑 이야기하는 게…… 무서워서…… 혼자 연습했어요……",
    "job>rest":  "사람 많은 데 가는 게…… 자신이 없어서…… 그냥 쉬었어요……"},
  hot:{
    "train>rest":"몸이 말을 안 듣더라고요! 쉬라는 신호인 줄 알았습니다!",
    "train>job": "{who}께서 일손이 모자라다는데 가만히 있을 수가 있습니까! 바로 달려갔습니다!",
    "rest>train":"쉬고 있으니 몸이 근질근질해서 못 참겠더라고요! 그래서 훈련했습니다!",
    "rest>job":  "{who}께서 힘들어 보이셨습니다! 그냥 지나칠 수가 없었습니다!",
    "job>train": "잡일보다 훈련이 급하다고 생각했습니다! 다음 대회에서는 지고 싶지 않습니다!",
    "job>rest":  "솔직히 그 일은 제 체질이 아닙니다! 그래서 차라리 쉬었습니다!"},
  stone:{
    "train>rest":"피로가 쌓여 효율이 떨어진다고 판단했습니다. 쉬는 쪽이 합리적이었습니다.",
    "train>job": "{job} 일손이 부족하다고 들었습니다. 그쪽이 더 급하다고 판단했습니다.",
    "rest>train":"컨디션은 충분했습니다. 쉬는 시간은 낭비라고 판단했습니다.",
    "rest>job":  "쉬는 것보다 {who+을} 돕는 편이 유익하다고 판단했습니다.",
    "job>train": "지금 제게 필요한 건 의뢰가 아니라 훈련이라고 판단했습니다.",
    "job>rest":  "의뢰를 할 상태가 아니라고 판단했습니다. 무리하면 실수가 나옵니다."},
  dilig:{
    "train>rest":"몸 상태가 좋지 않아서…… 무리하면 다른 친구들한테 폐가 될 것 같았어요. 죄송합니다.",
    "train>job": "{who}께서 일손이 모자라 곤란해하셔서요. 훈련은 다음에 그 몫까지 채울게요.",
    "rest>train":"쉬라고 하신 건 알았는데, 다들 훈련하는데 저만 쉬는 게 마음에 걸려서요.",
    "rest>job":  "{who}께서 힘들어 보이셔서 그냥 돌아올 수가 없었어요. 죄송해요.",
    "job>train": "의뢰도 중요하지만, 요즘 제 실력이 부족한 것 같아서 훈련을 더 하고 싶었어요.",
    "job>rest":  "의뢰하다 실수할까 봐서요…… 몸이 너무 무거워서 하루 쉬었어요. 죄송해요."},
  tsun:{
    "train>rest":"…피곤했을 뿐이에요. 딱히 게으름 피운 거 아니거든요.",
    "train>job": "…{who+이} 곤란해 보이길래요. 딱히 걱정돼서 그런 건 아니에요.",
    "rest>train":"…쉬는 게 지루해서요. 마스터 때문에 연습한 거 아니거든요.",
    "rest>job":  "…{who+이} 혼자 끙끙대는 게 거슬려서요. 그뿐이에요.",
    "job>train": "…그런 잡일보다 훈련이 낫잖아요. 뻔한 걸 왜 물어요.",
    "job>rest":  "…가기 싫었어요. 이유가 꼭 있어야 해요?"},
  lively:{
    "train>rest":"헤헤, 너무 피곤해서 그만 꿀잠을 자 버렸어요! 다음엔 두 배로 할게요!",
    "train>job": "{who+이} 일손이 모자라다고 하셔서 도와드렸어요! 엄청 고마워하셨어요!",
    "rest>train":"가만히 있으려니 너무 심심해서요! 다 같이 훈련하는 게 더 재밌잖아요!",
    "rest>job":  "{who+이} 힘들어 보이셔서 도와드렸어요!",
    "job>train": "의뢰도 좋지만, 다 같이 훈련하는 날이 더 신나서요! 헤헤.",
    "job>rest":  "헤헤…… 사실 너무 졸려서 그만 낮잠을…… 다음엔 꼭 갈게요!"},
  boast:{
    "train>rest":"영웅에게도 휴식은 필요한 법! 폭풍 전의 고요라고 해 두죠!",
    "train>job": "마을의 평화도 영웅의 몫이죠! {who+이} 저를 애타게 찾았거든요!",
    "rest>train":"전설은 쉬는 동안 만들어지지 않습니다! 그래서 남몰래 단련했죠!",
    "rest>job":  "곤경에 처한 시민을 외면하는 영웅은 없습니다! {who+을} 구해 드렸죠!",
    "job>train": "그런 잡일은 영웅의 격에 맞지 않거든요! 대신 필살기를 다듬었습니다!",
    "job>rest":  "진정한 영웅은 힘을 아낄 줄도 알죠! 다음 큰 무대를 위해서요!"},
  plain:{
    "train>rest":"그냥…… 좀 지쳐서 쉬었어요. 죄송해요.",
    "train>job": "{who}께서 일손이 모자라다고 하셔서, 그쪽을 도왔어요.",
    "rest>train":"쉬어도 되긴 했는데, 몸이 괜찮아서 그냥 훈련했어요.",
    "rest>job":  "{who}께서 바빠 보이셔서 잠깐 도와드렸어요.",
    "job>train": "이번 주는 의뢰보다 훈련을 하고 싶은 기분이었어요.",
    "job>rest":  "좀 피곤해서 의뢰 대신 쉬었어요."},
  genius:{
    "train>rest":"그 훈련은 이미 다 익혔어요. 반복할 이유가 없어서 쉬었죠.",
    "train>job": "훈련은 혼자서도 충분해요. {job} 쪽이 배울 게 더 많아 보여서요.",
    "rest>train":"쉴 만큼 지치지 않았어요. 시간이 아까워서 새 기술을 시험해 봤죠.",
    "rest>job":  "머리 식힐 겸 갔어요. {job}도 은근히 공부가 되거든요.",
    "job>train": "그 의뢰는 결과가 뻔히 보여서요. 훈련이 더 효율적이에요.",
    "job>rest":  "오늘은 쉬는 게 최적이라고 계산했어요. 그 의뢰는 다음에 해도 돼요."}
};
/* 마스터의 말 — 세 갈래는 늘 같은 성격에 닿는다: 0 공감(소심 · 평범 · 활발) · 1 원칙(차분 · 성실 · 새침) · 2 도전(열혈 · 허세 · 천재적) */
const DEFY_FIT = [["intro","plain","lively"], ["stone","dilig","tsun"], ["hot","boast","genius"]];
const DEFY_REPLY = {
  "train>rest":["힘들었구나. 다음엔 쉬기 전에 먼저 말해 다오. 같이 정하자.",
                "지침은 네 몸을 보고 짠 것이다. 힘들면 행동이 아니라 말로 알려라.",
                "쉰 만큼 다음 주에 증명해라. 나는 네가 해낼 거라 믿는다."],
  "train>job": ["남을 돕고 싶었던 마음은 안다. 다음엔 나와 먼저 상의하자.",
                "의뢰도 좋지만 지금 네 몫은 훈련이다. 정해진 일부터 해라.",
                "돕는 건 좋다. 대신 그만큼 훈련에서도 성장을 보여 줘라."],
  "rest>train":["뒤처질까 불안했구나. 쉬는 것도 훈련이라는 걸 기억해 다오.",
                "휴식도 계획의 일부다. 지친 몸으로 한 훈련은 남지 않는다.",
                "그 열정은 좋다. 그러니 푹 쉬고 나서 전력으로 부딪혀라."],
  "rest>job":  ["착한 마음은 고맙다. 하지만 네 몸을 챙겨야 남도 도울 수 있다.",
                "쉬라고 한 데는 이유가 있다. 의뢰는 회복한 다음이다.",
                "남을 돕는 영웅이 되고 싶다면, 먼저 네 몸부터 최고로 만들어라."],
  "job>train": ["훈련이 하고 싶었구나. 그래도 마을 사람들이 너를 기다렸다.",
                "의뢰도 수련이다. 사람을 상대하는 법은 훈련장에서 배울 수 없다.",
                "의뢰를 해내는 것도 실력이다. 그 일부터 완벽하게 해내 봐라."],
  "job>rest":  ["많이 지쳤구나. 다음엔 그런 날이라고 미리 말해 다오.",
                "맡은 일을 비우면 기다리던 사람이 곤란해진다. 약속은 지켜라.",
                "쉬고 싶은 마음을 이겨 내는 것도 실력이다. 다음엔 해내라."]
};
/* 학생의 반응 — [맞는 말 · 완벽하게 이해하고 따른다, 맞지 않는 말 · 납득은 안 되지만 따라 본다] */
const DEFY_REACT = {
  intro: ["작게 고개를 끄덕인다. “……네. 다음엔…… 꼭 먼저 말씀드릴게요.”", "고개를 숙인 채 한참 말이 없다. “……알겠어요. 해 볼게요……”"],
  hot:   ["“알겠습니다! 이제부터는 지침대로 전력으로 가겠습니다!”", "입술을 꾹 다문다. “……납득은 안 되지만, 마스터 말씀이니 따르겠습니다.”"],
  stone: ["“이해했습니다. 지침에 따르겠습니다.” 눈빛에 망설임이 없다.", "잠시 생각에 잠긴다. “……동의하긴 어렵습니다. 하지만 일단 따르겠습니다.”"],
  dilig: ["“네! 이제 마스터 뜻을 알겠어요. 지침대로 할게요.”", "“……네. 아직 잘 모르겠지만, 시키신 대로 해 볼게요.”"],
  tsun:  ["“…알았어요. 마스터가 그렇게까지 말하니까요.” 귀가 조금 빨갛다.", "“…흥. 이번만 따라 드리는 거예요.”"],
  lively:["“헤헤, 알겠어요! 다음엔 지침대로 열심히 할게요!”", "“음…… 잘 모르겠지만, 일단 해 볼게요!” 표정이 조금 시무룩하다."],
  boast: ["“역시 마스터! 영웅에겐 영웅의 길이 있는 법이죠. 지침대로 가겠습니다!”", "“……뭐, 영웅은 너그러운 법이니까요. 이번엔 따라 드리죠.”"],
  plain: ["“네, 알겠습니다. 앞으로는 지침대로 할게요.”", "“……네. 일단 그렇게 해 볼게요.”"],
  genius:["“이해했어요. 마스터 계산이 더 맞네요. 지침대로 할게요.”", "“…납득은 안 되지만, 마스터 방식대로 한번 해 보죠.”"]
};
function defyFill(t, p){
  const J = (p && p.jk) ? jobDef(p.jk) : null;
  const who = J ? J.who : "마을 사람", job = J ? J.n : "의뢰";
  return String(t||"").replace(/\{(who|job)(?:\+(이|을|은|와))?\}/g, (m, k, j)=>{
    const w = k==="who" ? who : job;
    return w + (j==="이" ? jo(w,"이","가") : j==="을" ? jo(w,"을","를") : j==="은" ? jo(w,"은","는") : j==="와" ? jo(w,"과","와") : "");
  });
}
function defyLine(st, key){
  const L = DEFY_LINES[(st && st.pers) || "plain"] || DEFY_LINES.plain;
  return masterQ(L[key] || DEFY_LINES.plain[key] || "", st);
}
function answerDefy(pi, oi){
  const D = defyState(), p = D.pend[pi];
  if(!p) return;
  const st = S.students.find(x=> x.id===p.sid);
  if(!st){ D.pend.splice(pi,1); save(); render(); return; }
  const key = p.from + ">" + p.to;
  const fit = (DEFY_FIT[oi]||[]).includes(st.pers||"plain");
  const byLead = !fit && (RNG() < cslLeadP());                // 지도력 — 성격에 맞지 않아도 설득해낸다
  const byTrust = !fit && !byLead && trustFull(st);
  const ok = fit || byLead || byTrust;
  let gain = null, dbl = false, capped = false, cond = 0;
  if(ok){
    const ks = MENTAL.filter(m=> !m.fixed && st.ment[m.k] < mentCapOf(st, m.k));
    capped = !ks.length;
    if(ks.length){
      const m = pick(ks);
      let d = ri(2,4);
      if(RNG() < cslNetP()){ d *= 2; dbl = true; }              // 호소력 — 상승폭 2배
      const before = st.ment[m.k];
      st.ment[m.k] = clamp(before + d, 1, mentCapOf(st, m.k));
      gain = {k:m.k, n:m.n, d: +(st.ment[m.k]-before).toFixed(2)};
    }
    const c0 = st.cond; setCond(st, st.cond + DEFY_FIT_COND); cond = Math.round(st.cond - c0);
    addTrust(st, 1);
  } else addTrust(st, -1);
  const seasons = ok ? DEFY_FIT_SEASONS : DEFY_MISS_SEASONS;
  D.imm[st.id] = defySeason() + seasons;
  D.pend.splice(pi, 1);
  const R2 = DEFY_REACT[st.pers||"plain"] || DEFY_REACT.plain;
  D.log.push({sid:st.id, name:dn(st), pers:st.pers||"plain", from:p.from, to:p.to, jk:p.jk||null, oi, ok, byLead, byTrust, dbl, gain, capped, cond, seasons,
    year:p.year||S.year, phase:p.phase||S.phase, week:p.week||(S.week+1),
    ans: defyFill(defyLine(st, key), p), reply: (DEFY_REPLY[key]||DEFY_REPLY["train>rest"])[oi]||"", react: masterQ(ok ? R2[0] : R2[1], st, true)});
  if(D.log.length > DEFY_LOG_MAX) D.log.splice(0, D.log.length - DEFY_LOG_MAX);
  logE(ok
    ? `지침 무시 상담 — <b>${dnH(st)}</b>(${personaOf(st).n})${iga(st.name)} 마스터의 뜻을 받아들였다.${byLead? ` <span style="color:var(--brass)">지도력으로 설득</span>`:""}${gain? ` <b style="color:var(--ok)">${gain.n} +${gain.d}</b>${dbl? ` <span style="color:var(--brass)">(호소력 2배)</span>`:""}`:""}${cond? ` · 컨디션 +${cond}`:""} · 신뢰 증가 · ${seasons}계절 동안 지침을 따른다.`
    : `지침 무시 상담 — <b>${dnH(st)}</b>(${personaOf(st).n})${eunn(st.name)} 납득하지 못했지만 일단 따르기로 했다. 신뢰 감소 · ${seasons}계절 동안 지침을 따른다.`, ok? "good" : "");
  save(); render();
  toast(ok ? `${dn(st)} — 지침을 따르겠다고 한다${gain? ` · ${gain.n} +${gain.d}${dbl?" (2배)":""}`:""}` : `${dn(st)} — 납득하지 못했지만 일단 따르겠다고 한다`);
}
/* 상담 탭 — 지침을 무시한 학생 (고민 상담 위에 따로) */
function defyBlock(p, pi){
  const st = S.students.find(x=> x.id===p.sid);
  if(!st) return "";
  const P = personaOf(st), key = p.from + ">" + p.to;
  const order = Array.isArray(p.order) && p.order.length===3 ? p.order : [0,1,2];
  const replies = DEFY_REPLY[key] || DEFY_REPLY["train>rest"];
  const face = faceHas(st.job)? faceHTML(st.job, dn(st))
    : (sprHas(st.job)? `<div class="facebox" style="display:flex;align-items:flex-end;justify-content:center">${sprHTML(st.job,"idle",.5,{p:sprPalOf(st), still:true})}</div>` : "");
  return `<div class="cslblock defyblock">
    <div class="cslcard defycard">
      <div class="cslrow">${face}<div class="cslmain">
      <div class="cslwho">${dnH(st)} ${roleTag(st.job)}<span class="tag yr">${st.year}학년</span>
        <span class="tag" style="color:var(--brass);border-color:var(--brass)">${P.n}</span>
        <span class="price">${PHASES[p.phase]? PHASES[p.phase].n+" "+p.week+"주 · ":""}지침 무시${(p.n|0)>1? ` ${p.n}주째`:""}</span></div>
      <div class="defyact"><span>지침</span><b>${actName(p.from)}</b><i aria-hidden="true">→</i><span>실제</span><b class="bad">${actName(p.to)}</b></div>
      <div class="defyask"><b>마스터</b>“${esc(defyFill(DEFY_ASK[key]||"", p))}”</div>
      <div class="cslq">“${esc(defyFill(defyLine(st, key), p))}”</div>
      </div></div>
    </div>
    ${p.reveal? `<p style="color:var(--muted);font-size:12.5px;margin:10px 0 8px"><b style="color:var(--brass)">정보력으로 ${dnH(st)}에게 통할 말을 미리 파악했다.</b></p>` : `<div style="height:10px"></div>`}
    <div class="grid2">
      ${order.map(i=>{
        const hit = p.reveal && (DEFY_FIT[i]||[]).includes(st.pers||"plain");
        return `<button class="opt cslopt ${hit?"cslhit":""}" data-defy="${pi}|${i}">
          <div class="on">${esc(replies[i]||"")}${hit? `<span class="price" style="color:var(--brass)">통할 말</span>`:""}</div>
        </button>`;
      }).join("")}
    </div>
  </div>`;
}
function defySection(){
  const D = defyState();
  if(!D.pend.length) return "";
  return `<div class="defyhead"><b>! 행동 지침을 무시한 학생</b><span>상담하지 않고 다음 주를 시작하면 이 학생은 또 지침을 무시한다</span></div>
    ${D.pend.map((p,i)=> defyBlock(p,i)).join('<div class="rule"></div>')}`;
}
/* 올해의 상담 기록 — 지침 무시 상담 */
function defyRecords(){
  const D = defyState();
  return D.log.filter(d=> (d.year|0)===(S.year|0)).slice().reverse().map(d=>{
    const P = PERSONA[d.pers] || PERSONA.plain;
    return `<div class="opt" style="cursor:default;border-color:${d.ok?"var(--ok)":"var(--bad)"}">
      <div class="on">${esc(d.name)} <span class="tag" style="color:var(--brass);border-color:var(--brass)">${P.n}</span>
        <span class="price">${PHASES[d.phase]?PHASES[d.phase].n:""} ${d.week}주</span></div>
      <div class="od" style="color:var(--bad)">지침 무시 — ${actName(d.from)} 대신 ${actName(d.to)}</div>
      <div class="od">“${esc(d.reply)}”</div>
      <div class="od" style="color:var(--${d.ok?"ok":"dim"})">${esc(d.react)}</div>
      ${d.byLead? `<div class="od" style="color:var(--brass)">성격에 맞는 말은 아니었지만, 지도력으로 설득했다</div>`:""}
      ${(d.gain || d.cond)? `<div class="od" style="color:var(--brass)">${d.gain? `${d.gain.n} +${d.gain.d}${d.dbl? ` <span style="color:var(--ok)">— 호소력으로 상승폭 2배</span>`:""}` : ""}${d.gain && d.cond? " · " : ""}${d.cond? `컨디션 +${d.cond}`:""}</div>`:""}
      <div class="od" style="color:var(--dim)">신뢰 ${d.ok?"증가":"감소"} · ${d.seasons}계절 동안 지침을 무시하지 않는다</div>
    </div>`;
  }).join("");
}

"""

CSS_CSL = """.defyhead{display:flex;align-items:baseline;gap:10px;flex-wrap:wrap;margin:0 0 12px;padding:8px 12px;border:1px solid var(--bad);border-radius:3px;background:color-mix(in srgb,var(--bad) 8%,transparent)}
.defyhead b{color:var(--bad);font-size:14px}
.defyhead span{font-size:12px;color:var(--muted)}
.cslcard.defycard{border-color:var(--bad);background:color-mix(in srgb,var(--bad) 5%,transparent)}
.defyact{display:flex;align-items:center;gap:6px;flex-wrap:wrap;margin-top:8px;font-size:12.5px}
.defyact span{color:var(--dim)}
.defyact i{font-style:normal;color:var(--dim);margin:0 2px}
.defyact b.bad{color:var(--bad)}
.defyask{margin-top:8px;font-size:13px;line-height:1.7;color:var(--muted)}
.defyask b{color:var(--text);margin-right:6px}
.defynote{font-size:11.5px;color:var(--bad);margin-top:6px;font-weight:600}
.defynote b{color:var(--bad)}
"""
CSS_FIN = """.fin-defy{margin:12px 0 0;color:var(--bad);font-weight:700;font-size:14px;text-align:center;opacity:0;transition:opacity .3s ease}
.fin-defy.on{opacity:1}
"""

OLD_TUT14 = ('    14:{title:"지침을 어긴 학생, 이유부터 들어 봐요",tag:"상담 · 행동 지침",job:"monk",'
         'lead:"1년차 봄 8주차부터, 학생이 그 주의 개인 행동 지침 대신 다른 행동을 할 때가 있어요. 한 주에 한 명까지예요.",visual:"defy",'
         'steps:[["경과 보고에서 확인", "결산 창에 빨간 글씨로 알려 줘요. 지침을 무시한 학생은 그 주에 바꾼 행동의 컨디션 소모가 2배, 회복은 절반이에요."],'
         '["상담 탭에서 이유를 물어요", "학생의 대답을 듣고 세 가지 말 중 하나를 골라요. 상담하지 않고 다음 주를 시작하면 그 학생은 또 지침을 무시해요."],'
         '["성격에 맞는 말을 골라요", `맞는 말이면 멘탈리티 · 컨디션 · 신뢰가 오르고 ${DEFY_FIT_SEASONS}계절 동안, 맞지 않으면 신뢰가 내리고 ${DEFY_MISS_SEASONS}계절 동안 지침을 무시하지 않아요.`]],'
         'tip:"지도력 · 정보력 · 호소력은 고민 상담과 똑같이 작용해요. 신뢰가 운명 단계인 학생은 지침을 무시하지 않아요."}   /* 1008 — 지침을 무시한 학생이 처음 나온 주 끝 */')
OLD_TUT14_VIS = ('    case "defy":return row("등급","D +10% · C +20% · B +30% · A +40% · S +50%","▲")+row("신뢰","타인 +20% · 면식 +10% · 관심 0 · 의지 -10% · 유대 -20% · 운명은 무시하지 않아요","♥")'
             '+row("학원 명성","무명 +20% · 유명 +10% · 강호 0 · 명문 -10% · 초명문 -20%","★")+row("성격","허세 · 천재적 +10% · 성실 -10%","◆")'
             '+row("바꾼 행동","훈련 ↔ 휴식 ↔ 의뢰 — 컨디션 소모 2배 · 회복 절반","!");\n')

TUT14 = ('    14:{title:"지침을 어긴 학생, 이유부터 들어 봐요",tag:"상담 · 행동 지침",job:"monk",'
         'lead:"가끔 학생이 그 주의 개인 행동 지침 대신 다른 행동을 할 때가 있어요.",visual:"defy",'
         'steps:[["경과 보고에서 확인", "결산 창에 빨간 글씨로 알려 줘요. 지침을 무시한 학생은 그 주에 바꾼 행동의 컨디션 소모가 2배, 회복은 절반이에요."],'
         '["상담 탭에서 이유를 물어요", "학생의 대답을 듣고 세 가지 말 중 하나를 골라요. 상담하지 않고 다음 주를 시작하면 그 학생은 또 지침을 무시해요."],'
         '["성격에 맞는 말을 골라요", `맞는 말이면 멘탈리티 · 컨디션 · 신뢰가 오르고 ${DEFY_FIT_SEASONS}계절 동안, 맞지 않으면 신뢰가 내리고 ${DEFY_MISS_SEASONS}계절 동안 지침을 무시하지 않아요.`]],'
         'tip:"지도력 · 정보력 · 호소력은 고민 상담과 똑같이 작용해요."}   /* 1008 — 지침을 무시한 학생이 처음 나온 주 끝 · 확률 · 시작 시점 · 한 주 한 명은 안내에 쓰지 않는다 */')
TUT14_VIS = ('    case "defy":return row("훈련 지침","대신 쉬거나 의뢰를 해요","↑")+row("휴식 지침","대신 훈련하거나 의뢰를 해요","☾")'
             '+row("의뢰 지침","대신 훈련하거나 쉬어요","G")+row("바꾼 행동","컨디션 소모 2배 · 회복 절반","!")'
             '+`<p class="tg-caption">의뢰는 마을 의뢰가 열린 뒤, 여름이 아닐 때만 해요.</p>`;\n')

EDITS = [
    # 실행 — 그날 할 일 · 라이벌 동기 · 컨디션 배율
    ("function dayActOf(st){\n  if(!actUnlocked()) return isInjured(st) ? \"rest\" : \"none\";\n",
     "function dayActOf(st){\n  if(!actUnlocked()) return isInjured(st) ? \"rest\" : \"none\";\n"
     "  { const dv = defyNow(st); if(dv && !isInjured(st)) return dv.to; }   // 1008 — 이번 주 지침을 무시한 학생\n"),
    ("      if(actOf(s)===\"auto\" && actOf(r)===\"auto\" && s._act!==\"rest\"",
     "      if(!defyNow(s) && !defyNow(r) && actOf(s)===\"auto\" && actOf(r)===\"auto\" && s._act!==\"rest\""),
    ("  const m = dayMul || 1, cm = (condMul==null ? m : condMul);\n",
     "  const m = dayMul || 1, cm = (condMul==null ? m : condMul) * defyCostMul(st, \"train\");   // 1008 — 지침을 무시하고 한 훈련은 소모 ×2\n"),
    ("  setCond(st, st.cond - JOB_COND);\n",
     "  setCond(st, st.cond - JOB_COND * defyCostMul(st, \"job\"));          // 1008 — 지침을 무시하고 한 의뢰는 소모 ×2\n"),
    ("  setCond(s, s.cond + Math.max(restFocusGain()*DAY_MUL, restWeekGain(tr)));\n",
     "  setCond(s, s.cond + Math.max(restFocusGain()*DAY_MUL, restWeekGain(tr)) * defyRecMul(s));   // 1008 — 지침을 무시하고 쉰 휴식은 회복 ×1/2\n"),
    # 주 시작 · 끝
    ("  if(isCampWeek()) dlog(`<b>합숙 기간</b> — 이번 주 훈련 효과가 크게 오르지만 컨디션 소모도 크다.`, \"note\");\n  weekRunStep();\n}\n",
     "  if(isCampWeek()) dlog(`<b>합숙 기간</b> — 이번 주 훈련 효과가 크게 오르지만 컨디션 소모도 크다.`, \"note\");\n"
     "  defyWeekStart(UI.wrun);   // 1008 — 이번 주에 지침을 무시할 학생 (한 명까지)\n  weekRunStep();\n}\n"),
    ("  tryCounsel();\n  tryEvolve();\n",
     "  tryCounsel();\n  defyWeekEnd(R);   // 1008 — 지침 무시 상담 이벤트 · 일지 · 첫 안내\n  tryEvolve();\n"),
    # 결산 창
    ("repaid:repayDone(), jobOn:!!R.jobOn0};\n",
     "repaid:repayDone(), jobOn:!!R.jobOn0, defy:!!R.defy};\n"),
    ("${r.base? `${fmt(r.v)} G` : sg(r.v)}</b></div>`).join(\"\")}</div>\n    <div class=\"ji-btn\">",
     "${r.base? `${fmt(r.v)} G` : sg(r.v)}</b></div>`).join(\"\")}</div>\n"
     "    ${fin.defy? `<p class=\"fin-defy\" role=\"alert\">! 행동 지침을 무시한 학생이 발생했습니다.</p>` : \"\"}\n    <div class=\"ji-btn\">"),
    ("    else { ok.disabled = false; ok.focus(); }\n",
     "    else { const dw = el.querySelector(\".fin-defy\"); if(dw) dw.classList.add(\"on\"); ok.disabled = false; ok.focus(); }\n"),
    # 상담 탭 — 배지 · 화면 · 단추
    ("  { const cv = tabs.find(v=>v.id===\"counsel\"); if(cv) cv.badge = counselState().queue.length || null; }\n",
     "  { const cv = tabs.find(v=>v.id===\"counsel\"); if(cv) cv.badge = (counselState().queue.length + defyState().pend.length) || null; }\n"),
    ("    <span class=\"hint\">${yrName(S.year)} · 상담 ${C.done.length}회 진행${q.length? ` · <b style=\"color:var(--brass)\">대기 ${q.length}/${CSL_QUEUE_MAX}건</b>`:\"\"}</span></div>`;\n  let body = \"\";\n  if(q.length){\n    body = `",
     "    <span class=\"hint\">${yrName(S.year)} · 상담 ${C.done.length}회 진행${q.length? ` · <b style=\"color:var(--brass)\">대기 ${q.length}/${CSL_QUEUE_MAX}건</b>`:\"\"}${defyState().pend.length? ` · <b style=\"color:var(--bad)\">지침 무시 ${defyState().pend.length}건</b>`:\"\"}</span></div>`;\n"
     "  let body = defySection();   // 1008 — 지침을 무시한 학생이 맨 위\n  if(q.length){\n    body += `${body? '<div class=\"rule\"></div>' : \"\"}"),
    ("    body = `<div class=\"empty\">지금은 찾아온 학생이 없다. 한 주를 보내면 누군가 문을 두드릴 수 있다.\n</div>",
     "    body += `${body? \"\" : `<div class=\"empty\">지금은 찾아온 학생이 없다. 한 주를 보내면 누군가 문을 두드릴 수 있다.\n</div>`}"),
    ("    ${log.length? `<div class=\"grid2\">${log.map(d=>{\n",
     "    ${(log.length || defyRecords())? `<div class=\"grid2\">${defyRecords()}${log.map(d=>{\n"),
    ("  v.querySelectorAll(\"[data-csl]\").forEach(b=> b.onclick=()=>{\n    const [qi,oi] = b.dataset.csl.split(\"|\").map(Number);\n    answerCounsel(qi, oi);\n  });\n",
     "  v.querySelectorAll(\"[data-csl]\").forEach(b=> b.onclick=()=>{\n    const [qi,oi] = b.dataset.csl.split(\"|\").map(Number);\n    answerCounsel(qi, oi);\n  });\n"
     "  v.querySelectorAll(\"[data-defy]\").forEach(b=> b.onclick=()=>{   // 1008 — 지침 무시 상담\n    const [pi,oi] = b.dataset.defy.split(\"|\").map(Number);\n    answerDefy(pi, oi);\n  });\n"),
    # 컨디션 줄 · 학생 목록 — 상담하지 않은 학생 표시
    ("  const c = ACT_TONE[k] || \"var(--text)\";\n  return ` <span class=\"tag\" style=\"color:${c};border-color:${c}\">${actName(k)}</span>`;\n}\n",
     "  const c = ACT_TONE[k] || \"var(--text)\";\n  return ` <span class=\"tag\" style=\"color:${c};border-color:${c}\">${actName(k)}</span>`"
     " + (defyPend(s)? ` <span class=\"tag\" style=\"color:var(--bad);border-color:var(--bad)\" title=\"상담 탭에서 이야기하지 않으면 이번 주에도 지침을 무시한다\">지침 무시</span>` : \"\");   // 1008\n}\n"),
    # 학생 화면 — 개인 행동 아래에 상담하지 않은 지침 무시
    ("매주 컨디션을 ${restFocusWeek()} 회복한다.</b>`}</div>\n        </div>`}\n",
     "매주 컨디션을 ${restFocusWeek()} 회복한다.</b>`}</div>\n"
     "          ${defyPend(s)? `<div class=\"defynote\">! 개인 행동 지침을 무시했다 — <b>상담</b> 탭에서 이야기하지 않으면 이번 주에도 무시한다.</div>` : \"\"}\n        </div>`}\n"),
    # 튜토리얼 14 — 지침 무시 상담
    ("\n  };return data[k]||data[1];\n", ",\n" + TUT14 + "\n  };return data[k]||data[1];\n"),
    ("    case \"marks\":return ", TUT14_VIS + "    case \"marks\":return "),
    ("\"12\":true, \"13\":true};", "\"12\":true, \"13\":true, \"14\":true};"),
    ("const TUT_LIVE = [\"13\"];", "const TUT_LIVE = [\"13\", \"14\"];"),
    # 스타일
    (".cslopt .on{white-space:normal;line-height:1.55}\n", ".cslopt .on{white-space:normal;line-height:1.55}\n" + CSS_CSL),
    (".fin-row.end{border-bottom:0;font-size:16px;font-weight:700}\n", ".fin-row.end{border-bottom:0;font-size:16px;font-weight:700}\n" + CSS_FIN),
]

ANCHOR_JS = "/* ============================================================\n   시즌 전환\n   ============================================================ */\n"


def sub1(src, old, new):
    n = src.count(old)
    if n != 1:
        raise RuntimeError("자리를 못 찾았다 (%d): %s" % (n, old[:120]))
    return src.replace(old, new)


def apply(src):
    if MARK not in src:
        for old, new in EDITS:
            src = sub1(src, old, new)
        src = sub1(src, ANCHOR_JS, DEFY_JS + ANCHOR_JS)
    # 1008 — 튜토리얼 14 에서 확률 · 시작 시점 · 한 주 한 명을 뺐다. 예전 판으로 넣은 game.html 도 새 문구로 고친다
    for old, new in ((OLD_TUT14, TUT14), (OLD_TUT14_VIS, TUT14_VIS)):
        if old in src:
            src = sub1(src, old, new)
    return src


if __name__ == "__main__":
    path = sys.argv[1]
    raw = open(path, encoding="utf-8", newline="").read()
    crlf = "\r\n" in raw
    src = apply(raw.replace("\r\n", "\n"))
    if crlf:
        src = src.replace("\n", "\r\n")
    open(path, "w", encoding="utf-8", newline="").write(src)
    print("applied", len(raw), "->", len(src), "chars", "· crlf" if crlf else "")
