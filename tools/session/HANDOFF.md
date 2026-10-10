# 새 세션 인수인계 — 용사 학원 키우기 (D:\heroschool)

Claude 가 새 세션을 시작할 때 읽는 작업 메모. **세션을 마칠 때 '7. 최근 작업'을 고쳐 둔다.**
기능별 상세는 `tools/gen/README.md`, 게임 전체 · 빌드는 `README.md`.

## 0. 시작 순서

1. 이 파일과 도우미를 받는다 — device_stage_files
   `["D:\\heroschool\\tools\\session\\HANDOFF.md", "D:\\heroschool\\tools\\session\\hs.py"]` → 이 파일을 Read.
2. 도우미를 꺼내 두고, 할 일에 맞는 묶음 목록을 찍는다.
   ```
   cp /mnt/user-data/uploads/heroschool/tools/session/hs.py ~/hs.py
   python3 ~/hs.py list core patch          # + counsel (상담창 그림) · rbook (학생 명부 책) · test (게임 테스트) · placer (상담 배치판) · roster (학생 명부 목업)
   ```
   찍힌 배열을 그대로 device_stage_files 의 paths 로 (한 번에 50개). **없는 파일이 하나라도 있으면 그 호출 전체가 실패**한다 — 그 경로만 빼고 다시.
3. `python3 ~/hs.py init` → 작업 폴더 `~/hs/work` (PC 와 같은 모양) + PC 원본 `~/hs/base`. 블록 지문(`blocks.sha.json`)도 작업 폴더에 넣는다.
4. 빌드하면 늘 커밋할 네 파일의 mtime 을 stage 결과에서 바로 적어 둔다 (나중에 찾느라 헤매지 않게):
   `python3 ~/hs.py mtimes game.html=… heroschool.html=… site/index.html=… site/version.json=…`
5. 나중에 파일을 더 받으면 `python3 ~/hs.py sync` — PC 쪽이 바뀌었으면 작업 폴더로 넘기거나 3-way 병합한다.

| 묶음 | 내용 |
|---|---|
| core | game.html · heroschool.html · site/index.html · site/version.json · wrap 스크립트들 · 이 폴더 |
| patch | tools/gen/README.md + tools/gen/patch 의 apply 스크립트 · 블록 · 배치 |
| counsel | apply_cslwin 이 읽는 상담창 그림 · 배치 (mockups/counsel-window/art · src/compose_desk.py) |
| rbook | apply_roster 가 읽는 학생 명부 책 — 목업 원본 `src/roster_tpl.html` · `art/book.png` · `ribbon.png` · `roster_layout.json` (4개) — patch 와 같이 |
| test | 학생 도트 · 전투 이펙트 (assets/spr_img · spr_x_img · fx_img — 게임 화면 테스트용 · 빌드에도 필요하다: split_assets 가 찾는다) |
| placer | 상담 목업 · 책상 배치판을 다시 만들 때 (src 전부 · 직업 도트 그림 · 목업의 학생 얼굴) — core · counsel 과 같이 |
| roster | 학생 명부 목업 · 배치판 (mockups/student-roster 전부 · 초상 16 · 스킬 아이콘 · 책상 겹) — core 와 같이 (121개 · 세 번에 나눠 받는다) |

## 1. 꼭 지킬 것

- **Firebase 서버에 쓰지 않는다** (사용자 허락 없이). 읽기는 된다. 테스트는 바깥 주소를 막고 돌린다 — `hs.py shot` · `open_game` 은 http(s) 를 전부 막는다.
- **Firebase 데이터베이스 secret 은 채팅 · 파일 · GitHub 어디에도 쓰지 않는다** — 대시보드(tools/players.html) 입력칸에 사용자가 직접 넣는 것뿐.
- **git commit · push 는 사용자가 한다.** Claude 는 PC 파일에 쓰기까지만 하고, 덮어쓴 파일 목록을 알려 준다.
- **PC 에 쓸 때는 항상 expectedMtimeMs** (새 파일만 빼고). force 금지. 거절되면 다시 받아 → `sync`(병합) → 다시 빌드 → pack.
- **다른 세션이 D:\heroschool\game.html 을 동시에 고친다.** 받은 지 오래됐으면 커밋 전에 다시 받아 sync. mtime 이 덮어쓰기는 막아 준다.
- 파일 하나 20MB 까지.
- 돌리지 않는 것: `ui/chronicle/pack.py` · `sprites/story.py`.
- 학생 프로필 얼굴(초상화)은 WebP 로 바꾸지 않는다.
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
- 긴 시나리오는 직접 스크립트로: `sys.path.insert(0, os.path.expanduser("~")); import hs; b, pg, errs = await hs.open_game(p)` — 띄우는 데 4초쯤.
- 게임 상태: `S` (세이브) · `UI.view` · `render()` · `closeModal()`. 상담 대기열 `counselState().queue` · 지침 무시 `defyState().pend` · 난수 `RNG`.
  새 브라우저마다 새 게임(1년차 봄 · 학생 3명)으로 시작한다.

## 6. 자주 걸린 것

- 도트 테마 `html[data-ui-finish="pixel"]` 가 모든 button 에 네모 테두리 · 그림자를 `!important` 로 붙인다 (특이도 0,4,2) → 덮으려면 클래스 다섯 개짜리 선택자.
- 상담창은 글자가 찍히는 중에 누르면 '바로 끝까지'라서, 테스트는 준비 상태(`CSLW.phase` · `!CSLW.typing`)를 기다린 뒤 누른다.
- game.html 은 CRLF. 직접 고칠 때는 파이썬으로 읽고 써서 줄바꿈을 지킨다 — `hs.py status` 가 섞이면 경고한다.
- 받은 파일은 1초쯤 늦게 나타난다 (init · sync 가 기다린다). 커밋은 outputs 에 복사하고 몇 초 뒤에, 매번 새 폴더로 (pack 이 한다).
- 학생 도트는 `sprCellCv` (256 칸 · 머리색 치환). 상담창은 128 칸으로 잘라 발끝(무대 2배 280, 288)을 축으로 직업별 `CSL_SPR` 크기 · 자리.
- `apply sched` 는 `tools/gen/kit` 의 모듈(schedule_mock · schedule_mock2 · desk_top)이 있어야 돈다 — patch 묶음에 없다. `apply desk` 는 `tools/gen/patch/desk_out/` 그림이 있어야 한다.
- 게임 함수로 견본 데이터를 만들 때는 `withSeed("이름", fn)` 으로 난수를 고정한다 (`let RNG = Math.random` · seedRNG).
- 학생 명부 책은 그림자 DOM(`#rbHost`) 안 — 테스트에서 `document.getElementById('rbHost').shadowRoot` 로 찾는다 (Playwright 의 `locator('#rbHost …')` 는 그대로 뚫고 들어간다).
  책은 가로 넓은 화면(1100px 이상)에서만 뜬다 — `open_game(p, w=1440, h=1000)`. 상태는 `RBK.isOpen()` · `RBK.state`.

## 7. 최근 작업 · 현재 상태 (2026-10-10 · 빌드 1010-1216)

- 마지막 게임 빌드 **1010-1216** — 새 시나리오 오프닝의 글 아홉 장면을 **APNG → 캔버스 글자(OPTX)** 로 바꿨다. 진행 중인 게임 수정 없음.
  - `tools/gen/patch/apply_optx.py` · `optx_block.js`(장면 · 글 · 효과 · 때 전부 — `SC`) · `optx_fonts.css`(나눔명조 ExtraBold · 고운돋움 조각 50KB) · `optx_fonts.py`(조각 굽기). 상세는 tools/gen/README 의 ‘오프닝 글’.
  - 예전 APNG(intro · rift · danger · date · title-type · dad-dontsay · dad-dream · dad-hero · date-winter, 합계 12.3MB)를 50ms 장마다 재서 효과 · 때를 옮겼다 — 비교 페이지에서 겹쳐 보면 글자 위치 0~4px.
    `OPTX.make(장면, 예전과 같은 클래스)` 가 예전 `apngImg` 자리에 (인트로 · 시공 균열 · 위험 · 날짜 · 타자기 · 아버지 넷). `OPENING.<장면>` 은 `{ms, tail}` 만.
    처음 내려받기에서 APNG 아홉 장이 빠졌다 (`bootAssetList` 는 HTML 의 assets/ 경로만 받는다). 파일은 PC 에 남아 있다 — 사용자가 지워도 된다.
  - 시험: 아홉 장면을 게임 안에서 멈춰 찍기 + 실제 오프닝 흐름(인트로 → 대화 → 시공 균열 → 위험 · openingFinish → 날짜 → 타자기 → 아버지 넷)에서 오류 없음.
- 오늘 한 것 (1010):
  - **오프닝 글 비교 페이지**(Artifact) — https://claude.ai/artifact/VnR97bQycuQZTSDSqjxWZV · 원본은 `Claude outputs/opening_compare/` (PC 에만).
    왼쪽 APNG · 오른쪽 캔버스를 같은 시계로 (나란히 · 겹쳐서). 인트로 · 시공 균열은 다섯 언어(영어 · 일본어 · 간체 · 번체는 비교용 초벌 번역 · 글꼴 Gelasio · Noto Serif/Sans CJK),
    한국어 글꼴 비교(APNG와 같은 글꼴 · 나눔명조 Bold · 물마루 · 물마루 가늘게 — 게임에는 ‘APNG와 같은 글꼴’). 시공 균열 비교 움짤 rift_compare.gif.
  - 사용자 결정: 오프닝 글은 지금 모양 그대로 캔버스로 교체. 로컬라이징(영 · 일 · 간 · 번)은 아직 고민 중 — 바꿀 때는 `SC` 의 글 · 글꼴만 언어별로 (효과 · 때 구조는 그대로).
  - 알아 둘 것: 물마루는 12px 에서 세로획 2칸 · 가로획 1칸인 글꼴이라 크게 키우면 굵어 보인다 (굵게 처리 아님). 나눔명조는 ExtraBold + 0.5px 덧칠로 APNG 굵기에 맞췄다.
- 다음 할 일: 사용자가 게임에서 오프닝을 보고 고칠 점을 준다 · 예전 APNG 아홉 장 지우기(사용자) · 로컬라이징 방식 결정.
- 그 앞(1009): 학생 명부 책 → 게임(apply_roster · 스킬 임의로 강화 · 유물 빈 칸 · 학적 색 · 육각형 차례) · 메뉴 단추 효과음(`SFX.menu`) · 학생 명부 목업 · 배치판.
  그 앞(1008): 상담창 · 상담 대사 성격별 · 행동 지침 무시 · 스킬 등급표 · 원정 3구간 · PNG→WebP · 두루마리 스케줄 · 마스터 노트 책상 · 쿼터뷰 대회 화면.

## 8. 이 문서 고치기

세션을 마칠 때나 사용자가 "인수인계 업데이트" 라고 하면 7번을 새로 쓰고(지난 내용은 줄여서), 새 규칙이 생겼으면 1번에 더한다.
`hs.py pack` 으로 다른 파일과 같이 PC 에 쓴다.
