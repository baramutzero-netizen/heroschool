# 인챈터 전투 · 노동 애니메이션

팔라딘의 큰 머리, 짧은 몸통과 팔다리를 기준으로 제작했습니다.
푸른 장발, 머리띠와 금색 장식, 남색·아이보리 의상, 마도서를 유지합니다.

- `source.png`: 노동 6종 생성 원본
- `combat-source.png`: 전투 5종 생성 원본
- `enchanter-complete.aseprite`: 44프레임, 11개 모션 태그 편집 원본
- `enchanter-complete.png`: 1024×2816, 256px 셀, 4열×11행
- `enchanter-complete.json`: 프레임 영역·시간 및 기준점 (128, 170)
- `preview.html`: 재생·정지·프레임 단위 확인
- `prompts.json`: 내장 image_gen 도구 제작·수정 프롬프트

행 순서: 대기, 공격, 피격, 쓰러짐, 승리, 풀 뽑기, 바닥 닦기, 먼지 털기, 음식 운반, 명상, 독서.
각 동작은 4프레임이며 음식 운반·명상·독서는 머리카락과 소품 대신 몸의 기준점으로 정렬합니다.
실제 투명 여백에 맞춘 행·열 경계를 사용해 이웃 동작이 섞이지 않게 추출합니다.
전투 시트의 큰 마법 이펙트는 제거해 머리카락과 이웃 프레임이 겹치지 않게 했습니다.

연결: 농경지 제초 → 풀 뽑기, 교회·미용실 → 먼지/바닥 청소,
여관·주점 → 먼지/바닥 청소/음식 운반, 묵상실 → 명상, 장서고 → 독서.
휴식·실패 상태에는 노동 모션을 사용하지 않습니다.

빌드 (D:/heroschool):
1. Aseprite 배치 모드로 `build-combined.lua` 실행, 종료까지 대기
2. `python sprites/enchanter-work/pack.py`
3. `python wrap.py` 및 `python wrap_site.py`

런타임 연결은 `reports/runtime.js`와 `game.html`의 `reportWorkMotion`에 반영합니다.
이번 수정은 외부 자산을 그대로 유지하고 연결 목록만 갱신했습니다.
배포 자산: `assets/spr_x_img/enchanter.png.js`.
검증: `node sprites/enchanter-work/check.cjs`.
