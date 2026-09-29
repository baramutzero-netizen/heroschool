# 바드 전투 · 노동 애니메이션

팔라딘의 큰 머리·짧은 몸통·짧은 팔다리를 기준으로 제작한 SD 바드입니다.
금발, 깃털 모자, 보라색 망토, 녹색 의상과 황금 하프를 유지합니다.

- `source.png`: 노동 6종 생성 원본
- `combat-source.png`: 전투 5종 생성 원본
- `bard-complete.aseprite`: 44프레임, 11개 모션 태그의 편집 원본
- `bard-complete.png`: 1024×2816, 256px 셀, 4열×11행
- `bard-complete.json`: 프레임 영역·시간, 기준점 (128, 170)
- `preview.html`: 동작 재생 / 정지 / 프레임 단위 확인
- `prompts.json`: 내장 image_gen 도구의 최종 제작 프롬프트

행 순서: 대기, 공격, 피격, 쓰러짐, 승리, 풀 뽑기, 바닥 닦기, 먼지 털기, 음식 나르기, 명상, 독서.
각 행은 4프레임입니다. 음식 운반은 좌우 발걸음, 독서는 페이지 넘김, 명상은 고정된 착석 기준점을 사용합니다.
원본의 실제 투명 여백을 기준으로 행을 분리하며 먼지털이의 옆 셀 침범도 별도 열 경계로 방지합니다.

게임 연결: 농경지 → 풀 뽑기, 교회·미용실 → 먼지/바닥 청소,
여관·주점 → 먼지/바닥 청소/음식 운반, 묵상실 → 명상, 장서고 → 독서.
휴식·실패 상태에는 노동 모션을 사용하지 않습니다.

재생성 순서 (작업 디렉터리 `D:/heroschool`):
1. Aseprite 배치 모드로 `build-combined.lua` 실행 후 프로세스 종료까지 대기
2. `python sprites/bard-work/pack.py`
3. `python reports/pack.py` (보고서 런타임 수정 시)
4. `python wrap.py` 및 `python wrap_site.py`

검증: `node sprites/bard-work/check.cjs` — 실제 게임의 44프레임 렌더, 시설·의뢰 동작 선택, 브라우저 오류 확인.
배포 자산은 `assets/spr_x_img/bard.png.js`로 분리됩니다.
