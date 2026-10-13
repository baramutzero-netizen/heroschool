# 새 세션 인수인계 — 용사 학원 키우기 (D:\heroschool)

Claude 가 새 세션을 시작할 때 읽는 작업 메모. **세션을 마칠 때 '7. 최근 작업'을 고쳐 둔다.**
기능별 상세는 `tools/gen/README.md`, 게임 전체 · 빌드는 `README.md`.

## 0. 시작 순서

1. 이 파일과 도우미를 받는다 — device_stage_files
   `["D:\\heroschool\\tools\\session\\HANDOFF.md", "D:\\heroschool\\tools\\session\\hs.py"]` → 이 파일을 Read.
2. 도우미를 꺼내 두고, 할 일에 맞는 묶음 목록을 찍는다.
   ```
   cp /mnt/user-data/uploads/heroschool/tools/session/hs.py ~/hs.py
   python3 ~/hs.py list core patch          # + counsel (상담창 그림) · rbook (학생 명부 책) · test (게임 테스트) · placer (상담 배치판) · roster (학생 명부 목업) · i18n (글 목록 다시 뽑기)
   ```
   찍힌 배열을 그대로 device_stage_files 의 paths 로 (한 번에 50개). **없는 파일이 하나라도 있으면 그 호출 전체가 실패**한다 — 그 경로만 빼고 다시.
3. `python3 ~/hs.py init` → 작업 폴더 `~/hs/work` (PC 와 같은 모양) + PC 원본 `~/hs/base`. 블록 지문(`blocks.sha.json`)도 작업 폴더에 넣는다.
4. 빌드하면 늘 커밋할 네 파일의 mtime 을 stage 결과에서 바로 적어 둔다 (나중에 찾느라 헤매지 않게):
   `python3 ~/hs.py mtimes game.html=… heroschool.html=… site/index.html=… site/version.json=…`
5. 나중에 파일을 더 받으면 `python3 ~/hs.py sync` — PC 쪽이 바뀌었으면 작업 폴더로 넘기거나 3-way 병합한다.

| 묶음 | 내용 |
|---|---|
| core | game.html · heroschool.html · site/index.html · site/version.json · wrap 스크립트들 · 이 폴더 · tools/i18n 의 빌드 · 시험 파일(빌드가 읽는다) |
| patch | tools/gen/README.md + tools/gen/patch 의 apply 스크립트 · 블록 · 배치 |
| counsel | apply_cslwin 이 읽는 상담창 그림 · 배치 (mockups/counsel-window/art · src/compose_desk.py) |
| rbook | apply_roster 가 읽는 학생 명부 책 — 목업 원본 `src/roster_tpl.html` · `art/book.png` · `ribbon.png` · `roster_layout.json` (4개) — patch 와 같이 |
| schedkit | apply_sched 가 두루마리 그림을 굽는 재료 — tools/gen/kit 모듈 7 · 소품 시트 · tools/gen/fonts 글꼴 7 (24개) — patch 와 같이. 그림은 바이트까지 같게 나온다 |
| test | 학생 도트 · 전투 이펙트 · 상담 쿠키 (assets/spr_img · spr_x_img · fx_img · counsel-cookie — 게임 화면 테스트용 · 빌드에도 필요하다: split_assets 가 찾는다) |
| placer | 상담 목업 · 책상 배치판을 다시 만들 때 (src 전부 · 직업 도트 그림 · 목업의 학생 얼굴) — core · counsel 과 같이 |
| roster | 학생 명부 목업 · 배치판 (mockups/student-roster 전부 · 초상 16 · 스킬 아이콘 · 책상 겹) — core 와 같이 (121개 · 세 번에 나눠 받는다) |
| i18n | 영어판 글 목록을 다시 뽑는 `extract_ko.cjs` · `classify_ko.py` — core 와 같이 (acorn 은 저장소 밖에서 npm i) |
| locker | 락커룸 목업을 다시 만들 때 · 시험에서 락커룸 창 배경(쿼터뷰 지도 다섯 장 · 장마다 3MB)을 볼 때 — mockups/locker-room 원본 4 + `assets/battle-fields/quarter/` city · regional · final · spring · winter.png |

## 1. 꼭 지킬 것

- **Firebase 서버에 쓰지 않는다** (사용자 허락 없이). 읽기는 된다. 테스트는 바깥 주소를 막고 돌린다 — `hs.py shot` · `open_game` 은 http(s) 를 전부 막는다.
- **Firebase 데이터베이스 secret 은 채팅 · 파일 · GitHub 어디에도 쓰지 않는다** — 대시보드(tools/players.html) 입력칸에 사용자가 직접 넣는 것뿐.
- **git commit · push 는 사용자가 한다.** Claude 는 PC 파일에 쓰기까지만 하고, 덮어쓴 파일 목록을 알려 준다.
- **PC 에 쓸 때는 항상 expectedMtimeMs** (새 파일만 빼고). force 금지. 거절되면 다시 받아 → `sync`(병합) → 다시 빌드 → pack.
- **다른 세션이 D:\heroschool\game.html 을 동시에 고친다.** 받은 지 오래됐으면 커밋 전에 다시 받아 sync. mtime 이 덮어쓰기는 막아 준다.
- 파일 하나 20MB 까지.
- 돌리지 않는 것: `ui/chronicle/pack.py` · `sprites/story.py`.
- 학생 프로필 얼굴(초상화)은 WebP 로 바꾸지 않는다.
- 화면 용어 (1010~): 미션은 **'목표'** · '지침'은 학생의 **행동 지침**만 · 학생 개인 명성은 **'평판'** (학원 명성 · 유명도와 따로). 새 글 · 그림 속 글자도 이 이름으로.
- **영어판 (1010~)** — 빌드가 game.html 의 한국어 글을 `_T("…")` · `` _L`…` `` 로 감싼다 (`tools/i18n` · 한국어로 띄우면 그대로). game.html 을 고칠 때:
  `_T` · `_L` 이라는 이름을 쓰지 않는다 · 화면 글을 정규식 · 비교로 판단하지 않는다 (상태 번호 · id 로 — 영어판에서 글이 바뀐다) ·
  숫자 · 이름이 끼는 문장은 템플릿 하나로 (조각 + 조사 함수로 잇지 않는다) · 늘 한국어여야 하는 글(언어 이름 · 서버로 보내는 글)은 바로 앞에 `/*no-i18n*/` ·
  날짜 · 숫자 형식은 `"ko-KR"` 대신 `uiLoc()`. 한국어 글을 고치면 그 영어 키가 어긋나 한국어로 돌아간다 — 빌드 끝 `영어 표에만 있고 지금 빌드에 없는 키 N` 이 그 수
  (영어 표 `tools/i18n/en.json` · `en/*.json` 의 키도 같이 고친다). 영어 화면은 `hs.py layout` 으로 넘치는 칸을 본다.
- **글을 더하거나 바꿀 때는 영어도 같이 한다** (사용자 지시 · 1011~). 빌드 끝이 `번역 단위 N가지 중 M 번역됨 · 영어 표에만 있고 지금 빌드에 없는 키 0` 이 되게 —
  새 단위는 `python3 tools/i18n/todo_en.py --cat ui --out a.tsv`(갈래마다) 로 찾아 영어 표에 넣고, 안 쓰게 된 옛 키는 지운다. 영어가 길어 넘치면 영어 글을 줄이거나 문맥 키(`맨위선언|키`)로 그 자리만 달리.
- 블록(`SCHED_SCROLL` · `MDESK` · `CSLWIN` · `LKWIN` · `ROSTERBK` · `OPTX`)은 블록 파일(`tools/gen/patch/*_block.js · .css`)에서 고치고 apply — game.html 안을 직접 고치면 다음 apply 가 지운다.
  오프닝 글(`OPTX`)은 `optx_block.js` · 글꼴 `optx_fonts.css` → `hs.py apply optx` (지킴이 없음 · 글을 바꾸면 `optx_fonts.py` 로 글꼴 조각부터).
  학생 명부 책의 모양(CSS · HTML)은 목업 원본 `mockups/student-roster/src/roster_tpl.html` 에서 고치고 apply roster.
  `tools/gen/patch/blocks.sha.json` 은 커밋하지 않는다 (hs.py pack 이 뺀다).
- 작은 수정은 가볍게 확인한다 — 빌드 + 고친 화면 스크린샷 한두 장. 시나리오 테스트는 큰 기능만.
- 사용자에게는 한국어 해요체로 짧게. SendUserFile 로 보내는 파일 이름은 ASCII.

## 2. 한 번의 수정 → PC 반영

```
python3 ~/hs.py apply cslwin        # 패치 스크립트 · 블록 · 배치를 고쳤으면 (순서는 4번)
python3 ~/hs.py build               # → heroschool.html · site/index.html · site/version.json (+ 빼낸 그림)
python3 ~/hs.py shot --click '#nav button[data-view=counsel]' --sel .cw-win --out c.png    # 고친 화면 확인
python3 ~/hs.py status              # 바뀐 파일 · 줄바꿈 경고 · mtime 없는 파일
python3 ~/hs.py diff game.html      # 바뀐 줄 (긴 줄은 잘라서)
python3 ~/hs.py pack 이름            # 보낼 폴더 + 커밋 목록 (끝에 8초 기다린다)
```
- 찍힌 **1차 목록**을 device_commit_files 에 그대로. 모두 written 이면 **2차 목록**(새 파일 · 빌드가 새로 뺀 그림).
- 그다음 둘 중 하나:
  - 확인까지: 찍힌 '다시 받을 목록'을 stage → `python3 ~/hs.py verify game.html=새mtime …` (그림은 픽셀로 비교)
  - 확인 생략: `python3 ~/hs.py done game.html=새mtime …` — 새 mtime 은 stage 결과나 device_list_dir 에서. 안 주면 지워 두고 다음 pack 이 묻는다.
- 사용자에게: 무엇을 바꿨는지 + PC 에 덮어쓴 파일 목록 (새 파일은 따로 표시).

## 3. 폴더 지도

| 경로 | 무엇 |
|---|---|
| `game.html` | 원본 소스 (CRLF · `<!doctype>` 없는 조각). 게임 로직 · 데이터 상수 전부 |
| `heroschool.html` | wrap.py 결과 — 테스트 기능을 빼고 `assets/` 를 같이 쓴다 |
| `site/index.html` · `site/version.json` | wrap_site.py 결과 (배포용 · `../assets` · `../bgm`) — 둘은 늘 같이 올린다 |
| `wrap.py` · `wrap_site.py` · `split_assets.py` · `build_boot.py` · `build_guard.py` · `build_strip.py` | 빌드 |
| `assets/` | 그림 — split_assets 가 game.html 의 data: 를 빼낸 것 + 원래 파일 |
| `bgm/` | 음악 · 효과음 (게임은 `.ogg` 만 읽는다 · 원본 mp3/wav 도 있다) |
| `tools/gen/` | game.html 블록 · 그림 생성 — README 에 기능별 설명 · apply 순서 |
| `tools/session/` | 이 문서 · hs.py |
| `tools/i18n/` | 영어판 — 빌드 변환 `i18n_build.py` · 번역 함수 `i18n_runtime.js` · 영어 표 `en.json` · 공개 여부 `config.json` · 시험 `check_i18n.py` · 글 뽑기 `extract_ko.cjs` · `classify_ko.py` (README) |
| `tools/field_lab.html` | 필드 배치 실험실 (전투 자리 · 크기 → apply_tune) |
| `tools/skill_upgrade_lab.html` | 스킬 강화 창 배치 실험실 (창 안 요소의 자리 · 크기 → `skup_layout.json` → apply_skup) |
| `tools/check_scale.py` · `tools/check_modes.py` | 화면 크기 틀(UISCALE) · 화면 모드(넓은 화면 · 좁은 화면 · 태블릿 · 폰) 시험 — Playwright |
| `mockups/ui-scale/` · `mockups/screen-modes/` | 화면 크기 틀 · 화면 모드 목업 (gitignore — PC 에만) |
| `mockups/counsel-window/` | 상담창 목업 · 상담 책상 배치판 · 그림 (gitignore — PC 에만) |
| `mockups/student-roster/` | 학생 명부 목업 · 학생 명부 배치판 · 견본 학생 · 책 그림 (gitignore — PC 에만 · README 에 굽는 법) |
| `Claude outputs/` | 예전 결과물 · 스케줄/책상 배치판 키트 (gitignore) |
| `sprites/` · `ui/` · `events/` · `reports/` · `captures/` | 원본 · 작업 폴더 (gitignore) |
| `test.py` | Playwright 3년 회귀 테스트 (오래 걸린다 — 전투 · 성장 수치를 건드렸을 때만) |
| `tools/players.html` | 플레이어 현황 (개인용 · gitignore) |

## 4. 빌드 · 패치 요점

- apply 순서 (`tools/gen/README.md` 쓰는 법): sched → desk → exped3 → skgrade → cslpers → cslwin → lkwin → roster → webp → wrap → wrap_site.
  모두 몇 번 돌려도 같은 결과라 **고친 것만** 다시 돌리면 된다. `hs.py apply 이름 [인자…]` = `python tools/gen/patch/apply_이름.py game.html [인자…]`.
- `hs.py build` 는 TZ=Asia/Seoul — 빌드 번호(`MMDD-HHMM`)가 한국 시간. 리눅스의 wrap 은 LF 로 쓰므로 heroschool.html · site/index.html 을 PC 원본처럼 CRLF 로 바꿔 둔다 (git 내용은 같다).
  split_assets 는 `assets/spr_img.webp.js` 등 test 묶음 파일이 없으면 멈춘다 — 빌드하려면 test 묶음도 받는다.
- 영어판 (1010) — wrap · wrap_site 가 strip_dev 다음에 `apply_i18n` 을 부른다: `i18n: 문자열 4226 · 템플릿 1251 감쌈 · 영어 표 N줄 · … 문법 검사 통과` 가 찍히면 정상.
  변환이 실패하면 경고하고 한국어만으로 빌드한다 (게임은 그대로 나간다). `HS_I18N=0` 이면 변환하지 않는다. `i18n: 확인 —` 줄은 영어 표의 키가 정규식 · 객체 키에도 쓰인다는 알림 (영어에서만 어긋난다).
- 빌드가 game.html 의 data: 그림을 `assets/` 로 빼며 `?v=해시` 를 단다. hs.py 는 PC 의 heroschool.html 과 `?v=` 가 같은 그림은 올리지 않는다.
- **C2PA** — Claude 가 PC 에 쓴 PNG · WebP · mp3 에는 출처 정보 조각이 붙는다 (픽셀은 같다). 그래서 PC 의 그림을 원료로 다시 구우면 `?v=` 가 바뀔 수 있다 — 그대로 커밋해도 된다.
  예: PC 원본으로 apply_cslwin 을 처음 돌리면 상담창 배경 `bg` 의 `?v=` 가 바뀐다 (`art/bg.webp` 에 C2PA 가 붙어서). 한 번 커밋하면 그 뒤로는 그대로.
- 블록 지킴이: `blockguard` 가 game.html 쪽 블록이 지난번 넣은 것과 다르면 멈춘다. 지문 파일은 세션마다 PC 것을 받아 쓴다 (`hs.py init` 이 넣는다 · 작업 폴더에 이미 있으면 그대로).
  PC 의 지문은 10-07 것이라 sched · mdesk 만 있고 상담창(cslwin) · 학생 명부 책(roster_js) 지문은 없다 — 그 블록을 apply 하기 전에는 시험으로 돌려 game.html 이 바뀌는지부터 본다.
- 상담 책상 배치판(Artifact) — https://claude.ai/artifact/QdjzxFheqqWLRoqLKJsSHf
  원본 `mockups/counsel-window/src/placer_tpl.html` → `python3 mockups/counsel-window/src/build_placer.py` (PC 용 `counsel_desk_placer.html`) ·
  `… build_placer.py --artifact ~/hs/placer_artifact.html` (아티팩트 본문). 새 세션에서 다시 올릴 때는 그 URL 을 먼저 read 한 뒤 `url` 로 publish (capabilities 는 빼면 그대로 간다).
  사용자가 배치판에서 저장한 `desk_layout.json` 을 주면 `mockups/counsel-window/art/` 에 덮어쓰고 apply cslwin → build.
- 학생 명부 배치판(Artifact) — https://claude.ai/artifact/Dtg12MfQi9CthUS79Lq7KH (capabilities: downloads)
  책 원본 `mockups/student-roster/src/roster_tpl.html` (표시 구간을 배치판이 가져다 쓴다) + 편집기 `src/placer_tpl.html` →
  `python3 mockups/student-roster/src/build_mockup.py` (`roster_mockup.html`) · `build_placer.py` (`roster_placer.html`) · `build_placer.py --artifact ~/hs/roster_placer_artifact.html`.
  새 세션에서 다시 올릴 때는 그 URL 을 먼저 read 한 뒤 `url` 로 publish (capabilities 는 빼면 그대로). 묶음은 `core roster`.
  사용자가 배치판에서 저장한 `roster_layout.json` 을 주면 `mockups/student-roster/art/` 에 덮어쓰고 build_mockup → build_placer (→ 아티팩트 다시 올리기) → apply roster → build (게임).

## 5. 테스트

- `hs.py shot` — heroschool.html 을 크로미움으로 띄워(시작 화면을 닫고 홈) 스크린샷 · 오류. 결과는 `~/hs/shots/`.
  - `--phone` (390×844) · `--js '코드'` (함수 본문 · return 값을 찍는다) · `--click 선택자` (여러 번) · `--sel 요소` · `--wait ms` · `--title` (시작 화면 그대로) · `--missing`
  - 작업 폴더에 assets 를 다 받지 않아서 그림이 빠져 보이는 게 정상이다. 모양을 봐야 하는 화면만 `--missing` 이 찍는 목록(PC 경로)을 받아서 다시 찍는다.
- `hs.py i18n` — 영어판 시험 (빌드 뒤에 · 45초쯤). 한국어: 변환 전 · 후 빌드를 같은 시드로 3년 돌려 세이브 · 화면 열아홉 개가 한 글자도 안 다른지.
  영어: `?lang=en` 으로 띄워 시험 단어 · 리그 잠금 토스트 · 설정의 언어 칸 · 언어 바꾸기 · 공개 뒤의 브라우저 언어 고르기. game.html 을 크게 고쳤거나 tools/i18n 을 고치면 돌린다.
  `hs.py layout` — 영어 화면 넘침 · 남은 한글 (세 크기 · 크기마다 1분 반쯤 · 10분 넘으면 `--sizes` 로 나눠 돌린다) · `python3 tools/i18n/check_save.py` — 세이브 왕복.
  **영어판은 공개됐다** — 브라우저 언어로 고르므로 시험 스크립트의 크로미움은 locale 을 정해 띄운다(`hs.py shot` 은 ko-KR). 영어로 보려면 `hs.py shot --page 'heroschool.html?lang=en'`.
- 긴 시나리오는 직접 스크립트로: `sys.path.insert(0, os.path.expanduser("~")); import hs; b, pg, errs = await hs.open_game(p)` — 띄우는 데 4초쯤.
- `python3 tools/check_scale.py` — 화면 크기 틀(UISCALE · PC 에서 게임을 iframe 에 넣어 키우고 줄인다 — 1분 반쯤). 틀 · 진짜 마우스(클릭 · 서명 긋기 · 휠) · 키보드 ·
  설정 '화면 크기' · 언어 바꾸기 · 새 버전 · 폰/iPad/자동화는 틀 없이 · file:// 과 http://. 맨 앞 스크립트(UISCALE)나 iframe 에 영향 가는 걸 고치면 돌린다.
  **Playwright(자동화)에서는 틀이 안 생긴다**(navigator.webdriver) — 다른 시험은 예전 그대로(창 크기 그대로). 틀로 보려면 주소에 `?scale=user`(사람처럼) · `auto` · `150` · `off`.
- `python3 tools/check_modes.py [--shots 폴더]` — 화면 모드(1013 · 1분 반쯤): PC 틀(1440 · 900×600 ×0.818 · 600) · 한 창에서 크기 바꾸기 · 설정 150% · 진짜 마우스로 스케줄 끌기 ·
  락커룸 → 쿼터뷰/세로 전투 · 태블릿 흉내(viewport width=1100 · 돌리기 · iPad Air · 화면 나누기 · 탭) · 폰 흉내(가로 덮개 · 전투 중 숨김 · 영어). 화면 모드 · 배치 판정을 고치면 돌린다.
  틀 안에서 직접 시험할 때: `b, pg, fr, errs = await hs.open_framed(p, 900, 600)` — fr 이 게임 frame (마우스 좌표 = 게임 좌표 × `HS_SCALE.k`).
- `node tools/check_skill_upgrade.cjs` — 스킬 강화 창(1013 재작업 세션 것 · PC 경로 `D:/heroschool` · msedge). 클라우드에서는 경로를 `~/hs/work` 로 바꾸고 `channel` 을 빼고
  바깥 주소를 막아 돌린다 (그림 `assets/skill-upgrade/` 전부 · 16 직업 스킬 아이콘을 받아야 통과). 창 배치를 고치면 이것과 `hs.py layout --only skillup`.
- 게임 상태: `S` (세이브) · `UI.view` · `render()` · `closeModal()`. 상담 대기열 `counselState().queue` · 지침 무시 `defyState().pend` · 난수 `RNG`.
  새 브라우저마다 새 게임(1년차 봄 · 학생 3명)으로 시작한다.

## 6. 자주 걸린 것

- 도트 테마 `html[data-ui-finish="pixel"]` 가 모든 button 에 네모 테두리 · 그림자를 `!important` 로 붙인다 (특이도 0,4,2) → 덮으려면 클래스 다섯 개짜리 선택자.
- 상담창은 글자가 찍히는 중에 누르면 '바로 끝까지'라서, 테스트는 준비 상태(`CSLW.phase` · `!CSLW.typing`)를 기다린 뒤 누른다.
- game.html 은 CRLF. 직접 고칠 때는 파이썬으로 읽고 써서 줄바꿈을 지킨다 — `hs.py status` 가 섞이면 경고한다.
- 받은 파일은 1초쯤 늦게 나타난다 (init · sync 가 기다린다). 커밋은 outputs 에 복사하고 몇 초 뒤에, 매번 새 폴더로 (pack 이 한다).
- 학생 도트는 `sprCellCv` (256 칸 · 머리색 치환). 상담창은 128 칸으로 잘라 발끝(무대 2배 280, 288)을 축으로 직업별 `CSL_SPR` 크기 · 자리.
- `apply sched` 는 `tools/gen/kit` 의 모듈 · 소품 시트와 `tools/gen/fonts` 글꼴이 있어야 돈다 — `hs.py list schedkit` 으로 받는다 (patch 묶음에 없다). `apply desk` 는 `tools/gen/patch/desk_out/` 그림이 있어야 한다.
  apply_sched · apply_desk 를 다시 돌리면 그 CSS 블록이 스타일시트 맨 끝으로 옮겨 가서 game.html diff 가 크게 보인다 (내용은 같다).
- 게임 함수로 견본 데이터를 만들 때는 `withSeed("이름", fn)` 으로 난수를 고정한다 (`let RNG = Math.random` · seedRNG).
- 학생 명부 책은 그림자 DOM(`#rbHost`) 안 — 테스트에서 `document.getElementById('rbHost').shadowRoot` 로 찾는다 (Playwright 의 `locator('#rbHost …')` 는 그대로 뚫고 들어간다).
  책은 넓은 화면(게임이 보는 폭 1100px 이상 — 1013 부터 방향은 안 본다)에서만 뜬다 — `open_game(p, w=1440, h=1000)`. 상태는 `RBK.isOpen()` · `RBK.state`.

## 7. 최근 작업 · 현재 상태 (2026-10-14 · 빌드 1014-0103)

- **스킬 강화 창 배치 도구 (1013 · 빌드 1013-2120)** — 사용자: '지금 스킬 강화 창을 재작업했거든? 확인해보고 스킬 강화 창 위치/사이즈 변경 툴을 만들어줘'.
  재작업(다른 세션 — `skillUpModal` · CSS `SKILL_CHOICE_STYLE` · 그림 `assets/skill-upgrade/` · 영어 `en/skill-upgrade.json` · 시험 `tools/check_skill_upgrade.cjs`)은 그대로 두고
  창 안 요소의 자리 · 크기만 표로 뺐다. 자세한 것은 `tools/gen/README.md` 의 '스킬 강화 창 배치'.
  - **배치표** — game.html `SKUP_LAYOUT` 블록(`SK_CHOICE_MARKS` 아래 · 블록 파일 없음 — 직접 고친다): `SK_CHOICE_LAYOUT`(한 줄 JSON · apply_skup 이 바꾼다) · `SK_CHOICE_SEL` · `skChoiceLayoutApply(scene)`.
    요소마다 {ax l·c·r, ay t·b, x, y, w, h, mw, tail} 를 인라인 style 로 (CSS 를 덮는다) · 넓은 화면(pc)과 폰(mobile — 폭 760 이하, CSS 와 같은 기준) 따로 · 창은 크기 + 화면 가운데에서
    옮긴 x·y (폰은 높이 + 완료 화면 높이 sceneEnd). 선택지 칸(`.suc-choices`)은 창 전체를 덮고(누르기는 통과) 말풍선이 창 기준 자리에 선다 · 완료 화면은 absolute.
    부르는 곳: 창을 열 때 `skChoiceLayoutWatch`(폭 760 을 넘나들면 다시) · 선택지를 그릴 때(`reveal`) · 완료 화면(`skChoiceSuccessHtml` — choose 와 실험실이 같이 쓴다).
    처음 값(`tools/gen/patch/skup_layout.json`)은 재작업한 CSS 그대로 — 재작업 빌드와 픽셀 비교에서 말풍선이 0.3px 옮겨 정수 자리에 선 것 말고 같다.
    완료 화면은 재작업 CSS 가 세로 흐름(결과 칸 아래 12px 에 확인 단추)이라, 결과 글이 길면 `skChoiceDoneFit` 이 단추를 내리고 창을 늘린다
    (이것 없이 절대 자리로만 두면 폰에서 효과 줄이 둘인 결과 96/240 이 단추에 겹쳤다 — 세션 scratchpad `skup/probe_succ.py`).
  - **실험실** `tools/skill_upgrade_lab.html` — `game.html?skuplab`(SKUP_LAB 블록 · 배포 빌드에서는 build_strip 이 뺀다)을 iframe 으로: 끌어 옮기기 · 노란 손잡이로 크기(비율 고정) ·
    빈 곳을 끌면 창 위치 · 방향키 1px(Shift 10) · 가운데 근처에서 붙기(Alt 면 안 붙음) · 기준 바꾸기(자리는 그대로) · 숫자 칸 · 말풍선 꼬리 · 요소 / 전체 기본값 · 장면 넷 · 학생 직업 16 ·
    화면 크기(PC 일곱 — 낮은 노트북 1280×720 · 1366×650 포함 · 폰 셋) · 차이점 글 · JSON 저장 / 불러오기. 세이브를 쓰지 않는다(Storage.setItem · save 막음) · 실험실 상태는 그 브라우저
    localStorage `heroschool_skuplab_v1`. 주고받기 postMessage `lab:"skup"` (게임 → ready · measure · pick · move / change, 실험실 → set · nudge).
    반영: 사용자가 저장한 `skup_layout.json` 을 `tools/gen/patch/` 에 두고 `python3 tools/gen/patch/apply_skup.py game.html` → build.
  - 확인하며 고친 것 — ① 폰에서 창이 맨 아래('나중에' 단추 focus)로 내려가 열렸다 → `focus({preventScroll:true})` ② 영어: 재작업이 만든 `en/skill-upgrade.json` 과 겹친 키를 빼고
    ui.json 에는 나머지 여섯(강화 포인트 · 규칙 글 · 제안 유지 · 보유 · 1개 사용 · 획득 경로)만, 옛 창 글 넷은 지웠다 · 폰 제목이 두 줄이 되어 아래가 잘려
    'Which skill will you develop?' → 'Which skill to develop?' (skill-upgrade.json) ③ 영어 스킬 이름 'Assassination' · 'Earthsplitter' 가 글자 중간에서 끊겼다 →
    `skChoiceNameFit`(긴 낱말이 들어가게 글자를 줄인다 — 21.5 · 22.5px · 한국어는 그대로) ④ `check_layout.py` 의 skillup 장면 — 옛 필드 `skPts` → `sp` · 말풍선이 나오기 전에 찍던 것을 1.5초 기다림.
  - 알게 된 것 (배치는 사용자가 실험실로 정한다) — 창 높이 740 이라 1280×720 · 1366×768 노트북(브라우저 안 650쯤)에서 아래 이름 띠 · '나중에'가 잘려 창 안에서 스크롤 /
    폰에서 선택지 말풍선 꼬리가 다음 말풍선에 겹친다 / 폰 '이국의 부채' 글 아래가 이름 띠에 걸친다.
  - **학생 머리 옆 표시 둘** (빌드 1013-2144 — 사용자: '도구에서 이 2개의 소품 이동이 처리가 안되있어') — 긴장(`anticipation.png` · 부채 들기) · 충격(`impact.png` · 부채 맞음).
    `skChoiceHero` 의 표시 `<img class="suc-mark">` 에 `data-art` · `data-mark` 를 달고 자리 · 크기를 `skChoiceMarkCss` 로 — 배치표 `marks`(두 화면 같이 · 학생 그림 192 칸):
    `{s 크기(가운데 그대로) · d 모든 직업 옮김 · at {직업 그림: [x, y]}}` 를 `SK_CHOICE_MARKS`(재작업 세션 것 · 그대로) 위에 더한다. 기본값이면 예전과 같은 자리(16 직업 × 2 확인).
    실험실: 요소 목록 '긴장 표시' · '충격 표시' — 끌면 자리('모든 직업 같이 옮기기' 기본 켬 · 끄면 지금 직업 그림만 at 에) · 모서리 손잡이 크기 · 방향키 1칸 · 숫자(그림 칸) ·
    '이 직업만 따로 정한 자리 지우기'. apply_skup 이 marks 를 확인해 넣는다(없는 예전 JSON 은 기본값). 시험 세션 scratchpad `skup/labtest_marks.py`.
  - **사용자 배치 반영 · 낮은 화면에서 창 줄이기** (빌드 1013-2210) — 사용자가 실험실에서 맞춘 배치(넓은 화면: 창 y 1 · 학생 아래에서 5 · 휘두르는 부채 105, 269 ·
    이국의 부채 단추 19, 125 · 표시 둘은 머리 오른쪽 — 긴장은 모든 직업 103, -16 옮긴 뒤 직업마다 · 충격은 직업마다)를 `skup_layout.json` 에 그대로 넣고 apply.
    + 사용자: '가로 모드에서 세로 화면 높이가 900 이하일 경우에는 창의 전체적인 비율을 축소' → 넓은 화면 배치에서 게임이 보는 세로 h 가 `scene.fitH`(900) 이하면
    `.suc-scene` 에 zoom h/900 (0.5 까지 · `skChoiceZoom` · 창 크기가 바뀌면 다시). 창 폭 · 옮긴 자리도 같은 배율. 1280×720 → 80% · 1366×650 → 72% · PC 900×600 창(틀 안 733) → 81% —
    창 안 스크롤이 없어졌다. 폰 배치는 그대로. 실험실: 창을 고르면 '줄이기 시작' 칸 · 배지에 줄인 배율 · 끈 거리는 배율로 나눈다. 시험 scratchpad `skup/labtest_zoom.py` ·
    실험실 시험은 처음 배치 나무(`skup/mk_tt.py` → `tt/`)에서 (`LABROOT=…/tt`).
  - **띠 불투명 · 배경 벨트** (빌드 1013-2231) — 사용자: '제목 띠와 이름 띠의 투명도를 없애고, 뒷 배경은 SKILL UPGRADE 가 쓰인 두 색 띠가 하나는 위로, 하나는 아래로
    벨트 스크롤' (목업 그림 — 연파랑 #c2e5ff · 민트 #c6faf6 · 20° 기울기). 재작업 CSS 의 `.suc-heading` · `.suc-footer` 배경 #5c94b0e0 → #5c94b0.
    배경은 배치표 `bg` (`skChoiceBg` — 방 그림 대신 · 띠 22개(넓은 화면) · 14개(폰)의 글 줄을 transform 으로 · 시계에 맞춘 animation-delay · 움직임 줄이기면 멈춤 ·
    CSS 는 `#sucBgCss` 로 한 번 넣는다). 밝은 띠 위 글은 테두리(`suc-belt`) · 완료 화면의 어두운 막은 뺐다. 실험실 '배경' 칸(색 셋 · 진하기 · 폭 · 기울기 · 속도 · 글 사이 · 크기 · 끄기).
    apply_skup 이 bg 를 확인(#rrggbb · 범위 · 크기 12·24·36·48 — 없으면 기본값). 시험 scratchpad `skup/labtest_bg.py` · `cap_bg.py`(벨트 GIF).
  - **전구 · 표시 테두리 · 완료 배경 · 부채 상자** (빌드 1013-2255) — 사용자: '전구 사이즈 보정/이동 가능하게, 잘 안 보여서 테두리 · 긴장 · 충격 표시도 테두리 ·
    완료 창의 뒷배경은 업그레이드 된 스킬의 배경색을 채도를 더 낮게 · 부채의 텍스트와 보유 수량은 이국의 부채 (2개) 로, 마우스 오버 때 박스에서'.
    전구는 thinking.png 에 그려져 있어(16 직업 같은 자리 82, 20 · 28×27) 그 칸을 마스크로 가리고 같은 그림을 잘라 `.suc-bulb` 로 — `marks.thinking` (실험실 '전구' · 고르기 장면).
    테두리 `outline {c #3d2b1f, w 1칸}` (실험실 표시 칸). 완료 배경 `bg.end` solid · `endSat` 50 (실험실 배경 칸 '완료 화면' · '완료 채도').
    부채 단추 — '이국의 부채 (N개)' 상자(`.suc-fan-tip` · 0개면 '획득 경로 추후 추가' 줄) · 터치 기기는 부채 아래 글 · 단추 상자가 그림만이 되어 사용자 배치 y 를 39 올렸다(그림 자리 그대로).
    영어: ui.json 에서 '보유 ' · ' · 1개 사용' 지우고 '이국의 부채 ({0}개)' → 'Exotic Fan ({0})'. 시험 scratchpad `skup/labtest_v4.py` · `cap_v4.py`.
  - **부채 그림 v2 · 효과음 다섯** (빌드 1013-2330) — 사용자: 참고 그림(은빛 부채 · 흰 테두리 · 붉은 손잡이)처럼 '부채도 이미지 같은 느낌으로 가공하고 테두리/그림자' ·
    소리 다섯(나중에 · 스킬과 부채에 마우스 오버 · 창 진입 후 전구 · 부채 맞고 다시 전구 · 부채 타격 · 옵션 출력) · '옵션 출력 소리는 진화 · 각성일 때 톤을 올릴 수 있나'.
    `fan-v2.svg`(새 파일 · 생성 스크립트 `tools/gen/patch/skup_fan.py`) + CSS 그림자 · `SK_CHOICE_FIT.fan` 높이 비율 89/150 · 66/110. 효과음 `bgm/skillup_{later,hover,bulb,hit,option}`
    (.ogg + 원본 .mp3) · `sfxPlay(key, rate)` 에 재생 빠르기(WebAudio playbackRate · <audio> 는 preservesPitch 끄고 playbackRate) — 진화 +4 · 각성 +7 반음.
    사용자 배치(휘두르는 부채 101, 260 · 폭 126 / 부채 단추 18, 134 · 폭 172 · 폰 y 100 / 전구 크기 36 · 위로 7 · 직업 13 따로 / 띠 색 #e5edff · #dbf5f3 · 글자 #000 25% ·
    완료 채도 30) 반영. 실험실 차이점 — 키 차례만 다른 것을 '바뀜'으로 보던 것(긴장 · 충격 표시 빈 줄) 고침(`canon`). 터치 기기 부채 글은 부채 위로(이름 띠에 걸리지 않게).
  - **새 부채 그림 테두리 · 휘두르기 시작 자리** (1014 · 빌드 1014-0020) — 사용자가 부채를 새 그림 `exotic-fan-v3.png`(64×64 도트 · 손잡이 왼쪽 아래 · 다른 세션이
    `SK_CHOICE_FAN` 과 정사각 128 / 64 CSS · 손잡이 축 22% 85% 를 넣었다)로 바꾼 뒤: '테두리 처리 해주고 스킬 강화 창 배치에서 부채 휘두를 때 시작 위치를 조정할 수 있게'.
    부채 둘은 그림 칸 정수배(64 · 128 · 192 — 배치 w 에 가장 가까운 · `SK_CHOICE_FAN_PX`)로 — 배치의 인라인 크기가 그 CSS 를 덮어 단추 그림이 102px(1.59배)로 고르지 않던 것.
    테두리 · 그림자는 배치표 `fan {flip, c, w}`(`skChoiceFanFilter` — 그림 1칸 단위 · 그림자는 각 자세 각도만큼 되돌려 늘 오른쪽 아래). 휘두르기는 `swing` 상자 = 맞는 자리(+ `r`) ·
    `swingFrom {x, y, r}` = 시작 자리(맞는 자리에서 옮긴 px) — `skChoiceSwing` 이 `#sucSwingCss` 에 .ready · .bonk · keyframes `suc-bonk-fan` 을 쓴다(손잡이 `SK_CHOICE_FAN_GRIP` 축).
    새 그림은 예전 그림과 좌우가 반대라 예전 회전(24 → -45 → -25도)으로는 맞을 때 종이가 머리 위로 섰다 → `flip`(손잡이를 오른쪽으로) + 기본 자세 시작 (24, -40) 35도(종이가 위로) ·
    맞음 -60도(머리 위에 눕는다) · 가운데 쯤 조금 더 나감. 사용자 배치의 휘두르는 부채(101, 260 · 폭 126 — 예전 그림의 '시작' 자리)는 새 뜻으로 바꿨다: 넓은 화면 맞는 자리 150, 302 · 폭 128 / 폰 75, 268.5 · 64.
    실험실: '부채 들기' 장면 '부채 — 시작 자리'(끌기 · 방향키 · 각도) · '부채 맞음' 장면 '부채 — 맞는 자리'(각도 · 모서리 손잡이 64 단위) · [ ] 키 5도(Shift 15) · '▶ 휘두르기 보기' ·
    부채 테두리 · 휘두를 때 좌우 뒤집기 · 테두리 상자는 보이는(돌린) 자리 · 1014 전 저장분의 swing(r 없음)은 게임 값으로. apply_skup — swingFrom · swing.r · fan (없으면 기본값).
    지난번 패치(효과음)가 주석 뒤로 밀어 버린 실험실 부팅 코드 `UI.ceremonies = []; UI.view = "home";` 되살림. `assets/skill-upgrade/README.md` 의 부채 줄도 v3 로.
    시험 scratchpad `skup/labtest_v6.py` · `swing_frames.py`(프레임 시트 — 애니메이션을 멈춰 찍는다) · `swing_jobs.py`(16 직업 맞는 자리).
  - **명부 '스킬 강화 가능!' 쪽지 · 완료 소리 · 말풍선 조각 2배 · 꼬리 픽셀 테두리 · 영어 Auto-Upgrade** (1014 · 빌드 1014-0035) — 사용자 목업(초상 원 위쪽에 걸친
    'SKILL UPGRADE!' / '스킬 강화 가능!' 쪽지 · '서식은 다른 것들을 따라가면'): 명부 책(roster_block.js · .css → apply_roster)의 학생 목록에서 `st.sp > 0` 이면
    `<span class="tag tm skb">스킬 강화 가능!</span>` — 원 아래 꼬리표와 같은 모양 · 원 위 15px(원을 따라 옮김) · 영어 'SKILL UPGRADE!'(ui.json).
    영어 '스킬 임의로 강화' → 'Auto-Upgrade'(예전 'Auto-Upgrade Skills' 가 정렬 칸을 침범 — 좁은 화면 학생 명부 단추도 같은 글).
    완료 화면 소리 `bgm/skillup_done.{ogg,mp3}`(새 파일 · SFX suc_done · `choose` 에서 완료 화면을 그린 뒤). 말풍선이 나오기 전 조각 64×56(2배 · 가운데 그대로).
    꼬리 · 점 — 계단 모서리 clip-path 두 겹(바깥 테두리 색 · 안 ::after 등급 색)으로 픽셀 테두리 · 말풍선 · 꼬리 · 점 사이 4px. 폰은 말풍선이 붙어 있어 꼬리가 다음 말풍선 뒤에 거의 숨는다.
    apply_roster 는 그림을 data: 로 넣지만 빌드(split_assets)가 같은 assets/roster_art 경로로 되돌린다(game.html 의 ROSTER_ART 줄은 그대로). 시험 scratchpad `skup/roster_shot.py` · `puff2.py` · `puff_tail.py` · `sfx_done_test.py`.
  - **명부 쪽지로 스킬 강화 · 강화 규칙 숨김 · 사용자 휘두르기 배치** (1014 · 빌드 1014-0050) — 사용자: '학생 명부의 스킬 강화 가능!/Skill Upgrade! 을 눌러서
    스킬 업그레이드 창을 띄우기 · 스킬 창의 Skill Upgrade 버튼은 숨김 · 강화 규칙 숨김' + 실험실 배치(넓은 화면 맞는 자리 126, 275 · 시작 자리 20, -3).
    쪽지 `<span class="tag tm skb" data-skup role=button tabindex=0>` — 목록 click · keydown(Enter · Space)에서 `openSkillUp(id)`(상세 쪽이면 select 뒤 `RB.want = true; skillUpModal`) ·
    `dragSrc` 는 [data-skup] 에서 끌기를 시작하지 않는다 · 마우스를 올리면 #fff3d6 · 초점 점선. 학생 상세 스킬 칸의 `#skUp` 단추와 그 연결 · `.pbtn` CSS 를 뺐다('강화 포인트 N' 글은 그대로).
    제목 글 '눌러서 스킬 강화 — 강화 포인트 {0}' (영어 표). 강화 규칙 `.suc-rules{display:none}`(skChoiceCss) · 실험실 목록에서 rules 를 뺐다(배치표 칸은 그대로).
    시험 scratchpad `skup/roster_click_test.py`(마우스 · Enter · 팀 편성 · 강화 뒤 사라짐).
  - **이국의 부채 — 도구 탭에서 판다** (1014 · 빌드 1014-0103) — 사용자: '이국의 부채 도구점에서 1000G 에 구매 가능 · 계절 당 2개 구입 가능'.
    쿠키(`COUNSEL_COOKIE` 블록 — 200G · 계절 2개)와 같은 방식으로 그 블록 바로 아래에: `EXOTIC_FAN_PRICE` 1000 · `EXOTIC_FAN_LIMIT` 2 · `fanShopState`(`S.fanShop {key 연도-계절, bought}`) ·
    `buyExoticFan` · `exoticFanShopCard`(쿠키 다음 칸 · 이름 · 값 · 설명 · '보유 N개 · 이번 계절 M/2개 구입 가능'). `ITEMS.exoticFan` pending 을 빼고 price 1000 · ex 0 ·
    `itemPrice` 는 할인 없는 1000. 도구 탭 클릭 처리에 exoticFan 갈래. 스킬 강화 창의 부채 상자(0개) 글 '획득 경로 추후 추가' → '도구상에서 구입 · 1,000 G'.
    영어 — 일지 · 알림 · 카드 줄 · 상자 글 (log.json · ui.json). `assets/skill-upgrade/README.md` 의 'pending' 줄도 고쳤다. 시험 scratchpad `skup/shop_fan_test.py`
    (넓은 화면 마을 · 좁은 화면 · 영어 · 한도 · 계절 바뀜 · 자금 부족 · 일지 · 스킬 강화 창 상자).
  - 시험: `tools/check_skill_upgrade.cjs`(경로 · 브라우저만 바꾸고 바깥 주소를 막아) 통과 · 실험실 조작 시험 · JSON → apply → 빌드 왕복 · 재작업 빌드와 픽셀 비교
    (세션 scratchpad `skup/labtest2.py` · `roundtrip.py` · `cmp.py`) · `hs.py layout --only skillup` · `hs.py i18n` · `check_modes.py` 통과.

- **화면 모드 — 넓은 화면을 기본으로 · 좁은 PC 창은 통째로 줄인다 (1013 · 빌드 1013-1649)** — 사용자: '가로 넓은 화면을 기본으로, 폭 1100 미만이면 전체 스케일을 축소,
  640 이하는 세로 모드 · 폰은 무조건 세로 · 세로 태블릿은 무조건 가로(넓은 화면) · PC 좁은 창은 줄이고 PC 640 이하는 세로'. 목업(아티팩트 '화면 모드 개편 목업' · PC
  `mockups/screen-modes/`)으로 문제점을 본 뒤 둘을 정했다 — ① 화면 크기 설정으로 틀 안 폭이 1100 보다 좁아지면 좁은 화면(세로 모드) ② 폰 가로 안내는 전투 화면에서 띄우지 않는다.
  - **배치는 게임이 보는 폭만 본다** — 1100 이상 = 넓은 화면(오른쪽 사이드 · 책상 · 마을 지도 · 두루마리 · 명부 책 · 가로 전투(쿼터뷰)), 그보다 좁으면 좁은 화면(위쪽 탭 ·
    640 이하는 폰 메뉴 · 세로 전투). 예전 `(min-width:1100px) and (orientation:landscape)` → `(min-width:1100px)`: game.html CSS 넷 · 스케줄 블록(sched_block.css 둘 ·
    sched_block.js 의 mq) · `TOWN_MQ`. `bfOrient()` = `townMode()` 면 landscape (예전: 창 폭 900 이하이거나 폭/높이 1.2 미만이면 portrait).
  - 기기마다 그 폭을 맨 앞 스크립트(UISCALE · 영문만)가 맞춘다 — `HS_SCALE.kind` 'pc' · 'tablet' · 'phone' (<html> 에 hs-pc · hs-tablet · hs-phone):
    · PC(`desktop()` 그대로 — 마우스 · iPad/폰/Android 빼고): **배율 1 이어도 늘 틀** — 창을 좁히면 다시 불러오지 않고 줄인다. 자동 배율 `kOf`: 폭 640 이하 ×1 · 641~1099 폭÷1100
      (천분의 일 내림 — 틀 안 폭이 늘 1100 이상) · 1100 이상 예전 큰 화면 규칙. 직접 고른 100~200% 는 그대로 — 틀 안이 1100 보다 좁으면 저절로 좁은 화면 (결정 ①).
      `set()` 은 틀 없이 돌던 데스크톱 창이면 늘 "reload"(다시 불러와 틀이 된다 · 자동화 · `?scale=off` 는 "saved").
    · 태블릿(PC 아님 · `screen` 짧은 변 600 이상): 창 폭 641~1099 면 viewport `width=1100`, 아니면 `width=device-width,initial-scale=1` — 처음 · resize · orientationchange 때마다.
      창 폭 = `visualViewport.width × scale` (viewport 를 바꿔도 · 두 손가락 확대에도 그대로). 화면 나누기로 640 이하면 좁은 화면 (계획 때 덧붙인 것).
    · 폰(짧은 변 600 미만): viewport 그대로.
    · `html{text-size-adjust:100%}` — 줄여 보이는 화면에서 iOS · 안드로이드 크롬이 글자를 멋대로 키우지 않게.
  - **ROTATE** (scalePanel 아래): 폰을 가로로 들면 `#rotateAsk` 덮개('화면을 세로로 돌려 주세요') — `#modalRoot .bf-stage`(전투 창)가 있으면 숨김(결정 ②) · 전투 창은 MutationObserver 로 본다.
    방향은 `HS_SCALE.landscape()`(screen.orientation → window.orientation → 창 모양) — 키보드가 올라와 창이 납작해져도 안 뜬다. 태블릿 세로 + 넓은 화면이면 토스트
    '가로로 돌리면 더 크게 보인다' 한 번(로딩 화면 뒤). `rotateInit()` 은 `boot()` 바로 앞.
  - 글 — 화면 크기 설명 · '가로 화면' → '넓은 화면' / '세로 화면' → '좁은 화면'(전투 연출 · 두루마리 스케줄 설명 · 알림 둘 · 설정 꼬리말). 영어: en/ui.json(바꿈 넷 + 새 셋) · en/log.json(바꿈 둘).
  - 필드 실험실(`tools/field_lab.html`) 크기 목록 — 1100 폭(태블릿 · PC 좁은 창이 보는 크기 셋) · 폰 가로 844×390 · PC 600×800 을 더했다 (게임이 보는 폭으로 가로 · 세로 전투가 갈리므로).
  - 시험: 새 `tools/check_modes.py` · `check_scale.py`(새 규칙 — 1440 · 100% 도 틀 ×1 · 900 ×0.818 · 600 ×1) · `hs.py layout`(1100×700 을 더해 네 크기) · `hs.py i18n` · `check_save.py` 통과.
    layout 이 처음 찾은 영어 넘침 둘은 en_layout.css 로 고쳤다 — 졸업생 카드 이명(`.gradcard-epi` · 1100 폭에서 말줄임 → 영어는 줄바꿈) · 입학식 역할 줄(`.cerrole` · 900 폭 도트 24px 에서
    'Assassination' 이 카드 밖으로 → 영어는 15px = 도트 12px). 둘 다 이번 화면 모드와 상관없이 전부터 있던 것 (1100 크기를 처음 재서 · 시뮬레이션 학생이 바뀌어서 보였다).
    크로미움 흉내뿐이라 **실제 기기 확인이 남았다** — iPad Safari 회전(배율이 남는지 · 두 손가락 확대 뒤) · 안드로이드 태블릿 크롬(기본이 데스크톱 사이트) · 폰 가로 덮개 · 키보드 ·
    맥 Safari · Firefox 의 틀 축소(641~1099 창 · 끌기 · 글자 번짐).
  - 알게 된 것 — 가로로 든 폰의 세로 전투는 실제 폰 크기(주소창 빼고 750×342 쯤)에서 전투판 높이가 170px 남짓으로 납작하다 (예전부터 같다 · 덮개를 안 띄우는 건 사용자가 정한 것).
    쿼터뷰가 없는 계절 필드 전투는 세로로 긴 넓은 화면(1100×1467)에서도 전투판 높이가 잘려(최대 752) 가로 비율 그대로 — 그림 · 자리가 어긋나지 않는다.
    apply_sched 를 다시 돌리면 그림 줄(SCHED_ART)이 data: 로 돌아가고 SCHED CSS 가 MDESK CSS 뒤로 옮겨 간다 — 이번에는 블록 파일과 game.html 블록을 같은 글로 고치고
    지문만 다시 적었다 (블록 파일로 apply 한 결과와 그림 줄 말고 같은지 확인함). 바꾼 스크립트: 세션 scratchpad `modes/apply_modes.py`.


- **명중 보정 — 피해를 주는 스킬 +10%p · 필살기 +20%p · 명중 확률 35 ~ 100% (1013 · 빌드 1013-0900)** — 사용자: '피해를 주는 스킬만 명중 보정 +10%,
  피해를 주는 필살기는 +20%, 기본기/반격은 보정 없음. 범위는 35%~100%로' (바로 앞 빌드 0850 은 기본기 · 반격도 +10%p 였다 — 사용자가 바로 고쳤다).
  - `HIT_BONUS_SKILL = .10` · `HIT_BONUS_ULT = .20` · `hitBonusOf(o)` (`DMG_K` 바로 아래) — `dealDamage` 의 명중 확률 = clamp(명중 + hitBonusOf(o) − 회피, .35, **1**).
    `o` 가 기술(sk)이면 kind 'basic' → 0 · 'ult' → .20 · 그 밖(스킬 1 · 2 — 중독의 첫 타 포함) → .10. 반격(`o.counter`) → 0. 양쪽 모두(적 · 마왕 포함).
    스킬 시전 판정(스킬 성공률 − 저항)은 그대로. 전투력 식(`PW`)은 다시 맞추지 않았다 (그쪽 clamp 의 .99 도 그대로).
  - 같은 팀 · 같은 상대 · 같은 시드로 1200판 (시험 세이브 봄 신인전) — 빗나간 타격: 스킬 14.6 → 5.0% · 필살기 17.4 → 0.6% · 기본기 16.4 → 15.8% · 반격 20.9 → 21.7%
    (기본기 · 반격은 보정이 없어 거의 그대로). 타격 수 약 6% 줄었다. 세션 scratchpad `hit_cmp.py`(보정 전 빌드와 견줌) · `hit_after.py`. `hs.py i18n` 통과.

- **기분 · 정보력 보정 글에 '속도' (1013 · 빌드 1013-0832)** — runBattle 은 기분(`moodStatMul`)과 정보력(`infoBattleMul`)을 체력 · 공격 · 방어 · **속도**에 곱하는데
  글은 '체력·공격력·방어력'만 말하고 있었다. 사용자: '글에 속도도 넣고' — 코드는 그대로, 글만 고쳤다.
  - 락커룸 칸 카드(`lockerHtml` · '체력·공격력·방어력·속도 ±5%') · 락커룸 창 결과 줄(`lkwResultHtml`) — LKWIN 블록. 정보력 설명(`MASTER_INFO.info.d`) · `MOOD_STAT` 주석 — 블록 밖 그대로 고침.
  - 영어: en/ui.json 다섯 줄 · en/core.json 한 줄 (HP·ATK·DEF·SPD). `hs.py layout --only tour_match,tour_lkwin,tour_lkwres` · `hs.py i18n` 통과.

- **락커룸 창이 출전과 같이 뜬다 (1013 · 빌드 1013-0811)** — 사용자: '경기 화면에 들어가서 락커룸에서 한마디 단추를 눌러 들어가지 말고, (출전 화면에서) 출전을 누르고 한마디를 안 했으면 락커룸이 같이 팝업'.
  - 경기 화면으로 넘어가는 단추 — 봄 신인전 '○팀 출전' · 친선전 '친선전 시작' · 가을 대회 '엔트리 확정' · '대진 확정'(광역처럼 대진 화면을 거치면 그 뒤) — 가 `lkwAuto(t)`.
    다음에 그려지는 그 대회의 경기 화면에서 `bindLocker` 가 한 번 쓰고 지우며, 한마디 전이면 `lkwOpen()` (경기 화면 위에 창).
  - 창(경기 시작 ▶ · 말없이 시작 ▶)이나 경기 화면의 '경기 시작'으로 전투를 열 때도 `lkwAuto` — 전투를 보고 '결과 확정'으로 다음 경기 화면에 오면 그 경기의 창이 같이 뜬다.
    '빠르게 결과만' · '남은 경기 한 번에' 뒤 · 다시 그리기(창을 닫은 뒤 · 리그 출전 팀 바꾸기)에는 뜨지 않는다 — 그때는 '경기 시작'이 창부터 (`lkwGate` 그대로).
  - 경기 화면의 '락커룸에서 한마디' 단추 · 안내(`.lkw-go` · `data-lkw`)는 뺐다 — 영어 두 줄도 en/ui.json 에서 뺐다. apply 확인에 `lkwAuto(t);` 5곳 · `data-lkw` 0.
  - 시험: 한/영 — 봄 신인전 출전 → 창(+ 튜토리얼 8) → 전투 → 결과 확정 → 다음 경기 + 창 → × → 빠르게 결과만(창 없음) → 경기 시작(창) → 말없이 시작 → 다음 경기 + 창 ·
    친선전 · 시내 · 예선(리그 — 출전 팀을 바꿔 다시 그려도 창 없음) · 광역(엔트리 확정 → 대진 확정 화면은 창 없음 → 대진 확정 → 창) ·
    `hs.py layout --only tour_match,tour_lkwin,tour_lkwres` · `hs.py i18n` 통과. 세션 scratchpad `lka_test.py`.

- **락커룸 창 — 목업 그대로 게임에 (1013 · 빌드 1013-0706)** — 사용자: '만든대로 진행하자'. 새 블록 `LKWIN` (`tools/gen/patch/apply_lkwin.py` · `lkwin_block.js` · `lkwin_block.css` — apply_cslwin 뒤). 자세한 것은 `tools/gen/README.md` 의 락커룸 창.
  - 경기 화면 셋(가을 대회 `renderLadder` · 친선전 `renderFriendly` · 봄 신인전 `renderTournament`)의 **'경기 시작' → `lkwGate`** — 그 경기에서 한마디 전이면 락커룸 창부터, 했으면 바로 전투.
    '빠르게 결과만' · '남은 경기 한 번에'는 창 없이. 경기 화면의 락커룸 칸 = 학생 기분 카드 그대로 (0706 에는 한마디 전에 '락커룸에서 한마디' 단추 · 안내가 있었다 — 0811 에 뺐다, 위) (예전 2 × 2 한마디 단추 `data-say` 는 없어졌다).
    `lockerHtml` · `bindLocker` 는 블록 안으로 (apply 가 블록 밖의 예전 것을 지운다) — `bindLocker(t, L, my, rerender, {title, label, foe, field, start})` 가 창이 쓸 것을 `LKW.ctx` 에 둔다.
  - 창 = 목업 그대로 (창 796 · 무대 768 × 432 · 쿼터뷰 지도 흐림 · 학생 1.5배 반원 · 구름 넷 · 고민 … → ~♪ / | | | · 이름표 ±20 · 결과 글 · '경기 시작 ▶' · '말없이 시작 ▶' · ×(Esc)는 경기 화면으로).
    `#modalRoot` 에 덧붙는 `.cw-ov.lkw-ov`(z 81 — 경기 화면 위 · 튜토리얼 아래). 상담창 CSS · `cslwSprUrl` · `cslwCloudArt` · `cwBlip` 을 그대로 쓴다. 고르는 순간 `lockerSpeak` + `save()`.
    튜토리얼 8 은 창을 처음 열 때 창 위에 (예전: 경기 화면에 처음 들어설 때). 좁은 화면은 상담창처럼 `.compact` (구름 · 이름표 격자는 무대 아래).
  - 영어 23줄(en/ui.json `_lkwin` 묶음 + '친선전') · 영어 이름표는 이름 · 성격 두 줄(`en_layout.css`). `check_layout.py` 에 `tour_match` · `tour_lkwin` · `tour_lkwres` (창은 점검용 `lkwOpen({instant:true, pick})`).
  - hs.py: patch 묶음에 lkwin 셋 · 새 묶음 `locker`(목업 원본 + 쿼터뷰 지도 다섯 장).
  - 시험: 한/영 · 시내 · 광역 · 예선 · 본선 · 친선전 · 봄 신인전 — 경기 시작 → 튜토리얼 8 → 구름 → 반응 → 결과 → 전투가 열린다 · 봄 신인전 세 경기 잇달아(경기마다 새 락커룸) ·
    단추로 먼저 열기 → × → 경기 화면에 결과 → 경기 시작은 바로 전투 · Esc · 말없이 시작 · 빠르게 결과만(창 없음) · 키 1 ~ 4 · 스페이스 · 폰 390 × 844(좁은 배치) ·
    `hs.py layout --only tour`(세 크기 · 넘침 0 · 남은 한글 0) · `hs.py i18n` · `check_save.py` 통과. 세션 scratchpad `lkg_test.py` · `lkg_paths.py` · `lkg_next.py`.

- **락커룸 목업 — 상담실 같은 창 (1012 · → 1013 에 게임에 넣었다(위))** — PC `mockups/locker-room/`(깃 밖) · `locker_room_mockup.html`(약 1.7MB · 인터넷 없이) · 자세한 것 · 다시 만들기는 그 README.
  - 사용자 요청: 배경은 목표 대회를 흐리게(→ 도중에 **쿼터뷰 지도** `assets/battle-fields/quarter` 로 바꿔 달라고 함 · `TQ_MAPS` · `tqMapKey` 대로 시내 city · 광역 / 예선 regional · 본선 final · 친선전 = 그 계절 학원),
    출전 3 ~ 5명이 허들, 대사는 둘레의 구름 선택지, 고르면 잠시 고민(…) → 납득은 머리 위 ~♪ · 못 납득은 머리 둘레 | | |.
  - 창 796 × 622 · 무대 768 × 432 — 상담창 CSS(`cslwin_block.css`)를 그대로 깔고 크기만 · 구름은 `cslwCloudArt` 그대로 · 학생 도트 `cslwSprUrl` 1.5배(상담창 2배의 0.95 — 다섯이면 커서) ·
    먼 쪽 반원(양 끝 앞 · 가운데 뒤, 오른쪽은 좌우 뒤집기) · 발 아래 이름표(이름 · 성격 / 기분 · 수치 / 막대 — 영어는 두 줄) · 규칙은 `makeSpeechOffers` · `lockerSpeak` · `baseMood` 그대로.
  - 목업 조작판: 대회 · 인원 · 학생 크기 · 전력 · 상대 전력 파악 · 호소력 · 흐림 · 배경 확대 · 한/영 · 운명 학생 · 말 종류 보기 · 단계 바로 보기(`?step=4`).
  - 쿼터뷰 지도 다섯 장(city · regional · final · spring · winter.png)은 hs.py 의 `locker` 묶음 (1013).

- **영어 학생 명부 책 넘침 · 상담실 확률 줄 (1011 · 빌드 1011-2038)** — 사용자 제보 넷 (스크린샷).
  - 전투 능력치 탭(영어) 오른쪽 칸이 책 밖으로 → 책에서만 짧은 이름: 책 블록 맨 위 표 `RB_BAT_N`(같은 한국어 · 맨 위 선언을 따로 둬 문맥 키 `RB_BAT_N|…`) →
    Skill Acc. · Skill Res. · Crit Res. · Daze Res. · Cond. (학생 상세 · 유물 등 다른 화면은 긴 이름 그대로). 넷째 칸까지 478px 안 (전 501).
  - 학적 탭 평판 덧말 `Earned in tournaments · expeditions`(두 줄 → 아래 줄이 책 밖) → 영어 표 값 ∅ 로 지움 (한국어 '대회 · 원정에서 쌓인다'는 그대로).
    같은 넘침이 다른 덧말에서도 날 수 있어 영어 CSS 로 덧말을 한 줄(넘치면 … · 진로 평가 덧말은 title 에 전체) · 업보 덧말 영어 `Overrides career`(예전 Karma has overtaken their career).
  - 육각형(영어) Composure · Endurance · Willpower · Drive 가 표식 · 카드 밖으로 → `drawHex` 가 영어일 때(`I18N.lang`) 옆 이름을 꼭짓점 위(위쪽 둘) · 아래(아래쪽 둘)에
    — 그린 뒤 폭을 재서 꼭짓점 가운데(정수 px · 카드 안 4px) · `.lab.vt`(en_layout_rbook.css 가 가운데 맞춤). 한국어는 예전 그대로.
  - 상담실(창이 빈 상담실일 때 · 상담 화면)에서 지도력 · 정보력 · 호소력 확률 줄 숨김 — 한/영. 일지 › 상담 기록의 확률 줄은 남겼다(사용자에게 물어볼 것).
  - **CSLWIN 블록 파일을 게임에 맞췄다** — 쿠키 기능이 game.html 블록을 직접 고쳐 `cslwin_block.js` 가 옛것이었다(그대로 apply 하면 쿠키가 사라질 뻔). game.html 블록을 블록 파일로 되돌리고
    `apply_cslwin.py` 를 고쳤다: EDITS 를 지금 코드에(쿠키 `cookie` · 잠긴 메뉴) · 블록을 **제자리에서** 갈아 끼움(뒤의 쿠키 CSS 와 차례 유지). 시험으로 돌려 그림 줄 말고 game.html 이 그대로인 것을 본 뒤 고침.
    상담창 배경 `assets/csl_art/bg.webp` 는 PC 원본(C2PA)으로 다시 구워 `?v=d6e7b139` (픽셀 같음 · 새 파일로 커밋).
  - 시험: 영어 · 한국어 책(전투 능력치 · 학적 · 육각형 — 칸 폭 · 높이 108 · 라벨 자리) · 업보 학생 · 긴 진로 덧말(… 한 줄) · 빈 상담실 창 · 상담 화면 · `hs.py i18n` · `hs.py layout`(전체).

- **배경 음악 처음부터 켜짐 (1011 · 빌드 1011-1955)** — 사용자: 영어 체험판(itch)에서 소리 기본이 꺼져 있다. 원인은 `const AUD = {on:false, …}` —
  저장된 설정(`heroschool_audio_v1`)이 없는 새 브라우저는 음악 없이 시작했다(효과음은 원래 70). 한국어판 · 사이트 · itch 모두 game.html 기본값을 쓴다.
  - game.html: `AUD.on` 기본 true · 저장값은 `typeof j.on === "boolean"` 일 때만 따른다(저장된 꺼짐/켜짐은 그대로 — 이미 꺼 둔 사람은 꺼진 채). 시작 화면은 원래 무음(BGM_NONE) ·
    NEW GAME / CONTINUE 클릭(브라우저가 소리를 풀어 주는 첫 동작)부터 곡이 흐른다. 새 브라우저는 부팅 때 계절 곡(봄 1.4MB)을 미리 받는다(음악을 켜 둔 사람은 예전부터 그랬다).
  - 시험: 새 브라우저 한/영(켜짐 · 시작 화면 SETTINGS 체크 · NEW GAME 클릭 뒤 오프닝 곡 · 설정 화면 '켜짐') · 저장된 꺼짐/켜짐/on 없는 값 ·
    itch 흉내(2560×1300 · iframe 안 틀 ×1.494 · 진짜 클릭 → WebAudio 로 opDemon · 404 없음 — 세션 scratchpad `itch/test_itch_snd.py`) · `test_itch.py` · `hs.py i18n` · `check_save.py` 통과.
  - itch 에서 이미 소리 설정을 만진 브라우저는 그 값(꺼짐)이 남는다 — 사용자 확인은 시크릿 창으로.

- **난이도별 시작 빚 (1011 · 빌드 1011-1819)** — 사용자 요청: 보통 30,000 G 에서 시작해 난이도 한 단계마다 +10,000 G (보통 3만 · 어려움 4만 · 악몽 5만 — 예전은 모두 5만).
  - game.html: `DIFFS[*].debt` · 새 시나리오가 `S.debt = S.debt0 = diffOf().debt` · `debtStart()`(= `S.debt0`, 없으면 옛 세이브라 `DEBT_START_OLD` 5만) ·
    `repayMax()`(원금 상환 상품 수 = 처음 빚 ÷ 1만 → 3 · 4 · 5 · 은행 'Lv.n / 3') · 아버지의 빚 목표 `갚은 / 처음 빚` · 은행장 첫 대사 `debtSay`(삼만 · 사만 · 오만 G일세 — 액수마다 한 문장 · 영어도) ·
    난이도 고르는 칸에 '시작 빚 30,000 G' 줄(`.nsdebt`). 옛 세이브는 그대로 5만 기준(부트가 `S.debt0` 이 없으면 5만을 적는다) · 빚이 생기기 전(0926) 세이브는 지금 난이도의 시작 빚.
    `DEBT_START` · `REPAY_MAX` 이름은 없어졌다.
  - 영어 4줄(en/ui.json `시작 빚 <b>{0} G</b>` · en/dialogue.json 은행장 3줄). `check_layout.py` 에 새 시나리오 창 화면 `newscen` 을 더했다.
  - 시험: 세 난이도 × 한/영(빚 · 상품 수 · 목표 · 은행장) · 보통에서 원금 상환 3번 → 예금 화면 · 옛 세이브(어려움 5만) · 빚 전 세이브 ·
    `hs.py i18n` · `check_save.py` · `hs.py layout --only newscen,facil_bank,mission,home,plan` 통과.
- **스케줄 단추 글자 → Jacquard 12 (1011 · 빌드 1011-1833)** — 사용자가 글꼴 목업에서 골랐다. 사이드 스케줄 단추 · 영어 운영 안내 1장의 단추 그림(`.tg-schedbtn`) 'Schedule' (한국어 운영 안내는 그림이라 그대로).
  - game.html: `@font-face "HsSchedFont"`(Mulmaru Mono 다음 줄 · A–Z a–z 2.6KB · data:) — `tools/gen/fonts/sched_font.py` 가 `Jacquard12-latin.woff2` 를 잘라 넣는다 (몇 번 돌려도 같다).
    OS/2 win 높이를 typo(960/300)와 맞췄다 — 원래 win 1020/720 이라 윈도우에서만 기준선이 6px 위로 뜰 수 있었다. 라이선스 `assets/fonts/Jacquard12-OFL.txt`(OFL 1.1 · 예약 이름 없음).
  - CSS: `font:400 42px/42px "HsSchedFont"`(21칸/em → 42px 가 2배로 또렷) · `padding:0 0 6px 62px` → 글자 상자 (92, 14) · 폭 138 · 기준선 46 — **목업과 잉크 픽셀이 똑같다**(0/1184 다름).
    `font-synthesis:none` · `-webkit-font-smoothing:none` · 굵기 400 (도트 폰트를 끈 모드에서도 같은 모양 — 확인함).
  - **물마루 바꾸기(`pixelRules`)에서 `side-sched` 를 뺐다** — 안 빼면 42px → 36px 로 줄이고 글꼴 앞에 물마루를 붙인다 (`tg-` 는 원래 빠져 있다). 예전 `html[data-font="pixel"] .tg-schedbtn` 규칙은 지웠다.
  - 시험: 한/영 · 1배/2배 · 스케줄 화면일 때 테두리 · 도트 폰트 끔/켬 · 영어 운영 안내 1장 · `hs.py i18n` · `hs.py layout --only home,plan,tut1,newscen`.
- **스케줄 단추 글꼴 목업 (1011)** — 후보 18가지 · PC `mockups/sched-font/`(깃 밖) · `sched_font_mockup.html` · 다시 만들기는 그 README. → Jacquard 12 로 반영(위).
  - 알게 된 것: hs.py 의 test 묶음에 `assets/counsel-cookie/*.png.js` 가 없어 빌드(split_assets)가 멈췄다 → 묶음에 더했다 (35개).

- **itch.io 영어 체험판 (1011 · 빌드 1011-1759)** — 사용자가 itch.io(baramutzero.itch.io/my-heros-academy · HTML · 초안)에 영어판을 올린다.
  - `tools/itch/build_itch.py`(+ 더블클릭 `build_itch.bat`) — wrap.py 와 같은 빌드에 ① 체험판 `DEMO_END = {year:2, phase:"spring", week:1}`(2년차 봄 2주차 시작에 끝)
    ② 영어가 기본(주소 ?lang= · 설정의 hs_lang 이 없으면 브라우저 언어와 상관없이 English) ③ 화면 크기 틀을 itch 의 iframe 안에서도(UISCALE `EMBED`) →
    `Claude outputs/itch/heroschool_demo_en_<빌드>.zip`(index.html + 빌드된 HTML 이 부르는 assets 476 · bgm 69 · 약 156MB — itch 제한 1000개 · 500MB 를 확인하고 멈춘다).
    빌드 번호는 `<날짜-시각>-itch`(의견 보내기에 찍힌다). **ZIP 이 30MB 를 넘어 Claude 가 PC 로 못 보낸다** — PC 에서 build_itch.bat 을 돌린다(파이썬 표준 라이브러리만).
    클라우드에서 돌릴 때는 `--root /mnt/user-data/uploads/heroschool --out <scratchpad>`(작업 폴더에 없는 그림을 받아 둔 곳 · ZIP 을 작업 폴더에 만들지 않는다).
  - game.html: `DEMO_END`(보통 null) · `demoOver` · `demoEndShow`(끝 화면 — 새 학원으로 다시 하기 = 오프닝 · 학원 둘러보기) · 0.7초마다 보고 · 행사 · 대회 · 팝업이 끝나면 띄운다 ·
    `weekRunGo` 맨 앞에서 막는다. UISCALE: `EMBED`(itch 빌드만 true — 남의 iframe 안에서도 틀이 된다) · 폴더 주소(…/)면 `index.html` 을 붙인다(itch 는 폴더 요청에 403).
    시작 때 받기(`bootAssetList`)가 템플릿 자리(`${…}`)가 든 주소를 받으려다 404 나던 것 고침. 영어 5줄(en/ui.json).
  - 시험: itch 처럼 다른 출처 페이지가 iframe 으로 띄워(2560×1300) — 영어 · iframe 안 화면 크기 ×1.494 · 404 없음 · 2년차 봄 2주차에 끝 화면 · 둘러보기 뒤 주를 못 넘김 · 새 학원 →
    오프닝 (세션 scratchpad `itch/test_itch.py`). 기존 시험 모두 통과(i18n · layout 세 크기 · check_save · check_scale · 스케줄 겹침 · 서명).
  - itch 쪽 설정(사용자에게 안내): No payments · ZIP 업로드 후 'This file will be played in the browser' · Click to launch in fullscreen · Enable scrollbars ·
    Genre Simulation · AI 공개 Yes(코드 · 영어 글). 표지(630×500) · 스크린샷은 아직 — 필요하면 만든다.

- **화면 크기 자동 맞춤 (1011 · 빌드 1011-1106)** — 사용자가 목업의 안 ① 을 골랐다. 큰 화면 PC 에서 게임 전체를 브라우저 확대처럼 키운다.
  (1013 — 위 '화면 모드'로 바뀌었다: PC 는 배율 1 이어도 늘 틀 · 100% 도 틀 ×1 · 641~1099 창은 줄인다. 아래는 1011 때의 설명)
  - game.html 맨 앞(`<title>` 바로 뒤) **UISCALE 스크립트** · `HS_SCALE`: 맨 위 창이 데스크톱(마우스가 주인 · iPad/폰/Android 빼고)이고 배율 k ≥ 1.05 면 '틀'이 된다 —
    `document.write('<body><script>…')` 로 body 를 열고 그 안에서 `window.stop()`(아래 게임은 읽지도 돌지도 않는다) → 같은 주소 `?hsf=k` 를 iframe 으로 `transform: scale(k)`.
    게임 안은 W/k × H/k 창이라 게임 코드 · 클릭 · 끌기 · 서명이 그대로. 창 크기가 바뀌면 다시 맞춘다. iframe 안은 devicePixelRatio ×k(오프닝 캔버스 또렷 · 진짜 값 `HS_SCALE.dpr0()`) ·
    탭 제목은 게임이 알려 준다(바뀔 때마다) · 언어 바꾸기 · 새 버전 불러오기는 `HS_SCALE.nav` 로 틀에 넘겨 탭째로 다시 불러온다.
  - 배율: 자동 = min(창 폭 ÷ 1280, 창 높이 ÷ 870) · 1.05 아래는 1 · 2.5 까지 (2560×1300 → ×1.494 · 1920×1070 → ×1.229 · 1920×950 → ×1.092).
    설정 › **화면 크기**(자동 · 100 ~ 200% — `scalePanel` · localStorage `hs_scale` · 폰/태블릿에서는 숨김). 100% 면 틀 없이 · 틀 없이 돌던 창에서 키우면 저장 뒤 다시 불러온다.
  - **Playwright(자동화)에서는 틀이 안 생긴다**(navigator.webdriver) — 다른 시험 · hs.py shot 은 예전 그대로. 틀 시험은 주소 `?scale=auto|150|…`(강제) · `user`(사람처럼) · `off`.
    새 시험 `tools/check_scale.py`(file:// · http:// · 진짜 마우스 · 키보드 · 설정 · 언어 · 새 버전 · 폰/iPad 제외) 통과 + 기존 시험 모두 통과.
  - 알게 된 것 — **맨 앞 스크립트에 한글을 쓰면 안 된다**: i18n 빌드가 '한글이 든 첫 스크립트'에 번역 장치를 넣는데 그게 <head> 면 정적 HTML 을 못 옮겨 영어 시험이 깨진다
    (그래서 UISCALE 은 주석까지 영어 · 한국어 설명은 scalePanel 위). **<head> 안에서 window.stop() 하면 크로미움이 다시 안 그린다**(rAF · 마우스 이동 멈춤) — body 를 먼저 연다.
    file:// 은 출처가 없어(opaque) iframe allow 는 `autoplay *; clipboard-write *`. `?hsf=k` 로 게임 쪽이 '우리 틀 안'임을 알고 처음 배율을 받는다
    (조상과 같은 주소의 iframe 은 표준상 막힐 수 있다 — 크로미움은 한 겹 허용). https 에서는 틀이 받다 만 앞부분 + 게임 한 번을 받는다.
  - 사용자 확인 대기: 실제 모니터에서의 크기(자동이 작거나 크면 설정에서) · 자동일 때 Ctrl + 확대가 거의 안 먹는 것.

- **마을 · 마스터 노트 · 스케줄 같은 액자 (1011 · 빌드 1011-0901)** — 사용자가 목업에서 마을 **안 A** 를 골랐다. 세 화면이 같은 상자(1544:1008) · 같은 나무 테두리라
  화면을 바꾸거나 두루마리 → 스케줄로 넘어가도 테두리 크기가 그대로다. 마을은 폭을 채우고 아래 16% 자름 · 마스터 노트는 책상 바탕을 746×478 로 넓힘(`desk_ext` · 소품 그대로) ·
  팝업은 액자 안에서 스크롤(나가기 · 닫기 줄은 늘 보임) · 사이드 스케줄 단추 글 한국어도 'Schedule'. 상세는 tools/gen/README '같은 액자'.
  - 고친 곳: `sched_art.py`(액자만 그림 `frame`) · `mdesk_block.js · .css` · `apply_desk.py` → `hs.py apply sched …` · `hs.py apply desk` · game.html(마을 CSS · `TOWN_FRAME` · 사이드 단추 · 운영 안내 단추) ·
    en_layout.css(영어 전용 사이드 단추 규칙 뺌). 새 그림 `assets/sched_art/frame.webp` · `assets/mdesk_art/ext.webp` — 예전 `assets/mdesk_art/base.webp` · `vig.webp` 는
    이제 아무도 안 읽는다(PC 에 남아 있다 — 사용자가 지워도 된다).
  - 시험: `hs.py i18n` · `hs.py layout`(세 크기) · `check_save.py` · 스케줄 겹침 · 서명 점검 통과. 세 화면 액자 상자 같음(1100 · 1280 · 1440 · 1920 · 영어) · 넘어가는 동안 액자 상자 그대로 ·
    다 다가갔을 때 책상 두루마리 축 = 스케줄 두루마리 축(±0.1px) · 시설 팝업 5 · 마스터 노트 팝업 2 가 액자 안.
  - PC 의 blocks.sha.json(커밋 안 함)은 SCHED_SCROLL · MDESK 가 옛 지문이다 — PC 에서 apply 하면 blockguard 가 멈춘다(위 2단계 메모와 같다 — 시험으로 돌려 보고 --force).
  - **화면 크기 자동 맞춤 목업** (사용자 요청 — 큰 모니터에서 150% 확대처럼 · → 안 ① 로 1011-1106 에 반영 · 위) — PC `mockups/ui-scale/`(깃 밖) · `ui_scale_mockup.html` · 다시 만들기 · 시험 결과는 그 폴더 README.
    배율 = min(창 폭 ÷ 1280, 창 높이 ÷ 870) · 1 ~ 2.5 (2560×1300 → ×1.49 · 1920×1070 → ×1.23 · 1920×950 → ×1.09 · 그보다 작은 창 · 폰은 그대로).
    추천안 ① 같은 파일이 큰 화면 PC 에서만 게임을 iframe 으로 한 겹 감싸 `transform: scale(k)` — 게임 안은 '작은 창'으로 보여 코드를 거의 안 건드린다(목업의 '실제 게임으로 해 보기').
    안 ② html 에 CSS zoom — vh · vw 100여 곳 · 화면 좌표 코드(skSideFit · mdeskGo · 책 · 상담창 맞춤 등)를 다 손봐야 한다. 설정 '화면 크기' 칸(자동 · 100~200%)도 제안.

- **스케줄 손보기 2 (1011 · 빌드 1011-0752)** — 사이드 '스케줄 [1주]' → '스케줄'(폰 메뉴의 큰 스케줄 단추 · 운영 안내 그림 단추도 · 위쪽 일정 칸에 이미 있다 — 900px 위쪽 탭은 그대로) ·
  원정 카드에서 '진로 평가 +' 줄 숨김(`TRAININGS` fx · 효과는 그대로) · 영어 카드 · 의뢰 쪽지의 멘탈리티 줄임말(Comp. · Gen. · Team. · Will. · End. · Drive — `MENT_SHORT` 문맥 키) ·
  명부 행동 칸 영어 **Work**(의뢰 — 칸에서만 · `SK_CHIP_N|의뢰`) · 행동 칸을 CSS 로 그려 영어에서 38 폭(`--sk-chipw` · 부상 '✚ 2wk' 자리 `--sk-injw` 40 — en_layout.css).
  영어 '1 wks' → '1wk'(`skRoster|{0}주`). 상세는 tools/gen/README '결재 · 위 단추 · 개인 행동 줄 · 명부'. 시험 모두 통과 · 영어 넘침 · 남은 한글 0.
  - 알게 된 것: `hs.py i18n` 의 '공개: 자동을 누른 뒤 (한국어 브라우저)' 가 한 번 새 게임(다른 학원 이름)으로 떠서 실패했다 — 6번 중 1번 · 같은 흐름만 12번 돌려서는 재현 안 됨.
    언어 바꾸기(`langSwitch` — save 뒤 location.replace)와 불러오기 쪽 원인은 못 찾았다. 다시 실패하면 그 페이지의 localStorage 세이브 · `curData` 예외부터 본다.
  - **마을 · 마스터 노트 화면 크기 통일 목업** (사용자 요청 · 게임은 그대로) — PC `mockups/scene-size/`(깃 밖) · `scene_size_mockup.html` 비교 페이지 · 다시 만들기는 그 폴더 README.
    지금 마을 · 마스터 노트 틀 1208×939 · 스케줄 1208×789 (창 폭 1240 이상). 통일안 = `.townmap` 을 1544:1008 · 틀 그림은 스케줄 over2 ·
    마스터 노트는 책상을 746×478 로 넓힌다(소품 그대로 · 오른쪽 사이드 밑은 판자) · 마을은 안 A(폭 채우고 아래 16% 자름) / 안 B(높이에 맞춰 왼쪽 · 오른쪽 책상 판자).
    → 사용자가 안 A 를 골라 1011-0901 에 반영(위). 배치판 · desk_layout.json 은 607×466 그대로 두고 apply 가 바탕만 넓힌다.

- **두루마리 스케줄 손보기 (1011 · 빌드 1011-0115)** — 사용자 요청 일곱 가지. 모두 `sched_block.js · .css` → `hs.py apply sched tools/gen/patch/sched_layout.json` (상세는 tools/gen/README '결재 · 위 단추 · 개인 행동 줄 · 명부').
  - 결재: 서명을 한 번 남긴 뒤로는 다섯 칸이 차면 **결재란도 깃펜처럼 반짝이고, 누르면 바로 깃펜이 서명**(`skAutoSign`) · 안내 '클릭으로 서명'. 결재란 맨 위 '결재' 옆에 비용(일과 · 식단) ·
    진행 글자 24 → 20 · 서명 칸 107×20 → 107×33 (예전 서명은 서명 줄에 붙여 그대로 쓴다 — `skSigFit`).
  - 위 단추(자동 배치 · 식단 · 전부 비우기) 크게 · 신비한 성수 · 예지의 서를 개인 행동 줄 오른쪽 끝으로 · 변경 취소 단추는 명부 맨 끝 빈칸으로 ·
    명부는 남는 자리를 다 쓰게(15명 두 단 8 + 7 이 1배 → 1.5배 · 9~13명은 1.625배).
  - **물마루 글꼴 모드는 스타일시트의 px 글자를 12 · 24 로 바꿔 끼운다** — 사이 크기는 `calc(18px)` 로 써야 한다 (README).
  - 영어: 두루마리 제목은 문맥 키로 짧게 `Kingdom Year 231 · Spring Wk 1`(고전 화면은 그대로) · 식단 단추 `Meals: Plain (20 G each)` · 결재란 비용 `Cards 520 G · Meals 20 G×15` ·
    첫 서명 안내 `Dip the quill to sign`(예전 글은 'Headmaster' 와 겹쳤다) · 교회 단추는 영어에서 거의 늘 이름을 숨긴다(아이콘 · 권수 · 값). 옛 키 4개 지움 · 새 키 11개.
  - 시험: `hs.py i18n` · `hs.py layout`(세 크기 · 넘침 · 남은 한글 0) · `check_save.py` 통과. 상태 11가지 × 한/영 × 5크기(1100~1920) 겹침 점검 0 ·
    서명 없음(안내만) · 예전 서명(빛남 → 누르면 자동 서명 → 진행) · 새로 그은 서명(107×33 저장 → 진행) 확인.

- **영어판 5단계 — 마무리 · 공개 + 용어집 검토 반영 (1011 · 빌드 1011-0018)** — 계획 문서 '5단계 결과' 절. **영어판이 켜졌다**: `tools/i18n/config.json` public:true.
  - 언어: 처음 접속은 브라우저 언어(ko… → 한국어 · 그 밖 → English) · 설정 › 언어(자동 · 한국어 · English · `hs_lang`) · `?lang=` 고정.
    공개 뒤 첫 방문에 세이브가 이미 있으면 한국어로 기억(`hs_lang0` 표시 · `i18n_build.py` 의 `head_script`) — 원래 하던 사람이 영어 브라우저여도 갑자기 바뀌지 않는다.
  - 공유 미리보기: 맨 위 **`en/index.html`**(영어 공유 링크 — 영어 og 태그 · `site/og-en.png` · `site/?lang=en` 으로 넘김) · `site/og-en.png`(1200×630) — `python3 tools/i18n/og_en.py` 가 둘 다 만든다.
    한국어 `site/og.png` 의 꼬리표(직업 12종 · 스킬 48종)는 옛 수 — 지금은 16 · 64 (사용자에게 알림 · 그림은 그대로 둠).
  - 지난 한국어 일지를 영어로: 런타임 `I18N.line` + game.html `curLog` — 일지(날짜 · 글) · 지침 무시 상담 기록의 대답 · 반응 · 오른 능력을 그릴 때 영어 표에 거꾸로 맞춘다
    (README '마무리 · 공개'). 한국어 3년 세이브의 일지 260줄 모두 영어 · 처음 0.4초. 상담창 블록 안의 고민 상담 기록(`cslRecHtml`)은 대답 · 반응이 불러올 때 이미 바뀌어(통째로 같은 글) 손대지 않았다.
  - 용어집 검토(사용자 · 탭 rev 273) 반영: 멘탈리티 **Stats**(한 항목은 Stat) · 필살 **Ult** · 전열/후열 **Front/Back**(이름 칸 · 능력 줄 — 이야기 · 설명 문장은 front row 그대로) ·
    고민 **Concern**(상담창 꼬리표) · 카드 Fitness · Spar · Drill · Meditate · Theory · Tactics · Self-Train · Hard Train · Live Duel · Deep Med. (도구 설명은 'Unlocks the … card') ·
    배지 3 wks → 2 wks → **Last wk** · 빈 칸 Place card · 소모품 Holy Water · 몽크 필살 Hundred Fist · 성도 the Capital City. 2단계 표의 '신뢰 단계 설명' 줄은 아직 검토 전.
  - 시험: `hs.py i18n`(공개 뒤 언어 고르기 · 예전 세이브 · 자동 포함) · `hs.py layout`(**남은 한글도 찾는다** — 언어 이름 말고 0) · `check_save.py` 통과.
    시험은 크로미움 locale 을 정해 띄운다(한국어 ko-KR · 영어 en-US) — 공개 뒤에는 브라우저 언어로 고르기 때문. `hs.py shot` 도 ko-KR (영어는 `?lang=en`).
  - 남은 것: 운영 안내 그림 6장 영어판(사용자 결정 — 나중) · 대사 검토 페이지의 검토(사용자 · 아래 4단계 '다음') · 용어집 '신뢰 단계 설명' 줄.
  - 알게 된 것: `apply_cslwin.py` 가 game.html 에서 멈췄다 — 쿠키 기능 뒤로 EDITS 의 옛 글을 못 찾았다 → **1011 빌드 2038 에 고침**(위 '영어 학생 명부 책 넘침' 항목).
    (EDITS 는 1011-2038 에 지금 코드에 맞췄다 — 이제 CSLWIN 블록은 블록 파일에서 고쳐 apply 하면 된다.) 그래서 1년차 암흑 사제의 ‘마스터’ 가 든 고민 상담 기록(블록 안 `cslRecHtml`)은 지난 한국어 글이 영어판에서도 한국어로 남을 수 있다(드묾).

- 영어판 4단계 — 대사 · 이야기 · 오프닝 (1010 · 빌드 1010-2248) — 계획 문서 '4단계 결과' 절 · 용어집 탭 맨 아래 '4단계에서 새로 정한 이름' 표 ·
  **대사 검토 페이지**(Artifact · db) https://claude.ai/artifact/3zCtNy45FqCpQmaxWXQKJn. 번역 단위 5,283가지 중 5,228 — 남은 것은 조사 조각 · 개발용 화면 · 채팅 금칙어(`CHAT_BAD` 36 — 한국어 그대로)뿐.
  - 영어 표: `en/dialogue.json`(1,103 — 상담 · 반응 · 지침 무시 · 신뢰 · 인사 · 진로 사유 · 입학 메모 · 대회 연설 · 라이벌/소울메이트 장면 · 상점 주인 말) ·
    `en/story.json`(354 — 이명 사연 · 의뢰처 이야기 · 불꽃놀이 · 발렌타인 · 합숙 깨달음 · 길드 · 이야기 팝업 머리글 · 마을 손님) · `en/opening.json`(62 — 오프닝 대화 · 아버지의 마지막 · 프롤로그).
    말투는 용어집의 성격별 말투 표대로 (stone 은 줄임말 없음 · Master 대문자). 만든 도구(세션 scratchpad `p4/`): `tr_P*.txt`(표 항목 번호) · `tr_R.txt`(나머지) · `fix_P.txt` → `merge4.py`
    (할 일 목록 전부 덮는지 · 자리표 · 태그 · 다른 표와 겹침 · 따옴표를 한국어 모양에 맞춤). 다시 만들 일은 없고 값은 json 을 직접 고친다.
  - **따옴표 규칙**(README '대사 · 이야기 · 오프닝'): 한국어가 “ ” 면 영어도 “ ” — `answerDefy` 가 “ ” 로 대사 · 서술을 가르고 `masterQ(…, true)` 가 “ ” 안만 바꾼다. 곧은 따옴표를 쓰면 지침 무시 반응이 두 번 찍힌다.
  - game.html (작은 고침): `masterQ` 가 영어 `Master` → ‘Master’ 도 · 불꽃놀이 대사 「 」 → 영어 “ ” · `STORY_ART_EN`(길드 4쪽 편지 영어판 그림 `assets/story_art/guild4-spring-en.webp` — 손글씨만 다시 씀) ·
    오프닝 대화창 글자 빠르기 영어 21ms. OPTX 블록(`optx_block.js` → `apply_optx.py`): 영어 장면 `SC_EN` (때 · 효과는 한국어와 같고 글 · 줄 · 글꼴만 — 세리프 EB Garamond ExtraBold `OpTxSerifEn` ·
    산세리프 고운돋움 라틴) · 타자기 제목은 소리 `OP_TYPE_AT` 에 맞춰 오른쪽부터 음절 조각 일곱 · `optx_fonts.py` 가 SC_EN 글자도 조각에 넣는다(라틴은 latin 묶음 한 곳에서 — 커닝).
  - 시험: `hs.py i18n` 통과 · `hs.py layout` 영어에서만 넘친 칸 0 (화면 88 · 86 · 86) — **이야기 팝업 37 · 프롤로그 3 · 마을 손님 2 를 화면 목록에 더했다**(`cer_*` · `prologue*` · `townev_*` — 이명이 붙은 학생의 컨디션 줄이 900px 에서 넘쳐 영어 CSS 를 모든 폭으로) ·
    `check_save.py` 통과 · 상담창(지침 무시 → 질문 → 답 구름 → 대답) 1440 · 390 · 오프닝 캔버스 장면 13개를 멈춰 찍어 확인. 서버에는 아무것도 쓰지 않았다.
  - 다음: 사용자가 대사 검토 페이지에서 줄마다 좋음 · 고치기를 남긴다 → 다음 세션이 `ArtifactData`(action list · url 위 · collection `review`)로 읽어 en/*.json 에 옮긴다.
    문서 하나 = 한 줄: `{s: ok|fix, en: 고친 영어, en0: 검토할 때의 영어, ko: 한국어 키, g: 표, path, note, at}` — 키는 `ko`(빌드 키 모양 그대로) · 오프닝 글(캔버스)은 g 가 `OPTX 장면` 이고
    optx_block.js 의 `SC_EN` 을 고친 뒤 optx_fonts.py → apply_optx. 페이지를 다시 올리려면 Artifact read 로 원본을 받아 같은 url 로 (줄 id = md5(갈래|키)[:10] — 바뀌면 기록이 끊긴다).
    (1011 에 확인했을 때 db 는 비어 있었다 — 아직 검토 전. 5단계에서 용어집대로 바꾼 줄 두 개(Ult)는 검토 페이지의 en 과 다르다 — 검토 반영 때 지금 json 값을 기준으로.)
    선택: 상담창 글자 빠르기(`CSLW_CPS` — CSLWIN 블록이라 apply 필요) · 이명 사연은 얻을 때의 언어로 세이브에 남는다(일지처럼).
- **영어판 3단계 — 데이터 · 이름 (1010 · 빌드 1010-2122)** — `en/data.json`(401) · `en/names.json`(818 — 이명 말고는 문맥 키) · 세이브 · 서버의 데이터 글이 언어를 따라간다
  (런타임 `I18N.toCur` · `toKo` + game.html `curData` · `koData` · `nameEnFirst` — README '세이브 · 서버의 데이터 글') · `dn()` 영어는 이름 먼저 · 의뢰 → **Errand** (사용자 결정) ·
  스킬 이름은 명부 책 칸(94px)에 맞춰 짧게 · `check_save.py`(새). 용어집 탭 '3단계에서 새로 정한 이름' 표 두 개는 사용자 검토 대기.
- **영어판 2단계 — 화면 · 일지 · 안내 · 전투 화면 (1010 · 빌드 1010-2014)** — 계획 문서 https://claude.ai/code/artifact/4196b470-b22d-4135-ac8d-392814696041
  (2단계 결과 절 · 용어집 탭 맨 아래 '2단계에서 새로 정한 이름' 표 — 사용자가 English · 검토 칸을 고친다. 고친 값은 다음 세션이 `tools/i18n/en/*.json` 에 옮긴다).
  - 영어 표 `tools/i18n/en/` — ui(1,369) · log(346) · tut(227) · battle(142) · core(377 — 직업 16 · 성격 · 멘탈리티 · 카드 · 시설 · 도구 · 원정지 · 진로 · 목표 · 신뢰 · 유명도 · 인가 등
    화면에 바로 보이는 데이터 이름). 번역 단위 5,282가지 중 2,496 (47%). 남은 것: 대사 1,139 · 이름 811 · 데이터 설명 401 · 이야기 353 · 오프닝 62 (`python3 tools/i18n/todo_en.py`).
  - 번역 장치 다시 짬 (README): 키는 **글 덩어리**(블록 태그로 나누고 짧은 태그는 속성을 뺀 채 남긴다) · 속성 값의 한글도 단위 · `맨위선언|키` 문맥 키(같은 한국어를 곳마다 달리 —
    `VIEWS|진행` = Schedule · `진행` = Continue · `DAY_N|월` = Mon …) · 값 `∅` = 빈 글 · 영어 화면 CSS(`en_layout.css` · 책 그림자 DOM 은 `en_layout_rbook.css` — 런타임이 영어일 때만 붙인다).
  - game.html (모두 작은 고침 · CRLF): 영어 어순을 막던 조각 잇기 9곳을 템플릿 하나로(`대상 유물 2 변경` · `${n}명` · `${L}주 뒤` · `${k}팀` · `${i+1}라운드` · 순위 `위` · 지침 무시 칸 · 시설 효율) ·
    현황판 `PING_PH` 와 when 은 `/*no-i18n*/`(서버로 가는 글은 한국어) · `uiLoc()`(날짜 · 숫자 형식 — 영어 en-US · `"ko-KR"` 9곳) · `FB_ICON` · `TUT_ICON` 이 영어면 `_en` 그림.
    두루마리 스케줄 블록(`sched_block.js` → apply sched): 카드의 컨디션 값을 `^컨디션` 대신 부호부터 읽는다 — **PC 의 블록 지문(blocks.sha.json)은 SCHED_SCROLL 도 옛것이 됐다** (PC 에서 apply sched 를 돌리면 blockguard 가 멈춘다 → 시험으로 돌려 game.html 이 그대로인지 보고 --force).
  - 그림: `assets/tut_icon_a_en.webp`(TUTORIAL) · `assets/fb_icon_a_en.webp`(FEEDBACK) — 같은 그림에 띠 글자만 다시 구움 (Poppins Bold). 운영 안내 그림 6장은 사용자 결정대로 나중 (영어는 글 안내).
  - 시험: `hs.py i18n` 통과(한국어 세이브 13 · 화면 19 같음) · **`hs.py layout`**(새 · `tools/i18n/check_layout.py`) — 화면 47가지 × 1440×900 · 900×1000 · 390×844 에서 영어에서만 생긴 잘림 · 넘침 0.
    한국어보다 줄이 늘어난 칸 179 는 넘침이 아니라 개수만 (`--wrap` 이면 목록). 스크린샷 `~/hs/shots/layout`.
  - 번역 방법(다음 단계도 같게): `todo_en.py --cat data --out a.tsv` → 영어 칸 채우기(용어집 · 말투 탭 기준 · 자리표 `{n}` · 복수 `{n} {n|x|xs}` · 조사 자리는 버림) →
    `todo_en.py --merge a.tsv en/data.json` → 빌드 → `hs.py i18n` · `hs.py layout`. 한 글자 낱말은 전체 키로 옮기지 않는다(성 '이' · '황' 등 — 문맥 키로만).
  - 다음: 사용자가 2단계 영어를 게임(`?lang=en`)과 표로 검토 → 3단계(데이터 · 이름 — 직업 · 스킬 · 유물 · 몬스터 설명 · 이명 · 학생 · 학원 이름 조각 · 세이브에 원문 번호).
    알려진 할 일: guildCeremony 의 `{when}` 자리(4단계 이야기와 같이) · masterQ(4단계) · acadNames 꼬리 정규식(`(용사\s*)?학원` — 5단계 이름) · 진형 강화 꼬리 `·改`(3단계) ·
    학생 명부 책 육각형의 Composure · Endurance 가 카드 테두리에 조금 걸린다(영어 CSS 로 7px 당김 — 더 고치려면 roster_tpl.html · apply roster).
- 영어판 1단계 — 번역 장치 (1010 · 빌드 1010-1818): 빌드 변환(`i18n_build.py` — 실패하면 한국어만 · `HS_I18N=0`) · 로딩 화면 두 언어(`build_boot.py`) · 설정 '언어 · Language' 칸(`?lang=` 시험 접속에서만) ·
  영어에서 조사 함수 빈 글 · 스크립트 밖 HTML 은 처음 한 번 표로 · 운영 안내 그림 대신 글 안내 · 페이지 제목. 사용자 결정: 영어 제목 **My Hero's Academy - The Academy Went Under** ·
  UI 글꼴 물마루 그대로 · 오프닝 세리프 EB Garamond ExtraBold(4단계) · 첫 실행은 브라우저 언어(공개 뒤 — `tools/i18n/config.json` public) · 학생 이름은 원래 철자(Gawain) · 이명은 이름 뒤 ·
  운영 안내 그림 6장은 나중에. 사용자는 영어 원어민이라 번역 검토를 직접 한다 · 성격별 말투 9줄은 확정, 핵심 용어 62줄은 검토 전.
- 그 앞 (빌드 **1010-1558**) — 세계관 피로도 진단 문서를 보고 사용자가 고른 세 가지를 반영했다.
  - **미션 '지침' → '목표'**: 사이드 단추(목표 1/4) · 위쪽 칸(#mMis) · 목표 창 · 달성 일지 · 토스트 · 초대장 안내 · 연간 흐름 글.
    '지침'은 이제 학생의 행동 지침(지침 무시 상담)만 뜻한다. 코드 이름(MISSIONS · S.mission · side-mis)과 주석은 그대로.
  - **'개인 명성' → '평판'**: 학생 상세 · 학생 명부 책 학적 탭(`roster_block.js` → apply roster) · 대회 결과 표 · 이명 일지 · 이명 창. 값은 그대로 `st.fame`. 학원 명성 · 유명도는 그대로.
  - **졸업생 리그 메뉴 잠금**: 첫 졸업생이 나오기 전(`S.graduates` 비어 있음)에는 메뉴 단추에 자물쇠 + 흐리게 (가로 사이드는 그림을 잿빛으로 + 가운데 자물쇠 · 위쪽 탭 · 폰 더보기는 글자 앞 자물쇠).
    누르면 토스트 '졸업생 리그는 첫 졸업생이 나오면 열린다.'만 (메뉴 소리 없음). 리그 묶음 화면(리그 · 등록 · SP 상점 · 순위)으로 가려 하면 마스터 노트로.
    코드: `lgUnlocked` · `LOCK_ICO`(도트 자물쇠 SVG) · `navLockToast` · render 가 `tabs[].lock` 을 단다 · CSS `NAV_LOCK_START~END`. 다른 메뉴도 `lock` 만 달면 같은 모양이 된다.
    SP 는 졸업생(리그 · 이적 · 마왕 대항전)으로만 생겨서 그 전에 잠가도 잃는 것이 없다. 운영 안내 9장(리그)은 졸업식 뒤에 뜨므로 그때는 이미 열려 있다.
  - 시험: 1440×900 · 900×760 · 폰 390 에서 잠금 모양 · 누르기(화면 그대로 · 토스트) · 리그 화면 막기 · 졸업생을 넣으면 열림 · 목표 창 · 평판(학생 상세 · 명부 책) — 오류 0.
- 그 앞 (1010-1530 · 다른 세션): 운영 안내 1 · 2 · 3 · 4 · 5 · 12장을 그림으로 (`assets/tutorial-illustrated/NN.webp` · `tutGuideHTML`). 그림 글자에 '지침' · '개인 명성'은 없다 (4장 제목은 '대회 목표').
- 그 앞 (1010-1250): 두루마리 스케줄에서 **사이드가 잉크 단지 · 깃펜을 가려 결재를 못 하던 것**(14인치 맥북 제보) — `sched_block.js` 의 `skSideFit`. 끝까지 내렸을 때 소품 위쪽을 재서
  사이드가 거기까지 내려오면 'MENU' 글자 → 스케줄 단추를 숨기고, 그래도 길면 높이를 줄인다. 상세 · 시험은 tools/gen/README.
- 그 앞 (1010-1216): 새 시나리오 오프닝의 글 아홉 장면을 **APNG → 캔버스 글자(OPTX)** 로 (`apply_optx.py` · `optx_block.js` · `optx_fonts.css` — 상세는 tools/gen/README 의 ‘오프닝 글’).
  예전 APNG 아홉 장(12.3MB)은 PC 에 남아 있다 — 사용자가 지워도 된다. **오프닝 글 비교 페이지**(Artifact) — https://claude.ai/artifact/VnR97bQycuQZTSDSqjxWZV · 원본 `Claude outputs/opening_compare/`.
  로컬라이징(영 · 일 · 간 · 번)은 아직 고민 중 — 바꿀 때는 `SC` 의 글 · 글꼴만 언어별로.
- **세계관 피로도 자가진단 문서**(Claude Docs) — https://claude.ai/code/artifact/b235b9ab-90cb-4792-b93a-15ca1bdb1d7a
  보이는 용어 55개를 가치 · 비용으로 판정하고 대체어 · 조치 계획(11장)을 적었다. 위 세 가지가 그중 반영한 것. '인가' · '유명도' 중 하나로 합칠지는 문서 댓글로 사용자에게 물어 두었다.
- 다음 할 일(그때): 진단 문서의 남은 조치(명성 단계 이름 합치기 · 스케줄 용어 통일 · '의식' 규칙을 보이는 곳에 등) 중 사용자가 고른 것 ·
  제보한 분이 14인치 맥북에서 결재가 되는지 확인 · 사용자가 게임에서 오프닝을 보고 고칠 점 · 예전 APNG 아홉 장 지우기(사용자).
- 그 앞(1009): 학생 명부 책 → 게임(apply_roster · 스킬 임의로 강화 · 유물 빈 칸 · 학적 색 · 육각형 차례) · 메뉴 단추 효과음(`SFX.menu`) · 학생 명부 목업 · 배치판.
  그 앞(1008): 상담창 · 상담 대사 성격별 · 행동 지침 무시 · 스킬 등급표 · 원정 3구간 · PNG→WebP · 두루마리 스케줄 · 마스터 노트 책상 · 쿼터뷰 대회 화면.

## 8. 이 문서 고치기

세션을 마칠 때나 사용자가 "인수인계 업데이트" 라고 하면 7번을 새로 쓰고(지난 내용은 줄여서), 새 규칙이 생겼으면 1번에 더한다.
`hs.py pack` 으로 다른 파일과 같이 PC 에 쓴다.
