# tools/gen — game.html 생성 블록과 그림 스크립트

game.html 의 아래 기능은 손으로 쓴 코드가 아니라 이 폴더의 스크립트가 **블록째 넣는다**.
그림(두루마리 · 책상 · 소품)도 여기서 굽는다.

| 기능 | 넣는 스크립트 | 블록 원본 | 그림 |
|---|---|---|---|
| 두루마리 스케줄 (가로 화면) | `patch/apply_sched.py` | `patch/sched_block.js` · `sched_block.css` | `patch/sched_art.py` → `assets/sched_art/` |
| 의뢰 (이번 주 의뢰 · 의뢰처별 등급) | `patch/apply_job.py` (apply_sched 가 같이 부른다) | 스크립트 안 | — |
| 마스터 노트 책상 | `patch/apply_desk.py` | `patch/mdesk_block.js` · `mdesk_block.css` | `patch/desk_art.py` → `patch/desk_out/` → `assets/mdesk_art/` |
| 전투 치명타 숫자 높이 · 학원 이름 맞추기 · 친선전 전부 거절 재확인 · 고른 칸 강조선 | `patch/apply_crit.py` · `apply_acadfit.py` · `apply_fdecline.py` · `apply_optsel.py` | 스크립트 안 | — |

모든 apply 는 몇 번을 돌려도 같은 결과다. 빌드 1007 의 game.html 에 그대로 돌리면 바뀌는 것이 없다 (Claude 작업 공간에서 확인 — game.html · 그림 모두 바이트 단위로 같음).

단, Claude 가 보낸 PNG 에는 콘텐츠 출처 정보(C2PA) 블록이 붙어서 온다 — 장당 약 5.8KB 커지고, 그림(픽셀)은 같다.
그래서 이 컴퓨터에서 다시 돌리면 그림은 같아도 `assets/sched_art/` · `assets/mdesk_art/` 의 PNG 파일이나 game.html 의 `?v=` 값이 바뀐 것으로 나올 수 있다. 그대로 커밋해도 된다.

## 필요한 것

- Python 3.10+, `pip install pillow numpy`
- 책상 그림을 **배치부터 다시 구울 때만**: `pip install playwright` 후 `playwright install chromium` (배치판 자신의 그리기 코드를 브라우저에서 돌린다)
- 배치판 HTML 을 다시 만들 때만 (`kit/build_editor*.py`): `pip install fonttools brotli`

## 쓰는 법 (저장소 맨 위에서)

```
python tools/gen/patch/apply_sched.py game.html tools/gen/patch/sched_layout.json
python tools/gen/patch/apply_desk.py  game.html                                   # desk_out 그림 그대로
python tools/gen/patch/apply_desk.py  game.html tools/gen/patch/desk_layout.json  # 책상 배치를 바꿨을 때 — 다시 굽는다
python wrap.py
python wrap_site.py
```

- apply 는 그림을 `data:` 로 넣는다. `wrap.py` · `wrap_site.py` 의 split_assets 가 `assets/sched_art/` · `assets/mdesk_art/` 로 빼고 game.html 에는 경로만 남긴다.
- `apply_desk.py` 는 줌 넘어가기를 맞추려고 `assets/sched_art/` 그림에서 스케줄 두루마리 축 자리를 잰다. 스케줄 그림을 바꿨다면 `wrap.py` 를 한 번 돌린 뒤 apply_desk.

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
- 전투 자리 · 직업 크기: 필드 배치 실험실(`tools/field_lab.html`)이 보여 주는 `BATTLE_TUNE_PATCH = {...}` 를 글 파일로 저장해
  `python tools/gen/patch/apply_tune.py game.html <그 파일> "메모"`. 바뀐 값을 '이전 → 새' 로 모두 찍으니 실험실의 차이점 목록과 맞춰 본다.

## 소품 키트 (드물게)

`kit/` 는 배치판과 두루마리 그림의 재료다 — 책상 판자 · 남색 천 · 3D 소품(15도마다 돌린 24장) · 두루마리 · 카드.

- 스케줄 배치판: `kit3.py frames` → `build_kit3.py` → `build_editor3.py`
- 책상 배치판: `kit2.py frames` → `kit2.py` → `build_editor2.py`

3D 소품의 낱장 프레임(`frames/`)은 크기 때문에 넣지 않았다 — 다시 그리면 오래 걸린다. 지금 쓰는 소품 시트는 `kit/out2/props` · `kit/out3/props` 에 있다.
마을 화면 캡처(`kit/town_shot.png`)가 없으면 메뉴판 참고 그림은 `kit/out3/menu_ref.png` 를 그대로 쓴다.

## 글꼴

`fonts/` — 갈무리(Galmuri, SIL OFL · `Galmuri-LICENSE.txt`)는 TTF 대신 작은 WOFF, 물마루는 WOFF2 로 넣었다. 그려지는 결과는 TTF 와 픽셀 단위로 같다.
