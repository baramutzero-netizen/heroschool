/* ── 도트 스프라이트 런타임 ─────────────────────────────────
   시트: 가로=프레임, 세로=모션 5행. 아틀라스는 직업별로 5행씩 세로로 쌓여 있다.
   canvas.spr 엘리먼트를 rAF 한 바퀴로 전부 갱신한다. 프레임 위상을 엘리먼트가
   아니라 시계에서 가져오기 때문에 DOM 을 통째로 다시 그려도 튀지 않는다.
   머리색은 팔레트 치환 — 원본 아틀라스에서 머리 계열 색만 갈아끼운 사본을
   (직업 × 색) 단위로 만들어 캐시한다. 그림은 한 장만 있으면 된다. */
const SPR_M   = {idle:0, attack:1, hit:2, down:3, win:4};
const SPR_MS  = [180, 70, 90, 110, 150];
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
  return `<canvas class="spr${o.flip?" flip":""}${o.cls?" "+o.cls:""}"`
    + ` width="${SPR_CELL}" height="${SPR_CELL}"`
    + ` data-j="${SPR_IDX[job]}" data-p="${o.p|0}" data-m="${m}" data-n="${n}" data-ms="${ms}"`
    + ` data-t0="${o.t0||0}" style="width:${SPR_CELL*k}px;height:${SPR_CELL*k}px"></canvas>`;
}
/* ── 팔레트 치환 사본 캐시 (LRU) ── */
const SPR_BASE = new Image();
let SPR_READY = false, SPR_RAF = 0, SPR_T0 = 0;
const SPR_CACHE = new Map(), SPR_CAP = 20;
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
function sprSheet(ji, pi){
  const key = ji+"|"+pi;
  let cv = SPR_CACHE.get(key);
  if(cv){ SPR_CACHE.delete(key); SPR_CACHE.set(key, cv); return cv; }   // LRU 갱신
  const job = SPR_KEYS[ji];
  const W = SPR_COLS*SPR_CELL, H = 5*SPR_CELL;
  cv = document.createElement("canvas"); cv.width=W; cv.height=H;
  const cx = cv.getContext("2d", {willReadFrequently:true});
  cx.imageSmoothingEnabled = false;
  cx.drawImage(SPR_BASE, 0, ji*H, W, H, 0, 0, W, H);
  const hairs = (typeof SPR_HAIR!=="undefined" && SPR_HAIR[job]) || [];
  const P = sprPal(pi);
  if(P && hairs.length){
    const lut = new Map();
    hairs.forEach(hx=>{
      const r=parseInt(hx.slice(0,2),16), g=parseInt(hx.slice(2,4),16), b=parseInt(hx.slice(4,6),16);
      const v = sprHsv(r,g,b);
      lut.set((r<<16)|(g<<8)|b, sprRgb(P.h, Math.min(1, v[1]*P.s), v[2]));
    });
    const im = cx.getImageData(0,0,W,H), d = im.data;
    for(let i=0;i<d.length;i+=4){
      if(d[i+3]===0) continue;
      const nc = lut.get((d[i]<<16)|(d[i+1]<<8)|d[i+2]);
      if(nc){ d[i]=nc[0]; d[i+1]=nc[1]; d[i+2]=nc[2]; }
    }
    cx.putImageData(im,0,0);
  }
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
    let f;
    if(SPR_LOOP[m]) f = Math.floor(now/ms) % n;
    else {
      const t0 = +el.dataset.t0;
      if(!t0) f = n-1;                          // t0 없으면 = 이미 끝난 모션, 마지막 프레임 유지
      else { f = Math.floor((now-t0)/ms); if(f>=n) f=n-1; if(f<0) f=0; }
    }
    if(el.__f===f && el.__key===j+"|"+pi+"|"+m) continue;
    el.__f=f; el.__key=j+"|"+pi+"|"+m;
    const cx = el.__cx || (el.__cx = el.getContext("2d"));
    cx.imageSmoothingEnabled = false;
    cx.clearRect(0,0,SPR_CELL,SPR_CELL);
    cx.drawImage(sprSheet(j,pi), f*SPR_CELL, m*SPR_CELL, SPR_CELL, SPR_CELL, 0,0, SPR_CELL, SPR_CELL);
  }
}
function sprStart(){
  if(!SPR_BASE.src){
    SPR_BASE.onload = ()=>{ SPR_READY = true; };
    SPR_BASE.src = SPR_IMG;
  }
  if(!SPR_RAF) sprTick();
}
