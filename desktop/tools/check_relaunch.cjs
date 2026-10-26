// (선택) 1026 셋째 — 새 게임 · 학원 이름 → 끄고 다시 켜면 시작 화면에서 오류(render · S.acadName)가 나지 않는다 · 처음 켜면 글자 크기 '크게'
//  xvfb-run -a -s "-screen 0 2560x1440x24" sh -c "openbox & sleep 1; node tools/check_relaunch.cjs"
const {_electron} = require("playwright");
const path = require("node:path"), fs = require("node:fs"), os = require("node:os");
const DIR = path.dirname(__dirname), HOME = fs.mkdtempSync(path.join(os.tmpdir(), "hsdesk-")), FAIL = [];
const ok = (c, m) => { console.log((c ? "  ok  " : "  XX  ") + m); if(!c) FAIL.push(m); };
async function inner(win){ for(let i = 0; i < 80; i++){ const f = win.frames().find(f => f.url().includes("hsf=")); if(f) return f; await win.waitForTimeout(250); } return null; }
async function boot(win){ await win.waitForTimeout(1500); const f = await inner(win); if(f) await f.waitForSelector(".title-screen #tQuit", {timeout: 20000}).catch(() => {}); await win.waitForTimeout(1200); return f; }
const sz = (app, w, h) => app.evaluate(({BrowserWindow}, [w, h]) => BrowserWindow.getAllWindows()[0].setContentSize(w, h), [w, h]);
async function launch(errs){
  const app = await _electron.launch({executablePath: require("electron"), args: ["--no-sandbox", "--disable-blink-features=AutomationControlled", DIR], cwd: DIR, env: {...process.env, HOME, APPDATA: HOME}});
  const win = await app.firstWindow();
  win.on("pageerror", e => errs.push(String(e).slice(0, 200)));
  win.on("console", m => { if(m.type() === "error" && !/net::|Failed to load/.test(m.text())) errs.push("console: " + m.text().slice(0, 200)); });
  return [app, win, await boot(win)];
}
(async () => {
  const e1 = [];
  let [app, win, fr] = await launch(e1);
  ok(await fr.evaluate(() => PREF.fontSize === "large" && document.documentElement.dataset.fontSize === "large"), "처음 켜면 글자 크기 크게 " + await fr.evaluate(() => PREF.fontSize));
  await fr.evaluate(() => { if(window.FST) FST.start = () => false; newScenarioStart("다시 켜기 학원"); closeModal(); render(); });
  await win.waitForTimeout(1500);
  ok(await fr.evaluate(() => !!localStorage.length), "저장됨");
  await app.close();
  const e2 = [];
  [app, win, fr] = await launch(e2);
  ok(await fr.evaluate(() => !!S && !!document.querySelector(".title-screen")), "다시 켜면 시작 화면 (세이브를 읽어 둔다)");
  await fr.evaluate(() => { window.__S0 = S; S = null; UI.view = "home"; });   // 켜는 중(세이브를 읽기 전 — S 없음)에 창 크기가 넓은 화면 경계를 넘는 경우
  for(const [w, h] of [[1000, 700], [1600, 900], [1050, 720], [1920, 1080]]){ await sz(app, w, h); await win.waitForTimeout(700); }
  await fr.evaluate(() => { window.__ew = []; window.addEventListener("error", e => window.__ew.push(String(e.message))); });
  for(const w of ["900px", "", "1000px", ""]){ await win.evaluate(w => { const f = document.querySelector("iframe"); f.style.minWidth = "0"; f.style.width = w; }, w); await win.waitForTimeout(500); }   // 틀 안 게임 폭이 1100 을 넘나든다 (켜는 중 틀이 자리 잡을 때처럼)
  const ew = await fr.evaluate(() => window.__ew); e2.push(...ew);
  await fr.evaluate(() => { S = window.__S0; });
  await win.waitForTimeout(800);
  ok(!e2.length, "다시 켜고 창 크기를 바꿔도 오류 없음 " + JSON.stringify(e2.slice(0, 3)));
  ok(await fr.evaluate(() => PREF.fontSize === "large"), "글자 크기 그대로 크게");
  await fr.evaluate(() => { FSZ.set("normal", true); });
  await app.close();
  const e3 = [];
  [app, win, fr] = await launch(e3);
  ok(await fr.evaluate(() => PREF.fontSize === "normal"), "보통으로 바꾸면 다시 켜도 보통 " + await fr.evaluate(() => PREF.fontSize));
  await app.close();
  ok(!e1.length && !e3.length, "다른 오류 없음 " + JSON.stringify(e1.concat(e3).slice(0, 3)));
  console.log("\n" + (FAIL.length ? "실패 " + FAIL.length : "통과"));
  process.exit(FAIL.length ? 1 : 0);
})().catch(e => { console.error(e); process.exit(1); });
