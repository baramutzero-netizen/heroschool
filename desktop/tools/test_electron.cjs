// (선택) PC 판 시험 — 리눅스 클라우드에서: xvfb + openbox 위에 Electron 을 띄워 화면 설정을 확인한다
//
//   cd desktop && npm install && node tools/prepare.mjs
//   xvfb-run -a -s "-screen 0 1920x1080x24" sh -c "openbox & sleep 1; node tools/test_electron.cjs"
//
// 확인: 시작 화면 EXIT · 채팅 숨김 · 시작 화면 설정 칸 · 설정 화면 줄(1920×1080 이상은 1080 모니터에 안 들어감) · 창 크기 1280×720 · 전체 화면 · F11 · Alt+Enter ·
//       테두리 없는 전체 화면(창을 새로 연다 · 저장이 남는다) · 다시 창 · 다시 실행해도 크기 · 저장 기억
// playwright 는 navigator.webdriver 라 게임이 화면 맞춤 틀을 만들지 않는다 → ?scale=user 로 다시 연다 (진짜 실행에서는 그대로 틀)
const {_electron} = require("playwright");
const path = require("node:path"), fs = require("node:fs"), os = require("node:os");
const DIR = path.dirname(__dirname), HOME = fs.mkdtempSync(path.join(os.tmpdir(), "hsdesk-")), FAIL = [];
const ok = (c, m) => { console.log((c ? "  ok  " : "  XX  ") + m); if(!c) FAIL.push(m); };
const W = app => app.evaluate(({BrowserWindow}) => BrowserWindow.getAllWindows().map(w => ({c: w.getContentSize(), fs: w.isFullScreen()})));
const key = (app, k, mod) => app.evaluate(({BrowserWindow}, [k, mod]) => BrowserWindow.getAllWindows()[0].webContents.sendInputEvent({type: "keyDown", keyCode: k, modifiers: mod}), [k, mod || []]);
async function inner(win){ for(let i = 0; i < 80; i++){ const f = win.frames().find(f => f.url().includes("hsf=")); if(f) return f; await win.waitForTimeout(250); } return null; }
async function boot(win){ await win.waitForTimeout(1500); await win.goto("app://heroschool/heroschool.html?scale=user", {waitUntil: "commit"}); const f = await inner(win); if(f) await f.waitForSelector(".title-screen #tQuit", {timeout: 20000}).catch(() => {}); await win.waitForTimeout(800); return f; }
async function launch(){
  const app = await _electron.launch({executablePath: require("electron"), args: ["--no-sandbox", DIR], cwd: DIR, env: {...process.env, HOME, APPDATA: HOME}});
  return [app, await app.firstWindow()];
}
(async () => {
  let [app, win] = await launch(), fr = await boot(win);
  ok(fr && await fr.evaluate(() => !!window.hsDesk && !!document.querySelector("#tQuit")), "게임에 hsDesk · 시작 화면 EXIT");
  ok(await fr.evaluate(() => !chatOn() && !document.getElementById("chatRoot")), "채팅 숨김 (PC 판)");
  await fr.evaluate(() => titleSettingsOpen()); await win.waitForTimeout(500);
  ok(await fr.evaluate(() => document.querySelector("#titlePcMode")?.value === "window" && !!document.querySelector("#titlePcSize")), "시작 화면 설정 — 화면 모드 · 창 크기 칸");
  await fr.evaluate(() => { document.querySelector(".title-settings")?.remove(); if(window.FST) FST.start = () => false; newScenarioStart("PC 학원"); closeModal(); UI.view = "opt"; render(); });
  await win.waitForTimeout(1200);
  const row = await fr.evaluate(() => [...document.querySelectorAll("section.pc-row button")].map(b => b.dataset.pcmode || b.dataset.pcsize || "quit"));
  ok(row.length === 8, "설정 화면 — 모드 셋 · 크기 넷 · 끝내기 " + row.join(","));
  await fr.click('section.pc-row [data-pcsize="1280x720"]'); await win.waitForTimeout(800);
  ok(JSON.stringify((await W(app))[0].c) === "[1280,720]", "창 크기 1280×720");
  await fr.evaluate(() => PCAPP.set({mode: "fullscreen"})); await win.waitForTimeout(1500);
  ok((await W(app))[0].fs, "전체 화면");
  await key(app, "F11"); await win.waitForTimeout(1500);
  ok(!(await W(app))[0].fs && JSON.stringify((await W(app))[0].c) === "[1280,720]", "F11 — 창 (크기 그대로)");
  await key(app, "Enter", ["alt"]); await win.waitForTimeout(1500);
  ok((await W(app))[0].fs, "Alt+Enter — 전체 화면");
  await key(app, "Enter", ["alt"]); await win.waitForTimeout(1500);
  const nw = app.waitForEvent("window");
  await fr.evaluate(() => PCAPP.set({mode: "borderless"}));
  win = await nw; fr = await boot(win);
  ok(await fr.evaluate(async () => (await hsDesk.get()).mode === "borderless" && localStorage.length > 0), "테두리 없는 전체 화면 — 창을 새로 열고 저장이 남는다");
  const nw2 = app.waitForEvent("window");
  await fr.evaluate(() => PCAPP.set({mode: "window"}));
  win = await nw2; await win.waitForTimeout(2500);
  ok(JSON.stringify((await W(app)).map(w => w.c)) === "[[1280,720]]", "다시 창 — 1280×720 · 창 하나");
  await app.close();
  [app, win] = await launch(); fr = await boot(win);
  ok(JSON.stringify((await W(app))[0].c) === "[1280,720]" && await fr.evaluate(() => !document.querySelector("#tCont")?.disabled), "다시 실행 — 크기 · 저장(이어하기) 기억");
  await app.close();
  console.log("\n" + (FAIL.length ? "실패 " + FAIL.length : "통과"));
  process.exit(FAIL.length ? 1 : 0);
})().catch(e => { console.error(e); process.exit(1); });
