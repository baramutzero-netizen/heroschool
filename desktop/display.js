// PC 판 화면 — 창 · 전체 화면 · 테두리 없는 전체 화면 · 창 크기(프리셋) · 자리 기억 (main.js 가 쓴다)
//
// 저장: <사용자 데이터>/display.json  {mode, w, h, x, y, max}   — w · h 는 창 안쪽 크기(DIP)
// 창 크기 프리셋은 실제 픽셀로 적는다 (1920×1080 = 배율 150% 모니터에서는 1280×720 DIP) · 모니터 작업 영역보다 큰 것은 고를 수 없다
// 테두리 없는 전체 화면 — 모니터 크기의 테두리 없는 창. 창 테두리는 실행 중에 바꿀 수 없어서 이 모드로 · 이 모드에서 바꿀 때는 창을 새로 연다
//   (게임은 그 전에 저장한다 — 게임 쪽 PCAPP 블록)
const fs = require("node:fs");
const path = require("node:path");
const {app, screen} = require("electron");

const MODES = ["window", "fullscreen", "borderless"];
const SIZES = [[1280, 720], [1600, 900], [1920, 1080], [2560, 1440]];
const MIN = {w: 960, h: 600};
const FILE = () => path.join(app.getPath("userData"), "display.json");

function load(){
  let s = {};
  try{ s = JSON.parse(fs.readFileSync(FILE(), "utf8")) || {}; }catch(e){}
  if(!MODES.includes(s.mode)) s.mode = "window";
  if(!(s.w > 0 && s.h > 0)){ const p = defaultSize(); s.w = p.w; s.h = p.h; }
  return s;
}
function save(s){ try{ fs.mkdirSync(path.dirname(FILE()), {recursive: true}); fs.writeFileSync(FILE(), JSON.stringify(s, null, 1)); }catch(e){} }

/* 처음 — 1600×900 이 들어가면 그것, 아니면 들어가는 가장 큰 프리셋 */
function defaultSize(){
  const d = screen.getPrimaryDisplay(), fit = SIZES.map(p => dip(p, d)).filter(p => fits(p, d));
  return fit.find(p => p.px[0] === 1600) || fit[fit.length - 1] || {w: Math.max(MIN.w, Math.round(d.workAreaSize.width * .8)), h: Math.max(MIN.h, Math.round(d.workAreaSize.height * .8))};
}
function dip(px, d){ const k = d.scaleFactor || 1; return {w: Math.round(px[0] / k), h: Math.round(px[1] / k), px}; }
function fits(p, d){ return p.w <= d.workAreaSize.width && p.h <= d.workAreaSize.height - 32; }   // 제목 줄 몫

/* 게임 설정 화면에 줄 상태 */
function state(win, s){
  const d = win ? screen.getDisplayMatching(win.getBounds()) : screen.getPrimaryDisplay();
  const [cw, ch] = win ? win.getContentSize() : [s.w, s.h], k = d.scaleFactor || 1;
  const sizes = SIZES.map(p => { const q = dip(p, d); return {k: p.join("x"), w: p[0], h: p[1], fits: fits(q, d), on: s.mode === "window" && Math.abs(q.w - cw) <= 1 && Math.abs(q.h - ch) <= 1}; });
  const on = sizes.find(z => z.on);                                           // 프리셋이면 그 픽셀 그대로 (1600 ÷ 1.5 = 1067 DIP × 1.5 = 1601 로 보이지 않게)
  const disp = {w: Math.round(d.size.width * k), h: Math.round(d.size.height * k)};
  const size = s.mode !== "window" ? disp : on ? {w: on.w, h: on.h} : {w: Math.round(cw * k), h: Math.round(ch * k)};   // 전체 화면 · 테두리 없음은 모니터 크기 (1919×1079 처럼 보이지 않게)
  return {mode: s.mode, size, sizes, display: {w: Math.round(d.size.width * k), h: Math.round(d.size.height * k), scale: k}, max: !!(win && win.isMaximized()), version: app.getVersion()};
}

/* BrowserWindow 옵션 — 모드에 따라 */
function windowOptions(s, base){
  const d = s.x != null ? screen.getDisplayMatching({x: s.x, y: s.y, width: s.w, height: s.h}) : screen.getPrimaryDisplay();
  if(s.mode === "borderless"){
    const b = d.bounds;
    return {...base, x: b.x, y: b.y, width: b.width, height: b.height, frame: false, resizable: false, movable: false, maximizable: false, fullscreenable: false, thickFrame: false};
  }
  const o = {...base, useContentSize: true, width: s.w, height: s.h, minWidth: MIN.w, minHeight: MIN.h, frame: true, resizable: true};
  const wa = d.workArea;
  if(s.x != null && s.x >= wa.x - 8 && s.y >= wa.y - 8 && s.x + 80 <= wa.x + wa.width && s.y + 40 <= wa.y + wa.height){ o.x = s.x; o.y = s.y; }   // 기억한 자리가 아직 화면 안이면
  return o;
}

module.exports = {MODES, SIZES, MIN, load, save, state, windowOptions, dip, fits};
