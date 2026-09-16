# 용사 학원 운영기

쓰러진 아버지의 용사 학원을 물려받아, 학생 세 명으로 시작해 3년간 학원을 키우는
한국어 웹 운영 시뮬레이션입니다. 라이브러리 없이 바닐라 JS·HTML·CSS로 만들었고,
**HTML 파일 하나로 완결**됩니다. 서버도 빌드 도구도 필요 없습니다.

👉 **[바로 플레이](site/index.html)** — 또는 `heroschool.html` 을 브라우저로 열기

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
| `heroschool.html` | `wrap.py` 가 만든 단독 실행 파일 |
| `site/index.html` | `wrap_site.py` 가 만든 배포용 파일 (메타 태그·파비콘·OG 이미지 포함) |
| `site/og.png` | 링크 미리보기 이미지 |
| `site/README.md` | Netlify / GitHub Pages / Vercel 배포 안내 |
| `wrap.py` | `game.html` → `heroschool.html` |
| `wrap_site.py` | `game.html` → `site/index.html` |
| `test.py` | Playwright 3년 회귀 테스트 (모든 화면 렌더 + 대회·원정·졸업까지 자동 진행) |
| `sprites/src/*.png` | 손으로 그린 직업별 스프라이트 시트 (128×128 · 6열 · 모션 5행) |
| `sprites/pack.py` | 시트들을 아틀라스 한 장으로 묶고 `game.html` 에 박을 JS 조각 생성 |
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

### 회귀 테스트

```bash
pip install playwright && playwright install chromium
python test.py
```

3년치를 자동으로 돌리면서 대회·원정·졸업·입학을 전부 거치고, 모든 탭을 한 번씩
렌더합니다. 출력의 `"err": []` 가 비어 있으면 통과입니다.

### 스프라이트 추가

1. `sprites/SPRITE_SPEC.md` 규격대로 시트를 그려 `sprites/src/<직업id>.png` 로 저장
2. `python sprites/pack.py` — 아틀라스와 `sprites/sprites.js` 가 만들어집니다
3. `sprites.js` 내용을 `game.html` 의 `const SPR_CELL=...` 로 시작하는 블록과 교체
4. `python wrap.py && python wrap_site.py`

머리색은 자동으로 검출됩니다 — 캐릭터 상단 42% 안에 몰려 있으면서 색상이 서로 가까운
색들만 머리로 잡고, 학생 ID 해시로 색상 24단 × 진하기 3단 중 하나를 골라 치환합니다.

---

## 배포

`site/` 폴더를 정적 호스팅에 그대로 올리면 됩니다. 자세한 절차는
[`site/README.md`](site/README.md) 에 정리해 뒀습니다.

---

## 라이선스

아직 정하지 않았습니다. 별도 표기가 없으면 저작권은 저자에게 있습니다.
