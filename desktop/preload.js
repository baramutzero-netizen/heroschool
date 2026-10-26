// PC 판 — 게임에 window.hsDesk 를 연다 (모든 프레임 — 게임은 화면 맞춤 iframe 안에서 돈다 · main.js 의 nodeIntegrationInSubFrames)
//   hsDesk.get()            → {mode, size:{w,h}, sizes:[{k,w,h,fits,on}], display:{w,h,scale}, max, version}
//   hsDesk.set({mode|size}) → 바뀐 상태   mode: "window" | "fullscreen" | "borderless" · size: "1600x900"
//   hsDesk.quit()           → 게임 끝 (저장은 게임이 먼저)
//   hsDesk.on(fn)           → 상태가 바뀌면 fn(state) (Alt+Enter · F11 · 창 끌기 · 모니터 바뀜)
const {contextBridge, ipcRenderer} = require("electron");

contextBridge.exposeInMainWorld("hsDesk", {
  platform: "electron",
  get: () => ipcRenderer.invoke("desk:get"),
  set: o => ipcRenderer.invoke("desk:set", o),
  quit: () => ipcRenderer.invoke("desk:quit"),
  on: fn => { if(typeof fn === "function") ipcRenderer.on("desk:changed", (e, st) => fn(st)); }
});
