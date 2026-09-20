# 수련관 공부 모션

기본 내장 image_gen 도구로 제작. 원본은 이 폴더에 보관하고, 게임에는 WebP를 내장한다.

- `source-0.png`: 배틀메이지(forcemage), 거너, 몽크, 소드맨. 각 행 4프레임.
- `source-1.png`: 아처, 바드, 암흑사제, 드루이드.
- `source-2.png`: 인챈터, 닌자, 팔라딘, 프리스트.
- `source-3.png`: 로그, 마법검사, 타임매지션, 마법사.
- `hall-classroom.png`: 수련관 배경. 기존 원본 `reports/sources/hall.png` 보존.
- `empty-source.png`: 빈 책상과 의자. 학생 수가 5명 미만이어도 총 5석 유지.
- `reference-0..3.png`: 기존 직업 idle 원본에서 구성한 외형 참조.

## 생성 프롬프트

공통 스프라이트: transparent alpha background; exact 4 columns by 4 rows, one character per row and four consecutive subtle animation frames; chibi pixel art preserving reference identity; seated on warm wooden chair at small wooden desk with open cream book; facing diagonally upper right toward the blackboard; generous cell margins, same camera and registered furniture. No weapons in hands, no room or labels. Normal study cycle: read, lean toward book, turn page, settle back.

특수 행: battle mage asleep with head on book as pillow and subtle breathing; gunner holding and tilting a hand mirror; monk and swordsman confused with golden ??? overhead and slight head tilt/blink.

배경: edit original hall; preserve warm wood, stone floor, blue/gold banners, isometric camera; wide 3:1 edge-to-edge room with blackboard on rear right and windows left; remove old round table and chairs, leave open floor for five separately rendered desks; no people, no UI, no purple margins.

빈 책상: isolate one desk and chair matching the special sprite atlas, open book, chair near-left, desk points upper-right, actual alpha, no characters, no floor.

## 재생 및 배치

16개 직업 × 4프레임을 1024×256 스트립으로 패킹. 프레임 추출 시 셀 전체를 유지하여 페이지/물음표가 잘리지 않도록 한다. 책상·의자와 인물을 한 프레임에 포함한다. 경과보고 시간으로 프레임을 전환하므로 속도 변경과 일시정지가 적용된다. 동작 줄이기 설정에서는 첫 프레임 표시.
수련관에서만 적용. 여름 해수욕장과 의무실, 전투 애니메이션은 기존 방식 유지.

빌드: `node reports/study/prepare.cjs` (원본 준비), `python reports/pack.py`, `python wrap.py`, `python wrap_site.py`.


## 가구 통일 수정 (2026-09-21)

사용자 표시한 다섯 원 위치에 맞춰 수련관 좌석을 오른쪽 계단식으로 이동. 가장 아래 좌석은 컨디션 바가 잘리지 않도록 화면 안쪽에 배치.

내장 image_gen 편집 도구 사용. `uniform-0..3.png`는 각 기존 원본을 편집한 파일, `wizard-furniture-reference.png`는 원래 마법사 첫 프레임에서 추출한 가구 기준. 기존 `source-0..3.png`를 보존한다. 패커는 uniform 파일을 우선 사용한다.

편집 프롬프트: Edit target sprite atlas, use wizard reference ONLY as exact desk/chair/book reference. Change ONLY furniture across all sixteen cells to the same warm brown straight-legged rectangular desk, narrow vertical-slat chair, and small open cream book. Preserve characters, faces, hair, costumes, poses, row/column order, animation and alpha. Same furniture dimensions, colors, perspective and baseline. Preserve sleeping, hand mirror and question-mark motions. No labels or room. Empty desk uses the same wizard reference with character removed and occluded furniture reconstructed.

## 특수 4직업 가구 재교정

`uniform-0-corrected.png`를 우선 패킹한다. 내장 image_gen 편집으로 마법사 가구를 다시 참조해 두껍게 막힌 등받이를 얇은 가운데 살과 길게 열린 틈으로 바꾸고, 책상 상판 기울기와 높이를 조정했다. 수면·거울·물음표 모션은 보존했다.

최종 프롬프트 핵심: Copy furniture from wizard reference; narrow top crossbar, one thin vertical middle bar, two tall open rectangular spaces all the way down to chair seat, no broad wooden panel or short square holes. Match shallow wizard desktop angle, apron, seat height and feet baseline. Four rows battle mage asleep / gunner mirror / monk confused / swordsman confused, four subtle frames, transparent alpha, equal cells.
