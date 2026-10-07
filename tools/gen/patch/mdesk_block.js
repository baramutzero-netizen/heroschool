/* MDESK_START — 마스터 노트 책상 (1006)
   책상 소품 배치판(2판)으로 사용자가 정한 배치(desk_layout.json)를 배치판 자신의 그리기 코드로 구운 그림(MDESK_ART · 1배 607×466)을
   마을 지도와 같은 액자 안에 띄운다. 가로 화면(townMode)에서만 — 세로 · 좁은 화면은 예전 마스터 노트(학원 정보 · 마스터 육성 서브탭) 그대로.
   누를 수 있는 소품: 말린 지도(튜토리얼) · 책 더미(마스터 육성 팝업) · 안경 + 회중시계(학원 정보 팝업) · 펼친 책(학생) · 두루마리(스케줄).
   누르는 자리는 그림 픽셀 그대로(MDESK_GEO.hit — 줄마다 [시작, 길이, 묶음]) — 위에 얹힌 다른 소품(잉크병 · 깃펜 등)은 누르지 않는다.
   남은 마스터 육성 포인트가 있으면 책 더미 오른쪽 위에 -15도로 기운 표식.
   두루마리를 누르면(mdeskGo) — 두루마리 위 내용이 사라지고, 책상이 두루마리로 다가가며 액자가 스케줄 크기로 줄어든 뒤
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
  const B = G.books;
  const badge = pts > 0 ? `<span class="mdbadge" style="left:${(B.bx / G.size[0] * 100).toFixed(3)}%;top:${(B.by / G.size[1] * 100).toFixed(3)}%" title="남은 마스터 육성 포인트">${pts}</span>` : "";
  return `<section class="town mdesk${pop ? " popopen" : ""}" aria-label="마스터 노트">`
    + `<div class="townmap mdesk-map"${pop ? " inert" : ""}><div class="townmap-in mdesk-in"><div class="mdesk-art">`
    + img(A.base) + img(A.items, "md-items") + img(A.props) + img(A.vig) + img(A.light, "md-light", mdeskBox(L.x, L.y, L.w, L.h))
    + hl + badge + btn
    + `</div></div><img class="town-frame mdesk-frame" src="${TOWN_FRAME}" alt="" draggable="false"></div>`
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
/* ── 두루마리 → 스케줄 (1006) ──
   ① 두루마리 위 내용(띠 · 카드 · 서명)이 사라진다 ② 책상이 두루마리로 다가간다 — 두 축(가운데)과 종이 가운데를 스케줄 두루마리에 맞춘다
   (MDESK_GEO.zoom — m: 책상 1배 [왼쪽 축, 오른쪽 축, 종이 세로 가운데] · s: 스케줄 무대 1배). 그동안 액자는 스케줄 무대 높이로 줄어든다
   (액자 그림을 위 · 아래 반쪽으로 나눠 아래쪽이 따라 올라온다 — 모서리가 찌그러지지 않게) ③ 끝무렵 스케줄 그림(내용 없이)이 겹쳐 나타나고
   ④ 스케줄 화면으로 바꾼 뒤 두루마리 위 내용(.sk-paper)이 떠오른다. 움직임 줄이기 설정이면 바로 넘어간다 */
function mdeskGo(){
  const go = ()=>{ UI.view = "plan"; render(); };
  const sec = document.querySelector("#view .mdesk"), map = sec && sec.querySelector(".mdesk-map");
  const reduce = typeof matchMedia === "function" && matchMedia("(prefers-reduced-motion: reduce)").matches;
  if(!map || reduce || !(typeof schedScrollOn === "function" && schedScrollOn()) || typeof SCHED_ART === "undefined" || typeof SCHED_GEO === "undefined"){ go(); return; }
  if(MDESK_GOING) return;
  const inn = map.querySelector(".mdesk-in"), art = map.querySelector(".mdesk-art"), fr = map.querySelector(".mdesk-frame");
  const R = map.getBoundingClientRect(), W = R.width, H0 = R.height, H1 = W * 1008 / 1544;
  if(!inn || !art || !fr || !W){ go(); return; }
  MDESK_GOING = true;
  delete sec.dataset.hot; art.style.cursor = "";
  const b = W * 26 / 1266, km = W * 2 / 1266, ks = W / 772, Z = MDESK_GEO.zoom;
  const s = (Z.s[1] - Z.s[0]) * ks / ((Z.m[1] - Z.m[0]) * km);
  const tx = (Z.s[0] + Z.s[1]) / 2 * ks - b - (Z.m[0] + Z.m[1]) / 2 * km * s;
  const ty = Z.s[2] * ks - b - Z.m[2] * km * s;
  const aw = W - 2 * b, ah = aw * MDESK_GEO.size[1] / MDESK_GEO.size[0];
  sec.classList.add("mdesk-go");
  /* 액자 — 위 반쪽은 그대로, 아래 반쪽은 상자 바닥에 붙어 올라온다 */
  const bot = fr.cloneNode();
  fr.classList.add("mf-top"); bot.classList.add("mf-bot");
  fr.style.height = bot.style.height = H0 + "px";
  fr.after(bot);
  map.style.aspectRatio = "auto"; map.style.height = H0 + "px";
  inn.style.cssText = `left:${b}px;top:${b}px;width:${aw}px;height:${H0 - 2 * b}px`;
  art.style.cssText = `left:0;top:0;width:${aw}px;height:${ah}px`;
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
    const t = Math.min(1, Math.max(0, (now - T0 - FADE) / ZOOM)), e = ease(t), k = 1 + (s - 1) * e, H = H0 + (H1 - H0) * e;
    map.style.height = H + "px";
    inn.style.height = (H - 2 * b) + "px";
    art.style.left = (tx * e) + "px"; art.style.top = (ty * e) + "px";
    art.style.width = (aw * k) + "px"; art.style.height = (ah * k) + "px";
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
