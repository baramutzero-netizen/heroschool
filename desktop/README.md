# 용사 학원 키우기 — PC 판 (Electron · STOVE)

1026 — 사용자 '스토브용 PC 버전으로 래핑 · 창모드/풀스크린/해상도 옵션' → '스토브 엘렉트론용 준비를 진행'
(답: 뼈대 + 화면 설정 목업 · 화면 모드 셋 + 창 크기 프리셋 · 세이브 그대로 · 리그 유지).

웹판 게임(`heroschool.html` + `assets/` + `bgm/`)을 Electron 창에 그대로 띄운다. 게임 코드는 웹판과 같고, PC 판에서만 설정 화면에 화면 줄이 생긴다
(게임 블록 `tools/gen/patch/pcapp_block.js` · `apply_pcapp.py` — 1026-0654 에 game.html 에 넣었다 · 목업 `mockups/pc-app` · 점검 `tools/gen/sim/pcapp_check.py`).

## 처음 한 번

Node.js 20 이상이 필요하다 (https://nodejs.org).
앱을 고친 뒤에는 열려 있는 창을 모두 닫고 `npm start` 만 다시 (npm install 은 처음 한 번 — 한 번만 실행되게 해 두어서 창이 남아 있으면 새로 띄우지 않고 그 창을 앞으로 가져온다).
PowerShell 이 `npm` 을 막으면(스크립트 실행 정책) `npm.cmd install` · `npm.cmd start` 처럼 `.cmd` 를 붙인다. `Electron failed to install correctly` 가 나오면 `node node_modules/electron/install.js` 한 번.

```
cd desktop
npm install
```

## 띄워 보기

```
python wrap.py          (저장소 맨 위에서 — heroschool.html 을 최신으로)
cd desktop
npm start               (tools/prepare.mjs 가 app/ 에 게임을 모은 뒤 Electron 창)
```

- 개발자 도구: Ctrl+Shift+I (빌드한 exe 에서는 꺼진다)
- 저장 위치: `%APPDATA%\HeroSchool` — 게임 저장(Local Storage)과 `display.json`(화면 모드 · 창 크기 · 자리)

## 윈도우용 빌드

```
cd desktop
npm run dist            → dist/win-unpacked/HeroSchool.exe (폴더째 배포 · STOVE 업로드용)
npm run dist:zip        → dist/HeroSchool-0.1.0-win-x64.zip
```

- 아이콘: `build/icon.png` (512 · 웹판 파비콘과 같은 방패) — 바꾸려면 같은 이름으로 덮어쓴다
- 이름 · 버전: `package.json` 의 `productName` · `version` · `build.executableName`

## 화면

| | |
|---|---|
| 화면 모드 | 창 · 전체 화면 · 테두리 없는 전체 화면 (모니터 크기의 테두리 없는 창 — 이 모드로 · 에서 바꿀 때는 창을 새로 연다 · 게임은 먼저 저장) |
| 창 크기 | 1280×720 · 1600×900 · 1920×1080 · 2560×1440 — 실제 픽셀 (배율 150% 모니터의 1920×1080 = 1280×720 DIP) · 모니터 작업 영역보다 큰 것은 고를 수 없다 |
| 손으로 | 창 가장자리를 끌어 바꿔도 된다 · 최대화 · 자리 · 크기를 기억한다 (최소 960×600) |
| 단축키 | F11 · Alt+Enter — 창 ↔ 전체 화면 |
| 끝내기 | 설정 화면 '게임 끝내기' · 시작 화면 EXIT (저장하고 닫는다) |
| 테두리 없음 | 이 모드로 · 에서 바꾸면 창을 새로 연다 — 새 창의 게임이 보던 곳(시작 화면 설정 창 · 게임 설정 화면)을 다시 연다 (1026 · main.js resume) |
| 시작 화면 | 배경 음악(title)이 바로 나온다 (PC 판은 자동 재생 허용) · 메뉴 단추에 마우스를 올리면 소리 · 선택지를 누르면 title_pick · 설정 창 안을 누르면 menu_pick (사용자 소리 — bgm/) |
| 설정 | 시작 화면 설정 창은 두 줄 (글자 아주 크게에서도 스크롤 없음) · 전투 재생 속도는 ×1 · ×2 · 전투 배치 격자 줄은 숨김 (1026 사용자 — PC 판만) |
| 채팅 | PC 판에서는 숨긴다 (채팅 단추 · 창 · 읽기 · 보내기 — 1026 사용자 '채팅은 PC 빌드에서 숨김') · 리그는 그대로 |

게임 화면은 창 크기에 맞춰 게임이 스스로 키우고 줄인다 (웹판의 화면 맞춤 틀 — 1100 아래는 넓은 화면을 통째로 줄이고, 큰 창에서는 ×1.05 ~ ×2.5).

## 파일

| 파일 | 하는 일 |
|---|---|
| `main.js` | 창 · `app://heroschool/` (app/ 를 정해진 주소로 — 저장이 이 주소에 남는다) · 키 · 새 창 링크는 기본 브라우저 · 한 번만 실행 |
| `display.js` | 화면 모드 · 창 크기 프리셋 · 자리 기억 (`display.json`) |
| `preload.js` | 게임에 `window.hsDesk` (get · set · quit · on) — 게임은 화면 맞춤 iframe 안에서 돌아서 모든 프레임에 연다. preload 가 게임 프레임에 닿지 않아도 게임(PCAPP)이 `app://heroschool/__desk/get · set · quit` 주소로 같은 일을 한다 (1026 — main.js deskHttp) |
| `tools/prepare.mjs` | `app/` 에 게임 모으기 — heroschool.html 과 그 안에 이름이 적힌 그림 · 소리만 (원본 png · 프롬프트 json · 큰 wav 는 뺀다 · 글꼴 사용 허락 글은 같이). 넣지 않은 파일은 `prepare-skipped.txt` — 게임에서 빠진 그림이 보이면 `KEEP` 에 |
| `tools/test_electron.cjs` | (선택) 리눅스 클라우드 시험 — playwright `_electron` · xvfb + openbox |
| `tools/check_pc2.cjs` | (선택) 1026 둘째 — 설정 창 두 줄 · 속도 · 격자 · 시작 화면 음악 · 메뉴 소리 · 테두리 없음 뒤 다시 열기 |

`node_modules/` · `app/` · `dist/` · `prepare-skipped.txt` 는 git 에 올리지 않는다 (`.gitignore`).

## STOVE

- STOVE PC SDK 가 공식으로 붙는 엔진은 Native(C/C++) · Unity · Unreal — Electron 은 없다.
  SDK 를 붙이지 않은 빌드(DRM 없는 빌드)를 STOVE Studio '빌드 업로드'에 올리면 DRM MAKER 가 필수 SDK 를 자동으로 넣어 준다 (2026-10 문서 기준).
  업적 · 친구 같은 SDK 기능까지 쓰려면 Native SDK DLL 을 Node 쪽(koffi 등)에서 불러 `preload.js` 로 게임에 여는 일이 따로 필요하다.
- 업로드할 것: `npm run dist` 의 `dist/win-unpacked/` 폴더 (실행 파일 `HeroSchool.exe`).
- 리그(Firebase)는 웹판과 같이 쓴다 — 인터넷이 없으면 리그만 안 된다.
