# 광역 대회 · 예선 리그 공용 필드

기존 석재 경기장과 천막 관람석을 유지하고 대회 깃발을 추가. 내장 image_gen으로 별도 가로·세로 원화를 제작.

- landscape.png: 1920×960, ground .40
- portrait.png: 1080×1920, ground .17
- *-source.png: 생성 원본
- export.lua: Aseprite 크기 내보내기
- preview.html: 원화와 실제 적용 화면
- prompts.json: 제작 프롬프트

game.html의 FIELD_VARIANTS.areatournament에서 방향별 바닥 시작 비율 조정. region(광역 대회)과 qual(예선 리그) 모두 이 필드를 선택. 무대 가로/세로 비율 1.2 미만이면 세로, 나머지는 가로. check.cjs로 두 빌드의 PC/모바일/회전과 경계값을 검증.
