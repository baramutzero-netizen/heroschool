# 팔라딘 스타일리시 전투 효과

각 PNG는 투명 배경의 단일 프레임이며 캐릭터 모션 시트와 독립적으로 관리합니다.

- 시전자: 실제 직업 `paladin` → `trail-particles.png`. 전수 스킬을 사용해도 직업 기준 유지.
- 대상: `pa_b` → `impact.png`, `pa_1` → `shield.png`, `pa_2` → `beam-particles.png`, `pa_u` → `beam-particles.png` + `shield.png`.
- 대상 목록은 전투 계산 프레임의 `fx.t`, 스킬 식별자는 `fx.skillId`를 사용합니다. 시전자 자신도 대상이 될 수 있습니다.
- 공격 3번째 프레임의 타격 순간부터 정지 연출 종료까지 표시합니다. 카메라 좌표 추적만 수행하며 이미지 프레임은 바뀌지 않습니다.
- 광선 시작점은 상단 경계선, 끝부분은 대상 머리입니다. 양쪽 경계 밖은 잘라냅니다.
- 기존 스타일리시 모드와 동일하게 가로 화면에서 동작하며, 미등록 스킬의 대상 효과는 기존 연출을 사용합니다.

`runtime.js` 수정 후 `python assets/skill-fx/paladin/pack.py`, `python wrap.py`, `python wrap_site.py` 순서로 반영합니다.
`check.cjs`는 두 실행 파일의 로딩, 4개 스킬, 전수 조합, 광선 시작점, 효과 정리를 검증합니다. 생성 프롬프트는 `prompts.md`.

2026-10-01: 철퇴 궤적과 치유 광선을 견습생용 파티클 버전으로 교체. 기존 원본 보관. 생성 프롬프트: particle-prompts.md (built-in image_gen).
