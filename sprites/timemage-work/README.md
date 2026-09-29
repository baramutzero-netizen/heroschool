# 타임 매지션 전투 · 노동 애니메이션

팔라딘의 큰 머리·짧은 몸통·짧은 팔다리를 기준으로 제작했습니다.
**양쪽 보라색 트윈테일과 남색 리본**을 유지하며, 사이드 포니테일로 그리지 않습니다.
보라색 눈, 남색 마법사 의상과 푸른 수정 지팡이를 사용합니다.

- `source.png`: 노동 6종 최종 생성 원본
- `combat-source.png`: 전투 5종 최종 생성 원본
- `timemage-complete.aseprite`: 44프레임, 11개 모션 태그
- `timemage-complete.png`: 1024×2816, 256px 셀, 4열×11행
- `timemage-complete.json`: 프레임 영역·시간, 기준점 (128, 170)
- `preview.html`: 재생·정지·프레임 단위 확인
- `prompts.json`: 내장 image_gen 제작·머리 수정 프롬프트

행 순서: 대기, 공격, 피격, 쓰러짐, 승리, 풀 뽑기, 바닥 닦기, 먼지 털기, 음식 운반, 명상, 독서.
각 동작 4프레임. 머리카락·소품 대신 몸의 기준점으로 음식 운반·명상·독서를 정렬합니다.

연결: 농경지 → 풀 뽑기, 교회·미용실 → 먼지/바닥 청소,
여관·주점 → 먼지/바닥 청소/음식 운반, 묵상실 → 명상, 장서고 → 독서.
휴식·실패 상태에는 노동 모션을 사용하지 않습니다.

빌드 (D:/heroschool):
1. Aseprite 배치 모드로 `build-combined.lua` 실행, 종료까지 대기
2. `python sprites/timemage-work/pack.py`
3. `python wrap.py` 및 `python wrap_site.py`

노동 연결은 `reports/runtime.js`와 `game.html`의 `reportWorkMotion`에 반영합니다.
배포 자산: `assets/spr_x_img/timemage.png.js`.
검증: `node sprites/timemage-work/check.cjs` — 실행·배포본 로딩, 44프레임 및 장소별 동작 연결.
