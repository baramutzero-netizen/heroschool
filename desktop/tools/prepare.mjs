// PC 판 준비 — 저장소의 게임(heroschool.html)과 게임이 쓰는 그림 · 소리만 desktop/app/ 에 모은다 (Electron 이 app:// 로 읽는다)
//
//   node tools/prepare.mjs            (desktop/ 에서 — npm start · npm run dist 가 먼저 부른다)
//
// · heroschool.html 은 저장소 맨 위에서 python wrap.py 로 만든 것 (없거나 game.html 보다 오래됐으면 알려 준다 — 빌드는 직접)
// · assets/ — heroschool.html 과 그 안에서 읽는 CSS · JS 글에 적힌 경로만 (끝이 폴더 · 이름 앞부분이면 그 폴더에서 이름이 맞는 것 모두)
//   이름을 코드에서 이어 붙이는 그림이 있어서 폴더째 들어가는 곳이 많다. 원본 그림(프롬프트 json · 미리보기 png)은 뺀다
// · bgm/ — .ogg 는 모두 · .mp3 는 같은 이름 .ogg 가 없을 때만 · .wav 는 1MB 아래(효과음)만 — 큰 .wav 는 원본 녹음
// · 바뀐 파일만 다시 복사한다 (크기 · 시각) · 이제 쓰지 않는 파일은 app/ 에서 지운다
// · --demo — PC 체험판 (1027 · 사용자 'stove pc 버전 데모 — 2년차 겨울에서 게임 진행이 종료' → 2년차 겨울 6주(마지막 주)를 마친 뒤 · 저장은 정식판과 같은 폴더):
//   app/heroschool.html 의 DEMO_END 를 채운다 — 게임이 그 주차를 마치면 끝 화면을 띄우고 주 · 계절을 더 넘기지 못한다 (itch 체험판과 같은 장치 ·
//   game.html demoOver · demoEndShow · endPhase · tools/itch/build_itch.py). 빌드 번호 뒤에 -demo (설정 화면 · 의견 보내기에 찍힌다).
//   끝 화면 글(DEMO_TEXT)이 끝 주차와 맞는지 본다. --demo 없이 돌리면 원래 heroschool.html 로 되돌린다 (크기가 달라 다시 복사된다)
import fs from "node:fs";
import path from "node:path";
import {fileURLToPath} from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const DESK = path.dirname(HERE);
const REPO = path.dirname(DESK);
const OUT = path.join(DESK, "app");
const GAME = path.join(REPO, "heroschool.html");
const SKIP_NAME = /(^|[-_])prompts?\.json$|-prompt\.json$|^preview-[^/]*\.png$|\.(psd|md|txt|py|wav)$/i;   // 폴더째 넣을 때 빼는 것 (원본 · 메모)
const LICENSE = /(LICENSE|LICENCE|OFL|COPYING)/i;                               // 글꼴 · 소리 사용 허락 글 — 그 폴더의 것이 하나라도 들어가면 같이 (OFL 은 같이 배포해야 한다)
const KEEP = [];                                                                // 코드에서 이름을 찾지 못해도 늘 넣을 것 (예: "assets/story_art/") — 게임에서 빠진 그림이 보이면 여기에
const TEXT = /\.(css|js|html|json|svg)$/i;
const DEMO = process.argv.includes("--demo");
const DEMO_END = '{year:2, phase:"winter", week:6}';                         // 2년차 겨울 6주차를 마치면 끝 (주차는 0 부터 — 겨울은 6주라 6 은 마지막 주를 마친 뒤)
const DEMO_TEXT = "2년차 겨울 6주차를 마쳤다";                                // game.html demoEndShow 의 끝 화면 글 — DEMO_END 를 바꾸면 이것과 game.html 글 · 번역 표도

if(!fs.existsSync(GAME)){
  console.error("heroschool.html 이 없다 — 저장소 맨 위에서 python wrap.py 를 먼저 돌린다");
  process.exit(1);
}
const gameSrc = path.join(REPO, "game.html");
if(fs.existsSync(gameSrc) && fs.statSync(gameSrc).mtimeMs > fs.statSync(GAME).mtimeMs + 1000)
  console.warn("※ game.html 이 heroschool.html 보다 새롭다 — 최신으로 하려면 python wrap.py 를 먼저");

const want = new Map();                                                       // app 안 경로 → 저장소 파일
const scanned = new Set();
const walk = d => fs.existsSync(d) ? fs.readdirSync(d, {withFileTypes: true}).flatMap(e => e.isDirectory() ? walk(path.join(d, e.name)) : [path.join(d, e.name)]) : [];
const rel = f => path.relative(REPO, f).split(path.sep).join("/");
function add(file, prefixed){
  const r = rel(file);
  if(r.startsWith("..") || want.has(r) || !fs.existsSync(file) || !fs.statSync(file).isFile()) return;
  if(prefixed && SKIP_NAME.test(path.basename(file))) return;
  want.set(r, file);
  for(const n of fs.readdirSync(path.dirname(file))) if(LICENSE.test(n)) { const l = path.join(path.dirname(file), n), lr = rel(l); if(!want.has(lr) && fs.statSync(l).isFile()) want.set(lr, l); }
  if(TEXT.test(file) && !scanned.has(r)){ scanned.add(r); scan(fs.readFileSync(file, "utf8"), path.dirname(file)); }
}
function addRef(ref, baseDir){
  ref = ref.split(/[?#]/)[0].replace(/\\/g, "/");
  if(!ref || /^(data:|https?:|blob:|#)/i.test(ref)) return;
  const abs = path.resolve(ref.startsWith("assets/") || ref.startsWith("bgm/") ? REPO : baseDir, ref.replace(/^(\.\.\/)+(?=(assets|bgm)\/)/, ""));
  if(!rel(abs).match(/^(assets|bgm)\//)) return;
  const last = path.basename(abs);
  if(/\.[a-z0-9]{2,5}$/i.test(last) && !ref.endsWith("/")){ add(abs, false); return; }
  const dir = ref.endsWith("/") ? abs : path.dirname(abs), head = ref.endsWith("/") ? "" : last;   // 이름을 이어 붙이는 경로 — 그 폴더에서 앞부분이 맞는 것 모두
  for(const f of walk(dir)) if(path.relative(dir, f).startsWith(head)) add(f, true);
}
function scan(text, baseDir){
  for(const m of text.matchAll(/(?:^|["'(`=\s,])((?:\.\.\/)*(?:assets|bgm)\/[^"'()`\s<>${}\\]*)/g)) addRef(m[1], baseDir);
  for(const m of text.matchAll(/url\(\s*["']?([^"')]+)["']?\s*\)/g)) if(!/^(data:|https?:|#)/.test(m[1])) addRef(m[1], baseDir);
}

const html = fs.readFileSync(GAME, "utf8");
want.set("heroschool.html", GAME);
scan(html, REPO);
for(const k of KEEP) addRef(k, REPO);
// 효과음 · 배경음 — 이름만 적고(BGM_DIR + 이름) 읽는다
const bgm = path.join(REPO, "bgm"), bf = walk(bgm);
const named = new Set([...html.matchAll(/["'`]([\w.-]+\.(?:ogg|mp3|wav))["'`]/g)].map(m => m[1]));
for(const f of bf){
  const n = path.basename(f), ext = path.extname(n).toLowerCase(), base = f.slice(0, -ext.length);
  const keep = named.has(n) || ext === ".ogg" || (ext === ".mp3" && !fs.existsSync(base + ".ogg")) || (ext === ".wav" && fs.statSync(f).size < 1e6);
  if(keep) add(f, false);
}

// 복사 (바뀐 것만) · 남은 것 지우기
let copied = 0, bytes = 0;
for(const [r, src] of want){
  const dst = path.join(OUT, r === "heroschool.html" ? r : r), s = fs.statSync(src);
  bytes += s.size;
  if(fs.existsSync(dst)){ const d = fs.statSync(dst); if(d.size === s.size && Math.abs(d.mtimeMs - s.mtimeMs) < 2) continue; }
  fs.mkdirSync(path.dirname(dst), {recursive: true});
  fs.copyFileSync(src, dst); fs.utimesSync(dst, s.atime, s.mtime); copied++;
}
let removed = 0;
for(const f of walk(OUT)){ const r = path.relative(OUT, f).split(path.sep).join("/"); if(!want.has(r)){ fs.unlinkSync(f); removed++; } }
let demoNote = "";
if(DEMO){                                                                      // 체험판 — app/heroschool.html 만 고쳐 쓴다 (저장소의 heroschool.html 은 그대로)
  const once = (s, re, to, what) => { const n = (s.match(new RegExp(re.source, "g")) || []).length;
    if(n !== 1){ console.error(`체험판: ${what} — 바꿀 자리를 ${n}곳 찾았다 (1곳이어야 한다)`); process.exit(1); } return s.replace(re, to); };
  let h = html, build = "";
  if(!h.includes(DEMO_TEXT)){ console.error(`체험판: 끝 화면 글에 '${DEMO_TEXT}' 이 없다 — game.html 의 demoEndShow 글을 DEMO_END 에 맞춘다`); process.exit(1); }
  h = once(h, /const DEMO_END = null;/, `const DEMO_END = ${DEMO_END};`, "체험판 끝 (const DEMO_END = null;)");
  h = once(h, /const BUILD = "([^"]*)";/, (m, b) => { build = b + "-demo"; return `const BUILD = "${build}";`; }, "빌드 번호 (const BUILD)");
  fs.writeFileSync(path.join(OUT, "heroschool.html"), h);
  demoNote = ` · 체험판 — 2년차 겨울 6주차를 마치면 끝 (DEMO_END ${DEMO_END}) · 빌드 ${build}`;
}
const skipped = [...walk(path.join(REPO, "assets")), ...bf].map(rel).filter(r => !want.has(r));
fs.writeFileSync(path.join(DESK, "prepare-skipped.txt"), "# tools/prepare.mjs 가 app/ 에 넣지 않은 파일 (코드에 이름이 없다 · 원본 · 큰 wav) — 게임에서 빠진 것이 있으면 KEEP 에\n" + skipped.join("\n") + "\n");
console.log(`app/ — 파일 ${want.size}개 · ${(bytes / 1e6).toFixed(1)} MB (새로 복사 ${copied} · 지움 ${removed}) · 넣지 않은 파일 ${skipped.length}개 → prepare-skipped.txt${demoNote}`);
