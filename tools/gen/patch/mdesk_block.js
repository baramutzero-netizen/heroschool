/* MDESK_START — 마스터 노트 책상 (1006)
   책상 소품 배치판(2판)으로 사용자가 정한 배치(desk_layout.json)를 배치판 자신의 그리기 코드로 구운 그림(MDESK_ART · 1배 607×466)을
   스케줄 두루마리와 같은 액자(1544:1008 · 액자 그림 SCHED_ART.over2 — 가장자리 그늘 포함)에 띄운다 (1011 — 마을 · 마스터 노트 · 스케줄 셋이 같은 크기 · 같은 액자).
   책상은 스케줄 책상 크기(746×478 — MDESK_GEO.ext)로 넓혔다: 예전 책상 바탕을 왼쪽 위(위 6 줄 띄움)에 두고 오른쪽 · 위아래는 거울로 이어 붙인 판자(MDESK_ART.ext — apply_desk 가 만든다).
   소품 · 누르는 자리 · 촛불은 예전 607×466 좌표 그대로(.mdesk-art 상자 안). 오른쪽 넓어진 자리는 사이드 밑.
   가로 화면(townMode)에서만 — 세로 · 좁은 화면은 예전 마스터 노트(학원 정보 · 마스터 육성 서브탭) 그대로.
   누를 수 있는 소품: 말린 지도(튜토리얼) · 책 더미(마스터 육성 팝업) · 안경 + 회중시계(학원 정보 팝업) · 펼친 책(학생) · 두루마리(스케줄).
   누르는 자리는 그림 픽셀 그대로(MDESK_GEO.hit — 줄마다 [시작, 길이, 묶음]) — 위에 얹힌 다른 소품(잉크병 · 깃펜 등)은 누르지 않는다.
   남은 마스터 육성 포인트가 있으면 책 더미 오른쪽 위에 -15도로 기운 표식.
   두루마리를 누르면(mdeskGo) — 두루마리 위 내용이 사라지고, 책상이 두루마리로 다가간 뒤(액자는 그대로 — 1011 부터 같은 크기)
   스케줄 그림이 겹쳐 나타나고, 스케줄 내용이 두루마리 위로 떠오른다 */
const MDESK_ART = __MDESK_ART__;
const MDESK_GEO = __MDESK_GEO__;
const MDESK_TAG = {map:"튜토리얼", books:"마스터 육성", info:"학원 정보", book:"학생 명부", scroll:"스케줄"};
let MDESK_ROWS = null, MDESK_GOING = false;
function mdeskOn(){ return typeof townMode === "function" && townMode(); }
/* 책상 1배 좌표 → 묶음 번호(1부터 · 0 = 누를 수 없는 곳) */
function mdeskHit(x, y){
  if(!MDESK_ROWS) MDESK_ROWS = MDESK_GEO.hit.split(";").map(r=> r ? r.split(",").map(Number) : []);
  const r = MDESK_ROWS[y];
  if(!r || x < 0) return 0;
  for(let i = 0; i < r.length; i += 3) if(x >= r[i] && x < r[i] + r[i+1]) return r[i+2];
  return 0;
}
function mdeskFrame(){ return (typeof SCHED_ART !== "undefined" && SCHED_ART.over2) || TOWN_FRAME; }   // 스케줄과 같은 액자 + 가장자리 그늘 (1011)
function mdeskBox(x, y, w, h){
  const [W, H] = MDESK_GEO.size, p = (v, d)=> (v / d * 100).toFixed(3) + "%";
  return `left:${p(x, W)};top:${p(y, H)};width:${p(w, W)};height:${p(h, H)}`;
}
/* 팝업 — 마을 상점처럼 책상 위에 뜬다 (책상은 흐려진다). 학원 정보 = 예전 '학원 정보' 서브탭 (튜토리얼 단추는 말린 지도가 맡는다) */
function mdeskPop(k){
  const body = k === "info" ? viewHome({desk:true}) : viewMaster();
  return `<div class="townpop mdesk-pop" role="dialog" aria-label="${k === "info" ? "학원 정보" : "마스터 육성"}">${body}`
    + `<div class="townpop-foot"><button type="button" class="btn primary" data-deskdone>닫기</button></div></div>`;
}
function viewHomeDesk(){
  const G = MDESK_GEO, A = MDESK_ART, L = G.light;
  const pop = UI.mdeskPop === "info" || UI.mdeskPop === "master" ? UI.mdeskPop : null;
  const pts = (S.master && S.master.pts|0) || 0;
  const img = (src, cls, st)=> `<img class="mdl${cls ? " " + cls : ""}" src="${src}" alt="" draggable="false"${st ? ` style="${st}"` : ""}>`;
  const hl = G.groups.map((g, i)=> `<img class="mdl mdh" data-g="${i + 1}" src="${A["hl_" + g.k]}" style="${mdeskBox(...g.hl)}" alt="" draggable="false">`).join("");
  const btn = G.groups.map((g, i)=>{
    const [x0, y0, x1, y1] = g.bb, below = g.k === "map";
    const tag = MDESK_TAG[g.k] + (g.k === "books" && pts ? ` · ${pts}pt` : "");
    return `<button type="button" class="mdk${below ? " below" : ""}" data-g="${i + 1}" data-mdesk="${g.k}" style="${mdeskBox(x0, y0, x1 - x0, y1 - y0)}" aria-label="${esc(tag)}">`
      + `<span class="mdtag" aria-hidden="true">${esc(tag)}</span></button>`;
  }).join("");
  const B = G.books, E = G.ext, pc = (v, d)=> (v / d * 100).toFixed(3) + "%";
  const badge = pts > 0 ? `<span class="mdbadge" style="left:${(B.bx / G.size[0] * 100).toFixed(3)}%;top:${(B.by / G.size[1] * 100).toFixed(3)}%" title="남은 마스터 육성 포인트">${pts}</span>` : "";
  /* 책상 상자(.mdesk-desk · 746×478 — 두루마리로 다가갈 때 통째로 커진다) = 넓힌 바탕(ext) + 예전 책상 자리(.mdesk-art · 607×466 — 소품 · 누르는 자리) */
  return `<section class="town mdesk${pop ? " popopen" : ""}" aria-label="마스터 노트">`
    + `<div class="townmap mdesk-map"${pop ? " inert" : ""}><div class="townmap-in mdesk-in"><div class="mdesk-desk">` + img(A.ext, "md-ext")
    + `<div class="mdesk-art" style="left:${pc(E.x, E.w)};top:${pc(E.y, E.h)};width:${pc(G.size[0], E.w)};height:${pc(G.size[1], E.h)}">`
    + img(A.items, "md-items") + img(A.props) + img(A.light, "md-light", mdeskBox(L.x, L.y, L.w, L.h))
    + hl + badge + btn
    + `</div></div></div><img class="town-frame mdesk-frame" src="${mdeskFrame()}" alt="" draggable="false"></div>`
    + (pop ? mdeskPop(pop) : "") + `</section>`;
}
function mdeskAct(k){
  if(MDESK_GOING) return;
  if(k === "map"){ showTutorial(0, {}); return; }
  if(k === "books"){ UI.mdeskPop = "master"; render(); return; }
  if(k === "info"){ UI.mdeskPop = "info"; render(); return; }
  if(k === "book"){ UI.view = "roster"; render(); return; }
  if(k === "scroll") mdeskGo();
}
function bindMasterDesk(v){
  const sec = v.querySelector(".mdesk");
  if(!sec) return;
  v.querySelectorAll("[data-deskdone]").forEach(b=> b.onclick = ()=>{ UI.mdeskPop = null; render(); });
  const art = sec.querySelector(".mdesk-art");
  if(!art || sec.classList.contains("popopen")) return;
  const hot = (g)=>{
    const s = g ? String(g) : "";
    if((sec.dataset.hot || "") === s) return;
    if(s) sec.dataset.hot = s; else delete sec.dataset.hot;
    art.style.cursor = g ? "pointer" : "";
  };
  const at = (e)=>{
    const r = art.getBoundingClientRect();
    if(!r.width || !r.height) return 0;
    return mdeskHit(Math.floor((e.clientX - r.left) / r.width * MDESK_GEO.size[0]), Math.floor((e.clientY - r.top) / r.height * MDESK_GEO.size[1]));
  };
  art.addEventListener("pointermove", e=>{ if(!MDESK_GOING) hot(at(e)); });
  art.addEventListener("pointerleave", ()=> hot(0));
  art.addEventListener("click", e=>{ const g = at(e); if(g) mdeskAct(MDESK_GEO.groups[g - 1].k); });
  sec.querySelectorAll(".mdk").forEach(b=>{
    b.onclick = (e)=>{ e.stopPropagation(); mdeskAct(b.dataset.mdesk); };
    b.onfocus = ()=> hot(+b.dataset.g);
    b.onblur = ()=> hot(0);
  });
}
/* ── 두루마리 → 스케줄 (1006 · 1011) ──
   ① 두루마리 위 내용(띠 · 카드 · 서명)이 사라진다 ② 책상이 두루마리로 다가간다 — 두 축(가운데)과 종이 가운데를 스케줄 두루마리에 맞춘다
   (MDESK_GEO.zoom — m: 예전 책상 1배 [왼쪽 축, 오른쪽 축, 종이 세로 가운데] · s: 스케줄 무대 1배). 액자는 그대로 (1011 — 마스터 노트도 스케줄과 같은 크기라
   예전처럼 액자를 줄이지 않는다. 책상 1배와 스케줄 1배가 화면에서 같은 배율 W/772) ③ 끝무렵 스케줄 그림(내용 없이)이 겹쳐 나타나고
   ④ 스케줄 화면으로 바꾼 뒤 두루마리 위 내용(.sk-paper)이 떠오른다. 움직임 줄이기 설정이면 바로 넘어간다 */
function mdeskGo(){
  const go = ()=>{ UI.view = "plan"; render(); };
  const sec = document.querySelector("#view .mdesk"), map = sec && sec.querySelector(".mdesk-map");
  const reduce = typeof matchMedia === "function" && matchMedia("(prefers-reduced-motion: reduce)").matches;
  if(!map || reduce || !(typeof schedScrollOn === "function" && schedScrollOn()) || typeof SCHED_ART === "undefined" || typeof SCHED_GEO === "undefined"){ go(); return; }
  if(MDESK_GOING) return;
  const desk = map.querySelector(".mdesk-desk"), art = map.querySelector(".mdesk-art");
  const R = map.getBoundingClientRect(), W = R.width, H1 = W * 1008 / 1544;
  if(!desk || !art || !W){ go(); return; }
  MDESK_GOING = true;
  delete sec.dataset.hot; art.style.cursor = "";
  /* 책상 1배 → 화면 k = W/772 (액자 안쪽 13 · 책상 746×478 — 스케줄 무대와 같다). 예전 책상 점 (mx, my) 은 넓힌 책상에서 (E.x + mx, E.y + my) */
  const k = W / 772, b = 13 * k, E = MDESK_GEO.ext, Z = MDESK_GEO.zoom;
  const s = (Z.s[1] - Z.s[0]) / (Z.m[1] - Z.m[0]);                       // 두 축 사이를 스케줄 두루마리와 같게
  const tx = (Z.s[0] + Z.s[1]) / 2 * k - b - (E.x + (Z.m[0] + Z.m[1]) / 2) * k * s;   // 다 다가갔을 때 책상 상자의 왼쪽 위 (액자 안쪽 칸 기준)
  const ty = Z.s[2] * k - b - (E.y + Z.m[2]) * k * s;
  const dw = E.w * k, dh = E.h * k;
  sec.classList.add("mdesk-go");
  desk.style.cssText = `left:0;top:0;width:${dw}px;height:${dh}px`;
  /* 스케줄 그림 (내용 없이) — 바뀌기 직전에 겹쳐 나타난다. 무대(1544×1008)와 같은 자리 · 크기 */
  const SG = SCHED_GEO, Q = SG.quill, P = (x, y, w, h)=> `left:${(x / 772 * 100).toFixed(3)}%;top:${(y / 504 * 100).toFixed(3)}%;width:${(w / 772 * 100).toFixed(3)}%;height:${(h / 504 * 100).toFixed(3)}%`;
  /* 문서 위에 따로 띄운다(사이드 메뉴 아래) — 화면이 스케줄로 바뀐 뒤 그 그림이 다 그려질 때까지 덮어 둔다
     (file:// 에서는 새 그림 요소가 그림을 다시 읽느라 한두 장면 비어 보인다) */
  const gh = document.createElement("div");
  gh.className = "mdesk-ghost"; gh.setAttribute("aria-hidden", "true");
  gh.style.cssText = `left:${R.left + scrollX}px;top:${R.top + scrollY}px;width:${W}px;height:${H1}px`;
  gh.innerHTML = `<img src="${SCHED_ART.under}" alt=""><img src="${SCHED_ART.over1}" alt="">`
    + (Q ? `<img src="${SCHED_ART.quill}" alt="" style="${P(Q.x - Q.px, Q.y - Q.py, Q.w, Q.h)}">` : "")
    + `<img src="${SCHED_ART.over2}" alt="">`;
  document.body.append(gh);
  const FADE = 260, ZOOM = 820, T0 = performance.now();
  const ease = t=> t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
  const step = (now)=>{
    if(!map.isConnected){ MDESK_GOING = false; gh.remove(); if(UI.view === "home") go(); return; }   // 그새 화면이 다시 그려졌다
    const t = Math.min(1, Math.max(0, (now - T0 - FADE) / ZOOM)), e = ease(t), z = 1 + (s - 1) * e;
    desk.style.left = (tx * e) + "px"; desk.style.top = (ty * e) + "px";
    desk.style.width = (dw * z) + "px"; desk.style.height = (dh * z) + "px";
    gh.style.opacity = String(Math.min(1, Math.max(0, (t - .58) / .36)));
    if(t < 1){ requestAnimationFrame(step); return; }
    MDESK_GOING = false;
    if(UI.view !== "home"){ gh.remove(); return; }
    go();
    /* 스케줄 그림이 다 그려지면 덮개를 걷고 두루마리 위 내용을 띄운다 */
    const w = document.querySelector("#view .skwrap");
    if(!w){ gh.remove(); return; }
    w.classList.add("mdesk-wait");
    const ready = (i)=> (i.complete && i.naturalWidth) ? Promise.resolve() : (i.decode ? i.decode().catch(()=>{}) : new Promise(r=>{ i.addEventListener("load", r); i.addEventListener("error", r); }));
    const imgs = [...w.querySelectorAll(".skstage > img, .sk-quill img")];
    Promise.race([Promise.all(imgs.map(ready)), new Promise(r=> setTimeout(r, 1500))]).then(()=> requestAnimationFrame(()=>{
      gh.remove();
      w.classList.remove("mdesk-wait"); w.classList.add("mdesk-intro");
      setTimeout(()=> w.classList.remove("mdesk-intro"), 800);
    }));
  };
  requestAnimationFrame(step);
}
/* MDESK_END */
