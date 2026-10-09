/* ROSTERBK_START — 학생 명부 책 (1009 · apply_roster.py) ─ 가로 넓은 화면(townMode)에서 책상의 펼친 책 · 메뉴의 '학생 명부' · '팀 편성'을 누르면 뜨는 책 팝업.
   mockups/student-roster 목업을 게임에 옮겼다. 세로 · 좁은 화면은 예전 학생 명부 · 팀 편성 화면 그대로.
   · 책의 모양(CSS) · 뼈대(HTML)는 목업 원본(roster_tpl.html 의 CORE_CSS · CORE_HTML)을 apply_roster 가 그대로 가져와 넣는다 — 이 파일은 그 위에서 도는 게임 쪽 코드
   · 그림자 DOM(#rbHost) 안에 그린다 — 게임 CSS(.tag · .slot · 도트 테마의 button 등)와 책 CSS 가 서로 섞이지 않게. 글꼴은 게임의 @font-face 를 그대로 쓴다
   · 왼쪽 쪽: 학생 목록(정렬을 따라가는 꼬리표 · S.opts.rbsort) / 오른쪽 쪽: 학생 상세 또는 팀 편성(명부 머리의 '팀 편성'으로 바꾼다)
   · 게임에 바로 반영 — 팀 편성은 S.teams 를 게임 함수(teamAssign · autoFillAllTeams · formOf …)로, 이름 변경 ✎ · 스킬 강화 · 스킬 임의로 강화(정렬 옆)는 게임 팝업, 유물 해제는 보관함으로.
     신뢰 한마디 · 훈련 성공률 · 부상 · 개인 행동은 넣지 않았다 (사용자 요청)
   · 배치(art/roster_layout.json — 학생 명부 배치판)는 RB_LAYOUT 으로 들어간다. 책은 창 크기에 맞춰 통째로 줄인다(1배까지)
   · 닫기: × · Esc · 책 바깥 누르기. 닫으면 게임 화면을 다시 그린다 */
const ROSTER_ART = __ROSTER_ART__;
(() => {
const RB_LAYOUT_SRC = __RB_LAYOUT__;
const RB_CSS = __RB_CSS__;
const RB_HTML = __RB_HTML__;
const RB = {host: null, root: null, open: false, mode: "detail", sel: null, sk: 0, rt: "rec", team: "A", slot: null,
  back: "home", want: false, vm: new Map(), wired: false, mq: false, ovf: ""};
const $ = id => RB.root ? RB.root.getElementById(id) : null;
const $$ = sel => RB.root ? [...RB.root.querySelectorAll(sel)] : [];
const h = s => String(s == null ? "" : s).replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const ROW_N = {front: "전열", back: "후열"};
const MK6 = MENTAL.filter(m => !m.fixed);                 // 잠재력은 보여 주지 않는다
/* 육각형 꼭짓점 차례 — 팀워크(12시)부터 시계 방향으로 지구력 · 적극성 · 천재성 · 정신력 · 침착성 (1009 사용자 요청 · MENTAL 차례와 다르다). 표에 없는 멘탈리티는 뒤에 */
const HEX_ORDER = ["team", "stam", "aggr", "genius", "will", "calm"];
const HEX6 = HEX_ORDER.map(k => MK6.find(m => m.k === k)).filter(Boolean).concat(MK6.filter(m => !HEX_ORDER.includes(m.k)));
/* 정렬 — 게임의 ROSTER_SORT 기준 + 레벨 (기본은 학년). 꼬리표(tag)는 정렬을 따라간다 */
const RB_SORT = [
  {k:"year",  n:"학년",      tag:"year"},
  {k:"team",  n:"소속 팀",   tag:"team"},
  {k:"level", n:"레벨",      tag:"level"},
  {k:"power", n:"전투력",    tag:"power"},
  {k:"eval",  n:"진로 평가", tag:null},
  {k:"cond",  n:"컨디션",    tag:null},
  {k:"name",  n:"이름",      tag:null}
];
function sortKey(){ const k = (S.opts && S.opts.rbsort) || "year"; return RB_SORT.some(o => o.k === k) ? k : "year"; }

/* ── 배치 (art/roster_layout.json) — 목업 · 배치판과 같은 항목 · 같은 범위 ── */
const LAYOUT_ITEMS = ["lring:100:64:140", "ltag", "lepi", "lname", "dring:108:72:168", "dname", "dtags", "bub", "xbtn", "sort", "tbtn", "spbtn", "ebtn", "rtabs", "ribbon"]
  .map(s => { const [id, a, b, c] = s.split(":"); return a ? {id, size: [+a, +b, +c]} : {id}; });
const MOVE_MAX = 600, FACE_DEF = {scale: 1.04, x: 0, y: 2}, FACE_RANGE = {scale: [0.6, 1.8], xy: [-40, 40]};
const clampNum = (v, d, lo, hi) => { v = +v; return Number.isFinite(v) ? Math.min(hi, Math.max(lo, v)) : d; };
const LAYOUT = (() => {
  const L = RB_LAYOUT_SRC || {}, items = {}, jobs = {};
  for(const it of LAYOUT_ITEMS){
    const s = (L.items || {})[it.id] || {};
    items[it.id] = {x: Math.round(clampNum(s.x, 0, -MOVE_MAX, MOVE_MAX)), y: Math.round(clampNum(s.y, 0, -MOVE_MAX, MOVE_MAX))};
    if(it.size) items[it.id].size = Math.round(clampNum(s.size, it.size[0], it.size[1], it.size[2]));
  }
  for(const [j, s] of Object.entries((L.face || {}).jobs || {})){
    jobs[j] = {scale: Math.round(clampNum(s.scale, FACE_DEF.scale, ...FACE_RANGE.scale) * 100) / 100,
      x: Math.round(clampNum(s.x, FACE_DEF.x, ...FACE_RANGE.xy) * 2) / 2, y: Math.round(clampNum(s.y, FACE_DEF.y, ...FACE_RANGE.xy) * 2) / 2};
  }
  return {items, jobs};
})();
function faceVars(job){ const f = LAYOUT.jobs[job] || FACE_DEF; return `--fs:${f.scale};--fx:${f.x}%;--fy:${f.y}%`; }
function applyLayout(){
  const b = $("book");
  if(!b) return;
  for(const it of LAYOUT_ITEMS){
    const v = LAYOUT.items[it.id];
    b.style.setProperty(`--${it.id}-x`, v.x + "px"); b.style.setProperty(`--${it.id}-y`, v.y + "px");
    if(it.size) b.style.setProperty(`--${it.id}-s`, v.size + "px");
  }
}

/* ── 도트 그림 — 문자열 비트맵 → SVG (1칸 = 2px), 테두리 한 칸은 line 색 ── */
function dots(rows, fill, line){
  const hh = rows.length, w = rows[0].length, out = [];
  const at = (x, y) => y >= 0 && y < hh && x >= 0 && x < w && rows[y][x] === "#";
  for(let y = -1; y <= hh; y++) for(let x = -1; x <= w; x++){
    if(at(x, y)) out.push(`<rect x="${x+1}" y="${y+1}" width="1" height="1" fill="${fill}"/>`);
    else if(line && (at(x-1,y)||at(x+1,y)||at(x,y-1)||at(x,y+1))) out.push(`<rect x="${x+1}" y="${y+1}" width="1" height="1" fill="${line}"/>`);
  }
  return `<svg class="mkr" width="${(w+2)*2}" height="${(hh+2)*2}" viewBox="0 0 ${w+2} ${hh+2}" shape-rendering="crispEdges" aria-hidden="true">${out.join("")}</svg>`;
}
const BM = {
  up:   ["...#...","..###..",".#####.","#######","..###..","..###.."],
  dn:   ["..###..","..###..","#######",".#####.","..###..","...#..."],
  dot:  [".####.","######","######","######","######",".####."],
  heart:[".##.##.","#######","#######",".#####.","..###..","...#..."],
  lock: ["..###..",".#...#.",".#...#.","#######","###.###","###.###","#######"],
  sUp:  ["..#..",".###.","#####",".###."],                 // 육각형 꼭짓점의 작은 표식 (막대 1칸)
  sDn:  [".###.","#####",".###.","..#.."],
  sNo:  [".##.","####","####",".##."],
  flag: ["#.....","######","#####.","######","#.....","#....."],
  caret:["#####",".###.","..#.."],
  plus: ["..#..","..#..","#####","..#..","..#.."],
  x:    ["#...#",".#.#.","..#..",".#.#.","#...#"],
  check:["......#",".....##","#...##.","##.##..",".###...","..#...."],
  pen:  ["....##","...#.#","..#.#.",".#.#..","##.#..","###..."]
};
const MC = {up: ["#e8483a", "#6a1810"], dn: ["#3a82d8", "#102e5c"], no: ["#ffffff", "#8a6a45"]};
const MARK = {up: dots(BM.up, MC.up[0], MC.up[1]), dn: dots(BM.dn, MC.dn[0], MC.dn[1]), no: dots(BM.dot, MC.no[0], MC.no[1])};
const ICO = {flag: dots(BM.flag, "currentColor"), caret: dots(BM.caret, "currentColor"), plus: dots(BM.plus, "#c4ac84"),
  x: dots(BM.x, "currentColor"), check: dots(BM.check, "#8a6a15"), lock: dots(BM.lock, "#d6c09a", "#b29c78"), pen: dots(BM.pen, "#45321f")};
const GC_PAGE = {D:"#82849a",C:"#5b5d72",B:"#3c6e9e",A:"#6d4ba8",S:"#8a6a15","S+":"#2a9d74",EX:"#b02e6b",E:"#9a9cae",F:"#b0b2c0"};
const ROLE_TONE = {tank:"tank", dps:"dps", heal:"heal", supp:"supp"};

/* ── 학생 → 책에 보일 값 (목업의 견본 JSON 과 같은 모양 — sample_roster.py 와 같은 게임 함수로) ── */
function vmOf(st){
  const J = JOBS[st.job] || {}, P = personaOf(st), tv = trustOf(st), tb = trustBand(tv);
  const cf = careerFor(st), dk = darkCareerFor(st), nx = nextCareer(cf.sc), nd = nextDark(st);
  const slots = relicSlots(st), pj = passiveJobOf(st), pas = passiveOf(pj);
  return {
    id: st.id, name: st.name, epithet: st.epithet || null,
    job: st.job, jobName: J.name || st.job, role: J.role || "dps", roleLabel: ROLE_LABEL[J.role] || "", sub: J.sub || "", jobDesc: J.desc || "",
    year: st.year, grade: st.grade, level: st.level || 1,
    pers: {k: st.pers || "plain", n: P.n, d: P.d, m: P.m || {}},
    ment: Object.fromEntries(MK6.map(m => [m.k, Math.round((st.ment && st.ment[m.k]) || 0)])),
    greet: greetLine(st),
    trust: {v: tv, step: tb.step, rel: tb.rel},
    fame: Math.round(st.fame || 0), fameBonus: Math.round(fameGoldBonus(st) * 100),
    karma: karmaOf(st), karmaNext: nd ? {n: nd.n, need: nd.karma - karmaOf(st)} : null,
    eval: cf.sc, career: {n: cf.c.n, d: cf.c.d, dark: !!dk},
    nextCareer: (!dk && nx) ? {n: nx.n, need: nx.min - cf.sc} : null,
    note: st.note || "",
    relicSlots: slots,
    relics: Array.from({length: slots}, (_, i) => {
      const r = (st.relics || [])[i];
      return r ? {name: r.name, grade: r.grade, score: relicScore(r), aff: affSorted(r.aff).map(a => ({n: a.n, v: "+" + affValTxt(a.v)}))} : null;
    }),
    passive: pas ? {n: pas.n, d: pas.d, grade: skGrade(st, "passive"), lv: skLevel(st, "passive"), icon: SKILL_ICON_PASSIVE[pj] || ""} : null,
    skills: skillsOf(st).map(sk => ({
      id: sk.id, name: sk.name, kind: sk.kind || "skill",
      kindLabel: sk.kind === "basic" ? "일반 공격" : sk.kind === "ult" ? "필살기" : "스킬",
      txt: sk.txt, grade: skGrade(st, sk.id), lv: skLevel(st, sk.id), icon: SKILL_ICON_ART[sk.id] || "",
      pow: Math.round(skPow(st, sk) * 100), target: targetLabel(sk.target), dur: skDur(st, sk),
      proc: sk.kind ? null : +(skProc(st, sk, st.ment.genius) * 100).toFixed(1)
    })),
    cond: Math.round(st.cond), eff: effPct(st), condTone: condEff(st.cond).tone, power: Math.round(power(st)), sp: st.sp || 0,
    battle: (bs => BATTLE.map(b => { const v = bs[b.k] || 0;
      return {n: b.n, v: b.p === 1 ? (b.k === "critDmg" ? (v * 100).toFixed(0) + "%" : (v * 100).toFixed(1) + "%") : b.p === 2 ? "×" + v.toFixed(2) : fmt(v)}; }))(battleStats(st)),
    cons: Math.round(consThr(st.ment.stam)), willCut: Math.round((1 - clamp(1 - st.ment.will / 100 * .7, .3, 1)) * 100)
  };
}
function buildVM(){ RB.vm = new Map(S.students.map(st => [st.id, vmOf(st)])); }
function students(){ return S.students.map(st => RB.vm.get(st.id)).filter(Boolean); }
function stuById(id){ return RB.vm.get(id) || null; }
function rawById(id){ return S.students.find(s => s.id === id) || null; }

function persMark(st, k){ const v = (st.pers.m || {})[k] || 0; return v > 0 ? "up" : v < 0 ? "dn" : "no"; }
function faceHTML(st, ed){ return `<span class="ring"${ed ? ` data-ed="${ed}"` : ""} data-job="${h(st.job)}"><span class="face"><img src="${h(FACE_IMG[st.job] || "")}" alt="" draggable="false" style="${faceVars(st.job)}"></span></span>`; }
function teamTagB(st, cls){
  const at = teamOfStudent(st.id);
  return at ? `<span class="tag tm ${cls||""}" title="${h(formOf(at.t.form).n)} · ${ROW_N[slotRow(at.slot)]}">${h(teamLabel(at.t))}</span>` : `<span class="tag tm none ${cls||""}">무소속</span>`;
}
function gradeTag(g){ return `<span class="tag g-${h(g)}">${h(g)}</span>`; }

/* ── 정렬 (게임의 sortRoster 와 같은 기준 + 레벨) ── */
function sorted(list){
  const L = list.slice(), m = sortKey();
  if(m === "team") return L.sort((a, b) => { const ka = teamSortKey(a), kb = teamSortKey(b); return ka[0] - kb[0] || ka[1] - kb[1] || b.year - a.year || b.power - a.power; });
  if(m === "level") return L.sort((a, b) => b.level - a.level || b.power - a.power);
  if(m === "power") return L.sort((a, b) => b.power - a.power);
  if(m === "eval") return L.sort((a, b) => b.eval - a.eval || b.power - a.power);
  if(m === "cond") return L.sort((a, b) => a.cond - b.cond || b.power - a.power);
  if(m === "name") return L.sort((a, b) => a.name.localeCompare(b.name, "ko"));
  return L.sort((a, b) => b.year - a.year || b.power - a.power);       // 학년 — 높은 학년부터, 같으면 전투력
}
/* 원 아래 꼬리표 — 지금 정렬의 기준 값. 팀 편성 모드에서는 정렬과 상관없이 소속 팀 고르기 */
function teamSetTag(st){
  const at = teamOfStudent(st.id), cur = at && at.t.n === RB.team;
  const txt = at ? `${teamLabel(at.t)} · ${ROW_N[slotRow(at.slot)]}` : "무소속";
  return `<span class="tag tm lt tset${at ? "" : " none"}${cur ? " cur" : ""}" data-ed="ltag" data-tset="${h(st.id)}" role="button" tabindex="0" aria-haspopup="menu"
    title="소속 팀 정하기 — ${h(txt)}"><span class="tx">${h(txt)}</span>${ICO.caret}</span>`;
}
function listTag(st){
  if(RB.mode === "team") return teamSetTag(st);
  const t = (RB_SORT.find(o => o.k === sortKey()) || {}).tag, ed = ' data-ed="ltag"';
  if(t === "team") return teamTagB(st, "lt").replace("<span ", `<span${ed} `);
  if(t === "year") return `<span class="tag tm lt"${ed}>${st.year}학년</span>`;
  if(t === "level") return `<span class="tag tm lt num"${ed}>Lv.${st.level}</span>`;
  if(t === "power") return `<span class="tag tm lt num"${ed} title="전투력">${st.power.toLocaleString()}</span>`;
  return "";
}

/* ── 왼쪽 쪽 — 학생 목록 ── */
function renderList(){
  cleanTeams();
  const L = sorted(students()), tm = RB.mode === "team";
  const into = tm ? teamLabel(teamByName(RB.team)) + (RB.slot ? " " + ROW_N[slotRow(RB.slot.split("|")[1])] + " 자리" : "") : "";
  $("grid").innerHTML = L.length ? L.map(st => {
    const at = tm ? teamOfStudent(st.id) : null;
    const cls = tm ? (at ? (at.t.n === RB.team ? " cur" : " oth") : "") : (st.id === RB.sel ? " on" : "");
    const aria = tm ? ` title="${h(st.name)} — 누르면 ${h(into)}에 넣는다 · 끌어서 자리에 놓을 수도 있다"` : ` aria-pressed="${st.id === RB.sel}"`;
    return `<button class="cell${cls}" data-sid="${h(st.id)}"${aria}>
      <span class="epi" data-ed="lepi">${st.epithet ? "“" + h(st.epithet) + "”" : ""}</span>
      ${faceHTML(st, "lring")}${listTag(st)}
      <span class="nm" data-ed="lname">${h(st.name)}</span></button>`;
  }).join("") : `<p style="grid-column:1/-1;margin:20px 0;color:var(--ink3);text-align:center">학생이 없다.</p>`;
  $("tbtn").title = `재학생 ${L.length}명 — ${tm ? "누르면 학생 상세로 돌아간다" : "누르면 오른쪽 쪽에서 팀 · 진형 · 배치를 짠다"}`;
  spBtn();
}
/* 스킬 임의로 강화 — 강화 포인트가 남은 학생이 있을 때만 정렬 옆에 (예전 학생 명부 머리의 단추와 같다 — spReady · spTotal) */
function spBtn(){
  const b = $("spbtn");
  if(!b) return;
  const ready = spReady(), tot = spTotal();
  b.hidden = !ready.length;
  b.innerHTML = `<span>스킬 임의로 강화</span><b class="spn num">${tot}</b>`;
  b.title = `강화 포인트가 남은 ${ready.length}명이 포인트 ${tot}점을 모두 쓴다 — 학생마다 세 제안 중 가장 높은 강화 등급으로 (먼저 확인 창)`;
}

/* ── 팀 편성 — 게임의 S.teams 를 게임 함수로 (teamsOf · teamAssign · autoFillAllTeams · formOf — 진형 강화의 서 ·改 도 그대로) ── */
function autoByPower(t){                                 // 게임의 '전투력 순으로 자동 편성'과 같다 — 이 팀을 비우고, 다른 팀에 없는 학생을 전투력 순으로
  const taken = new Set();
  teamsOf().forEach(x => { if(x.n !== t.n) formSlots(x.form).forEach(k => { if(x.slots[k]) taken.add(x.slots[k]); }); });
  const pool = S.students.filter(x => !taken.has(x.id)).sort((a, b) => power(b) - power(a));
  t.slots = {};
  formSlots(t.form).forEach((k, i) => { if(pool[i]) t.slots[k] = pool[i].id; });
}
function setForm(t, k){                                  // 진형을 바꾸면 있던 학생을 차례대로 새 자리에 (게임과 같다)
  if(t.form === k) return;
  const keep = teamMembers(t).map(x => x.id);
  t.form = k; t.slots = {};
  formSlots(k).forEach((s, i) => { if(keep[i]) t.slots[s] = keep[i]; });
}
/* 진형 작은 그림 — 앞줄(전열) 위 · 뒷줄(후열) 아래, 쓰는 자리만 잉크로 칠한다 (1칸 = 2px) */
function formMini(F){
  const cw = 6, chh = 4, out = [];
  ["f", "b"].forEach((r, ri) => [1, 2, 3].forEach((c, ci) => {
    const id = r + c, on = (r === "f" ? F.front : F.back).includes(id), x = ci * (cw + 1), y = ri * (chh + 1);
    out.push(on ? `<rect x="${x}" y="${y}" width="${cw}" height="${chh}" fill="${r === "f" ? "#654a30" : "#b08a52"}"/>`
                : `<rect x="${x + .5}" y="${y + .5}" width="${cw - 1}" height="${chh - 1}" fill="none" stroke="#d6c09a" stroke-width="1"/>`);
  }));
  const W = cw * 3 + 2, H = chh * 2 + 1;
  return `<svg class="fmini" width="${W * 2}" height="${H * 2}" viewBox="0 0 ${W} ${H}" shape-rendering="crispEdges" aria-hidden="true">${out.join("")}</svg>`;
}
function foHTML(k, on){
  const F = formOf(k);
  return `<button class="fo${on ? " on" : ""}" data-form="${h(k)}" aria-pressed="${on}" title="${h(F.n)} — ${h(F.d)}">
    <span class="fh">${formMini(F)}<span class="fnm">${h(F.n)}</span><span class="fsh num">${h(F.sh)}</span>${on ? `<span class="fck">${ICO.check}</span>` : ""}</span>
    <span class="fx">${F.txt.map(x => `<span>${h(x)}</span>`).join("")}</span></button>`;
}
function slotHTML(t, k, used, sel){
  if(!used) return `<div class="fs off"><span class="fe">사용 안 함</span></div>`;
  const key = `${t.n}|${k}`, st = t.slots[k] && stuById(t.slots[k]), row = ROW_N[slotRow(k)];
  if(!st){
    const want = (FORM_ROLES[t.form] || {})[k] || [];
    return `<div class="fs empty${sel ? " on" : ""}" data-slot="${key}" role="button" tabindex="0" aria-pressed="${sel}" title="${row} 빈 자리 — 눌러서 고른 뒤 명부의 학생을 누른다">
      ${ICO.plus}<span class="fe">빈 자리</span>${want.length ? `<span class="fw">알맞은 역할<br><b>${want.map(r => `<span class="c-${ROLE_TONE[r]}">${ROLE_LABEL[r]}</span>`).join(" · ")}</b></span>` : ""}</div>`;
  }
  return `<div class="fs fill${sel ? " on" : ""}" data-slot="${key}" role="button" tabindex="0" aria-pressed="${sel}" title="${st.epithet ? "“" + h(st.epithet) + "” " : ""}${h(st.name)} — ${row} · 끌어서 옮기거나 명부로 끌어내면 뺀다">
    <button class="x" data-unslot="${key}" aria-label="${h(st.name)} 빼기" title="팀에서 빼기">${ICO.x}</button>
    ${faceHTML(st, "")}
    <span class="fn"><span class="nm">${h(st.name)}</span>${gradeTag(st.grade)}</span>
    <span class="ft"><span class="tag r-${ROLE_TONE[st.role]}">${h(st.jobName)}</span><span class="tag lv num">Lv.${st.level}</span></span>
    <span class="fp">전투력<b class="num">${st.power.toLocaleString()}</b></span>
    <span class="fc">컨디션<b class="num c-${st.condTone}">${st.cond}</b></span></div>`;
}
function renderTeam(){
  const box = $("tmw");
  if(!box) return;
  cleanTeams();
  const ts = teamsOf(), cur = teamByName(RB.team);
  RB.team = cur.n;
  const slots = formSlots(cur.form), mem = teamMembers(cur);
  const sel = RB.slot && RB.slot.startsWith(cur.n + "|") && slots.includes(RB.slot.split("|")[1]) ? RB.slot.split("|")[1] : null;
  if(!sel) RB.slot = null;
  const full = mem.length >= TEAM_MIN, pw = mem.reduce((a, s) => a + Math.round(power(s)), 0);
  const all = allTeams();
  const tabs = TEAM_NAMES.map((n, i) => {
    if(i >= ts.length) return `<span class="tt lock" title="학생이 ${(i + 1) * 3}명이 되면 열린다">${ICO.lock}팀 ${h(n)}</span>`;
    const t = all[i], m = teamMembers(t).length, c = formSlots(t.form).length, on = t.n === cur.n;
    return `<button class="tt${on ? " on" : ""}" data-team="${h(t.n)}" role="tab" aria-selected="${on}" title="${h(formOf(t.form).n)} · ${m}/${c}">${h(teamLabel(t))}<span class="tc num${m >= TEAM_MIN ? " ok" : ""}">${m}/${c}</span></button>`;
  }).join("");
  const row = r => `<div class="frow"><span class="frl">${ROW_N[r]}</span>${[1, 2, 3].map(c => { const k = (r === "front" ? "f" : "b") + c; return slotHTML(cur, k, slots.includes(k), sel === k); }).join("")}</div>`;
  const hint = sel ? `<b>${h(teamLabel(cur))} ${ROW_N[slotRow(sel)]}</b> 자리 — 명부의 학생을 클릭하면 이 자리에 배치` : `명부의 학생을 클릭/드래그로 배치`;
  box.innerHTML = `<div class="ph"><h2 title="출전은 ${TEAM_MIN}명부터 · 학생 3명마다 팀 하나">팀 편성</h2></div>
    <div class="rule"></div>
    <div class="card tmc">
      <div class="ttabs" role="tablist" aria-label="팀">${tabs}</div>
      <span class="pw" title="${h(teamLabel(cur))} 학생 전투력의 합">총 전투력<b>${pw.toLocaleString()}</b></span>
      <div class="th"><b>진형</b></div>
      <div class="fos">${FORM_KEYS.map(k => foHTML(k, k === cur.form)).join("")}</div>
      <div class="th"><b>배치 — ${h(teamLabel(cur))}</b><span class="st ${full ? "c-ok" : "c-dim"}">${full ? `편성 완료 (${mem.length}/${slots.length})` : `${mem.length}/${slots.length} · 최소 ${TEAM_MIN}명`}</span></div>
      <div class="fld">${row("front")}${row("back")}</div>
    </div>
    <div class="tmbar">
      <button class="pbtn pri" data-act="role" title="모든 팀의 빈 자리에, 아직 팀이 없는 학생을 진형이 원하는 역할대로 넣는다 (맞는 역할이 없으면 전투력 순)">진형에 맞춰 임의 편성</button>
      <button class="pbtn" data-act="power" title="${h(teamLabel(cur))}을(를) 비우고, 다른 팀에 없는 학생을 전투력 높은 순으로 채운다">전투력 순으로 자동 편성</button>
      <button class="pbtn" data-act="clear"${mem.length ? "" : " disabled"}>비우기</button>
    </div>
    <p class="tmhint">${hint}</p>`;
}
/* 팀이 바뀌면 — 저장 · 오른쪽 쪽 · 왼쪽 꼬리표를 다시 그리고, 키보드로 누르던 것에 다시 초점 · 넣은 자리는 잠깐 빛낸다 */
function refreshTeam(flash, changed){
  if(changed) save();
  const a = RB.root.activeElement, box = $("tmw");
  const keep = a && box.contains(a) ? ["data-team", "data-form", "data-act", "data-slot"].map(k => a.getAttribute(k) != null ? `[${k}="${a.getAttribute(k)}"]` : null).find(Boolean) : null;
  if(changed) buildVM();
  if(RB.mode === "team") renderTeam();
  renderList();
  if(keep){ const el = box.querySelector(keep); if(el) el.focus({preventScroll: true}); }
  if(flash){ const el = box.querySelector(`.fs[data-slot="${flash}"]`); if(el){ el.classList.remove("flash"); void el.offsetWidth; el.classList.add("flash"); } }
}
function setRosterMode(m){
  m = m === "team" ? "team" : "detail";
  if(RB.mode === m) return;
  RB.mode = m; RB.slot = null; closeSlip();
  showMode();
  const show = m === "team" ? $("tmw") : $("det");
  show.classList.add("turn");
  if(m === "team") renderTeam(); else renderDetail(false);
  renderList();
  requestAnimationFrame(() => requestAnimationFrame(() => show.classList.remove("turn")));
}
function showMode(){
  const tm = RB.mode === "team";
  $("book").classList.toggle("teammode", tm);
  $("tbtn").setAttribute("aria-pressed", String(tm));
  $("det").hidden = tm; $("tmw").hidden = !tm;
}
function renderRight(){ if(RB.mode === "team") renderTeam(); else renderDetail(false); }
/* 명부의 학생을 누르면 — 고른 자리, 없으면 지금 팀의 첫 빈 자리 */
function placeFromList(id){
  const st = stuById(id), t0 = teamByName(RB.team);
  if(!st) return;
  let slot = RB.slot;
  if(!slot){
    const at = teamOfStudent(id);
    if(at && at.t.n === t0.n){ toast(`${st.name} — 이미 ${teamLabel(t0)} ${ROW_N[slotRow(at.slot)]}에 있다 (빼려면 × 또는 꼬리표)`); return; }
    const empty = formSlots(t0.form).find(k => !t0.slots[k]);
    if(!empty){ toast(`${teamLabel(t0)} — 빈 자리가 없다. 자리를 먼저 고르거나 학생을 자리로 끌어다 놓는다`); return; }
    slot = `${t0.n}|${empty}`;
  }
  const [tn, k] = slot.split("|");
  teamAssign(tn, k, id); RB.slot = null;
  refreshTeam(slot, true);
}
function teamAct(act){
  const cur = teamByName(RB.team);
  if(act === "role"){
    const res = autoFillAllTeams();
    if(!res.length){ toast("빈 자리가 없거나 넣을 학생이 없다."); return; }
    const n = res.reduce((a, x) => a + x.filled.length, 0);
    logE(`팀 편성 — 진형에 맞춰 ${n}명을 배치했다 (${res.map(x => `${teamLabel(x.t)} ${x.filled.length}명`).join(" · ")})`, "good");
    RB.slot = null; refreshTeam(null, true);
    toast(`진형에 맞춰 ${n}명을 넣었다 — ${res.map(x => `${teamLabel(x.t)} ${x.filled.length}명`).join(" · ")}`);
    return;
  }
  if(act === "power"){ autoByPower(cur); RB.slot = null; refreshTeam(null, true); toast(`${teamLabel(cur)} 자동 편성`); return; }
  if(act === "clear"){ cur.slots = {}; RB.slot = null; refreshTeam(null, true); toast(`${teamLabel(cur)} — 비웠다`); }
}

/* ── 쪽지 (책 위에 뜨는 작은 종이) — 소속 팀 고르기 ── */
let SLIP = null;
function bookBox(el){ const bk = $("book"), b = bk.getBoundingClientRect(), r = el.getBoundingClientRect(), s = b.width / bk.offsetWidth || 1; return {x: (r.left - b.left) / s, y: (r.top - b.top) / s, w: r.width / s, h: r.height / s}; }
function closeSlip(back){
  if(!SLIP) return;
  const a = SLIP.anchor;
  SLIP.el.remove(); SLIP = null;
  if(a){ a.classList.remove("open"); a.removeAttribute("aria-expanded"); if(back && a.isConnected) a.focus({preventScroll: true}); }
}
function openSlip(anchor, html, opt){
  closeSlip();
  const bk = $("book"), el = document.createElement("div");
  el.className = "slip"; el.setAttribute("role", (opt && opt.role) || "menu"); el.innerHTML = html;
  bk.append(el);
  const a = bookBox(anchor), W = el.offsetWidth, H = el.offsetHeight, BOT = 880;      // 책장 아래 끝 (끈 자리 위)
  const x = Math.max(8, Math.min(bk.offsetWidth - W - 8, Math.round(a.x + a.w / 2 - W / 2)));
  const above = (opt && opt.above) || a.y + a.h + 6 + H > BOT;
  const y = Math.max(8, Math.round(above ? a.y - H - 6 : a.y + a.h + 6));
  el.style.left = x + "px"; el.style.top = y + "px";
  anchor.classList.add("open"); anchor.setAttribute("aria-expanded", "true");
  SLIP = {el, anchor};
  el.addEventListener("keydown", e => {                    // 위 · 아래로 고르기, Tab 은 쪽지 안에서만
    const its = [...el.querySelectorAll("button:not(:disabled), input")], i = its.indexOf(RB.root.activeElement);
    if(!its.length) return;
    if(e.key === "ArrowDown" || e.key === "ArrowUp"){ if(e.target.tagName === "INPUT") return; e.preventDefault(); its[(i + (e.key === "ArrowDown" ? 1 : its.length - 1)) % its.length].focus(); }
    else if(e.key === "Tab"){ e.preventDefault(); its[(i + (e.shiftKey ? its.length - 1 : 1)) % its.length].focus(); }
  });
  const f = el.querySelector("input, .so.on:not(:disabled), button:not(:disabled)");
  if(f) f.focus({preventScroll: true});
  return el;
}
function openTeamPicker(tag){
  if(SLIP && SLIP.anchor === tag){ closeSlip(true); return; }
  const id = tag.dataset.tset, st = stuById(id), at = teamOfStudent(id), ts = teamsOf(), all = allTeams();
  if(!st) return;
  const rows = TEAM_NAMES.map((n, i) => {
    if(i >= ts.length) return `<button class="so" disabled><i class="sp0"></i><span>팀 ${h(n)}</span><span class="sd">학생 ${(i + 1) * 3}명부터</span></button>`;
    const t = all[i], m = teamMembers(t).length, c = formSlots(t.form).length, mine = !!(at && at.t.n === t.n), full = m >= c && !mine;
    if(!full) return `<button class="so${mine ? " on" : ""}" data-pick="${h(t.n)}" role="menuitemradio" aria-checked="${mine}">${mine ? ICO.check : `<i class="sp0"></i>`}<span>${h(teamLabel(t))}</span><span class="sd">${h(formOf(t.form).n)} · ${m}/${c}${mine ? " · 지금" : ""}</span></button>`;
    /* 자리가 다 찬 팀 — 바꿀 학생을 고르면 그 자리에 들어간다 (있던 학생은 무소속) */
    const sw = formSlots(t.form).filter(k => t.slots[k]).map(k => { const o = stuById(t.slots[k]); if(!o) return "";
      return `<button class="sw" data-swap="${h(t.n)}|${k}" title="${h(o.name)} 대신 넣는다 — 그 학생은 무소속이 된다">${h(o.name)}<i>${ROW_N[slotRow(k)]}</i></button>`; }).join("");
    return `<div class="sog"><div class="so dis"><i class="sp0"></i><span>${h(teamLabel(t))}</span><span class="sd">${h(formOf(t.form).n)} · ${m}/${c} · 바꿀 학생</span></div><div class="sws">${sw}</div></div>`;
  });
  rows.push(`<button class="so${at ? "" : " on"}" data-pick="" role="menuitemradio" aria-checked="${!at}">${at ? `<i class="sp0"></i>` : ICO.check}<span>무소속</span><span class="sd">${at ? "팀에서 뺀다" : "지금"}</span></button>`);
  const el = openSlip(tag, `<div class="slip-h">${h(st.name)} — 소속 팀</div>${rows.join("")}`, {});
  el.addEventListener("click", e => {
    const w = e.target.closest("[data-swap]");
    if(w){
      const [tn, k] = w.dataset.swap.split("|"), t = teamByName(tn), o = stuById(t.slots[k]);
      closeSlip(true);
      teamAssign(tn, k, id); RB.team = tn; RB.slot = null;
      refreshTeam(`${tn}|${k}`, true);
      toast(`${st.name} → ${teamLabel(t)} ${ROW_N[slotRow(k)]}${o ? ` (${o.name} — 무소속)` : ""}`);
      return;
    }
    const b = e.target.closest("[data-pick]");
    if(!b || b.disabled) return;
    const tn = b.dataset.pick;
    closeSlip(true);
    if(!tn){ if(at){ delete at.t.slots[at.slot]; if(RB.slot === `${at.t.n}|${at.slot}`) RB.slot = null; refreshTeam(null, true); toast(`${st.name} — ${teamLabel(at.t)}에서 뺐다`); } return; }
    if(at && at.t.n === tn) return;
    const t = teamByName(tn), k = formSlots(t.form).find(s => !t.slots[s]);
    if(!k){ toast(`${teamLabel(t)} — 자리가 다 찼다`); return; }
    teamAssign(tn, k, id); RB.team = tn; RB.slot = null;
    refreshTeam(`${tn}|${k}`, true);
    toast(`${st.name} → ${teamLabel(t)} ${ROW_N[slotRow(k)]}`);
  });
}

/* ── 끌어 놓기 (팀 편성 모드) — 명부의 학생 → 자리 · 자리 → 자리(바꾸기) · 자리 → 명부(빼기). 마우스 · 터치 같이 ── */
let DRAG = null, dragEat = false;
function dragSrc(e){
  if(!RB.open || RB.mode !== "team" || e.button !== 0) return null;
  if(e.target.closest("[data-tset],[data-unslot],.slip")) return null;
  const cell = e.target.closest("#grid .cell");
  if(cell) return {kind: "stu", id: cell.dataset.sid};
  const fs = e.target.closest(".fs.fill[data-slot]");
  if(fs){ const [tn, k] = fs.dataset.slot.split("|"), t = teamByName(tn); if(t && t.slots[k]) return {kind: "slot", tn, k, id: t.slots[k]}; }
  return null;
}
function dragStart(){
  const st = stuById(DRAG.src.id);
  if(!st){ DRAG = null; return; }
  DRAG.on = true; closeSlip();
  const g = document.createElement("div");
  g.className = "tm-ghost"; g.innerHTML = faceHTML(st, "");
  $("book").append(g); DRAG.g = g;
  RB.root.getElementById("rbw").classList.add("tm-drag");
  const from = DRAG.src.kind === "slot" ? $("tmw").querySelector(`.fs[data-slot="${DRAG.src.tn}|${DRAG.src.k}"]`) : RB.root.querySelector(`#grid .cell[data-sid="${DRAG.src.id}"]`);
  if(from) from.classList.add("lift");
}
function dragMove(e){
  const bk = $("book"), b = bk.getBoundingClientRect(), s = b.width / bk.offsetWidth || 1;
  DRAG.g.style.left = Math.round((e.clientX - b.left) / s - 28) + "px"; DRAG.g.style.top = Math.round((e.clientY - b.top) / s - 28) + "px";
  const el = RB.root.elementFromPoint(e.clientX, e.clientY);
  const fs = el && el.closest ? el.closest("#tmw .fs[data-slot]") : null;
  const out = !fs && DRAG.src.kind === "slot" && el && el.closest && el.closest(".page.l");
  $$("#tmw .fs.drop").forEach(x => { if(x !== fs) x.classList.remove("drop"); });
  if(fs) fs.classList.add("drop");
  const pl = RB.root.querySelector(".page.l"); if(pl) pl.classList.toggle("dropout", !!out);
  DRAG.over = fs ? fs.dataset.slot : out ? "out" : null;
}
function dragDrop(d){
  const st = stuById(d.src.id);
  if(!d.over || !st) return;
  if(d.over === "out"){ const t = teamByName(d.src.tn); delete t.slots[d.src.k]; RB.slot = null; refreshTeam(null, true); toast(`${st.name} — ${teamLabel(t)}에서 뺐다`); return; }
  const [tn, k] = d.over.split("|"), t = teamByName(tn);
  if(!t || t.slots[k] === d.src.id) return;              // 제자리에 놓았다
  teamAssign(tn, k, d.src.id); RB.slot = null;
  refreshTeam(d.over, true);
}
function dragClean(){
  if(!RB.root) return;
  $$(".tm-ghost").forEach(x => x.remove());
  $$("#book .drop, #book .lift").forEach(x => x.classList.remove("drop", "lift"));
  const pl = RB.root.querySelector(".page.l"); if(pl) pl.classList.remove("dropout");
  const w = RB.root.getElementById("rbw"); if(w) w.classList.remove("tm-drag");
}

/* ── 오른쪽 쪽 — 상세 ── */
function hexCard(st){
  return `<div class="card hex" id="hexCard" title="꼭짓점 표식 — 성격(${h(st.pers.n)})이 빨간 ▲ 올림 · 파란 ▼ 내림 · 흰 ● 영향 없음"><span class="cap">멘탈리티</span><canvas id="hexCv"></canvas><svg class="hexsv" id="hexSv" aria-hidden="true"></svg><div id="hexLab"></div></div>`;
}
function relicCard(st){
  const ROW = [];
  const have = st.relics.filter(Boolean).length;
  for(let i = 0; i < RELIC_SLOT_MAX; i++){
    if(i >= st.relicSlots){
      ROW.push(`<div class="slot lock">${dots(BM.lock, "#c4ac84", "#8a7356")}<span>Lv.${i * RELIC_SLOT_EVERY} 에 열린다</span></div>`);
      continue;
    }
    const r = st.relics[i];
    if(!r){ ROW.push(`<button class="slot empty" data-relic-go="${h(st.id)}" title="Slot ${i + 1} — 비어 있다. 누르면 유물 보관고로 (이 학생에게 장착할 유물을 고른다)"><span class="pl">+</span><span>Slot ${i + 1}</span></button>`); continue; }
    const c = GC_PAGE[r.grade] || GC_PAGE.C;
    ROW.push(`<div class="slot" style="border-left-color:${c}" title="${h(r.name)} — ${h(r.aff.map(a => a.n + " " + a.v).join(" · "))}"><div class="bd">
      <div class="rn"><span class="rnm" style="color:${c}">${h(r.name)}</span>${gradeTag(r.grade)}<span class="sc num">${r.score}점</span></div>
      <div class="af">${r.aff.map(a => `<span>${h(a.n)} <b style="color:var(--ink);font-weight:400">${h(a.v)}</b></span>`).join("")}</div></div>
      <button class="uq" data-unequip="${h(st.id)}|${i}" title="해제 — 유물 보관함으로 돌아간다">해제</button></div>`);
  }
  return `<div class="card rel"><span class="cap">유물<i>${have} / ${st.relicSlots}칸</i></span>${ROW.join("")}</div>`;
}
function skillList(st){ return (st.passive ? [Object.assign({id:"passive", kindLabel:"패시브", kind:"passive", txt:st.passive.d, name:st.passive.n}, st.passive)] : []).concat(st.skills); }
function skillCard(st){
  const L = skillList(st);
  RB.sk = Math.max(0, Math.min(RB.sk, L.length - 1));
  const up = st.sp > 0 ? `<span class="spr">강화 포인트 <b>${st.sp}</b><button class="pbtn pri" id="skUp" data-skup="${h(st.id)}">스킬 강화</button></span>` : "";
  return `<div class="card skc"><span class="cap">패시브 · 스킬<i>강화 상한 Lv.${SK_LV_MAX}</i></span>${up}
    <div class="sks">${L.map((s, i) => `<button class="sk${i === RB.sk ? " on" : ""}" data-sk="${i}">
      <span class="ic"><img class="fr" src="${h(SKILL_ICON_FRAME[s.grade] || SKILL_ICON_FRAME.D)}" alt=""><img class="ar" src="${h(s.icon || "")}" alt=""></span>
      <span class="sn" style="color:${GC_PAGE[s.grade]}">${h(s.name)}</span>
      <span class="sl"><b class="num" style="color:var(--ink)">Lv.${s.lv}</b> · <b style="color:${GC_PAGE[s.grade]}">${h(s.grade)}</b></span></button>`).join("")}</div>
    <div class="skd" id="skd"></div></div>`;
}
function skillDesc(st){
  const s = skillList(st)[RB.sk];
  if(!s) return "";
  const m = s.kind === "passive" ? "" : ` <span class="m">— 효과량 ${s.pow}% · 대상 ${h(s.target)}${s.dur ? ` · 지속 ${s.dur}턴` : ""}${s.proc != null ? ` · 출현 ${s.proc}%` : ""}</span>`;
  return `<b style="color:${GC_PAGE[s.grade]}">${h(s.name)}</b> <span class="m">${h(s.kindLabel)}</span> ${h(s.txt)}${m}`;
}
function hearts(v){
  let out = "";
  for(let i = 1; i <= TRUST_MAX; i++) out += i <= v ? dots(BM.heart, "#e0605a", "#7a2420") : dots(BM.heart, "#efdfba", "#c4ac84");
  return `<span class="hearts" title="신뢰 ${v} / ${TRUST_MAX}">${out}</span>`;
}
/* 학적 — 이름(황동 · 점선 밑줄) / 값(잉크 — 업보만 주의 · 위험 색) / 덧말(옅은 잉크). 진로 설명 · 다음 업보 진로까지는 숨김 (1009) */
function recordBody(st){
  const kc = st.karma >= 150 ? "c-bad" : st.karma ? "c-warn" : "";
  return `<div class="rgrid">
    <div class="it"><div class="k">신뢰 단계</div><div class="v">${h(st.trust.step)} <span class="num sub">${st.trust.v} / ${TRUST_MAX}</span></div>${hearts(st.trust.v)}</div>
    <div class="it"><div class="k">관계 상태</div><div class="v">${h(st.trust.rel)}</div></div>
    <div class="it"><div class="k">개인 명성</div><div class="v num">${st.fame.toLocaleString()}</div><div class="s">${st.fameBonus > 0 ? `졸업 후원금 <span class="c-ok">+${st.fameBonus}%</span>` : "대회 · 원정에서 쌓인다"}</div></div>
    <div class="it"><div class="k">업보</div><div class="v num ${kc}"${!st.career.dark && st.karmaNext ? ` title="${h(st.karmaNext.n)}까지 ${st.karmaNext.need}"` : ""}>${st.karma}</div>${st.career.dark ? `<div class="s">업보가 진로를 덮었다</div>` : ""}</div>
    <div class="it"><div class="k">진로 평가</div><div class="v num">${st.eval}</div><div class="s">${st.nextCareer ? `${h(st.nextCareer.n)}까지 ${st.nextCareer.need}` : st.career.dark ? "" : "최고 진로 도달"}</div></div>
    <div class="it"><div class="k">진로 전망</div><div class="v ${st.career.dark ? "c-bad" : ""}" title="${h(st.career.d)}">${h(st.career.n)}${st.career.dark ? `<span class="tag inj">업보</span>` : ""}</div></div>
  </div>`;
}
function battleBody(st){
  const B = st.battle.map(b => ({n: b.n, v: b.v}));
  B.push({n: "의식 유지선", v: st.cons + "%", t: `체력이 ${st.cons}% 이상이면 의식을 잃지 않는다`});
  B.push({n: "의식 저하 경감", v: st.willCut + "%"});
  B.push({n: "컨디션", v: `<span class="c-${h(st.condTone)}">${st.cond} · ${st.eff}%</span>`, t: `컨디션 ${st.cond} — 효율 ${st.eff}%`, raw: true});
  return `<div class="bgrid">${B.map(b => `<div class="b"${b.t ? ` title="${h(b.t)}"` : ""}><span class="k">${h(b.n)}</span><span class="v">${b.raw ? b.v : h(b.v)}</span></div>`).join("")}</div>`;
}
function recordCard(st){
  const bat = RB.rt === "bat";
  return `<div class="card rec" id="recCard">
    <div class="tabs" role="tablist" data-ed="rtabs"><button class="rt${bat ? "" : " on"}" data-rt="rec" role="tab" aria-selected="${!bat}">학적</button><button class="rt${bat ? " on" : ""}" data-rt="bat" role="tab" aria-selected="${bat}">전투 능력치</button></div>
    ${bat ? `<span class="pw">전투력<b>${st.power.toLocaleString()}</b></span>` : ""}
    ${bat ? battleBody(st) : recordBody(st)}</div>`;
}
function persLine(st){
  const ks = Object.keys(st.pers.m || {});
  const same = ks.length === MK6.length && ks.every(k => st.pers.m[k] === st.pers.m[ks[0]]);
  const sgn = v => v > 0 ? "+" + v : "−" + Math.abs(v);
  const eff = same ? `<span class="eff ${st.pers.m[ks[0]] > 0 ? "up" : "dn"}">${st.pers.m[ks[0]] > 0 ? MARK.up : MARK.dn}모든 멘탈리티 ${sgn(st.pers.m[ks[0]])}</span>`
    : ks.length ? ks.map(k => { const v = st.pers.m[k], m = MENTAL.find(x => x.k === k);
        return `<span class="eff ${v > 0 ? "up" : "dn"}">${v > 0 ? MARK.up : MARK.dn}${m ? m.n : h(k)} ${sgn(v)}</span>`; }).join("")
    : `<span class="eff" style="color:var(--ink3)">${MARK.no} 보정 없음</span>`;
  return `<div class="pers"><span class="k">성격</span><span class="tag" style="color:var(--frame)">${h(st.pers.n)}</span>${eff}</div>
    <div class="pdesc">${h(st.pers.d)}</div>`;
}
function renderDetail(anim){
  const st = stuById(RB.sel);
  const det = $("det");
  if(!st){ det.innerHTML = ""; return; }
  const put = () => {
    if(!RB.open && anim) return;
    const bc = st.pers.k === "boast" ? " boast" : st.pers.k === "intro" ? " timid" : "";
    det.innerHTML = `<div class="hd">${faceHTML(st, "dring")}
        <div class="who">
          <div class="nmrow" data-ed="dname">${st.epithet ? `<span class="epi">“${h(st.epithet)}”</span>` : ""}<span class="nm">${h(st.name)}</span><button class="ebtn" id="ebtn" data-ed="ebtn" title="이름 변경" aria-label="이름 변경">${ICO.pen}</button></div>
          <div class="tags" data-ed="dtags">${gradeTag(st.grade)}<span class="tag r-${ROLE_TONE[st.role]}" title="${h(st.roleLabel)}${st.sub ? " · " + h(st.sub) : ""} — ${h(st.jobDesc)}">${h(st.jobName)}</span>
            <span class="tag yr">${st.year}학년</span><span class="tag lv num">Lv.${st.level}</span></div>
          <div class="bub${bc}" data-ed="bub">${h(st.greet)}</div>
        </div></div>
      ${st.note ? `<div class="note-band"><b>입학 당시</b> — ${h(st.note)}</div>` : ""}
      ${persLine(st)}
      <div class="row2">${hexCard(st)}${relicCard(st)}</div>
      ${skillCard(st)}
      ${recordCard(st)}`;
    $("skd").innerHTML = skillDesc(st);
    drawHex(st);
    bindDetail(st);
  };
  if(anim){ det.classList.add("turn"); setTimeout(() => { put(); det.classList.remove("turn"); }, 140); }
  else put();
}

/* ── 육각형 — 책장 위 잉크 그림. 바닥 · 눈금 · 바깥 육각형 · 표식은 1배 도트로 그려 2배로 본다 (책 · 책상과 같은 도트 크기)
   학생 값(푸른 면 · 테두리)만 매끈한 SVG (1009 — 도트의 계단이 자글자글해서). 테두리 2px
   꼭짓점 바로 바깥에 성격 표식(빨간 ▲ 올림 · 파란 ▼ 내림 · 흰 ● 영향 없음)을 작게, 그 바깥에 이름 · 값 · 등급 ── */
function drawHex(st){
  const card = $("hexCard"), cv = $("hexCv"), sv = $("hexSv"), lab = $("hexLab");
  if(!card || !card.clientWidth) return;
  const cw = card.clientWidth, ch = card.clientHeight;
  const MO = 5, LW = 36, GAP = 8;                                         // 표식 자리(꼭짓점에서 1배 5칸 바깥) · 옆 글 너비(2배)
  const byW = Math.floor((cw / 2 - 4 - GAP - LW) / (2 * 0.866)) - MO;
  const byH = Math.floor(((ch - 26) / 2 - 42) / 2) - MO;
  const R = Math.max(26, Math.min(44, byW, byH));                // 1배 반지름 — 값 100 이 바깥 육각형
  const PAD = MO + 5, W = (R + PAD) * 2 + 1, H = W;
  const cx = (W - 1) / 2, cy = (H - 1) / 2;
  const CX = cw / 2, CY = Math.round((ch + 22) / 2);             // 2배 — 머리띠 아래 가운데
  cv.width = W; cv.height = H;
  cv.style.width = W * 2 + "px"; cv.style.height = H * 2 + "px";
  const X0 = Math.round(CX - W), Y0 = Math.round(CY - H);
  cv.style.left = X0 + "px"; cv.style.top = Y0 + "px";
  const g = cv.getContext("2d"), img = g.createImageData(W, H), d = img.data;
  const set = (x, y, c, a) => {                                   // 겹쳐 칠하기 (source-over)
    x = Math.round(x); y = Math.round(y); if(x < 0 || y < 0 || x >= W || y >= H) return;
    const i = (y * W + x) * 4, sa = (a == null ? 255 : a) / 255, da = d[i+3] / 255, oa = sa + da * (1 - sa);
    for(let k = 0; k < 3; k++) d[i+k] = oa ? (c[k] * sa + d[i+k] * da * (1 - sa)) / oa : 0;
    d[i+3] = oa * 255;
  };
  const rgb = c => [parseInt(c.slice(1,3),16), parseInt(c.slice(3,5),16), parseInt(c.slice(5,7),16)];
  const ang = i => -Math.PI / 2 + i * Math.PI / 3;
  const pt = (i, r) => [cx + Math.cos(ang(i)) * r, cy + Math.sin(ang(i)) * r];
  const line = (a, b, plot, every) => {                           // 브레젠햄 — plot(x, y) 로 한 칸씩 · every=2 면 점선
    let [x0, y0] = a.map(Math.round), [x1, y1] = b.map(Math.round), n = 0;
    const dx = Math.abs(x1 - x0), dy = -Math.abs(y1 - y0), sx = x0 < x1 ? 1 : -1, sy = y0 < y1 ? 1 : -1; let e = dx + dy;
    for(;;){ if(!every || n % every === 0) plot(x0, y0); n++; if(x0 === x1 && y0 === y1) break;
      const e2 = 2 * e; if(e2 >= dy){ e += dy; x0 += sx; } if(e2 <= dx){ e += dx; y0 += sy; } }
  };
  const paint = c => (x, y) => set(x, y, rgb(c));                 // 캔버스(도트)에 칠하기
  const cells = () => {                                           // SVG 도트 — 1배 한 칸 = 네모 하나 (crispEdges 라 또렷하다)
    const S = new Set(), f = (x, y) => { x = Math.round(x); y = Math.round(y); if(x >= 0 && y >= 0 && x < W && y < H) S.add(`M${x} ${y}h1v1h-1z`); };
    f.d = () => [...S].join("");
    return f;
  };
  const inPoly = (P, x, y) => { let s = false; for(let i = 0, j = P.length - 1; i < P.length; j = i++){
      const [xi, yi] = P[i], [xj, yj] = P[j]; if(((yi > y) !== (yj > y)) && (x < (xj - xi) * (y - yi) / (yj - yi) + xi)) s = !s; } return s; };
  const poly = (P, c, a) => { for(let y = 0; y < H; y++) for(let x = 0; x < W; x++) if(inPoly(P, x + .5, y + .5)) set(x, y, c, a); };
  const six = r => [0,1,2,3,4,5].map(i => pt(i, r));
  const sprite = (rows, x, y, fill, edge) => {                    // 작은 표식 — 가운데 (x, y), 테두리 한 칸 (fill · edge 는 plot)
    const hh = rows.length, w = rows[0].length, ox = Math.round(x - w / 2), oy = Math.round(y - hh / 2);
    const at = (i, j) => j >= 0 && j < hh && i >= 0 && i < w && rows[j][i] === "#";
    for(let j = -1; j <= hh; j++) for(let i = -1; i <= w; i++){
      if(at(i, j)) fill(ox + i, oy + j);
      else if(at(i-1,j)||at(i+1,j)||at(i,j-1)||at(i,j+1)) edge(ox + i, oy + j);
    }
  };
  // 캔버스(도트) — 바닥: 책장보다 조금 짙은 종이, 한 칸 아래로 그늘 · 눈금 점선
  poly(six(R).map(([x, y]) => [x + 1, y + 1]), rgb("#e2cfa6"));
  poly(six(R), rgb("#f3e4c3"));
  for(const f of [.25, .5, .75]){ const P = six(R * f); for(let i = 0; i < 6; i++) line(P[i], P[(i+1)%6], paint("#d3bd94"), 2); }
  for(let i = 0; i < 6; i++) line([cx, cy], pt(i, R), paint("#d3bd94"), 2);
  g.putImageData(img, 0, 0);
  // 그 위 SVG (같은 자리 · 같은 1배 좌표) — 학생 값 면(매끈하게) → 바깥 육각형(도트) → 학생 값 테두리(매끈하게 · 1배 1칸 = 2px) → 꼭짓점 표식(도트)
  const VP = HEX6.map((m, i) => pt(i, R * Math.min(Math.max(st.ment[m.k], 3), 118) / 100));   // 100 이 바깥, 넘으면 조금 바깥으로 · 118 까지
  const pts = VP.map(([x, y]) => `${(x + .5).toFixed(2)},${(y + .5).toFixed(2)}`).join(" ");   // 도트 칸 가운데에 맞춘다
  const OP = six(R), rim = cells();
  for(let i = 0; i < 6; i++) line(OP[i], OP[(i+1)%6], rim);
  const mk = {}, col = c => mk[c] || (mk[c] = cells());
  HEX6.forEach((m, i) => { const k = persMark(st, m.k), [x, y] = pt(i, R + MO);
    sprite(k === "up" ? BM.sUp : k === "dn" ? BM.sDn : BM.sNo, x, y, col(MC[k][0]), col(MC[k][1])); });
  sv.setAttribute("viewBox", `0 0 ${W} ${H}`);
  sv.style.cssText = `left:${X0}px;top:${Y0}px;width:${W * 2}px;height:${H * 2}px`;
  sv.innerHTML = `<polygon points="${pts}" fill="#7f9fcf" fill-opacity=".59"/>`
    + `<path d="${rim.d()}" fill="#8a6a45" shape-rendering="crispEdges"/>`
    + `<polygon points="${pts}" fill="none" stroke="#3f5f95" stroke-width="1" stroke-linejoin="round"/>`
    + Object.entries(mk).map(([c, f]) => `<path d="${f.d()}" fill="${c}" shape-rendering="crispEdges"/>`).join("");
  // 글 — 표식 바깥 (이름 줄 · 값 줄)
  lab.innerHTML = HEX6.map((m, i) => {
    const [x, y] = pt(i, R + MO), v = Math.round(st.ment[m.k]), gr = mentalGrade(v);
    const c = Math.cos(ang(i)), sn = Math.sin(ang(i));
    const side = Math.abs(c) < .2 ? "C" : (c < 0 ? "L" : "R");
    const X = X0 + x * 2, Y = Y0 + y * 2;
    const pos = side === "C" ? `left:${Math.round(X - 30)}px;width:60px;top:${Math.round(sn < 0 ? Y - 42 : Y + 8)}px`
      : side === "L" ? `right:${Math.round(cw - (X - GAP))}px;top:${Math.round(Y - 17)}px`
      : `left:${Math.round(X + GAP)}px;top:${Math.round(Y - 17)}px`;
    return `<div class="lab ${side}" style="${pos}" title="${h(m.n)} — ${h(m.d)}">
      <div class="n">${h(m.n)}</div><div class="v">${v}<b style="color:${GC_PAGE[gr] || "var(--ink)"}">${h(gr)}</b></div></div>`;
  }).join("");
}

function bindDetail(st){
  $$("#det .sk").forEach(b => {
    const go = () => { RB.sk = +b.dataset.sk; $$("#det .sk").forEach(x => x.classList.toggle("on", x === b)); $("skd").innerHTML = skillDesc(st); };
    b.onmouseenter = go; b.onclick = go; b.onfocus = go;
  });
  $$("#recCard .rt").forEach(b => b.onclick = () => setRecTab(b.dataset.rt));
  const e = $("ebtn"); if(e) e.onclick = () => { RB.want = true; renameStudent(st.id); };          // 게임의 이름 변경 팝업 (책 위에 뜬다)
  const u = $("skUp"); if(u) u.onclick = () => { RB.want = true; skillUpModal(st.id); };           // 게임의 스킬 강화 팝업
  $$("#det [data-relic-go]").forEach(b => b.onclick = () => goRelic(b.dataset.relicGo));          // 빈 유물 칸 → 유물 보관고
  $$("#det [data-unequip]").forEach(b => b.onclick = () => {                                     // 유물 해제 — 예전 학생 상세와 같다 (보관함으로)
    const [sid, idx] = b.dataset.unequip.split("|"), s = rawById(sid);
    if(!s || !s.relics) return;
    const r = s.relics.splice(+idx, 1)[0];
    if(r) addRelicToPool(r);
    save(); refreshAll();
    if(r) toast(`${r.name} — 해제했다 (유물 보관함으로)`);
  });
}
/* 빈 유물 칸 → 책을 닫고 유물 보관고로 (일단은 — 1009). 보관고 유물마다의 '장착할 학생'을 이 학생으로 골라 둔다 */
function goRelic(sid){
  rbClose(true);
  UI.view = "relic"; render();
  const v = document.getElementById("view");
  if(!v || !sid) return;
  v.querySelectorAll("select[data-eqsel]").forEach(sel => {
    if(![...sel.options].some(o => o.value === sid)) return;
    sel.value = sid;
    if(typeof sel.onchange === "function") sel.onchange();             // 장착 미리보기도 이 학생으로
  });
}
function setRecTab(rt){                                  // 고른 탭은 다른 학생을 봐도 그대로
  if(RB.rt === rt) return;
  RB.rt = rt;
  const st = stuById(RB.sel), old = $("recCard");
  if(!st || !old) return;
  const tmp = document.createElement("div");
  tmp.innerHTML = recordCard(st); old.replaceWith(tmp.firstElementChild);
  bindDetail(st);
}

/* ── 고르기 · 정렬 ── */
function select(id, anim){
  if(RB.sel === id) return;
  RB.sel = id; RB.sk = 0;
  $$("#grid .cell").forEach(c => { const on = c.dataset.sid === id; c.classList.toggle("on", on); c.setAttribute("aria-pressed", on); });
  renderDetail(anim);
}
function setSort(k){ if(!S.opts) S.opts = {}; S.opts.rbsort = k; $("sort").value = k; save(); renderList(); }
function pickSel(){
  if(RB.sel && RB.vm.has(RB.sel)) return;
  const L = sorted(students());
  RB.sel = L.length ? L[0].id : null; RB.sk = 0;
}
/* 다시 그리기 — 게임 값이 바뀌었을 때 (열 때 · 이름 변경 · 스킬 강화 · 유물 해제 뒤) */
function refreshAll(){
  buildVM(); pickSel(); closeSlip();
  showMode(); renderList(); renderRight(); applyLayout();
}

/* ── 열고 닫기 · 창에 맞추기 ── */
function fit(){
  if(!RB.root) return;
  const fi = $("fitIn"), W = 1214, H = 980, vw = window.innerWidth, vh = window.innerHeight;
  const s = Math.min(1, (vw - 16) / W, (vh - 8) / H);
  fi.style.transform = `translate(${Math.round((vw - W * s) / 2)}px,${Math.round((vh - H * s) / 2)}px) scale(${s})`;
}
function ensureHost(){
  if(RB.host) return;
  const host = document.createElement("div");
  host.id = "rbHost";
  host.style.cssText = "position:fixed;inset:0;z-index:79;display:none";      // 게임 팝업(.overlay 80) · 알림(90) 아래, 화면 위
  const root = host.attachShadow({mode: "open"});
  root.innerHTML = `<style>${RB_CSS}</style><div class="rbw closed" id="rbw"><div class="rbscrim" id="rbScrim"></div>${RB_HTML}</div>`;
  document.body.append(host);
  RB.host = host; RB.root = root;
  const fi = $("fitIn"), bk = $("book");
  fi.classList.add("closed");
  bk.style.setProperty("--rb-book", `url("${ROSTER_ART.book}")`);
  bk.style.setProperty("--rb-ribbon", `url("${ROSTER_ART.ribbon}")`);
  bk.tabIndex = -1;
  $("tbtn").innerHTML = ICO.flag + "<span>팀 편성</span>";
  $("sort").innerHTML = RB_SORT.map(o => `<option value="${o.k}">정렬 — ${o.n}</option>`).join("");
  wire();
}
function wire(){
  $("xbtn").onclick = () => rbClose();
  $("rbScrim").onclick = () => rbClose();
  $("tbtn").onclick = () => setRosterMode(RB.mode === "team" ? "detail" : "team");
  $("spbtn").onclick = () => { RB.want = true; autoSkillUpConfirm(); };     // 게임의 임의 강화 확인 창 (책 위에) → 결과 창 · 책은 render() 끝에서 다시 그린다
  $("sort").onchange = e => setSort(e.target.value);
  $("grid").addEventListener("click", e => {
    const tg = e.target.closest("[data-tset]");                       // 팀 편성 — 꼬리표는 소속 팀 쪽지
    if(tg){ e.stopPropagation(); openTeamPicker(tg); return; }
    const c = e.target.closest(".cell");
    if(!c) return;
    if(RB.mode === "team") placeFromList(c.dataset.sid); else select(c.dataset.sid, true);
  });
  $("grid").addEventListener("keydown", e => {
    const tg = e.target.closest && e.target.closest("[data-tset]");
    if(tg && (e.key === "Enter" || e.key === " ")){ e.preventDefault(); e.stopPropagation(); openTeamPicker(tg); return; }
    const cells = $$("#grid .cell");
    const mv = {ArrowRight: 1, ArrowLeft: -1, ArrowDown: 3, ArrowUp: -3}[e.key];
    if(mv == null) return;
    if(RB.mode === "team"){                                            // 팀 편성 — 초점만 옮긴다
      const a = RB.root.activeElement, i = cells.indexOf(a && a.closest ? a.closest(".cell") : null);
      if(i < 0) return;
      e.preventDefault(); cells[Math.max(0, Math.min(cells.length - 1, i + mv))].focus();
      return;
    }
    const i = cells.findIndex(c => c.dataset.sid === RB.sel);
    if(i < 0) return;
    e.preventDefault();
    const j = Math.max(0, Math.min(cells.length - 1, i + mv));
    select(cells[j].dataset.sid, true); cells[j].focus();
  });
  $("tmw").addEventListener("click", e => {
    const b = e.target.closest("[data-team],[data-form],[data-unslot],[data-act],[data-slot]");
    if(!b || b.disabled) return;
    const cur = teamByName(RB.team);
    if(b.dataset.team){ RB.team = b.dataset.team; RB.slot = null; refreshTeam(); return; }
    if(b.dataset.form){ if(b.dataset.form !== cur.form){ setForm(cur, b.dataset.form); RB.slot = null; refreshTeam(null, true); } return; }
    if(b.dataset.unslot != null){ const [tn, k] = b.dataset.unslot.split("|"), t = teamByName(tn), st = stuById(t.slots[k]); delete t.slots[k]; if(RB.slot === b.dataset.unslot) RB.slot = null; refreshTeam(null, true); if(st) toast(`${st.name} — ${teamLabel(t)}에서 뺐다`); return; }
    if(b.dataset.act){ teamAct(b.dataset.act); return; }
    if(b.dataset.slot){ RB.slot = RB.slot === b.dataset.slot ? null : b.dataset.slot; refreshTeam(); }
  });
  $("tmw").addEventListener("keydown", e => {
    const s = e.target.closest && e.target.closest(".fs[data-slot]");
    if(s && e.target === s && (e.key === "Enter" || e.key === " ")){ e.preventDefault(); s.click(); }
  });
  const bk = $("book");
  bk.addEventListener("pointerdown", e => { const src = dragSrc(e); if(src) DRAG = {src, x: e.clientX, y: e.clientY, on: false}; });
  bk.addEventListener("click", e => { if(dragEat){ dragEat = false; e.stopPropagation(); e.preventDefault(); } }, true);   // 끌기가 끝나며 따라오는 누르기 하나는 버린다
  RB.root.addEventListener("pointerdown", e => { if(SLIP && !SLIP.el.contains(e.target) && !SLIP.anchor.contains(e.target)) closeSlip(); }, true);
  if(RB.wired) return;
  RB.wired = true;
  document.addEventListener("pointermove", e => {
    if(!DRAG) return;
    if(!DRAG.on){ if(Math.abs(e.clientX - DRAG.x) + Math.abs(e.clientY - DRAG.y) < 6) return; dragStart(); if(!DRAG) return; }
    e.preventDefault(); dragMove(e);
  });
  document.addEventListener("pointerup", () => {
    if(!DRAG) return;
    const d = DRAG; DRAG = null;
    if(d.on){ dragEat = true; setTimeout(() => { dragEat = false; }, 0); dragDrop(d); }
    dragClean();
  });
  document.addEventListener("pointercancel", () => { if(DRAG){ DRAG = null; dragClean(); } });
  document.addEventListener("keydown", e => {                         // Esc — 쪽지 닫기 → 고른 자리 풀기 → 책 닫기 (게임 팝업이 위에 있으면 그쪽 차례)
    if(!RB.open || e.key !== "Escape") return;
    const mr = document.getElementById("modalRoot");
    if(mr && mr.firstChild) return;
    e.preventDefault();
    if(SLIP){ closeSlip(true); return; }
    if(RB.mode === "team" && RB.slot){ RB.slot = null; refreshTeam(); return; }
    rbClose();
  });
  window.addEventListener("resize", () => { if(RB.open) fit(); });
}
function rbOn(){ return typeof townMode === "function" && townMode() && typeof S !== "undefined" && !!S && Array.isArray(S.students); }
function rbOpen(opt){
  opt = opt || {};
  ensureHost();
  if(!RB.mq && typeof TOWN_MQ !== "undefined" && TOWN_MQ){                  // 창이 좁아지면 예전 화면으로 (같은 학생 · 같은 쪽)
    RB.mq = true;
    const onMq = () => { if(RB.open && !townMode()){ const m = RB.mode, sel = RB.sel; rbClose(true); UI.view = m === "team" ? "team" : "roster"; if(sel) UI.sel = sel; render(); } };
    if(TOWN_MQ.addEventListener) TOWN_MQ.addEventListener("change", onMq); else if(TOWN_MQ.addListener) TOWN_MQ.addListener(onMq);
  }
  if(opt.mode) RB.mode = opt.mode === "team" ? "team" : "detail";
  if(opt.sel) RB.sel = opt.sel;
  RB.slot = null;
  if(!S.opts) S.opts = {};
  $("sort").value = sortKey();
  const was = RB.open;
  RB.open = true;
  RB.host.style.display = "block";
  if(!was){ RB.ovf = document.documentElement.style.overflow; document.documentElement.style.overflow = "hidden"; }
  fit();
  refreshAll();
  if(!was){
    const fi = $("fitIn"), w = RB.root.getElementById("rbw");
    void fi.offsetWidth;
    requestAnimationFrame(() => { fi.classList.remove("closed"); w.classList.remove("closed"); });
    $("book").focus({preventScroll: true});
  }
}
function rbClose(quiet){
  if(!RB.open) return;
  RB.open = false; RB.want = false; DRAG = null;
  closeSlip(); dragClean();
  const fi = $("fitIn"), w = RB.root.getElementById("rbw");
  fi.classList.add("closed"); w.classList.add("closed");
  setTimeout(() => { if(!RB.open && RB.host) RB.host.style.display = "none"; }, 200);
  document.documentElement.style.overflow = RB.ovf || "";
  if(!quiet) render();                                       // 메뉴 숫자 · 학원 정보 등 — 바뀐 편성 · 이름이 보이게
}
/* render() 맨 앞 — 가로 넓은 화면에서 학생 명부 · 팀 편성으로 가려 하면 책을 연다 (화면은 원래 보던 곳 그대로) */
function rbIntercept(){
  if(UI.view === "roster" || UI.view === "team"){
    if(!rbOn()) return;
    const mode = UI.view === "team" ? "team" : "detail", sel = UI.view === "roster" && UI.sel ? UI.sel : null;
    UI.view = (RB.back && RB.back !== "master") ? RB.back : "home";
    rbOpen({mode, sel});
  } else RB.back = UI.view;
}
/* render() 맨 끝 — 책에서 연 게임 팝업(이름 변경 · 스킬 강화 · 임의 강화)이 끝나면 책을 다시 그린다 */
function rbAfter(){ if(RB.open && RB.want){ RB.want = false; refreshAll(); } }
window.RBK = {open: rbOpen, close: rbClose, on: rbOn, intercept: rbIntercept, after: rbAfter, isOpen: () => RB.open, state: RB};
})();
/* ROSTERBK_END */
