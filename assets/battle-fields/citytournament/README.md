# 가을 시내 대회

기존 시내 대회장(흙바닥·목책·벤치)을 참고해 단풍과 대회 깃발을 더한 별도 가로/세로 원화. 내장 image_gen 사용.

- landscape.png: 1920×960 / 바닥 시작 비율 .44
- portrait.png: 1080×1920 / 바닥 시작 비율 .19
- *-source.png: 생성 원본
- export.lua: Aseprite 크기 내보내기
- preview.html: 원화와 실제 게임 적용 화면
- prompts.json: 제작 프롬프트

game.html의 FIELD_VARIANTS.citytournament에서 위치 조정. 무대 비율 1.2 미만이면 세로, 그 외 가로. 기존 city 대회 필드 선택을 통해 연결. PC·웹 빌드에서 화면 회전 및 경계값 검증: check.cjs.
