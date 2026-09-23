# 책갈피 손패 구성

테스트 모드에서만 사용합니다. `runtime.js`의 `chronBookmark`가 종이, 색상 끈, 남은 기간 태그, 실제 카드 정보, 훈련 아이콘을 조합합니다.

- 크기, 겹침, 기울기, 글씨: `bookmarks.css`
- 카드별 기울기/높이와 획득 순 정렬: `runtime.js`
- 이미지: `ornaments/bookmark-paper.webp`, `cord-*.webp` 6종, `tag-*.webp` 3종
- 원본: `ornaments/bookmark-source.png`
- 기존 훈련 아이콘을 하단에 재사용합니다.
- 흰 바탕은 화면에서 SVG 색상 필터로 제거합니다. 원본 그림은 유지됩니다.
- 데스크톱은 hover/focus로 카드를 앞으로 꺼내며 좁은 화면은 가로 스크롤합니다.
- 빌드: `ui/chronicle/pack.py` → `wrap.py` → `wrap_site.py`
- 검증: `check-bookmarks.cjs` (분리된 미리보기 데이터 사용)

## 이미지 제작 기록
Built-in image_gen, 2026-09-23.
Prompt: A production UI sprite atlas, five columns by two rows, warm watercolor and ink fantasy academy style. Blank tall narrow ivory textured paper bookmark with punched hole; six independent braided cord loops in red, green, blue, turquoise, gold and ivory; three blank paper tags in dusty rose, lavender and sage. Large gutters, no text, isolated components.
The first transparent-background request and subsequent transparency edit returned colored backgrounds. Final edit prompt: Replace ALL background with pure flat solid white #FFFFFF. No gradients, colored glow or shadows. Keep the ten objects in identical positions, including white inside cord loops.
Final generated source: exec-6c797a67-28e9-4b57-90ca-fdc09911251c.png. Cropped individual components and encoded WebP; CSS/SVG composites the white matte at runtime.

## 좌상단 구멍 / 검은 끈 수정 (2026-09-23)
- image_gen으로 기존 종이 이미지를 수정: 중앙 구멍 제거, 좌상단(width 16%, height 6%) 단일 구멍, 질감 유지. 원본 `bookmark-paper-left-source.png`, 사용 이미지 `bookmark-paper-left.webp`.
- 색상 끈 이미지를 가는 검은 SVG 선으로 교체하여 종이 구멍과 태그 구멍을 연결.
- 태그 회전 0도, 36×68px. 기간 숫자는 17px 굵은 글씨, 남음은 13px로 분리 표시.
- 기존 선택/되돌리기/드래그/모바일 스크롤 검증 통과.

## 진행 도구 이미지 (2026-09-23)
Built-in image_gen으로 참조의 붉은 왁스 봉인/양피지 버튼 스타일을 이용한 4종 atlas 제작. Prompt: four isolated fantasy parchment-journal assets on white, crimson wax botanical seal, parchment plaque with exact Korean 이번 주를 진행한다, midnight-blue eye-emblem Book of Prophecy, crystal aqua holy-water bottle with golden wing stopper. Source: journal-actions-source.png (exec-f82e8602-d9cc-434f-9613-038ce4324ed3.png).
각각 wax-stamp, proceed-button, prophecy-book, supreme-water의 PNG와 WebP로 분리. 버튼과 아이콘은 테스트 모드에 연결. 기존 disabled/클릭 처리 유지, 진행 버튼 접근성 라벨 및 조건 안내 유지.
