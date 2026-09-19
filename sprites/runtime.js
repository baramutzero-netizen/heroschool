/* ── 도트 스프라이트 런타임 ─────────────────────────────────
   독립 256px 프레임을 SPR_META 사각형으로 읽는다. 기준점은 (128,170).
   canvas.spr 엘리먼트를 rAF 한 바퀴로 전부 갱신한다. 프레임 위상을 엘리먼트가
   아니라 시계에서 가져오기 때문에 DOM 을 통째로 다시 그려도 튀지 않는다.
   머리색은 팔레트 치환 — 원본 아틀라스에서 머리 계열 색만 갈아끼운 사본을
   (직업 × 색) 단위로 만들어 캐시한다. 그림은 한 장만 있으면 된다. */
const SPR_M   = {idle:0, attack:1, hit:2, down:3, win:4};
const SPR_MS  = [180, 70, 90, 110, 150];
const SPR_PLAYBACK_RATE = 0.7; // 70% 속도: 모션 길이는 약 1.43배
const SPR_LOOP= [1, 0, 0, 0, 1];
const SPR_KEYS= Object.keys(SPR_JOB);
const SPR_IDX = (()=>{ const o={}; SPR_KEYS.forEach((k,i)=>o[k]=i); return o; })();
/* 머리색 — 원본의 명도·채도 단계는 그대로 두고 색상만 돌린다.
   색상 24단 × 진하기 3단 = 72가지. 열두 명이면 겹칠 일이 거의 없다. */
const SPR_HUE_N = 24, SPR_TONE = [1.00, .70, .25];
const SPR_HUE_NAME = ["빨강","주홍","주황","호박","노랑","연노랑","연두","풀색","초록","비취","청록","터콰즈",
                      "하늘","담청","파랑","군청","남색","보라","자주","자수정","진분홍","분홍","연분홍","산호"];
const SPR_TONE_NAME = ["선명한","차분한","옅은"];
function sprPal(pi){
  pi = pi|0;
  const hi = pi % SPR_HUE_N, ti = Math.floor(pi/SPR_HUE_N) % SPR_TONE.length;
  return {h: hi/SPR_HUE_N, s: SPR_TONE[ti]};
}
function sprHas(job){ return !!SPR_JOB[job]; }
function sprN(job,m){ const a=SPR_JOB[job]; return a? (a[m]|0) : 0; }
/* 학생 ID 로 고정 — 졸업할 때까지 안 바뀐다 */
function sprPalOf(o){
  const k = String((o && (o.id || o.sid || o.ref || o.name)) || "");
  let h = 2166136261;
  for(let i=0;i<k.length;i++){ h ^= k.charCodeAt(i); h = Math.imul(h,16777619)>>>0; }
  h ^= h>>>15; h = Math.imul(h,2246822507)>>>0; h ^= h>>>13;
  return (((h>>>11)>>>0) % SPR_TONE.length) * SPR_HUE_N + ((h>>>0) % SPR_HUE_N);
}
function sprPalName(o){
  const pi = (typeof o==="number") ? (o|0) : sprPalOf(o);
  const hi = pi % SPR_HUE_N, ti = Math.floor(pi/SPR_HUE_N) % SPR_TONE.length;
  return SPR_TONE_NAME[ti] + " " + SPR_HUE_NAME[hi];
}
function sprHTML(job, mot, k, o){
  o = o||{};
  if(!SPR_JOB[job]) return "";
  let m = SPR_M[mot]!=null ? SPR_M[mot] : 0;
  if(!sprN(job,m)) m = 0;                       // 빈 행은 idle 로 대체
  const n = sprN(job,m) || 1;
  k = k || 1;
  const ms = o.ms || SPR_MS[m];
  return `<span class="spr-anchor" style="width:${128*k}px;height:${128*k}px"><canvas class="spr${o.flip?" flip":""}${o.cls?" "+o.cls:""}"`
    + ` width="${SPR_CELL}" height="${SPR_CELL}"${o.still?' data-still="1"':""}`
    + ` data-j="${SPR_IDX[job]}" data-p="${o.p|0}" data-m="${m}" data-n="${n}" data-ms="${ms}"`
    + ` data-t0="${o.t0||0}" style="left:${-64*k}px;top:${-64*k}px;width:${SPR_CELL*k}px;height:${SPR_CELL*k}px"></canvas></span>`;
}
/* ── 팔레트 치환 사본 캐시 (LRU) ── */
const SPR_BASE = new Image();
let SPR_READY = false, SPR_RAF = 0, SPR_T0 = 0;
const SPR_CACHE = new Map(), SPR_CAP = 180;   // 여백 포함 256×256, 최대 약 45MB
function sprHsv(r,g,b){
  r/=255; g/=255; b/=255;
  const mx=Math.max(r,g,b), mn=Math.min(r,g,b), d=mx-mn;
  let h=0;
  if(d){ h = mx===r ? ((g-b)/d+(g<b?6:0)) : mx===g ? ((b-r)/d+2) : ((r-g)/d+4); h/=6; }
  return [h, mx? d/mx : 0, mx];
}
function sprRgb(h,s,v){
  const i=Math.floor(h*6), f=h*6-i, p=v*(1-s), q=v*(1-f*s), t=v*(1-(1-f)*s);
  let r,g,b;
  switch(i%6){
    case 0: r=v;g=t;b=p; break; case 1: r=q;g=v;b=p; break; case 2: r=p;g=v;b=t; break;
    case 3: r=p;g=q;b=v; break; case 4: r=t;g=p;b=v; break; default: r=v;g=p;b=q;
  }
  return [Math.round(r*255), Math.round(g*255), Math.round(b*255)];
}
/* 머리색 치환표 — 원래 색 → 바꿀 색 */
function sprLut(job, pi){
  if(pi < 0) return null; // 원본 검수용
  const hairs = (typeof SPR_HAIR!=="undefined" && SPR_HAIR[job]) || [];
  if(!hairs.length) return null;
  const P = sprPal(pi);
  if(!P) return null;
  const lut = new Map();
  hairs.forEach(hx=>{
    const r=parseInt(hx.slice(0,2),16), g=parseInt(hx.slice(2,4),16), b=parseInt(hx.slice(4,6),16);
    const v = sprHsv(r,g,b);
    lut.set((r<<16)|(g<<8)|b, sprRgb(P.h, Math.min(1, v[1]*P.s), v[2]));
  });
  return lut;
}
function sprSwap(cx, w, h, lut){
  const im = cx.getImageData(0,0,w,h), d = im.data;
  for(let i=0;i<d.length;i+=4){
    if(d[i+3]===0) continue;
    const nc = lut.get((d[i]<<16)|(d[i+1]<<8)|d[i+2]);
    if(nc){ d[i]=nc[0]; d[i+1]=nc[1]; d[i+2]=nc[2]; }
  }
  cx.putImageData(im,0,0);
}
/* 칸 하나만 칠해 둔다 — 시트 한 장을 통째로 칠하는 것보다 서른 배 싸다.
   순위표처럼 도트가 수십 개 뜨는 화면에서도 캐시가 밀려나지 않는다. */
function sprCellCv(ji, pi, m, f){
  const key = ji+"|"+pi+"|"+m+"|"+f;
  let cv = SPR_CACHE.get(key);
  if(cv){ SPR_CACHE.delete(key); SPR_CACHE.set(key, cv); return cv; }   // LRU 갱신
  cv = document.createElement("canvas"); cv.width = SPR_CELL; cv.height = SPR_CELL;
  const cx = cv.getContext("2d", {willReadFrequently:true});
  cx.imageSmoothingEnabled = false;
  const frame = SPR_META[SPR_KEYS[ji]][m][f];
  cx.drawImage(SPR_BASE, ...frame.rect, 0, 0, SPR_CELL, SPR_CELL);
  const lut = sprLut(SPR_KEYS[ji], pi);
  if(lut) sprSwap(cx, SPR_CELL, SPR_CELL, lut);
  // 이펙트는 복장 색상 교체와 분리한다.
  if(frame.fx) cx.drawImage(SPR_BASE, ...frame.fx, 0, 0, SPR_CELL, SPR_CELL);
  SPR_CACHE.set(key, cv);
  if(SPR_CACHE.size > SPR_CAP) SPR_CACHE.delete(SPR_CACHE.keys().next().value);
  return cv;
}
function sprTick(){
  SPR_RAF = requestAnimationFrame(sprTick);
  if(!SPR_READY) return;
  const now = performance.now();
  const list = document.querySelectorAll("canvas.spr");
  for(let q=0;q<list.length;q++){
    const el = list[q];
    const m = +el.dataset.m, n = +el.dataset.n || 1, j = +el.dataset.j, pi = +el.dataset.p || 0;
    const ms = +el.dataset.ms || SPR_MS[m] || 120;
    const t0 = +el.dataset.t0;
    const f = el.dataset.still ? 0 : sprFrameAt(j, m, SPR_LOOP[m] ? now : now-t0, ms, !t0);
    if(el.__f===f && el.__key===j+"|"+pi+"|"+m) continue;
    el.__f=f; el.__key=j+"|"+pi+"|"+m;
    const cx = el.__cx || (el.__cx = el.getContext("2d"));
    cx.imageSmoothingEnabled = false;
    cx.clearRect(0,0,SPR_CELL,SPR_CELL);
    cx.drawImage(sprCellCv(j, pi, m, f), 0, 0);
  }
  fxTick(now);
}
// 개별 프레임의 상대 시간을 보존하면서 전투 속도(ms)는 기존과 동일하게 맞춘다.
function sprFrameAt(j, m, elapsed, ms, ended){
  const frames = SPR_META[SPR_KEYS[j]][m];
  if(!SPR_LOOP[m] && ended) return frames.length-1;
  const rawTotal = frames.reduce((s,f)=>s+f.duration,0);
  const total = frames.length*ms/SPR_PLAYBACK_RATE;
  let t = SPR_LOOP[m] ? ((elapsed%total)+total)%total : Math.max(0,Math.min(elapsed,total));
  for(let i=0;i<frames.length;i++){
    t -= frames[i].duration/rawTotal*total;
    if(t < 0) return i;
  }
  return frames.length-1;
}
/* ══════ 스킬 이펙트 ══════
   형태 6종을 한 장으로만 그려두고, 원소별로 색상·채도·명도만 돌려 쓴다.
   전투 프레임이 "누구에게 무슨 이펙트"를 들고 오면 대상 카드 위에 한 번 재생한다. */
const FX_IDX = (()=>{ const o={}; (typeof FX_KEYS!=="undefined"?FX_KEYS:[]).forEach((k,i)=>o[k]=i); return o; })();
const FX_EL = {
  phys  : {h:.58, s:.24, v:1.00},
  fire  : {h:.045,s:1.15,v:1.00},
  frost : {h:.53, s:1.00,v:1.00},
  arcane: {h:.75, s:1.05,v:1.00},
  holy  : {h:.125,s:.95, v:1.00},
  dark  : {h:.80, s:1.10,v:.66},
  poison: {h:.27, s:1.10,v:.92},
  heal  : {h:.35, s:.90, v:1.00},
  buff  : {h:.12, s:.95, v:1.00},
  debuff: {h:.72, s:.75, v:.78}
};
const FX_ELK = Object.keys(FX_EL);
const FX_BASE = new Image();
let FX_READY = false;
const FX_CACHE = new Map(), FX_CAP = 32;   // 한 전투에서 최대 15종까지 나온다 — 캐시가 밀리면 매 프레임 다시 칠한다
/* 투명도 — 0 이면 그대로, 100 이면 아예 안 나온다. 기본값은 반투명. */
const FX_A_DEFAULT = 50;
function fxAlpha(){
  const v = (S && S.opts && typeof S.opts.fxA === "number") ? S.opts.fxA : FX_A_DEFAULT;
  return clamp(1 - v/100, 0, 1);
}
function fxSheet(fi, el){
  const key = fi+"|"+el;
  let cv = FX_CACHE.get(key);
  if(cv){ FX_CACHE.delete(key); FX_CACHE.set(key, cv); return cv; }
  const W = FX_N*FX_CELL, H = FX_CELL;
  cv = document.createElement("canvas"); cv.width=W; cv.height=H;
  const cx = cv.getContext("2d", {willReadFrequently:true});
  cx.imageSmoothingEnabled = false;
  cx.drawImage(FX_BASE, 0, fi*FX_CELL, W, H, 0, 0, W, H);
  const P = FX_EL[el] || FX_EL.phys;
  const im = cx.getImageData(0,0,W,H), d = im.data;
  for(let i=0;i<d.length;i+=4){
    if(d[i+3]===0) continue;
    const v = sprHsv(d[i], d[i+1], d[i+2]);
    const c = sprRgb(P.h, Math.min(1, v[1]*P.s), Math.min(1, v[2]*P.v));
    d[i]=c[0]; d[i+1]=c[1]; d[i+2]=c[2];
  }
  cx.putImageData(im,0,0);
  FX_CACHE.set(key, cv);
  if(FX_CACHE.size > FX_CAP) FX_CACHE.delete(FX_CACHE.keys().next().value);
  return cv;
}
function fxHTML(name, el, ms, k, t0){
  if(typeof FX_KEYS==="undefined" || FX_IDX[name]==null) return "";
  const a = fxAlpha();
  if(a <= 0) return "";
  k = k || 1;
  return `<canvas class="fxspr" width="${FX_CELL}" height="${FX_CELL}"`
    + ` data-x="${FX_IDX[name]}" data-e="${el||"phys"}" data-ms="${Math.max(18, ms||32)}"`
    + ` data-t0="${t0 || SPR_T0 || 0}" style="width:${FX_CELL*k}px;height:${FX_CELL*k}px;opacity:${a.toFixed(2)}"></canvas>`;
}
function fxTick(now){
  if(!FX_READY) return;
  const list = document.querySelectorAll("canvas.fxspr");
  for(let q=0;q<list.length;q++){
    const el = list[q];
    const x = +el.dataset.x, ms = +el.dataset.ms || 32, t0 = +el.dataset.t0;
    const e = el.dataset.e || "phys";
    let f = t0 ? Math.floor((now-t0)/ms) : FX_N-1;
    if(f >= FX_N){ if(el.__f !== -1){ el.__f=-1; const c=el.__cx||(el.__cx=el.getContext("2d")); c.clearRect(0,0,FX_CELL,FX_CELL); } continue; }
    if(f < 0) f = 0;
    if(el.__f===f && el.__key===x+"|"+e) continue;
    el.__f=f; el.__key=x+"|"+e;
    const cx = el.__cx || (el.__cx = el.getContext("2d"));
    cx.imageSmoothingEnabled = false;
    cx.clearRect(0,0,FX_CELL,FX_CELL);
    cx.drawImage(fxSheet(x,e), f*FX_CELL, 0, FX_CELL, FX_CELL, 0,0, FX_CELL, FX_CELL);
  }
}
function sprStart(){
  if(!SPR_BASE.src){
    SPR_BASE.onload = ()=>{ SPR_READY = true; };
    SPR_BASE.src = SPR_IMG;
  }
  if(typeof FX_IMG!=="undefined" && !FX_BASE.src){
    FX_BASE.onload = ()=>{ FX_READY = true; };
    FX_BASE.src = FX_IMG;
  }
  if(!SPR_RAF) sprTick();
}
sprStart();
