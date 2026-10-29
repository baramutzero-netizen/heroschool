// 용사 학원 키우기 — PC 판 (Electron · STOVE) 메인 프로세스
//
// · 게임 파일은 app/ (tools/prepare.mjs 가 모은다) 를 app://heroschool/ 로 연다 — file:// 대신 정해진 주소라 저장(localStorage)이 이 주소에 남고
//   fetch · 오디오 버퍼 읽기가 웹판과 같이 된다. 저장 위치: %APPDATA%\HeroSchool (게임 저장 · display.json)
// · 화면 — display.js (창 · 전체 화면 · 테두리 없는 전체 화면 · 창 크기 · 자리 기억). Alt+Enter · F11 — 창 ↔ 전체 화면
// · 게임 쪽은 preload.js 의 window.hsDesk 로 설정을 읽고 바꾼다 (게임 블록 PCAPP — tools/gen/patch/pcapp_block.js)
// · 리그(Firebase) 등 https 는 그대로 · 새 창으로 여는 링크는 기본 브라우저로
const path = require("node:path");
const fs = require("node:fs");
const {Readable} = require("node:stream");
const {app, BrowserWindow, Menu, ipcMain, net, protocol, shell, screen} = require("electron");
const {pathToFileURL} = require("node:url");
const D = require("./display");

const ROOT = path.join(__dirname, "app");
const START = "app://heroschool/heroschool.html";
const TITLE = "용사 학원 키우기";

app.setPath("userData", path.join(app.getPath("appData"), "HeroSchool"));     // 저장 폴더 — 영문 이름으로 고정 (%APPDATA%\HeroSchool)
protocol.registerSchemesAsPrivileged([{scheme: "app", privileges: {standard: true, secure: true, supportFetchAPI: true, corsEnabled: true, stream: true}}]);
app.commandLine.appendSwitch("autoplay-policy", "no-user-gesture-required");   // 시작 화면 음악 — 웹판은 첫 클릭을 기다린다

let win = null, S = null, saveT = 0, quitting = false, resume = null;   // resume — 창을 새로 열 때 새 창의 게임이 이어서 열 화면 (설정 창 · 설정 화면 — 한 번만)

if(!app.requestSingleInstanceLock()) app.quit();
app.on("second-instance", () => { if(win){ if(win.isMinimized()) win.restore(); win.focus(); } });

function serve(){
  protocol.handle("app", req => {
    const u = new URL(req.url);
    if(u.pathname.startsWith("/__desk/")) return deskHttp(u);
    const p = path.normalize(path.join(ROOT, decodeURIComponent(u.pathname)));
    if(!p.startsWith(ROOT + path.sep)) return new Response("not found", {status: 404});
    const mime = MEDIA[path.extname(p).toLowerCase()];
    if(mime) return media(p, mime, req.headers.get("range"));
    return net.fetch(pathToFileURL(p).toString()).catch(() => new Response("not found", {status: 404}));
  });
}
/* 1029 — 소리 · 영상은 Range(바이트 구간) 요청에 206 으로 답한다. 사용자 1029: '메인 화면 · 왕국력 236년 · 여신 · 도움이 안되서 미안하다 · 계절 bgm 이
   잠시 재생되다가 몇 초 뒤 페이드 아웃되면서 안 들린다' (PC 빌드). net.fetch(file://) 는 Range 를 무시하고 파일을 통째로 준다 — 빌드한 exe(게임 파일이
   app.asar 안)에서는 <audio> 가 곡 길이를 읽은 데까지만 보고 ~8초로 잡는다(재생하면서 조금씩 늘어난다) → 게임의 곡 끝 처리(끝나기 3초 전부터 줄인다 ·
   BGM_END)가 5초쯤에 곡을 꺼 버렸다. npm start(asar 아님)에서는 길이를 '끝 모름'(Infinity)으로 잡아 곡 끝 처리를 건너뛰어서 드러나지 않았다.
   fs 는 Electron 이 asar 안도 읽게 해 준다 (1029 시험 — asar 로 묶은 게임: 예전 아버지 곡 8초 → 7초에 꺼짐 · 고친 뒤 178.8초 · 효과음 fetch 그대로) */
const MEDIA = {".ogg": "audio/ogg", ".mp3": "audio/mpeg", ".wav": "audio/wav", ".m4a": "audio/mp4", ".mp4": "video/mp4", ".webm": "video/webm"};
function media(p, mime, range){
  let size;
  try{ size = fs.statSync(p).size; }catch(e){ return new Response("not found", {status: 404}); }
  const head = {"Content-Type": mime, "Accept-Ranges": "bytes"};
  const m = range && /^bytes=(\d*)-(\d*)$/.exec(range.trim());
  if(!m || (m[1] === "" && m[2] === "")) return new Response(Readable.toWeb(fs.createReadStream(p)), {status: 200, headers: {...head, "Content-Length": String(size)}});
  let s, e;
  if(m[1] === ""){ s = Math.max(0, size - +m[2]); e = size - 1; }            // bytes=-N — 끝에서 N 바이트
  else { s = +m[1]; e = m[2] === "" ? size - 1 : Math.min(+m[2], size - 1); }
  if(!(s <= e) || s >= size) return new Response(null, {status: 416, headers: {...head, "Content-Range": `bytes */${size}`}});
  return new Response(Readable.toWeb(fs.createReadStream(p, {start: s, end: e})), {status: 206, headers: {...head, "Content-Range": `bytes ${s}-${e}/${size}`, "Content-Length": String(e - s + 1)}});
}

function remember(){                                                          // 창 모드에서 크기 · 자리 (끌어서 바꾼 것도)
  if(!win || win.isDestroyed() || S.mode !== "window" || win.isFullScreen()) return;
  S.max = win.isMaximized();
  if(!S.max && !win.isMinimized()){ const [w, h] = win.getContentSize(), [x, y] = win.getPosition(); Object.assign(S, {w, h, x, y}); }
  clearTimeout(saveT); saveT = setTimeout(() => D.save(S), 400);
}
function tell(){                                                              // 게임(모든 프레임 — 게임은 화면 맞춤 iframe 안에서 돈다)에 바뀐 상태
  if(!win || win.isDestroyed()) return;
  const st = D.state(win, S);
  try{ win.webContents.mainFrame.framesInSubtree.forEach(f => { try{ f.send("desk:changed", st); }catch(e){} }); }catch(e){}
}

function open(){
  const base = {title: TITLE, backgroundColor: "#F6F3E9", show: false, autoHideMenuBar: true, icon: path.join(__dirname, "build", "icon.png"),
    webPreferences: {preload: process.env.HS_NO_PRELOAD ? undefined : path.join(__dirname, "preload.js"),   // HS_NO_PRELOAD — 시험용 (preload 없이 __desk 다리만)
      contextIsolation: true, sandbox: true, nodeIntegrationInSubFrames: true, backgroundThrottling: false, spellcheck: false}};
  const w = new BrowserWindow(D.windowOptions(S, base));
  w.webContents.setWindowOpenHandler(({url}) => { if(/^https?:/i.test(url)) shell.openExternal(url); return {action: "deny"}; });
  w.webContents.on("will-navigate", (e, url) => { if(!url.startsWith("app://")){ e.preventDefault(); if(/^https?:/i.test(url)) shell.openExternal(url); } });
  w.webContents.on("before-input-event", (e, input) => {
    if(input.type !== "keyDown") return;
    if(input.key === "F11" || (input.alt && input.key === "Enter")){ e.preventDefault(); setMode(S.mode === "window" ? "fullscreen" : "window"); }
    else if(!app.isPackaged && input.control && input.shift && input.key.toLowerCase() === "i") w.webContents.toggleDevTools();
  });
  w.on("resize", remember); w.on("move", remember); w.on("maximize", remember); w.on("unmaximize", remember);
  w.on("enter-full-screen", () => { if(S.mode === "window"){ S.mode = "fullscreen"; D.save(S); } tell(); });
  w.on("leave-full-screen", () => { if(S.mode === "fullscreen"){ S.mode = "window"; D.save(S); } tell(); });
  w.once("ready-to-show", () => {
    if(S.mode === "fullscreen") w.setFullScreen(true);
    else if(S.mode === "window" && S.max) w.maximize();
    w.show(); w.focus();
  });
  w.on("closed", () => { if(win === w) win = null; });
  w.loadURL(START);
  return w;
}

/* 모드 — 창 ↔ 전체 화면은 그 창에서 · 테두리 없는 전체 화면이 끼면 창을 새로 연다 (테두리는 실행 중에 바꿀 수 없다) */
function setMode(m){
  if(!D.MODES.includes(m) || !win) return;
  const prev = S.mode;
  if(prev === m) return;
  if(prev === "borderless" || m === "borderless"){
    S.mode = m; D.save(S);
    const old = win; win = open();
    win.once("ready-to-show", () => { if(!old.isDestroyed()) old.destroy(); });
    return;
  }
  S.mode = m; D.save(S);
  if(m === "fullscreen") win.setFullScreen(true);
  else { win.setFullScreen(false); setTimeout(() => { if(win && !win.isFullScreen()) { win.setContentSize(S.w, S.h); tell(); } }, 120); }
}
function setSize(k){
  if(!win) return;
  const p = D.SIZES.find(x => x.join("x") === k); if(!p) return;
  const d = screen.getDisplayMatching(win.getBounds()), q = D.dip(p, d);
  if(!D.fits(q, d)) return;
  if(S.mode !== "window") setMode("window");
  if(win.isMaximized()) win.unmaximize();
  Object.assign(S, {w: q.w, h: q.h, max: false});
  win.setContentSize(q.w, q.h); win.center(); remember(); tell();
}

/* 게임 ↔ 창 — preload 의 hsDesk(IPC) 와 같은 일을 app://heroschool/__desk/ 주소로도 (1026 — preload 가 게임 프레임에 닿지 않는 PC 에서도 화면 설정이 보이게 · 게임 PCAPP 의 대신 다리) */
function deskGet(fromNew){
  const st = D.state(win, S);
  if(resume && fromNew){ st.resume = resume; resume = null; }   // 1026 — 테두리 없는 전체 화면으로 · 에서 바꾸면 창을 새로 연다: 새 창이 보던 설정을 다시 연다
  return st;
}
function deskSet(o){
  o = o || {};
  if(o.mode){ const m = String(o.mode); if(m !== S.mode && (m === "borderless" || S.mode === "borderless")) resume = (o.resume === "opt" || o.resume === "title") ? o.resume : null; setMode(m); }
  if(o.size) setSize(String(o.size));
  setTimeout(tell, 200);
  return D.state(win, S);
}
function deskHttp(u){
  const op = u.pathname.slice("/__desk/".length), J = o => new Response(JSON.stringify(o), {headers: {"content-type": "application/json", "cache-control": "no-store"}});
  try{
    if(op === "get") return J(deskGet(u.searchParams.get("first") === "1"));
    if(op === "set"){ let o = {}; try{ o = JSON.parse(u.searchParams.get("o") || "{}"); }catch(e){} return J(deskSet(o)); }
    if(op === "quit"){ quitting = true; setTimeout(() => app.quit(), 50); return J({ok: true}); }
  }catch(e){ return J({error: String(e && e.message || e)}); }
  return new Response("not found", {status: 404});
}
ipcMain.handle("desk:get", e => deskGet(!!(win && e.sender === win.webContents)));
ipcMain.handle("desk:set", (e, o) => deskSet(o));
ipcMain.handle("desk:quit", () => { quitting = true; app.quit(); });

app.whenReady().then(() => {
  Menu.setApplicationMenu(null);
  serve();
  S = D.load();
  win = open();
  screen.on("display-metrics-changed", tell);
});
app.on("window-all-closed", () => app.quit());
