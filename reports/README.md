# 시설 장면 경과 보고

`runtime.js`와 `style.css`가 편집 원본입니다. `rooms/*.webp`는 게임에 포함되는 배경이며, `sources/*.png`는 생성된 원본입니다. `game.html`의 실제 `dayRun`과 원정 완료 처리에서 결과를 기록합니다. 재생, 배속, 요일 이동은 게임 수치나 난수를 변경하지 않습니다.

빌드 순서: `python reports/pack.py`, `python wrap.py`, `python wrap_site.py`.
기능 검수: `node reports/check.cjs` (Playwright와 Microsoft Edge 필요).
미리보기: 로컬 서버의 `/reports/preview.html`. 저장소를 별도 메모리로 대체해 기존 저장 데이터와 분리합니다.

## 배경 생성 기록

### 능력치 표시와 컨디션

학생 카드와 같은 `Math.round` 기준으로 전후 표시 정수가 달라진 능력치만 `39 → 40` 형식으로 표시합니다. 변화는 1배속 기준 450ms 간격으로 연달아 나타나며 900ms 동안 머리 위 두 줄 높이까지 올라가면서 사라집니다. 중간 높이에서 불투명도는 50%입니다. 하락도 빠짐없이 표시합니다. 컨디션은 전용 바로 전후 값을 보간하고, 표시 값 70 이상은 초록색, 40~69는 주황색, 39 이하는 빨간색입니다. 등급 문자는 사용하지 않습니다.

상승 효과음은 `bgm/statup.mp3`를 빌드에 포함해 사용하며 기존 효과음 음량을 따릅니다. 일시정지·장면 이동·닫기 때 중지합니다. 항목 수에 맞춰 장면 길이를 늘려 마지막 변화가 잘리지 않도록 합니다. 검수: `node reports/check-stat-sequence.cjs`.

### 크롭 및 재생 규칙

모든 시설은 동일한 3:1 영역으로 원본을 잘라 보여줍니다. 가로는 원본의 96%(좌우 2% 제외), 세로는 32%를 사용합니다. 원본 이미지는 보존하며 `REPORT_LAYOUTS`에서 세로 크롭 위치와 시설별 캐릭터 자리를 관리합니다. 의무실은 침대 3곳에 기존 `down` 모션의 누운 프레임을 사용합니다.

하루에 오전 대표 시설 한 곳, 오후 집중 대표 시설 한 곳만 재생합니다. 오후 집중 기록이 없는 날은 오전만 표시합니다. 부분 휴식이나 다른 집중 분야가 있어도 추가 시설 장면은 재생하지 않습니다. 상세 성장 계산과 주간 텍스트 기록은 보존합니다.

내장 image_gen 도구로 생성했습니다. CLI/API 대체 경로는 사용하지 않았습니다. 실제 화면에는 이미지 위에 기존 학생 스프라이트와 UI를 표시합니다.

장서고 최종 프롬프트:

> Create a square 1024x1024 game background illustration: cozy fantasy hero academy LIBRARY. Isometric cutaway dollhouse room, two rear walls meeting at top center, diamond wooden floor extending to bottom center, diagonal elevated camera angle like a Japanese chibi mobile RPG room. Warm hand drawn anime game art with clean outlines, soft cel shading, detailed bookshelves along both rear walls, tall arched window, small globe and magical reading lamps, two reading desks located close to the rear walls. Entire room visible, no roof, no front walls. Spacious completely clear central and front floor occupying lower 55 percent to place several animated student sprites later. Neutral pale lavender outside the room. No people, no characters, no text, no UI, no logos. Furniture must not obstruct central floor. Polished cozy illustrated game asset, square composition.

나머지 시설 최종 공통 프롬프트 (`{room}`에 아래 시설 문구 삽입):

> Create one square 1024x1024 game background illustration: cozy fantasy hero academy {room}. Isometric cutaway dollhouse room, two rear walls meeting at top center, diamond floor extending to bottom center, diagonal elevated camera like a Japanese chibi mobile RPG room. Warm hand drawn anime game art, clean outlines, soft cel shading and charming detailed furnishings. Entire room visible, no roof or front walls. Spacious completely CLEAR central and front floor occupying lower 55 percent for five animated student sprites added later. Furniture only near rear walls, never obstruct central floor. Pale lavender outside the room. No people, no characters, no text, no UI, no logos. Polished cozy illustrated game background, square composition.

- gym: training gym with wooden exercise equipment, racks of wooden weights, hanging punching bag and a practice bench along the walls
- arena: indoor sparring dojo with wood floor, weapon racks full of wooden swords and shields, banners, practice dummies along the walls
- hall: tactics classroom with a large tactical chalkboard, small round strategy table along the rear wall, academy banners and wooden practice mannequins
- chapel: serene meditation sanctuary with arched stained glass window, candles, small crystal altar, pale stone floor and purple meditation cushions along the walls
- infirm: sunlit infirmary with cozy white curtained beds along the rear walls, medicine cabinets, potted green plants and pale wooden floor

원본은 방별로 검사 후 1024px WebP로 패키징했습니다. 도구가 제공한 원본은 삭제하지 않았습니다.
