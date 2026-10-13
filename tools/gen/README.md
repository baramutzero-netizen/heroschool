# tools/gen — game.html 생성 블록과 그림 스크립트

game.html 의 아래 기능은 손으로 쓴 코드가 아니라 이 폴더의 스크립트가 **블록째 넣는다**.
그림(두루마리 · 책상 · 소품)도 여기서 굽는다.

| 기능 | 넣는 스크립트 | 블록 원본 | 그림 |
|---|---|---|---|
| 두루마리 스케줄 (넓은 화면) | `patch/apply_sched.py` | `patch/sched_block.js` · `sched_block.css` | `patch/sched_art.py` → `assets/sched_art/` (WebP) |
| 의뢰 (이번 주 의뢰 · 의뢰처별 등급) | `patch/apply_job.py` (apply_sched 가 같이 부른다) | 스크립트 안 | — |
| 마스터 노트 책상 | `patch/apply_desk.py` | `patch/mdesk_block.js` · `mdesk_block.css` | `patch/desk_art.py` → `patch/desk_out/` → `assets/mdesk_art/` (WebP) |
| 원정 3구간 (원정지 깊이 · 구간 보상 · 잡몹 배율 — 아래) | `patch/apply_exped3.py` | 스크립트 안 | — |
| 행동 지침 무시 (주 시작 판정 · 상담 이벤트 · 결산 창 문구 · 튜토리얼 14 — 아래) | `patch/apply_defy.py` | 스크립트 안 | — |
| 스킬 등급표 (등급 6단계 · 등급 · 레벨로 정하는 수치 · 적도 같은 표 · 원정 잡몹 배율 — 아래) | `patch/apply_skgrade.py` (apply_exped3 뒤) | 스크립트 안 | — |
| 상담 대사를 성격마다 (고민을 털어놓는 말 · 답변에 대한 반응 · 지침 무시 효과 문구 — 아래) | `patch/apply_cslpers.py` | 스크립트 안 (`BLOCK`) | — |
| 상담창 (상담 메뉴를 누르면 뜨는 창 · 일지 › 상담 기록 — 아래) | `patch/apply_cslwin.py` (apply_cslpers 뒤) | `patch/cslwin_block.js` · `cslwin_block.css` | `mockups/counsel-window/art` → `assets/csl_art/` (WebP) |
| 락커룸 창 (경기 직전 한마디 — 출전해 경기 화면에 들어서면 같이 뜨는 창 — 아래) | `patch/apply_lkwin.py` (apply_cslwin 뒤) | `patch/lkwin_block.js` · `lkwin_block.css` | — (쿼터뷰 지도 · 전투 도트 · 상담창 구름을 그대로 쓴다) |
| 스킬 강화 창 배치 (창 안 요소의 자리 · 크기 · 넓은 화면 / 폰 따로 — 아래) | `patch/apply_skup.py` (아무 때나 — 한 줄만 바꾼다) | `patch/skup_layout.json` (배치 실험실 `tools/skill_upgrade_lab.html` 이 저장) | — |
| 학생 명부 책 (가로 넓은 화면 — 책상의 펼친 책 · 메뉴의 학생 명부 · 팀 편성을 누르면 뜨는 책 — 아래) | `patch/apply_roster.py` | `patch/roster_block.js` · `roster_block.css` + 목업 원본 `mockups/student-roster/src/roster_tpl.html` 의 CORE_CSS · CORE_HTML | `mockups/student-roster/art/book.png` · `ribbon.png` → `assets/roster_art/` (WebP) |
| PNG → WebP (게임이 받는 그림 일부 — 아래) | `patch/apply_webp.py` (다른 apply 를 다 돌린 뒤 · wrap 앞) | 스크립트 안 | 원래 PNG 옆에 같은 이름의 `.webp` |
| 전투 치명타 숫자 높이 · 학원 이름 맞추기 · 친선전 전부 거절 재확인 · 고른 칸 강조선 · 3인 리그 · 봄 신인전 시내 대회 필드 · 대회 쿼터뷰 제목 칸 · 줌 · 클로즈업 · 쿼터뷰 지도 11장 · 쿼터뷰 경기 이름(BATTLE START 동안) · 진영 칸 나무판 · 범례 숨김 · 실험실 확대 · 이동을 받는 쿼터뷰 지도 · 이름 길이만큼 늘어나는 진영 칸 · 경기 이름 맞춤(왼쪽 · 가운데 · 오른쪽) · 화면 · 배너를 나무 테두리 가운데로 | `patch/apply_crit.py` · `apply_acadfit.py` · `apply_fdecline.py` · `apply_optsel.py` · `apply_lgfield.py` · `apply_rookiefield.py` · `apply_tq.py` → `apply_tqcam.py` → `apply_tqmaps.py` → `apply_tqui.py` → `apply_tqfield.py` → `apply_tqgrow.py` → `apply_tqalign.py` → `apply_tqcenter.py` | 스크립트 안 | — |

모든 apply 는 몇 번을 돌려도 같은 결과다. 빌드 1007 의 game.html 에 그대로 돌리면 바뀌는 것이 없다 (Claude 작업 공간에서 확인 — game.html · 그림 모두 바이트 단위로 같음).
다만 그 뒤 스타일시트 끝에 다른 CSS 가 붙어서, apply_sched · apply_desk 를 다시 돌리면 두 CSS 블록이 스타일시트 맨 끝으로 옮겨 간다 (자리만 바뀌고 내용은 같다).

단, Claude 가 보낸 PNG · WebP 에는 콘텐츠 출처 정보(C2PA) 블록이 붙어서 온다 — 장당 약 5.8KB 커지고, 그림(픽셀)은 같다.
그래서 이 컴퓨터에서 다시 돌리면 그림은 같아도 `assets/` 의 그림 파일이나 game.html 의 `?v=` 값이 바뀐 것으로 나올 수 있다. 그대로 커밋해도 된다.

## 필요한 것

- Python 3.10+, `pip install pillow numpy`
- 책상 그림을 **배치부터 다시 구울 때만**: `pip install playwright` 후 `playwright install chromium` (배치판 자신의 그리기 코드를 브라우저에서 돌린다)
- 배치판 HTML 을 다시 만들 때만 (`kit/build_editor*.py`): `pip install fonttools brotli`

## 쓰는 법 (저장소 맨 위에서)

```
python tools/gen/patch/apply_sched.py game.html tools/gen/patch/sched_layout.json
python tools/gen/patch/apply_desk.py  game.html                                   # desk_out 그림 그대로
python tools/gen/patch/apply_desk.py  game.html tools/gen/patch/desk_layout.json  # 책상 배치를 바꿨을 때 — 다시 굽는다
python tools/gen/patch/apply_exped3.py game.html                                   # 원정 3구간 (바뀐 게 없으면 그대로)
python tools/gen/patch/apply_skgrade.py game.html                                  # 스킬 등급표 (apply_exped3 뒤 — 잡몹 배율을 다시 쓴다)
python tools/gen/patch/apply_cslpers.py game.html                                  # 상담 대사 (성격마다 — 대사를 고쳤으면 다시)
python tools/gen/patch/apply_cslwin.py game.html                                   # 상담창 (상담 책상 배치 · 창 블록을 고쳤으면 다시)
python tools/gen/patch/apply_lkwin.py  game.html                                   # 락커룸 창 (apply_cslwin 뒤 — 창 블록을 고쳤으면 다시)
python tools/gen/patch/apply_roster.py game.html                                   # 학생 명부 책 (목업 원본 · 책 그림 · 배치 · 책 블록을 고쳤으면 다시)
python tools/gen/patch/apply_skup.py  game.html                                   # 스킬 강화 창 배치 (skup_layout.json 을 바꿨으면 — SK_CHOICE_LAYOUT 한 줄만)
python tools/gen/patch/apply_webp.py  game.html                                   # PNG → WebP (바뀐 게 없으면 그대로)
python tools/gen/patch/apply_optx.py  game.html                                   # 오프닝 글 (장면 · 글 · 효과를 고쳤으면 다시 — 글을 바꿨으면 optx_fonts.py 먼저)
python wrap.py
python wrap_site.py
```

- apply 는 그림을 `data:` 로 넣는다 (1008 — 무손실 WebP). `wrap.py` · `wrap_site.py` 의 split_assets 가 `assets/sched_art/` · `assets/mdesk_art/` · `assets/roster_art/` 등으로 빼고 game.html 에는 경로만 남긴다.
- `apply_desk.py` 는 줌 넘어가기를 맞추려고 `assets/sched_art/` 그림(`.webp` 가 있으면 그것)에서 스케줄 두루마리 축 자리를 잰다. 스케줄 그림을 바꿨다면 `wrap.py` 를 한 번 돌린 뒤 apply_desk.

### 두루마리 스케줄 — 사이드가 잉크 단지 · 깃펜을 가릴 때 (`sched_block.js` 의 `skSideFit` · 1010)

- 가로 화면 사이드(`#app>.topbar`)는 화면에 고정이고 무대 오른쪽 위에 얹힌다. 소품(잉크 단지 · 깃펜)은 그 아래 책상 자리라, 화면이 낮으면(14인치 맥북 등 — 창 높이 860 아래)
  무대를 끝까지 내렸을 때, 창이 좁으면(1272 아래 — 무대가 작다) 처음부터 사이드가 소품을 덮어 잉크를 찍을 수 없었다.
- 페이지를 끝까지 내렸을 때의 소품 위쪽을 재서, 사이드가 거기까지 내려오면 차례로 ① 'MENU' 글자(`html.sk-side1`) ② 스케줄 단추(`html.sk-side2` — 지금 보는 화면) 를 숨기고
  ③ 그래도 길면 사이드 높이를 줄인다(안에서 스크롤). 스크롤하는 동안에는 바뀌지 않는다. 스케줄을 그릴 때 · 창 크기 · 글꼴이 바뀔 때 다시 재고, 다른 화면으로 가면 되돌린다(`skLeave`).
- 사이드 규칙처럼 무대 밖을 꾸미는 CSS 는 `sched_block.css` 에 `html` 로 시작하는 선택자로 쓴다 — apply_sched 의 `prefix_css` 가 무대 접두어를 붙이지 않는다.

### 두루마리 스케줄 — 결재 · 위 단추 · 개인 행동 줄 · 명부 (`sched_block.js` · 1011)

- **결재**: 저장된 서명(`PREF.sign`)이 있으면 다섯 칸이 찼을 때 결재란도 깃펜과 같이 반짝이고(`.sk-appr.glint` — `skFxUpd`), 결재란을 누르면 깃펜이 스스로 잉크를 찍어
  그 서명을 쓴 뒤 진행한다(`skAutoSign` — 예전엔 Enter 만). 안내 글도 '깃펜을 잉크에 찍어 서명' → '클릭으로 서명'. 서명이 없으면 예전처럼 안내만.
- 결재란 안: 비용 줄(일과 · 식단)을 맨 위 '결재' 옆으로 올리고 진행 글자를 24 → 20 으로 줄여, 서명 칸을 107×20 → 107×33 으로 키웠다(위로 · 서명 줄은 그대로).
  예전 서명(높이 20)은 늘리지 않고 서명 줄에 붙여 쓴다(`skSigFit`). 새 서명은 107×33 으로 남는다.
- 위 단추 셋(자동 배치 · 식단 · 전부 비우기)은 큰 단추 `skB(…, "lg")` — 글자 18 · 높이 36 · 아이콘 3배(`skSpr` 의 k).
- **글자 크기는 `calc()` 로** — 물마루 글꼴 모드(`pixelFontApply`)가 스타일시트의 `px` 글자를 12 · 24 · 36 으로 바꿔 끼운다. 18 · 20 처럼 사이 크기는 `calc(18px)` 로 써야 그대로 간다 (카드 이름 `.sk-cn` 과 같은 수).
- 개인 행동 줄: 오른쪽 끝에 교회 단추(예지의 서 · 구매 · 신비한 성수 — `skChurch`, 예전엔 일과 머리 줄 · 명부 머리 줄). 줄이 넘치면 `skActFit` 이 단추 이름을 숨긴다(아이콘 · 권수 · 값만 — 영어는 거의 늘).
  변경 취소 · 지난주 변경 취소는 명부 맨 끝 빈칸 오른쪽으로 옮겼다(`skRoster` 의 `slot` — 지난주 기록이 있으면 늘 한 칸 비워 둔다).
- 명부: 한 단 · 두 단 중 더 크게 들어가는 쪽으로, 크기는 2배까지 1/8 단위(`skRosterFit`). 두 단은 왼쪽부터 채운다(15명 = 8 + 7 · 1.5배 — 예전 1배).
  두 단을 키우면 줄 폭이 좁아지는 만큼 컨디션 막대를 줄인다(`skRowGeo` · 최소 60). 결재란 맨 위 줄이 넘치면 '결재'를 뺀다(영어에서 값이 클 때).
- 명부의 행동 칸은 그림(`chip_*`) 대신 **CSS 로 같은 모양**을 그린다(1칸 테두리 · 바탕 · 윗줄 밝게 — 색은 `.sk-chip.k-*`). 폭은 CSS 변수 `--sk-chipw`(기본 30 · 영어 38),
  부상 표시(✚ N주) 자리는 `--sk-injw`(기본 36 · 영어 40) — 영어 값은 `tools/i18n/en_layout.css`. `skRoster` 가 `skCssPx` 로 읽어 막대 자리를 정한다.
  칸 글은 짧은 이름 `SK_CHIP_N`(영어 문맥 키로 Train · Rest · **Work** — 다른 곳의 의뢰는 Errand 그대로). 시트의 `chip_*` 그림은 남아 있지만 쓰지 않는다.
- 카드 효과 줄 · 의뢰 쪽지의 멘탈리티는 `mentShortOf` · `mentShort`(game.html — `MENT_SHORT` 표 · 영어 문맥 키로 Comp. · Gen. · Team. · Will. · End. · Drive · 한국어는 이름 그대로).
  예전 스케줄 화면의 카드(`fxHtml`)도 같다. 원정 카드의 '진로 평가 +' 줄은 뺐다(`TRAININGS` 의 fx — 보이는 글만 · 효과는 그대로).

### 마을 · 마스터 노트 · 스케줄 — 같은 액자 (1011)

- 가로 화면의 세 화면은 **같은 상자 · 같은 나무 테두리**다: 1544:1008(스케줄 무대 2배) · 안쪽 칸 1492×956(테두리 26 — 1배 13). 창 폭 1240 이상이면 셋 다 1208×789.
  화면을 바꾸거나 두루마리로 넘어가도 테두리 크기가 그대로다.
- 액자 그림: 스케줄 · 마스터 노트는 `SCHED_ART.over2`(액자 + 그늘), 마을은 `SCHED_ART.frame`(액자만 — `sched_art.py` 가 같이 굽는다 → `assets/sched_art/frame.webp`).
  game.html 의 `TOWN_FRAME` 이 그것을 쓰고, 예전 `assets/town/frame.webp` 는 SCHED_ART 가 없을 때만.
- **마을**: 지도(1214×931)를 안쪽 칸 폭에 맞추고 아래를 자른다(지도 높이의 약 16% — 사람 자리는 모두 보인다). 지도 상자(`.townmap-in`)만 지도 비율로 늘리고
  `clip-path` 로 안쪽 칸에서 자르므로 그림 · NPC 자리(%)는 그대로 (game.html CSS `.town:not(.mdesk) .townmap-in`).
- **마스터 노트**: 책상 1배 = 스케줄 1배(화면 k = 폭 / 772). 책상 바탕을 746×478 로 넓힌 `MDESK_ART.ext` — `apply_desk.py` 의 `desk_ext` 가 `desk_out/base.png` 의 오른쪽 · 위 · 아래를
  거울로 이어 붙인다(오른쪽은 사이드 밑 판자). 예전 책상 607×466 자리는 `.mdesk-art`(소품 · 누르는 자리 · 표식 — 자리는 `MDESK_GEO.ext` 의 x · y). 배치판 · `desk_out` 은 그대로 607×466.
- 두루마리 → 스케줄(`mdeskGo`): 액자는 두고 안쪽 책상(`.mdesk-desk`)만 커져 두루마리 축이 스케줄 두루마리 축에 온다(예전처럼 액자를 나눠 줄이지 않는다).
- 팝업(시설 · 학원 정보 · 마스터 육성)은 액자 안에 띄운다(예전 바깥 여백 자리). 길면 팝업 안에서 스크롤하고 나가기 · 닫기 줄은 아래에 붙어 늘 보인다(`.townpop-foot` sticky).
- 사이드 스케줄 단추 글은 한국어도 **'Schedule'**(aria-label 은 '스케줄') · 운영 안내의 단추 그림(`tutSchedBtn`)도 같다. 폰 메뉴의 큰 단추는 '스케줄' 그대로.

### 원정 3구간 (`apply_exped3.py` · 1008)

- 원정지는 모두 3구간이다. `DUNGEONS` 의 `depth` 는 예전 구간 수(연습장 3 · 성터 4 · 종탑 5 · 균열 6 · 무덤 7) — 구간마다 마물 레벨이 그만큼 가파르게 오르고(마지막 구간 = 예전 보스 레벨),
  지구력 한계 · 의식 리타이어도 이 깊이를 따른다 (예전에 몇 구간까지 버티던 팀은 그에 해당하는 구간까지).
- 구간당 경험 · 자금 · 유물 확률 · 진로 평가 · 학생 명성 · 업보 · 컨디션 소모는 **완주 합계가 예전과 같도록** 커졌다 (`dgK` = 깊이 ÷ 3, 경험은 `dgExpK`).
- 잡몹 배율(`MOB_K`)은 `sim/exped_sim.py` 로 바꾸기 전 · 뒤 빌드를 같은 설정으로 돌려 완주율이 같아지도록 다시 맞췄다 — 다시 맞출 때는 그 파일 머리말을 본다 (`pip install playwright` 필요).
  균열만은 예전부터 잡몹이 유난히 세서 무덤보다 어려웠던 것을 바로잡아 종탑과 무덤 사이로 낮췄다 (1.7 — 예전 완주율에 맞추면 2.0).

### 행동 지침 무시 (`apply_defy.py` · 1008)

- 1년차 봄 8주차부터 매주 스케줄을 시작할 때 학생마다 확률을 굴려, 걸린 학생 중 한 명(한 주에 한 명까지)이 그 주 개인 행동 지침 대신 다른 행동을 한다.
  상담 탭의 이벤트를 하지 않고 다음 주를 시작하면 그 학생이 무조건 또 무시한다.
- 수치는 game.html 의 `DEFY_*` 상수 — 등급 `DEFY_GRADE` · 신뢰 `DEFY_TRUST` · 학원 명성 `DEFY_FAME` · 성격 `DEFY_PERS` · 바꾼 행동의 소모/회복 `DEFY_COST` · `DEFY_REC` ·
  상담 뒤 면제 `DEFY_FIT_SEASONS` · `DEFY_MISS_SEASONS` · 맞는 말 컨디션 `DEFY_FIT_COND` · 시작 주차 `DEFY_START_WEEK`.
- 대사 — 마스터 질문 `DEFY_ASK` · 학생 대답 `DEFY_LINES`(성격 × 안 한 것>한 것 · `{who}` 의뢰인 · `{job}` 의뢰 이름, `+이` · `+을` 을 붙이면 조사까지) ·
  마스터의 말 `DEFY_REPLY`(0 공감 · 1 원칙 · 2 도전 — 어느 성격에 닿는지는 `DEFY_FIT`) · 학생 반응 `DEFY_REACT`(맞는 말 · 안 맞는 말).
- 세이브 `S.defy` — `pend` 상담 대기 · `imm` 학생별 면제가 끝나는 계절 · `log` 상담 기록 · `cur` 이번 주 · `first` 첫 안내를 띄웠는가.

### 스킬 등급표 (`apply_skgrade.py` · 1008)

- 스킬 수치는 **등급 · 레벨로만** 정한다 — 같은 등급 · 레벨이면 학생 · 졸업생 · 리그 · 적 · 마왕 모두 같은 수치.
  표는 game.html 의 `SK_POW_LV`(레벨당 효과량 D 12 · C 16 · B 20 · A 25 · S 30 · EX 40%) · `SK_PROC_LV`(레벨당 출현 확률 7 · 10 · 13 · 16 · 19 · 25%, 스킬 1 · 2 만) ·
  `SK_DUR_LV`(지속 시간 `[등급][레벨−1]` — B Lv.5 +1 · A Lv.3 +1 · S Lv.3 +1 / Lv.5 +2 · EX Lv.3 +2 / Lv.5 +3, 지속형 스킬만 · `noDur` 제외). Lv.n 은 표의 값 × (n−1).
- 등급 6단계 `SK_GRADE` D · C · B · A · S · EX (S 를 새로 넣었다). 강화 한 번 = 레벨 +1, 진화 강화 등급 +1 · 각성 강화 등급 +2 (`evoChance` 는 그대로) —
  등급이 오르면 지난 레벨 몫도 새 등급으로 다시 계산된다. 3지선다는 어느 스킬 · 어떤 강화만 고르고(효과량 · 출현 · 지속 중 하나를 고르던 것은 없앴다),
  EX 위로는 등급이 없어서 제안을 만들 때 실제로 오르는 칸으로 깎는다 (`evCap`). 임의 강화 · 시뮬레이션은 `skAutoSpend`.
- 저장 `skMod[id]` 는 `{grade, up}` 만 읽는다 (예전 `pow · proc · dur` 가 남아 있어도 쓰지 않는다). 옛 저장(`S.skgV` < 2)은 boot 에서 EX(4) → EX(5) 로 한 번 옮긴다 (`skgMigrate`).
  리그 팀 · 마왕전 기록은 `v` 가 2 보다 작으면 받을 때 옮긴다 (`skModSane` — 서버는 고치지 않는다). 보낼 때는 등급 · 강화 횟수만 (`skModPack`, `v` 2) — 받는 쪽도 등급 · 강화 횟수만 믿는다.
- 적 — `autoSkMod` 는 강화 횟수 · 등급만 정한다 (난수 쓰는 순서는 예전과 같다). 마왕 `DEMON_SK` 는 Lv.5 EX (효과량 +160% · 출현 +100% · 지속 +3턴 — 예전 +144% 만) · 이계 결승 1군 기록도 6단계로.
- 전투 수치가 바뀌어 `RULES_VER` 7. 보관고 처분 가격에 S(1250 G)를 넣었고, 졸업 선물은 강화 횟수가 같으면 등급이 높은 것.
- 원정 잡몹 배율 — 마물 스킬도 등급표를 따라 세진 만큼 낮췄다 (스크립트의 `MOB_K_SKG`: 성터 1.02 · 종탑 .94 · 균열 1.67 · 무덤 1.01).
  학생 스킬을 임의 강화 방식으로 키운 B급 3인(`sim/exped_sim.py` 의 `"sk":"auto"`)이 권장 +0 · +2 · +4 에서 마물 스킬을 바꾸기 전과 같은 완주율이 나오도록.
  apply_exped3 를 다시 돌리면 배율이 그 스크립트 값으로 돌아가므로 apply_skgrade 를 뒤에 한 번 더 돌린다.

### 상담 대사를 성격마다 (`apply_cslpers.py` · 1008)

- 고민 상담 `COUNSEL` — 학생이 고민을 털어놓는 말 `q` 를 성격 9가지마다 따로 (고민 12 × 9). 내용은 같고 말투만 그 성격으로
  (열혈은 분해서 소리치듯 · 차분은 따지듯 · 소심은 말끝을 흐리며 · 새침은 아닌 척 · 허세는 영웅 타령 …).
- 답변에 대한 반응 — 맞는 말: 선택지마다 성격별 대답 `o[].a` + 그 뒤 일을 적은 서술 `o[].r` /
  맞지 않는 말: 성격마다 `CSL_REACT` 의 `lead`(지도력으로 설득) · `trust`(신뢰 운명) · `miss` 와 서술 `missR`(납득 못함).
  고르는 것은 `cslQ` · `cslAnswer` (1년차 암흑 사제는 `masterQ` 로 ‘마스터’). 상담 기록에 마스터의 말 · 학생의 대답 · 서술이 남는다
  (`C.done` 의 `reply` · `react` — 예전 기록은 예전처럼).
- 대사 블록은 `const COUNSEL = [` 부터 `/* ── 상담 대사 끝 (apply_cslpers) ── */` 까지 통째로 바꾼다 — 대사를 고칠 때는 스크립트의 `BLOCK` 을 고쳐 다시 돌린다.
- 행동 지침 무시 상담의 효과 문구에서 기간을 뺐다 — 맞는 말 ‘앞으로 한동안 지침을 잘 따를 것 같다’ · 맞지 않는 말 ‘일단은 지침을 따를 것 같다’
  (일지 · 상담 기록 · 튜토리얼 14). 실제 기간은 그대로 `DEFY_FIT_SEASONS` 4 · `DEFY_MISS_SEASONS` 2 계절.
- 상담창 목업(`mockups/counsel-window`)은 이 표를 game.html 에서 그대로 옮겨 쓴다 — 대사를 고친 뒤 목업의 `build_mockup.py` 를 다시 돌린다.

### 상담창 (`apply_cslwin.py` · 1008)

- 메뉴의 **상담**(가로 화면 사이드 · 폰 메뉴)을 누르면 화면을 바꾸지 않고 상담창이 뜬다 — 목업(`mockups/counsel-window/counsel_mockup.html`) 그대로.
  학생이 책상 뒤로 들어온다 → 학생을 누르면 고민을 털어놓는다(지침 무시는 마스터가 먼저 묻는다) → 답변 구름 셋 중 하나 → 학생의 대답 · 효과 → 넘어가기 / 마치기.
  지침을 무시한 학생(`S.defy.pend`)이 먼저, 그다음 고민 상담 대기열(`counselState().queue`) 차례로. 찾아온 학생이 없으면 빈 상담실
  (1011 — 지도력 · 정보력 · 호소력 확률 줄은 상담실(창 · 상담 화면)에서 숨겼다 · 일지 › 상담 기록에는 남는다 — 사용자).
- **블록 파일 = 게임 그대로 (1011)** — 쿠키 기능(쿠키 접시 · `cslCookie…`)이 game.html 블록에 직접 들어가 `cslwin_block.js` 가 옛것이 되어 있었다 → 블록 파일을 game.html 블록으로 되돌려 맞췄다
  (`CSL_ART` · `CSL_SPR` 줄만 자리표). apply 는 블록이 있으면 **그 자리에서** 갈아 끼운다(예전엔 지우고 기준 줄에 다시 넣어 뒤에 붙은 쿠키 CSS 와 차례가 바뀌었다) ·
  EDITS 는 지금 코드(쿠키 `cookie` · 잠긴 메뉴 `navLockToast`)에 맞췄다. 블록을 고칠 때는 블록 파일에서 → apply (game.html 안을 직접 고치지 않는다).
- 답을 고르는 순간 게임에 반영한다 — `answerCounsel(qi, oi, true)` · `answerDefy(pi, oi, true)` 는 화면을 다시 그리지 않고 결과(대답 · 서술 · 효과 · 신뢰 변화 · 바뀐 신뢰 단계)를 돌려준다.
  연출 중에 창을 닫아도 결과는 남고, 고르기 전에 닫으면 그 상담은 그대로 남는다. 일지 문구 · 저장은 예전과 같다.
- 학생이 들어오는 모습은 성격마다 (`CSL_ENTER` · 지침 무시는 `CSL_DEFY_ENTER`). 대사는 apply_cslpers 의 표 그대로.
- 학생 그림 — 전투 idle 도트 네 장(학생마다 머리색 치환 · `sprCellCv`)을 128 칸으로 잘라 전투처럼 `#111` 테두리를 둘러 쓴다 (`cslwSprUrl` — 그림 파일은 따로 없다). 도트가 없는 직업은 얼굴 그림.
  크기 · 자리는 직업마다 — 상담 책상 배치판의 **학생 도트**(배치 JSON 의 `sprites`)를 apply_cslwin 이 `CSL_SPR` 로 넣는다 (없는 직업은 2배의 0.95배 · 0, 0).
  발끝(무대 2배 280, 288)을 축으로 `scale` 하고 (2x, 2y) 옮긴다 — 누르는 자리(`.cw-hit`)도 같은 셈으로 따라간다 (`cslwSetLook`).
  머리 위 말줄임 · 효과 숫자는 도트의 실제 머리 꼭대기(말줄임 밑 열들에서 가장 높은 칸 — `cslwSprUrl` 의 `top`)를 재서 그 위에 둔다 — 배치판의 말줄임 자리도 같은 셈.
  도트를 자르는 틀(`.cw-stu`)은 무대 윗부분 전체(책상 윗변 y 232 까지)라 옆으로 옮겨도 잘리지 않는다. 학생 말 상자 머리는 이름 · 성격만 (직업은 그림으로 보여서 뺐다).
- 게임의 도트 마감 테마(`html[data-ui-finish="pixel"]`)와 팔레트가 모든 button 에 붙이는 네모 테두리 · 입체 그림자(`!important`)는 이 창에서 걷는다 —
  답변 구름은 구름 그림만, 닫기 · 넘어가기는 창의 모양 그대로 (`cslwin_block.css` 의 더 센 선택자).
- 그림 `CSL_ART` — `bg` 배경(목업의 `art/bg.webp`) · `front` 책상 + 소품(1배 280 × 180 · 무손실 WebP — `art/desk.png` 위에 `art/desk_layout.json` 배치를 `src/compose_desk.py` 로 구운 것).
  상담 책상 배치(소품 · 직업별 학생 도트)를 바꿨으면 배치판(`mockups/counsel-window/counsel_desk_placer.html`)에서 저장한 `desk_layout.json` 을 `mockups/counsel-window/art/` 에 덮어쓰고 apply_cslwin → wrap.
- 좁은 화면(창을 0.8배보다 줄여야 할 때 — 세로 폰 · 가로 폰) — 무대만 폭에 맞춰 줄이고 학생 말 · 답변 구름은 무대 아래로 (글자 크기는 그대로). 그보다 넓으면 창을 통째로 줄인다.
- 키: 스페이스 · 엔터 넘기기(글자가 찍히는 중이면 바로 끝까지) · 1 · 2 · 3 구름 고르기 · Esc 닫기.
- 효과음 — `SFX` 표 끝의 `csl_tap`(학생을 누를 때) · `csl_pick`(답변 구름을 고를 때) · `csl_ok` · `csl_ng`(반응 성공 · 실패 — 학생의 대답이 다 찍히고 효과 숫자가 뜰 때) ·
  `csl_stu` · `csl_mst`(학생 · 마스터의 말이 한 글자씩 찍힐 때마다 — 빈칸 · 말줄임표 `……` 에서는 울리지 않는다).
  파일은 `bgm/counsel_tap · counsel_pick · counsel_ok · counsel_ng · counsel_type_student · counsel_type_master` `.ogg` (앞뒤 무음을 잘랐다 · 원본 `.mp3` 도 같은 이름으로 `bgm/` 에).
  글자 소리는 `cwBlip` — 한 목소리로 앞 글자의 소리를 짧게 끊고 새로 울린다 (sfxPlay 의 55ms 막기를 쓰지 않는다). 학생 · 마스터의 말은 같은 빠르기 `CSLW_CPS`(초당 32자).
- **상담 기록은 일지의 서브탭 '상담 기록'**(`csllog` · `viewCslLog`) — 예전 상담 탭 아래쪽의 올해 상담 기록 그대로 + 상담 확률 + 상담실 열기.
  예전 상담 화면(`UI.view` "counsel")은 안내 + 상담실 열기 단추만 남겼다 (메뉴로는 들어가지 않는다).

### 락커룸 창 (`apply_lkwin.py` · 1013)

- 경기 직전 감독의 한마디를 상담창 같은 창으로 — 목업(`mockups/locker-room/locker_room_mockup.html`) 그대로. 경기 화면 셋(가을 대회 `renderLadder` · 친선전 `renderFriendly` · 봄 신인전 `renderTournament`) 위에 겹쳐 뜬다.
  - **경기 화면에 들어서면 같이 뜬다**(`lkwAuto(t)` → 다음 `bindLocker` 가 한 번 쓰고 지운다) — 출전 · 친선전 시작 · 엔트리 확정 · 대진 확정을 눌러 경기 화면이 그려질 때,
    그리고 창이나 '경기 시작'으로 연 전투를 보고 '결과 확정'으로 다음 경기 화면에 왔을 때 — 그 경기에서 한마디 전이면 창이 같이 뜬다
    (1013 사용자: '경기 화면에 들어가 락커룸에서 한마디 단추를 누르지 말고, 출전을 누르고 한마디를 안 했으면 락커룸이 같이 팝업').
    다시 그리기(창을 닫은 뒤 · 리그에서 출전 팀 바꾸기)와 '빠르게 결과만' · '남은 경기 한 번에' 뒤의 경기 화면에는 뜨지 않는다.
  - **'경기 시작'**(`lkwGate`) — 이 경기에서 한마디를 아직 안 했으면 창부터, 했으면 바로 전투. 경기 화면의 락커룸 칸은 학생 기분 카드 그대로 — 창을 여는 단추는 없다 (예전 '락커룸에서 한마디' 단추 · 안내는 뺐다)
  - 창: 출전 학생 3 ~ 5명이 하나씩 들어와 둥글게 선다 → 구름 넷(기대치 충족 요구 1 · 부담감 완화 1 · 동기부여 2 — `makeSpeechOffers`)이 차례로 떠서 제자리에서 원을 그린다(창이 두근거린다)
    → 고르면 마스터의 말 · 학생들이 가운데로 살짝 다가서고 머리 위에 `…` → 한 명씩(차례는 섞어서 · 연출이라 `Math.random`): 납득 **~♪**(폴짝 · 가끔 ♫ 가 떠오른다) · 못 납득 **| | |**(어깨가 처지고 어둡고 흐려진다)
    · 이름표의 기분 ±20(숫자가 위로) → 글 상자: 말 종류 — 설명 · 통함(호소력 · 운명 표시) + 신뢰 · 빗나감 · 이번 경기 기분 보정 → **'경기 시작 ▶'** 로 전투
  - **'말없이 시작 ▶'**(고르는 동안) — 한마디 없이 전투 · **×(Esc)** — 경기 화면으로 (한마디를 했으면 경기 화면을 다시 그려 결과를 보인다). '빠르게 결과만' · '남은 경기 한 번에'는 창 없이
  - 고르는 순간 게임에 반영한다 — `lockerSpeak` 그대로(기분 · 신뢰 · 일지) + `save()`. 연출 중에 창을 닫아도 결과는 남는다. 전투는 `lockerApply` 가 같은 `t.locker` 를 돌려줘 그 기분으로 싸운다.
- 화면 — 창 796 · 무대 768 × 432(1배 384 × 216 의 2배) · 위 탭(왼쪽 '락커룸 · 대회 · 라운드' · 오른쪽 전력 — 모르면 ??? 파악 못 함) · 아래 글 상자. 상담창 CSS(`.cw-*`)를 그대로 쓰고 크기만 바꾼다(`lkwin_block.css` 는 CSLWIN CSS 바로 뒤).
  - 배경 — 그 경기의 대회 쿼터뷰 지도(`TQ_MAPS` · `tqMapKey` — 시내 city · 광역 / 예선 regional · 본선 final · 친선전 = 연습장 = 그 계절 학원)를 흐리게(blur 4px · 채도 0.92 · 밝기 0.86 + 가장자리 어둡게).
    확대 1.4(지도 폭 = 무대 폭이 1) · 바닥 문장(mx, my)을 무대 y 250 에 — 허들 바로 뒤. 쿼터뷰 지도가 없는 필드면 필드 그림(`fieldOf`). 다 받으면 나타난다(전투도 같은 그림을 쓰니 미리 받는 셈)
  - 학생 — 상담창과 같은 전투 idle 도트(`cslwSprUrl`)를 **1.5배**. 둥글게 선 원의 먼 쪽 반원(`LKW_SLOTS` — 3 · 4 · 5명 · 1.5배 기준 · 양 끝이 앞(아래) · 가운데가 뒤(위)) — 오른쪽 학생은 좌우를 뒤집어 가운데를 본다.
    머리 · 발 자리는 도트에서 잰다(`lkwMeasure` — 머리 덩어리 가운데 · 그 둘레 맨 위 · 발끝 · 발 가운데). 말줄임 · 음표 · 세로줄이 따라간다. 발밑 그림자 + 무리 전체 그림자
  - 이름표 — 발 아래 한 줄(이름 · 성격 / 기분 이름 · 수치 / 막대 — 30 · 70 눈금). 겹치면 벌린다. 영어는 이름 · 성격을 두 줄로(`tools/i18n/en_layout.css`) — 이름표 높이를 재서 허들이 그만큼 위로
  - 구름 — 양옆 위아래 둘씩(너비 188 · 글 길이에 맞춰 높이 · 아래 구름은 같은 쪽 위 구름 바로 밑). 구름 그림은 `cslwCloudArt`. 효과 그림(♪ · ♫ · ~ · | | |)은 캔버스로 1배를 찍어 2배로(`lkwArt`)
  - 좁은 화면(창을 0.8배보다 줄여야 할 때) — 무대만 폭에 맞춰 줄이고 구름 · 이름표(격자)는 무대 아래로 · 위 탭은 '락커룸'과 전력만 (상담창 `.compact` 와 같은 방식)
- 키: 1 ~ 4 구름 · 스페이스 · 엔터(글자가 찍히는 중이면 끝까지 · 결과에서는 경기 시작) · Esc 닫기. 위에 튜토리얼 · 확인 창이 떠 있으면 그쪽이 먼저.
- 소리 — 상담창 것: 구름 `csl_pick` · 마스터의 말 `csl_mst`(글자마다 `cwBlip`) · 반응 `csl_ok` / `csl_ng`.
- 튜토리얼 8(전투 전, 학생들에게 한마디)은 창을 처음 열 때 창 위에 (예전: 경기 화면에 처음 들어설 때).
- 점검 · 시험용 `lkwOpen({instant:true, pick:k})` — 기다림 · 글자 찍기 없이 그 단계까지 (pick 을 주면 그 말을 골라 결과까지 · 튜토리얼도 건너뛴다). `tools/i18n/check_layout.py` 의 `tour_match` · `tour_lkwin` · `tour_lkwres`.
- 예전 락커룸 칸의 한마디 넷(2 × 2 단추 · `data-say`)은 없어졌다. `lockerHtml` · `bindLocker` 는 블록 안으로 옮겼다(apply 가 블록 밖의 예전 것을 지운다) — `bindLocker(t, L, my, rerender, {title, label, foe, field, start})`.

### 스킬 강화 창 배치 (`apply_skup.py` · 1013)

- 스킬 강화 창(`skillUpModal` — 1013 재작업 · CSS `SKILL_CHOICE_STYLE` · 그림 `assets/skill-upgrade/`) 안 요소의 자리 · 크기를 표 하나로 정한다 — game.html 의 `SKUP_LAYOUT` 블록
  (`SK_CHOICE_MARKS` 아래): `const SK_CHOICE_LAYOUT = /*SKUP_LAYOUT*/{…};` 한 줄 + 놓는 코드(`skChoiceLayoutApply` — 인라인 style 로 CSS 를 덮는다).
  apply_skup 은 **그 한 줄만** 바꾼다 (요소 이름 · 값 모양을 확인하고 모르는 이름이면 멈춘다 · 몇 번 돌려도 같음). 블록 파일은 없다 — 놓는 코드는 game.html 에서 직접 고친다.
- 요소마다 `{ax, ay, x, y, w, h}` — 창 테두리 안 px. `ax` l 왼쪽에서 · c 가운데에서(요소 가운데가 창 가운데에서 x) · r 오른쪽에서, `ay` t 위에서 · b 아래에서. w · h 가 null 이면 글 크기대로.
  `mw` — 폰에서 w 가 화면에 안 들어가면 양옆에 남길 여백. `tail` — 선택지 말풍선 꼬리(l · c · r). 제목 띠 · 이름 띠(`heading` · `footer`)는 높이만.
  `scene` — 창 크기(w · h)와 화면 가운데에서 옮긴 x · y. 폰(`mobile` — 화면 폭 760 이하, CSS 의 폰 배치와 같은 기준)은 창 높이만 + 완료 화면 높이(`sceneEnd`).
  넓은 화면 `scene.fitH`(기본 900) — 게임이 보는 세로가 이 값 이하면 창 전체를 세로 ÷ fitH 배로 줄인다 (`.suc-scene` 에 CSS zoom · 0.5 까지 · 0 이면 안 줄임 ·
  창 크기가 바뀌면 다시 — `skChoiceZoom`). zoom 이라 창 안의 값 · offset · client 는 그대로 창 기준 px (실험실은 끈 거리를 배율로 나눠 쓴다).
  요소: scene · heading · points(강화 포인트) · slot1~3(선택지) · hero(학생) · swing(부채 — 맞는 자리 · + r 각도) · swingFrom(부채 — 시작 자리 {x, y, r}) · reroll(이국의 부채 단추) · footer · later(나중에) · rules(강화 규칙) ·
  완료 화면 sLabel · sTitle · sHero · sInfo(결과 칸) · sDone(확인) + 두 화면 같이 쓰는 `marks`(아래). 처음 값(지금 `skup_layout.json`)은 재작업한 CSS 그대로다.
- 맞추는 도구 — **스킬 강화 창 배치 실험실** `tools/skill_upgrade_lab.html` (브라우저로 연다): 실제 게임을 `game.html?skuplab` 으로 띄워(세이브는 쓰지 않는다)
  요소를 끌어 옮기고 노란 손잡이로 크기를 바꾼다. 빈 곳을 끌면 창 위치 · 방향키 1px(Shift 10px) · 가운데 기준 요소는 가운데 근처에서 붙는다(Alt 면 안 붙음).
  왼쪽 칸에서 화면(넓은 화면 · 폰 · 크기) · 장면(고르기 · 부채 들기 · 부채 맞음 · 완료) · 학생 직업 · 기준 · 숫자 · 비율 고정 · 말풍선 꼬리 · 기본값.
  '차이점 확인'이 게임 기본값과 다른 곳을 글로 · 'JSON 저장'이 `skup_layout.json` 을 내려받는다 → `tools/gen/patch/` 에 덮어쓰고 apply_skup → wrap.
- 실험실 코드(`SKUP_LAB` 블록)는 배포 빌드에서 빠진다 (`build_strip.py`). 주고받기는 postMessage `lab:"skup"`.
- 배경 벨트 `bg` (두 화면 같이) — 방 그림 대신 'SKILL UPGRADE' 가 쓰인 두 색 띠가 번갈아 서서 첫 색 띠는 위로 · 둘째 색 띠는 아래로 흐른다 (`skChoiceBg` ·
  기울인 판 `.suc-bg-rot` 의 띠마다 글 줄이 한 바퀴(글 + 간격)씩 transform 으로 · 시작 시각을 시계에 맞춰 창을 다시 그려도 이어진다 · 움직임 줄이기면 멈춤).
  `{on, a · b 띠 색, ink 글자 색, inkA 진하기, w 폭, tilt 기울기, speed 초당 px, gap 글 사이, size 12·24·36·48}` — 실험실 '배경' 칸. 켜면 창에 `suc-belt` —
  밝은 띠 위 글(완료 머리글 · 제목 · 이국의 부채 글)에 테두리, 완료 화면을 어둡게 덮던 막은 뺀다. 제목 띠 · 이름 띠는 불투명(#5c94b0 — 재작업 CSS 에서 고침).
- 전구(고르기) — thinking.png 에 그려져 있다(16 직업 모두 82, 20 · 28×27 — 몸은 y 48 아래). 그 칸을 `.suc-think`(SVG evenodd 구멍 마스크)로 가리고 같은 그림을 잘라 `.suc-bulb` 로
  따로 놓는다 — `marks.thinking`(s 너비 · d · at — 아래 표시와 같은 방식). 표시 셋(전구 · 긴장 · 충격)은 `outline {c 색, w 그림 칸 0~3}` 테두리 — drop-shadow 네 방향(창의 `--suc-ol`).
- 완료 화면 배경 `bg.end` — solid(기본 · 고른 스킬 등급 색(결과 칸 `--grade-bg`)을 채도 `bg.endSat`% 로 · 띠 없음) · grade(그 색 띠) · same(고르기와 같게) — `skChoiceTone`.
- 이국의 부채 — 이름 · 개수는 '이국의 부채 (2개)'(0개면 '도구상에서 구입 · 1,000 G' 한 줄 더 — 1014)를 마우스 오버 · 키보드 초점 상자(`.suc-fan-tip`)로. 터치 기기(hover:none)는 부채 위 글.
  구하는 곳 (1014 사용자: '도구점에서 1000G 에 구매 · 계절 당 2개') — 마을 · 시설의 **도구** 탭(쿠키 다음 · `exoticFanShopCard` · `buyExoticFan`). 정해진 값 `EXOTIC_FAN_PRICE` 1000
  (도구상 할인 없음 — 쿠키와 같다) · 계절마다 `EXOTIC_FAN_LIMIT` 2개(`S.fanShop {key 연도-계절, bought}` — 쿠키의 `S.cookieShop` 과 같은 방식) · 보유는 `S.items.exoticFan` 개수.
  도구 탭은 첫 시내 대회 뒤(`shopUnlocked`)에 열린다. `ITEMS.exoticFan` 은 pending 을 뺐다(price 1000 · ex 0 · consumable).
  그림은 `assets/skill-upgrade/exotic-fan-v3.png`(`SK_CHOICE_FAN` · 1014 사용자가 바꿈 · 64×64 도트 · 붉은 끝 하리센 · 손잡이 왼쪽 아래). 예전 fan.svg · fan-v2.svg(`skup_fan.py` 로 만든 것) ·
  exotic-fan-v2.png(초록 끝)는 그대로 둔다. 그림을 바꾸면 `SK_CHOICE_FAN_PX`(그림 크기 칸) · `SK_CHOICE_FAN_GRIP`(손잡이 % — 휘두르는 축)도 맞춘다.
- 이국의 부채 그리기 (1014) — 부채 둘(단추 · 휘두르기)은 그림 칸 정수배(64 · 128 · 192 …)로 그린다(도트가 고르게 — 배치표 w 에 가장 가까운 배수 · 단추는 단추 폭 × `SK_CHOICE_FIT.fan[0]`).
  테두리 · 그림자는 게임이 그린다 — 배치표 `fan {flip, c, w}`(두 화면 같이 · 실험실 '부채 테두리') → drop-shadow 네 방향(그림 1칸 = 그린 크기 ÷ 64) + 그림자(그림 1, 2칸 · `skChoiceFanFilter`).
  휘두르기 — `swing` 상자가 **맞는 자리**(`r` 맞을 때 각도 · 도 · + 시계), `swingFrom {x, y, r}` 이 **시작 자리**(맞는 자리에서 옮긴 px · 각도) — 화면마다. 손잡이(`SK_CHOICE_FAN_GRIP`)를 축으로 돌고,
  `flip` 이면 좌우를 뒤집어(손잡이가 오른쪽 — 오른쪽에서 머리를 내려친다) 그린다. 부채를 들면 시작 자리(.ready · 0.65초) → 0.4초 동안 맞는 자리로(.bonk · steps(4) · 40% 에 조금 더 나감 —
  각도 0.3 배 · 자리 0.25 배 + 아래 4칸). CSS 는 배치를 놓을 때마다 `skChoiceSwing` 이 `#sucSwingCss` 에 다시 쓴다(keyframes `suc-bonk-fan` · 그림자는 각 자세의 각도만큼 되돌려 늘 오른쪽 아래).
  실험실 — 장면 '부채 들기' 의 '부채 — 시작 자리'(끌기 · 방향키 · 각도) · '부채 맞음' 의 '부채 — 맞는 자리'(끌기 · 모서리 손잡이 64 단위 · 각도) · [ ] 키 5도(Shift 15도) ·
  '▶ 휘두르기 보기'(게임과 같은 때) · 부채 테두리 · 휘두를 때 좌우 뒤집기. 1014 전 실험실 저장분의 swing(r 없음 — 예전 그림의 시작 자리)은 게임 값으로 바꿔 읽는다.
- 강화 규칙(`.suc-rules` — 왼쪽 아래 '강화 규칙')은 숨겼다 (1014 사용자 · skChoiceCss 의 display:none — 배치표 rules 칸은 그대로 · 실험실 목록에서는 뺐다).
- 말풍선 (1014) — 나오기 전 조각(`.suc-puff i`)은 64×56(예전 32×28 의 2배 · 가운데는 그대로). 꼬리 둘(`.suc-tail` 36×30 · `.suc-tail-dot` 22×20)은 픽셀 테두리 —
  바깥(테두리 색)은 계단 2칸 · 안(::after · 등급 색)은 계단 1칸 clip-path 로 테두리 한 칸(3px · 점은 2px) 두께. 말풍선 · 꼬리 · 점 사이를 4px 띄웠다(bottom -29 · -53).
  폰은 말풍선이 6px 간격으로 붙어 있어 꼬리 대부분이 다음 말풍선 뒤에 숨는다(배치 실험실에서 간격을 벌리면 보인다).
- 효과음 (1013) — `SFX` 의 suc_later(나중에 단추) · suc_hover(말풍선 · 부채에 마우스 — 마우스만) · suc_bulb(창을 열 때 · 부채를 맞고 다시 생각할 때) ·
  suc_hit(부채 타격 — 650ms) · suc_opt(말풍선이 하나씩 나올 때 — 560 + 300×i ms, CSS suc-appear 와 같은 때) · suc_done(완료 화면 — 1014). 파일 `bgm/skillup_*.ogg`(끝 무음을 잘라 48kHz Vorbis · 원본 mp3 도).
  제안 소리는 진화 · 각성이면 음을 올린다 — `sfxPlay(key, rate)` 의 재생 빠르기(`SK_CHOICE_SFX_RATE` = 반음 0 · +4 · +7). 실험실은 소리를 끈다(AUD.sfx = 0).
  단추 상자는 부채 그림만이라 예전(글 포함) 배치는 y 가 39 내려간다 — 1013 에 사용자 배치를 39 올려 그림 자리를 지켰다.
- 학생 머리 옆 표시 둘 — 긴장(`anticipation.png` · 부채 들기) · 충격(`impact.png` · 부채 맞음): 배치표의 `marks` (넓은 화면 · 폰 같이 · 학생 그림 192 칸 기준이라 학생 크기를 따라간다).
  직업 그림마다 자리가 있다(`SK_CHOICE_MARKS` — 크기 32 일 때 왼쪽 위 · 재작업 세션 것 그대로). `marks.before` · `marks.hit` = `{s 크기, d 모든 직업을 같이 옮긴 양 [x, y], at {직업 그림: [x, y]} 따로 정한 자리}`.
  크기를 바꾸면 가운데 그대로 커진다. 실험실: 끌면 자리('모든 직업 같이 옮기기'를 끄면 지금 직업 그림만) · 모서리 손잡이로 크기 · 방향키 1칸. 표시가 없는 예전 JSON 도 받는다(기본값).
- 스킬 이름이 칸보다 긴 낱말이면(영어 'Assassination' 등) 글자 중간에서 끊지 않고 그 낱말이 들어가게 글자를 줄인다 (`skChoiceNameFit` — 말풍선 너비를 줄여도 따라간다).
- 완료 화면의 결과 칸은 높이가 글 길이대로라(효과 줄 1 ~ 2 · 폰은 이름도 두 줄) 확인 단추에 닿으면 단추를 결과 칸 아래 12px 로 내리고 창을 그만큼 늘린다
  (`skChoiceDoneFit` — 재작업 CSS 의 세로 흐름과 같게). 배치를 바꾼 뒤에는 실험실에서 직업을 바꿔 가며 완료 화면을 본다.

### 학생 명부 책 (`apply_roster.py` · 1009)

- 넓은 화면(`townMode` — 게임이 보는 폭 1100px 이상 · 1013 부터 방향은 안 본다)에서 책상의 펼친 책 · 메뉴의 **학생 명부** · **팀 편성**을 누르면 화면을 바꾸지 않고 책이 뜬다 — 목업(`mockups/student-roster/roster_mockup.html`) 그대로.
  대회 준비의 '팀 편성' 등 `UI.view` 를 "roster" · "team" 으로 바꾸는 곳은 모두 책으로 간다 ("team" 은 책의 팀 편성 쪽).
  세로 · 좁은 화면은 예전 학생 명부(`viewRoster`) · 팀 편성(`viewTeam`) 그대로 — 책이 열린 채 창이 좁아지면 책을 닫고 같은 학생 · 같은 쪽의 예전 화면으로.
- 길목은 `render()` 의 앞 · 끝 한 줄씩 — 앞의 `RBK.intercept()` 는 `UI.view` 가 roster · team 이면 원래 보던 화면으로 되돌리고 책을 연다
  (책상의 마스터 육성 팝업 "master" 에서 왔으면 홈). 끝의 `RBK.after()` 는 책에서 연 게임 팝업(이름 변경 · 스킬 강화)이 끝나면 책을 다시 그린다.
- 왼쪽 쪽 — 학생 목록. 정렬(학년 · 소속 팀 · 레벨 · 전투력 · 진로 평가 · 컨디션 · 이름 — `S.opts.rbsort`)을 원 아래 꼬리표가 따라간다.
  강화 포인트가 남은 학생(`st.sp > 0` — '스킬 임의로 강화' 단추의 `spReady` 와 같은 기준)은 원 위쪽에 걸친 쪽지 **스킬 강화 가능!**(영어 SKILL UPGRADE! · 1014 —
  모양은 원 아래 꼬리표 `.tag.tm` 그대로 · `.skb` · 원을 따라 옮긴다 · 팀 편성의 다른 팀 학생은 흐리게). 영어 단추 글은 'Auto-Upgrade'(1014 — 'Skills' 까지면 정렬 칸을 침범했다).
  쪽지를 누르면(Enter · Space 도 — 칸 안의 `role=button` · 팀 편성 꼬리표와 같은 방식) 게임의 스킬 강화 팝업(`openSkillUp` — 학생 상세 쪽이면 그 학생을 고른 뒤 · 끌기는 시작하지 않는다).
  그래서 학생 상세 스킬 칸의 '스킬 강화' 단추는 뺐다 (1014 사용자 — '강화 포인트 N' 글만 남는다).
  정렬 바로 왼쪽에 **스킬 임의로 강화** — 강화 포인트가 남은 학생이 있을 때만(`spReady` · 오른쪽 칸은 `spTotal`). 누르면 게임의 확인 창(`autoSkillUpConfirm`) → 결과 창 (예전 학생 명부 머리의 단추와 같다).
  오른쪽 쪽 — 학생 상세 또는 팀 편성 (명부 머리의 '팀 편성' 단추로 바꾼다).
- 상세 — 이름 변경 ✎(게임의 `renameStudent` 팝업이 책 위에) · 스킬 칸 머리의 **스킬 강화**(강화 포인트가 있을 때만 — `skillUpModal`) ·
  유물 칸의 **해제**(보관함으로 — 예전 학생 상세와 같다) · 빈 유물 칸(`+ Slot N`)을 누르면 책을 닫고 유물 보관고로 (보관고 유물마다 ‘장착할 학생’을 이 학생으로 골라 둔다 — `goRelic`).
  신뢰 한마디 · 훈련 성공률 · 부상 · 개인 행동 고르기는 넣지 않았다 (사용자 결정).
- 팀 편성 — 게임의 `S.teams` 를 게임 함수(`teamAssign` · `autoFillAllTeams` · `formOf` · `formSlots` · `cleanTeams` …)로 바로 고치고 저장한다 (진형 강화의 서 ·改 다섯 자리도 그대로).
  팀 탭 · 진형 넷 · 자리 누르기 · 끌어 놓기(명부 → 자리 · 자리 → 자리 · 자리 → 명부는 빼기) · 진형에 맞춰 임의 편성(일지에도 남긴다) · 전투력 순으로 자동 편성 · 비우기.
  왼쪽 꼬리표는 소속 팀 고르기 쪽지 (자리가 다 찬 팀은 바꿀 학생을 고른다).
- 그림자 DOM(`#rbHost` · z-index 79 — 게임 팝업 `.overlay` 80 · 알림 90 아래) 안에 그린다 — 게임 CSS(도트 테마가 button 에 붙이는 `!important` 등)와 책 CSS 가 섞이지 않는다. 글꼴은 게임의 `@font-face`.
- 책 모양 — 목업 원본 `src/roster_tpl.html` 의 CORE_CSS · CORE_HTML 을 apply_roster 가 그대로 가져온다 (그림 자리 `{{BOOK}}` · `{{RIBBON}}` 은 CSS 변수로).
  책을 다시 디자인하면 목업 원본을 고쳐 목업 · 배치판을 다시 굽고(목업 README) apply_roster → wrap. 게임에서만 필요한 것(덮개 · 스킬 강화 · 해제 단추)은 `roster_block.css`, 동작은 `roster_block.js`.
- 그림 `ROSTER_ART` — `book`(책) · `ribbon`(책갈피 끈), 목업의 `art/book.png` · `art/ribbon.png` 를 무손실 WebP 로. 배치 `RB_LAYOUT` — 목업의 `art/roster_layout.json` (`items` · `face.jobs` 만).
- 책은 창에 맞춰 통째로 줄인다 (1배까지 — 1214 × 980 기준). 닫기: × · Esc · 책 바깥 누르기. Esc 는 쪽지 → 고른 자리 → 책 차례 (게임 팝업이 떠 있으면 그쪽 차례). 닫으면 게임 화면을 다시 그린다.

### 오프닝 글 (`apply_optx.py` · 1010)

- 새 시나리오 오프닝의 글 아홉 장면을 캔버스로 그린다 — 예전 APNG(12.3MB · `assets/opening/` 의 intro · rift · danger · date · title-type · dad-dontsay · dad-dream · dad-hero · date-winter)를 대신한다.
  APNG 를 50ms 장마다 재서 효과 · 때(ms)를 옮겼다 (비교 · 측정은 Claude 세션에서 — 겹쳐 보면 글자 위치가 0~4px 안).
  - 인트로 · 날짜 둘 — 글자가 흐림에서 선명해지기(0.42초) · 연이 통째로 흐려지기. 날짜 '가을' 은 검은 글자(푸른 빛 위)
  - 시공 균열 · '아, 이건 위험...' — 같은 등장 + 지지직(청록 잔상 · 밀린 띠 · 검은 줄 · 50ms 장) · 글자마다 깜빡이다 꺼지기 · '위험' 은 꺼질 듯 깜빡이는 59장(`MAL_DANGER`)
  - 타자기 제목 — 오른쪽부터 한 글자씩 찍기(`OP_TYPE_AT` 타자 소리와 같은 때) · 가로줄 긋고 걷기 · 은빛 그라데이션 · 테두리 · 그림자
  - 아버지 대사 셋 — 흐림 없이 서서히 · 연이 흐려지기
- `OPTX.make(장면, 클래스)` → 그릴 준비가 된 canvas (글꼴을 기다리고 글자를 미리 굽는다). 붙이는 순간부터 돌고, 떼면 멈춘다 — 예전 `apngImg` 자리에 그대로.
  클래스는 예전 APNG 와 같다(`op-intro` · `op-rift` · `op-date`) — 크기 · 자리가 그대로. 캔버스는 화면 폭 × 배율(최대 1920)로 그린다.
  `OPENING.<장면>` 은 `{ms, tail}` 만 남았다 (끝의 빈 시간 — 다음 장면까지의 간격 계산). 시험용 `OPTX.seek(canvas, ms)` (그때에 멈춰 그리기).
- 글 · 효과 · 때는 `optx_block.js` 의 `SC` 한 곳 — 줄마다 `at`(글자마다 나오는 때) 또는 연의 `ln`(첫 · 끝 글자 때 · 그 사이는 글자 무게대로).
  글꼴은 나눔명조 ExtraBold(`OpTxSerif` — 인트로 · 날짜 둘)와 고운돋움(`OpTxSans` — 나머지)을 쓰는 글자만 남긴 조각 `optx_fonts.css`(50KB · data: woff2).
  **글을 바꾸면** `optx_fonts.py` 로 조각을 다시 만든다 (`npm i @fontsource/nanum-myeongjo @fontsource/gowun-dodum` 한 폴더를 인자로) → apply_optx.
- 블록 지킴이에는 넣지 않았다 — game.html 의 `/* OPTX 시작 */ ~ /* OPTX 끝 */` · `/* OPTX-FONTS 시작 … 끝 */` 은 apply 할 때마다 블록 파일로 덮는다.
- 예전 APNG 아홉 장은 게임이 더 이상 읽지 않는다 (지워도 된다). `tools/apngen/*-en.png`(영어 APNG)도 게임은 안 쓴다.

### PNG → WebP (`apply_webp.py` · 1008)

- 무손실 (보이는 픽셀은 PNG 와 같다 — 완전히 투명한 곳의 숨은 색만 정리): 이야기 그림(`story_art`) · 스킬 이펙트(PNG 로 남아 있던 5장) · UI 리소(`ui-riso`) · 마을 지도(`town`) ·
  시작 화면 목판(`title-art`) · 메뉴 아이콘(`menu_sc`) · NPC 도트(`npc_px`) · 몬스터 도트(`mon_img` — 큰 그림 `*-warm-pixel` 은 q90) · 스케줄 · 책상 그림 · 효과 아틀라스(`fx_img.webp.js` — 캔버스에서 읽는 그림이라 JS 로 감싼다)
- q90 (손실 · 투명도는 그대로): 쿼터뷰 나무 테두리(`battle-fields/quarter/frame`) · 버튼 박스(`controls`) · 몬스터 큰 그림(`mon_img/*-warm-pixel` — 무손실로는 -21% 뿐이라 q90, 7.4MB → 1.7MB).
  `Q90` 은 글롭 무늬 — q90 쪽은 이미 WebP 로 바꾼 경로(`…webp?v=`)도 옆에 PNG 가 있으면 다시 굽는다
- 바꾸지 않는 것: 직업 스프라이트(`spr_x_img/*.png.js`) · 쿼터뷰 지도 11장 · 움직이는 PNG(오프닝 · 전투 배너) · 얼굴 그림(학생 · 오프닝)
- 원래 PNG 는 지우지 않는다 — 게임은 더 이상 읽지 않는다 (편집기 · 원본 보관용으로 남겨도 되고 지워도 된다).
- 그림을 `data:` 로 다시 넣는 pack 스크립트를 돌렸다면 `wrap.py` 를 한 번 돌려 파일로 뺀 뒤 `apply_webp.py` → `wrap.py`.
- 새 그림을 PNG 로 더한 경우: 위 폴더면 apply_webp 가 다음에 같이 바꾼다. 다른 폴더는 `LOSSLESS_DIRS` · `Q90` 에 더한다.

## 꼭 지킬 것 — 블록은 블록 파일에서 고친다

`/* SCHED_SCROLL_START … */ ~ /* SCHED_SCROLL_END */`, `/* MDESK_START … */ ~ /* MDESK_END */`, `/* CSLWIN_START … */ ~ /* CSLWIN_END */` · `/* LKWIN_START … */ ~ /* LKWIN_END */` (와 각 CSS 블록), `/* ROSTERBK_START … */ ~ /* ROSTERBK_END */`(책 CSS 는 이 블록 안의 문자열), `/* OPTX 시작 */ ~ /* OPTX 끝 */`(+ 글꼴 `/* OPTX-FONTS 시작 … 끝 */` · 지킴이 없음) 안은 apply 할 때마다 블록 파일 내용으로 **통째로 갈아 끼운다**.
game.html 에서 블록 안을 직접 고치면 다음 apply 가 그 수정을 지운다.

그래서 `patch/blockguard.py` 가 지킨다 — apply 가 끝날 때 넣은 블록의 지문을 `patch/blocks.sha.json` 에 적어 두고, 다음 apply 전에 game.html 쪽 블록이 그 지문과 다르면 멈춘다.
멈추면 game.html 에서 고친 내용을 `*_block.js` · `*_block.css` 로 옮긴 뒤 다시 돌린다. 덮어써도 될 때만 `--force`.
(블록 파일을 고친 것은 상관없다 — 비교 대상은 game.html 쪽이다. 그림 줄 `const SCHED_ART/GEO`, `MDESK_ART/GEO`, `CSL_ART`, `ROSTER_ART` 는 빌드가 바꾸므로 비교에서 뺀다.)

## 배치를 바꿀 때

- 스케줄: 스케줄 배치판(`Claude outputs/schedule_kit/schedule_editor.html`)에서 JSON 을 내보내 `patch/sched_layout.json` 을 바꾸고 apply_sched.
- 책상: 책상 소품 배치판(`Claude outputs/desk_kit/desk_editor.html` — 사본 `kit/desk_editor.html`)에서 JSON 을 내보내 `patch/desk_layout.json` 을 바꾸고 `apply_desk.py game.html tools/gen/patch/desk_layout.json`.
  누를 수 있는 소품(말린 지도 · 책 더미 + 봉랍 · 안경 + 회중시계 · 펼친 책 · 두루마리)은 `desk_art.py` 의 `GROUPS` 에서 고른다.
- 학생 명부 책: 학생 명부 배치판(`mockups/student-roster/roster_placer.html`)에서 저장한 `roster_layout.json` 을 `mockups/student-roster/art/` 에 덮어쓰고 apply_roster → wrap (목업 · 배치판도 다시 구우려면 목업 README).
- 스킬 강화 창: 스킬 강화 창 배치 실험실(`tools/skill_upgrade_lab.html`)에서 'JSON 저장' → `patch/skup_layout.json` 에 덮어쓰고 `python tools/gen/patch/apply_skup.py game.html` → wrap.
- 쿼터뷰 지도: `assets/battle-fields/quarter/` 의 그림을 바꿨으면 `python tools/gen/patch/apply_tqmaps.py game.html assets/battle-fields/quarter` — 그림 내용으로 `?v=` 를 새로 매겨 캐시를 넘긴다.
  지도 더하기 · 필드 잇기 · 클로즈업 가운데(mx · my)는 스크립트 위쪽 표(SRC · MXY)에서.
- 전투 자리 · 직업 크기 · 필드(쿼터뷰 지도 포함) 확대 · 이동 · 쿼터뷰 경기 이름 · 진영 칸(자리 · 크기 · 글자 크기): 필드 배치 실험실(`tools/field_lab.html`)이 보여 주는 `BATTLE_TUNE_PATCH = {...}` 를 글 파일로 저장해
  `python tools/gen/patch/apply_tune.py game.html <그 파일> "메모"`. 바뀐 값을 '이전 → 새' 로 모두 찍으니 실험실의 차이점 목록과 맞춰 본다.

## 소품 키트 (드물게)

`kit/` 는 배치판과 두루마리 그림의 재료다 — 책상 판자 · 남색 천 · 3D 소품(15도마다 돌린 24장) · 두루마리 · 카드.

- 스케줄 배치판: `kit3.py frames` → `build_kit3.py` → `build_editor3.py`
- 책상 배치판: `kit2.py frames` → `kit2.py` → `build_editor2.py`

3D 소품의 낱장 프레임(`frames/`)은 크기 때문에 넣지 않았다 — 다시 그리면 오래 걸린다. 지금 쓰는 소품 시트는 `kit/out2/props` · `kit/out3/props` 에 있다.
마을 화면 캡처(`kit/town_shot.png`)가 없으면 메뉴판 참고 그림은 `kit/out3/menu_ref.png` 를 그대로 쓴다.

## 글꼴

`fonts/` — 갈무리(Galmuri, SIL OFL · `Galmuri-LICENSE.txt`)는 TTF 대신 작은 WOFF, 물마루는 WOFF2 로 넣었다. 그려지는 결과는 TTF 와 픽셀 단위로 같다.
