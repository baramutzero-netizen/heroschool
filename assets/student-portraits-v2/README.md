# 학생 얼굴 전용 원화 v2

새 전투 원화의 학생 외형을 참고해 내장 이미지 생성 도구로 제작한 16개 직업의 프로필입니다. NPC·상점 얼굴과 전투 스프라이트는 변경하지 않습니다.

- `<직업>.png`: 생성 원본 (투명 배경)
- `<직업>-512.png`: 게임용 512px PNG, 원본의 알파 유지
- `prompts.json`: 최종 프롬프트 및 참조 파일
- `preview.html`: 기존 프로필과 새 48px·72px 비교
- `export.lua`: Aseprite 배치 내보내기

갱신: Aseprite에서 `export.lua` 실행 → `python tools/pack_student_portraits.py` → `python wrap.py` → `python wrap_site.py`.
튜토리얼 내 프로필은 자동 연결되며 PNG 안내 이미지는 `ui/tutorial/check.cjs`로 다시 내보냅니다.
이전 `tools/faces_from_sprites.py`는 구형 스프라이트 확대 방식이므로 현재 프로필 갱신에 사용하지 않습니다.
