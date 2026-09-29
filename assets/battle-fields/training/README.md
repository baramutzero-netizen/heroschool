# 학원 전투 연습장

첫 원정지 dummy / d1에 적용. 지하 수련장에서 지상 전투 연습장으로 변경.

별도로 제작한 원화: landscape-source.png, portrait-source.png. Aseprite export.lua로 각각 1920×960, 1080×1920 PNG를 내보냄. 내장 image_gen 사용, prompts.json에 제작 프롬프트 저장.

game.html의 FIELD_VARIANTS.dummy에서 각 방향의 src, aspect, ground(그림의 바닥 시작 높이 비율)를 수정. 가로 .31, 세로 .20. 무대 자체 너비/높이가 1.2 미만이면 portrait, 1.2 이상이면 landscape. 회전/리사이즈에도 재선택. 다른 필드는 기존 배경 유지하며, 두 원화를 완성하면 FIELD_VARIANTS에 같은 형식으로 추가.

검증: check.cjs — PC/모바일/회전 화면, 두 배포 빌드, 1.2 경계값, 실제 이미지 크기 확인.
install_training_field.py는 최초 적용 기록이므로 다시 실행하지 않음.
