# tools/gen — game.html 생성 블록과 그림 스크립트

game.html 의 아래 기능은 손으로 쓴 코드가 아니라 이 폴더의 스크립트가 **블록째 넣는다**.
그림(두루마리 · 책상 · 소품)도 여기서 굽는다.

| 기능 | 넣는 스크립트 | 블록 원본 | 그림 |
|---|---|---|---|
| 두루마리 스케줄 (가로 화면) | `patch/apply_sched.py` | `patch/sched_block.js` · `sched_block.css` | `patch/sched_art.py` → `assets/sched_art/` (WebP) |
| 의뢰 (이번 주 의뢰 · 의뢰처별 등급) | `patch/apply_job.py` (apply_sched 가 같이 부른다) | 스크립트 안 | — |
| 마스터 노트 책상 | `patch/apply_desk.py` | `patch/mdesk_block.js` · `mdesk_block.css` | `patch/desk_art.py` → `patch/desk_out/` → `assets/mdesk_art/` (WebP) |
| 원정 3구간 (원정지 깊이 · 구간 보상 · 잡몹 배율 — 아래) | `patch/apply_exped3.py` | 스크립트 안 | — |
| 행동 지침 무시 (주 시작 판정 · 상담 이벤트 · 결산 창 문구 · 튜토리얼 14 — 아래) | `patch/apply_defy.py` | 스크립트 안 | — |
| 스킬 등급표 (등급 6단계 · 등급 · 레벨로 정하는 수치 · 적도 같은 표 · 원정 잡몹 배율 — 아래) | `patch/apply_skgrade.py` (apply_exped3 뒤) | 스크립트 안 | — |
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
python tools/gen/patch/apply_webp.py  game.html                                   # PNG → WebP (바뀐 게 없으면 그대로)
python wrap.py
python wrap_site.py
```

- apply 는 그림을 `data:` 로 넣는다 (1008 — 무손실 WebP). `wrap.py` · `wrap_site.py` 의 split_assets 가 `assets/sched_art/` · `assets/mdesk_art/` 로 빼고 game.html 에는 경로만 남긴다.
- `apply_desk.py` 는 줌 넘어가기를 맞추려고 `assets/sched_art/` 그림(`.webp` 가 있으면 그것)에서 스케줄 두루마리 축 자리를 잰다. 스케줄 그림을 바꿨다면 `wrap.py` 를 한 번 돌린 뒤 apply_desk.

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

`/* SCHED_SCROLL_START … */ ~ /* SCHED_SCROLL_END */`, `/* MDESK_START … */ ~ /* MDESK_END */` (와 각 CSS 블록) 안은 apply 할 때마다 블록 파일 내용으로 **통째로 갈아 끼운다**.
game.html 에서 블록 안을 직접 고치면 다음 apply 가 그 수정을 지운다.

그래서 `patch/blockguard.py` 가 지킨다 — apply 가 끝날 때 넣은 블록의 지문을 `patch/blocks.sha.json` 에 적어 두고, 다음 apply 전에 game.html 쪽 블록이 그 지문과 다르면 멈춘다.
멈추면 game.html 에서 고친 내용을 `*_block.js` · `*_block.css` 로 옮긴 뒤 다시 돌린다. 덮어써도 될 때만 `--force`.
(블록 파일을 고친 것은 상관없다 — 비교 대상은 game.html 쪽이다. 그림 줄 `const SCHED_ART/GEO`, `MDESK_ART/GEO` 는 빌드가 바꾸므로 비교에서 뺀다.)

## 배치를 바꿀 때

- 스케줄: 스케줄 배치판(`Claude outputs/schedule_kit/schedule_editor.html`)에서 JSON 을 내보내 `patch/sched_layout.json` 을 바꾸고 apply_sched.
- 책상: 책상 소품 배치판(`Claude outputs/desk_kit/desk_editor.html` — 사본 `kit/desk_editor.html`)에서 JSON 을 내보내 `patch/desk_layout.json` 을 바꾸고 `apply_desk.py game.html tools/gen/patch/desk_layout.json`.
  누를 수 있는 소품(말린 지도 · 책 더미 + 봉랍 · 안경 + 회중시계 · 펼친 책 · 두루마리)은 `desk_art.py` 의 `GROUPS` 에서 고른다.
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
