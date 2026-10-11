# 용사 학원 키우기 — 학원이 망했다

쓰러진 아버지의 용사 학원을 물려받아, 학생 세 명으로 시작해 3년간 학원을 키우는
한국어 웹 운영 시뮬레이션입니다. 라이브러리 없이 바닐라 JS·HTML·CSS로 만들었고,
서버도 빌드 도구도 필요 없습니다. 게임 코드는 HTML 파일 하나, 그림·효과음은 `assets/` 폴더에 있습니다.

👉 **[바로 플레이](site/index.html)** — 또는 `heroschool.html` 을 브라우저로 열기 (`assets/` · `bgm/` 폴더가 옆에 있어야 합니다)

---

## 무엇을 하는 게임인가

- **카드로 짜는 주간 스케줄** — 한 주는 월~금 다섯 칸. 손패 9장 중 다섯 장을 끌어다 놓고
  진행하면 월요일부터 순서대로 치러집니다. 전날과 같은 색 카드가 이어지면 효과가
  10%씩, 최대 40%까지 오릅니다.
- **3인 1팀 ATB 전투** — 진형(전열·후열)과 스킬 발동 확률, 의식 유지선이 맞물립니다.
  대회·친선전·원정 모두 같은 전투 엔진을 씁니다.
- **원정** — 던전 구간을 차례로 돌파하며 자금·유물·진로 평가를 얻고, 대신 업보가 쌓입니다.
- **대회 사다리** — 가을 시내 대회(1팀) → 광역 대회(2팀) → 학원제 예선 리그·본선(3팀).
  성적에 따라 다음 해 초대장이 오고, 명성이 오르면 신입생 정원과 원정지가 열립니다.
- **학생** — 여섯 가지 멘탈리티와 잠재력, 성격, 라이벌·소울메이트 관계, 이명(異名),
  상담, 업보에 따라 갈리는 졸업 진로.

저장은 브라우저 `localStorage` 에 남습니다. 서버가 없어 기기·브라우저마다 진행이 따로 갑니다.

---

## 파일 구조

| 경로 | 설명 |
|---|---|
| `game.html` | **원본 소스.** 게임 로직 전체가 여기 있습니다. `<!doctype>`·`<html>`·`<body>` 가 없는 조각 파일입니다 |
| `assets/` | 그림 · 효과음. `split_assets.py` 가 `game.html` 에서 빼낸 파일들 (게임과 **같이 커밋**해야 합니다) |
| `assets/**/*.js` | 캔버스에서 픽셀을 읽는 그림(스프라이트 · 전투 이펙트)을 data: 로 감싼 파일 — 파일로 열어도 머리색 치환이 되게 |
| `split_assets.py` | `game.html` 에 박힌 data: 그림 · 효과음을 `assets/` 로 빼고 경로(`assets/…?v=해시`)로 바꾼다. wrap 두 개가 먼저 부른다 |
| `heroschool.html` | `wrap.py` 가 만든 실행 파일 (테스트 기능 제외 · `assets/` 를 같이 씀) |
| `site/index.html` | `wrap_site.py` 가 만든 배포용 파일 (메타 태그·파비콘·OG 이미지 포함 · `../assets/` · `../bgm/` 을 씀) |
| `index.html` | 저장소 루트에서 `site/` 로 넘겨주는 페이지 (GitHub Pages 용) |
| `site/og.png` | 링크 미리보기 이미지 |
| `site/README.md` | Netlify / GitHub Pages / Vercel 배포 안내 |
| `wrap.py` | `game.html` → `heroschool.html` |
| `wrap_site.py` | `game.html` → `site/index.html` |
| `test.py` | Playwright 3년 회귀 테스트 (모든 화면 렌더 + 대회·원정·졸업까지 자동 진행) |
| `sprites/src/*.png` | 손으로 그린 직업별 스프라이트 시트 (128×128 · 6열 · 모션 5행) |
| `sprites/pack.py` | 시트들을 아틀라스 한 장으로 묶고 `game.html` 에 박을 JS 조각 생성 |
| `sprites/fx.py` | 전투 이펙트 시트 생성기 — 형태 6종을 도트로 찍는다 (`fx_*.png`) |
| `sprites/runtime.js` | 스프라이트 런타임 원본 (애니메이션 · 머리색 팔레트 치환) |
| `sprites/SPRITE_SPEC.md` | 스프라이트 시트 규격서 — 새 직업을 그릴 때 참고 |
| `og.html` | OG 이미지를 만들 때 쓴 페이지 |

---

## 고치고 빌드하기

`game.html` 만 고치면 됩니다. 전투 수치, 성장 계수, 카드 효과, 대회 보상은 모두
파일 상단의 데이터 블록에 상수로 모여 있습니다.

```bash
python wrap.py        # game.html → heroschool.html
python wrap_site.py   # game.html → site/index.html
```

두 스크립트 모두 먼저 `split_assets.py` 를 돌립니다. pack 스크립트(`sprites/pack.py` 등)가 `game.html` 에
data: 그림을 다시 넣어도 여기서 `assets/` 로 빠지고, 이름이 같은 파일은 덮어씁니다. 그림이 바뀌면 경로 뒤
`?v=` 값이 바뀌어 브라우저가 새로 받습니다. 쓰지 않게 된 그림 파일은 자동으로 지우지 않으니 가끔 정리하세요.

### 큰 화면 (화면 크기 자동 맞춤)

큰 모니터의 PC 에서는 게임 전체를 브라우저 확대처럼 키웁니다 — `game.html` 맨 앞 스크립트(UISCALE)가 같은 주소(`?hsf=배율`)를
iframe 으로 띄워 `transform: scale()` 로 키우는 '틀'이 됩니다. 배율은 창 크기에 맞추고(`min(폭 ÷ 1280, 높이 ÷ 870)`) 설정 › 화면 크기에서
100 ~ 200% 로 고를 수 있습니다. 폰 · 태블릿은 그대로입니다. 시험: `python3 tools/check_scale.py` (주소에 `?scale=off` 를 붙이면 틀 없이).

### 회귀 테스트

```bash
pip install playwright && playwright install chromium
python test.py
```

3년치를 자동으로 돌리면서 대회·원정·졸업·입학을 전부 거치고, 모든 탭을 한 번씩
렌더합니다. 출력의 `"err": []` 가 비어 있으면 통과입니다.

### 스프라이트 추가

1. `sprites/SPRITE_SPEC.md`의 v3 규격으로 **독립 256×256 프레임**을 제작합니다. 기준점은 (128,170), 안전 여백은 16px입니다.
2. `sprites/frames-v3/<직업id>/`의 개별 PNG와 `manifest.json`을 사용합니다. Aseprite 편집본을 수정했다면 `sprites/export_frames.lua`로 먼저 내보냅니다.
3. `python sprites/pack.py` — 검사를 통과한 프레임을 여백 있는 아틀라스로 묶고 `game.html`에 자동 반영합니다.
4. `python wrap.py`와 `python wrap_site.py`를 실행합니다.
5. `sprites/review.html`에서 모션, 좌우 반전, 기준점을 확인합니다. `node sprites/check_runtime.cjs`는 Playwright와 설치된 Edge로 렌더링 검사를 수행합니다.

기존 `sprites/src/` 캐릭터 시트는 보관용입니다. v3 manifest가 있으면 새 빌드는 기존 시트를 읽지 않습니다.

전투 이펙트는 `python sprites/fx.py` 로 다시 찍습니다. 형태 6종(참격·관통·타격·폭발·오라·회복)만
기준 색 하나로 그려두고, 게임에서 원소별로 색상·채도·명도를 돌려 씁니다. 스킬마다 `fx`·`el` 태그가
붙어 있어서 이펙트를 바꾸려면 그 태그만 고치면 됩니다.

복장 색은 피부와 머리 전용 색을 제외하여 검출합니다. 학생 ID 해시로 색상 24단 × 진하기
3단 중 하나를 골라 치환하며, 분리된 효과는 이 치환을 적용하지 않습니다.

---

## 배포

저장소를 GitHub Pages 로 켜면 (Settings → Pages → Deploy from a branch → `main` / `/ (root)`)
루트의 `index.html` 이 `site/` 로 넘겨주므로 `https://<아이디>.github.io/heroschool/` 에서 바로 열립니다.

영어로 링크를 나눌 때는 `https://<아이디>.github.io/heroschool/en/` — 맨 위 `en/index.html` 이 영어 미리보기(`site/og-en.png`)를 보여 주고
영어판(`site/?lang=en`)으로 넘겨줍니다. 게임 언어는 처음 접속할 때 브라우저 언어로 정하고, 설정에서 바꿀 수 있습니다 (`tools/i18n/README.md`).

`site/index.html` 은 저장소 맨 위의 `assets/` · `bgm/` 을 `../` 로 읽습니다. Netlify·Vercel 등 다른 호스팅에는
`site/` 만이 아니라 저장소 전체(최소 `site/` · `assets/` · `bgm/`)를 올려야 합니다.
자세한 절차는 [`site/README.md`](site/README.md) 에 정리해 뒀습니다.

---

## 라이선스

아직 정하지 않았습니다. 별도 표기가 없으면 저작권은 저자에게 있습니다.
