# 로그 전투 · 노동 애니메이션

팔라딘 기준의 큰 머리, 짧은 몸통과 팔다리로 제작했습니다.
금발 포니테일, 푸른 눈, 검은 복면·가죽 의상과 쌍단검을 유지합니다.

- `source.png`: 노동 6종 생성 원본
- `combat-source.png`: 전투 5종 생성 원본
- `rogue-complete.aseprite`: 44프레임, 11개 모션 태그
- `rogue-complete.png`: 1024×2816, 256px 셀, 4열×11행
- `rogue-complete.json`: 프레임 영역·시간 및 기준점 (128, 170)
- `preview.html`: 재생·정지·프레임 단위 확인
- `prompts.json`: 내장 image_gen 제작 프롬프트

행 순서: 대기, 공격, 피격, 쓰러짐, 승리, 풀 뽑기, 바닥 닦기, 먼지 털기, 음식 운반, 명상, 독서.
각 동작은 4프레임입니다. 음식 운반·명상·독서는 몸의 기준점을 사용해 정렬합니다.
원본의 실제 투명 여백에 맞춘 행·열 경계로 이웃 프레임의 머리카락·소품이 섞이지 않도록 추출합니다.

장소 연결: 농경지 → 풀 뽑기, 교회·미용실 → 먼지/바닥 청소,
여관·주점 → 먼지/바닥 청소/음식 운반, 묵상실 → 명상, 장서고 → 독서.
휴식·실패 상태에는 노동 모션을 재생하지 않습니다.

빌드 (D:/heroschool):
1. Aseprite 배치 모드로 `build-combined.lua` 실행 후 종료까지 대기
2. `python sprites/rogue-work/pack.py`
3. `python wrap.py` 및 `python wrap_site.py`

노동 클래스 연결은 `reports/runtime.js`와 `game.html`의 `reportWorkMotion`에 반영합니다.
외부 배포 자산: `assets/spr_x_img/rogue.png.js`.
검증: `node sprites/rogue-work/check.cjs` — 실행본·배포본의 아틀라스 로딩과 44프레임 및 의뢰·시설 연결 확인.
