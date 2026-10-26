// (선택) 1026 둘째 PC 판 점검 — xvfb-run -a -s "-screen 0 2560x1440x24" sh -c "openbox & sleep 1; node tools/check_pc2.cjs"
//  — 설정 창 두 줄(아주 크게 · 스크롤 없음) · 속도 ×1 · ×2 · 격자 숨김 · 시작 화면 음악 · 메뉴 마우스 소리 · 테두리 없음으로 바꾼 뒤 설정 창이 다시 열린다
const {_electron} = require("playwright");
const path = require("node:path"), fs = require("node:fs"), os = require("node:os");
const DIR = path.dirname(__dirname), HOME = fs.mkdtempSync(path.join(os.tmpdir(), "hsdesk-")), FAIL = [];
const ok = (c, m) => { console.log((c ? "  ok  " : "  XX  ") + m); if(!c) FAIL.push(m); };
async function inner(win){ for(let i = 0; i < 80; i++){ const f = win.frames().find(f => f.url().includes("hsf=")); if(f) return f; await win.waitForTimeout(250); } return null; }
async function boot(win){ await win.waitForTimeout(1500); const f = await inner(win); if(f) await f.waitForSelector(".title-screen #tQuit", {timeout: 20000}).catch(() => {}); await win.waitForTimeout(1200); return f; }
const sz = (app, w, h) => app.evaluate(({BrowserWindow}, [w, h]) => BrowserWindow.getAllWindows()[0].setContentSize(w, h), [w, h]);
(async () => {
  const app = await _electron.launch({executablePath: require("electron"), args: ["--no-sandbox", "--disable-blink-features=AutomationControlled", DIR], cwd: DIR, env: {...process.env, HOME, APPDATA: HOME}});
  let win = await app.firstWindow(); let fr = await boot(win);
  ok(!!fr, "화면 맞춤 틀 안의 게임");
  ok(await fr.evaluate(() => typeof ANOW !== "undefined" && !!ANOW && ANOW.key === "title" || (typeof AOVER !== "undefined" && AOVER === "title")), "시작 화면 음악 title");
  ok(await fr.evaluate(() => JSON.stringify(BSPEEDS) === "[280,120]"), "전투 재생 속도 ×1 · ×2");
  // 마우스 소리
  await fr.evaluate(() => { window.__sfx = []; const f0 = sfxPlay; window.sfxPlay = function(k){ window.__sfx.push(k); return f0.apply(this, arguments); }; });
  for(const id of ["#tNew", "#tSettings", "#tQuit"]){ const b = await fr.$(id); await b.hover(); await win.waitForTimeout(150); }
  ok(await fr.evaluate(() => window.__sfx.filter(k => k === "xm_hover").length >= 3), "메뉴 마우스 소리 " + await fr.evaluate(() => window.__sfx.join(",")));
  for(const [w, h] of [[1280, 720], [1600, 900], [1920, 1080]]){
    await sz(app, w, h); await win.waitForTimeout(900);
    for(const f of ["normal", "xlarge"]){
      await fr.evaluate(v => { document.querySelector(".title-settings")?.close(); if(window.FSZ) FSZ.set(v, true); }, f); await win.waitForTimeout(300);
      await fr.evaluate(() => titleSettingsOpen()); await win.waitForTimeout(700);
      const m = await fr.evaluate(() => { const d = document.querySelector(".title-settings"); return {pc2: d.classList.contains("pc2"), sh: d.scrollHeight, ch: d.clientHeight, grid: !!d.querySelector('[data-title-pref="bfGrid"]'), sp: [...d.querySelectorAll("#titleBattleSpeed option")].map(o => o.textContent).join(" "), foot: (d.querySelector("footer") || {}).innerText}; });
      ok(m.pc2 && m.sh <= m.ch + 1 && !m.grid && m.sp === "×1 ×2", `${w}×${h} ${f} — 두 줄 · 스크롤 없음 (${m.sh}/${m.ch}) · 격자 없음 · 속도 ${m.sp}`);
      if(w === 1280 || w === 1920) await win.screenshot({path: `/tmp/claude-0/pr/pc2_${w}_${f}.png`});
    }
  }
  await fr.evaluate(() => { document.querySelector(".title-settings")?.close(); FSZ.set("normal", true); });
  await sz(app, 1600, 900); await win.waitForTimeout(600);
  // 테두리 없음 — 설정 창에서 바꾸면 새 창에서 설정 창이 다시 열린다
  await fr.evaluate(() => titleSettingsOpen()); await win.waitForTimeout(500);
  const nw = app.waitForEvent("window");
  await fr.evaluate(() => { const s = document.querySelector("#titlePcMode"); s.value = "borderless"; s.dispatchEvent(new Event("change")); });
  win = await nw; await win.waitForTimeout(2500); fr = await inner(win);
  await fr.waitForSelector(".title-settings #titlePcMode", {timeout: 15000}).catch(() => {});
  const b = await fr.evaluate(() => { const d = document.querySelector(".title-settings"); return d ? {mode: d.querySelector("#titlePcMode") && d.querySelector("#titlePcMode").value, size: d.querySelector("#titlePcSize") && d.querySelector("#titlePcSize").selectedOptions[0] && d.querySelector("#titlePcSize").selectedOptions[0].textContent} : null; });
  ok(b && b.mode === "borderless", "테두리 없음 — 새 창에서 설정 창이 다시 열린다 " + JSON.stringify(b));
  await win.screenshot({path: "/tmp/claude-0/pr/pc2_borderless.png"});
  // 게임 설정 화면에서 바꾸기 — 다시 창으로 · 설정 화면으로 돌아온다
  await fr.evaluate(() => { document.querySelector(".title-settings")?.close(); if(window.FST) FST.start = () => false; newScenarioStart("PC 학원"); closeModal(); UI.view = "opt"; render(); });
  await win.waitForTimeout(1200);
  const nw2 = app.waitForEvent("window");
  await fr.evaluate(() => document.querySelector('section.pc-row [data-pcmode="window"]').click());
  win = await nw2; await win.waitForTimeout(3000); fr = await inner(win);
  await fr.waitForSelector("section.pc-row", {timeout: 15000}).catch(() => {});
  ok(await fr.evaluate(() => UI.view === "opt" && !!document.querySelector("section.pc-row") && !document.querySelector("#optBfGrid")), "설정 화면에서 바꾸면 — 새 창도 설정 화면 · 격자 줄 없음");
  await app.close();
  console.log("\n" + (FAIL.length ? "실패 " + FAIL.length : "통과"));
  process.exit(FAIL.length ? 1 : 0);
})().catch(e => { console.error(e); process.exit(1); });
