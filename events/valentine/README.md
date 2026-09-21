# 발렌타인 팝업 이미지

내장 image_gen으로 제작한 3:2 연속 장면. `page-1.png` ~ `page-3.png` 원본을 보관하며 WebP를 game.html에 내장한다. 실제 이름·년도·감사 편지는 HTML에 별도로 표시한다.

1. page-1: 겨울 집무실 책상 위의 포장된 선물 상자.
2. page-2: 같은 상자를 열어 발견한 초콜릿과 봉인된 편지.
3. page-3: 초콜릿 옆에 펼친 졸업생들의 감사 편지.

## 프롬프트

1: Warm fantasy hero academy office, 3:2 landscape, winter afternoon golden light, oak desk and brass lamp left, books right, blue/gold academy banner and snowy arched window. Small closed burgundy gift box with ivory ribbon centered on leather blotter. Heartfelt graduation gratitude, no people/hands/UI/names/dates/text. Detailed game illustration.

2 (1번 원본 편집): Preserve identical room/composition/light. Open same burgundy box revealing handmade chocolates; lid behind it, untied ivory ribbon, cream sealed envelope with burgundy wax seal beside chocolates. No readable words or characters.

3 (1번 원본 편집): Preserve room continuity. Unfolded cream letter and overlapping notes foreground, opened envelope with broken wax seal, open chocolate box upper right. Faint illegible handwritten decorative strokes; actual personalized text rendered in game. No readable names/dates/UI or people.

## 게임 연결

기존 겨울 4주차 종료 시점에 3년차부터 등장. 졸업 예정 학생이 있을 때 3페이지를 큐에 넣으며 S.valentine으로 같은 해 재등장을 방지한다. 다음 해 졸업생으로 재등장한다.

빌드: `python events/valentine/pack.py`, `python wrap.py`, `python wrap_site.py`.

미리보기: `/events/valentine/preview.html` (저장 데이터 격리).
검증: `node events/valentine/check.cjs`.
