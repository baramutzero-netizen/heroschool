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
| test | 학생 도트 · 전투 이펙트 (assets/spr_img · spr_x_img · fx_img — 게임 화면 테스트용 · 빌드에도 필요하다: split_assets 가 찾는다) |
| placer | 상담 목업 · 책상 배치판을 다시 만들 때 (src 전부 · 직업 도트 그림 · 목업의 학생 얼굴) — core · counsel 과 같이 |
| roster | 학생 명부 목업 · 배치판 (mockups/student-roster 전부 · 초상 16 · 스킬 아이콘 · 책상 겹) — core 와 같이 (121개 · 세 번에 나눠 받는다) |
| i18n | 영어판 글 목록을 다시 뽑는 `extract_ko.cjs` · `classify_ko.py` — core 와 같이 (acorn 은 저장소 밖에서 npm i) |

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
- 블록(`SCHED_SCROLL` · `MDESK` · `CSLWIN` · `ROSTERBK` · `OPTX`)은 블록 파일(`tools/gen/patch/*_block.js · .css`)에서 고치고 apply — game.html 안을 직접 고치면 다음 apply 가 지운다.
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
| `mockups/counsel-window/` | 상담창 목업 · 상담 책상 배치판 · 그림 (gitignore — PC 에만) |
| `mockups/student-roster/` | 학생 명부 목업 · 학생 명부 배치판 · 견본 학생 · 책 그림 (gitignore — PC 에만 · README 에 굽는 법) |
| `Claude outputs/` | 예전 결과물 · 스케줄/책상 배치판 키트 (gitignore) |
| `sprites/` · `ui/` · `events/` · `reports/` · `captures/` | 원본 · 작업 폴더 (gitignore) |
| `test.py` | Playwright 3년 회귀 테스트 (오래 걸린다 — 전투 · 성장 수치를 건드렸을 때만) |
| `tools/players.html` | 플레이어 현황 (개인용 · gitignore) |

## 4. 빌드 · 패치 요점

- apply 순서 (`tools/gen/README.md` 쓰는 법): sched → desk → exped3 → skgrade → cslpers → cslwin → roster → webp → wrap → wrap_site.
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
  책은 가로 넓은 화면(1100px 이상)에서만 뜬다 — `open_game(p, w=1440, h=1000)`. 상태는 `RBK.isOpen()` · `RBK.state`.

## 7. 최근 작업 · 현재 상태 (2026-10-11 · 빌드 1011-0115)

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
  - 알게 된 것: **`apply_cslwin.py` 가 지금 game.html 에서 멈춘다** — 쿠키 기능 뒤로 `answerCounsel` 의 `res` 에 `cookie` 가 붙어 EDITS 의 옛 글을 못 찾는다(1011 확인 · 고치지 않음).
    CSLWIN 블록을 고칠 일이 생기면 EDITS 부터 지금 코드에 맞춘다. 그래서 1년차 암흑 사제의 ‘마스터’ 가 든 고민 상담 기록(블록 안 `cslRecHtml`)은 지난 한국어 글이 영어판에서도 한국어로 남을 수 있다(드묾).

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
