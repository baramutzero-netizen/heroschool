# 영웅의 기상 작업물 안내

정리일: 2026-10-15  
보관 위치: D:/heroschool/tools/herospirit/  
원본 작업 위치: C:/Users/mjkki/Documents/Codex/2026-09-16/aesprite/outputs/

## 목적과 구현 범위

의식 저하 상태에서 피격했을 때, 즉시 기절할 가능성과 별개로 '영웅의 기상'이 발동하는 게임 구상을 위한 캐릭터 포즈·효과·전투 연출 시안이다. 발동 확률, 기절과 기상의 판정 순서, HP 회복, 버프, 상태 해제는 아직 확정하거나 구현하지 않았다.

현재 HTML은 발동 상황을 강제로 재생하는 독립 목업이다. 실제 게임의 전투 로직이나 에셋 참조를 변경하는 설치 작업은 포함하지 않는다.

## 제작 공통 컨셉

- 기존 게임 전투 스프라이트를 외형·복장·무기 참고로 사용했다.
- 큰 머리와 짧은 몸·팔다리의 2.5등신 치비 픽셀아트를 프롬프트 기준으로 삼았다. 생성 이미지의 비율과 픽셀 크기를 수작업으로 완전히 규격화한 상태는 아니다.
- 피격 후 다시 일어서는 의지와 클래스별 개성을 포즈에 반영했다.
- 내장 ImageGen으로 캐릭터와 후광을 각각 생성했다. 이번 영웅의 기상 원화는 Aseprite 최종 전투 시트가 아니다.
- 캐릭터 원화, 뒤쪽 후광 이미지, 목업 코드로 그리는 앞쪽 입자를 분리했다.
- 투명 배경을 요청했지만, 생성 결과의 알파·반투명 가장자리·잔여 광채는 게임 적용 전에 확인해야 한다.

## 폴더와 파일

클래스와 버전별 폴더 이름을 그대로 보존했다. 20개 폴더, 126개 작업 파일을 복사했으며 원본과 복사본의 SHA-256 일치를 확인했다. manifest.json에는 복사한 파일의 경로 구성, 크기, 해시가 있다. 이 안내문과 manifest.json은 126개에 포함되지 않는다.

일반적인 폴더 구성:

- resolve-character.png: 채택된 캐릭터 생성 원화. 최종 게임 해상도용 스프라이트가 아니다.
- resolve-aura.png: 별도로 생성한 뒤쪽 후광 원화.
- *-existing.png: 게임의 기존 전투 시트를 PNG로 추출한 참고 자료. 신규 영웅의 기상 이미지와 구분한다.
- generation-prompts.txt: 캐릭터·효과 생성 프롬프트.
- preview.html: 발동 연출 확인용 HTML.
- battle-background.webp: 목업 배경.

생성 원화는 리사이즈하거나 색상을 재변환하지 않고 작업 폴더의 파일 그대로 복사했다. 채택되지 않은 ImageGen 중간 결과 전체를 수집한 것은 아니다.

팔라딘은 초기 실험 파일명이 다르다. 현재 preview.html은 resolve-character-v3-original-prompt.png와 resolve-aura-master.png를 사용한다. resolve-character-master.png, resolve-character-v2.png, preview-v1.html, preview-v2.html 및 각 프롬프트도 보존했다.

## 클래스별 시안

각 링크는 해당 폴더의 목업이다. 최신 번호는 가장 최근 시안이며 최종 채택을 뜻하지 않는다.

| 클래스 / 버전 | 포즈와 연출 방향 |
| --- | --- |
| [팔라딘](heroic-resolve-paladin/preview.html) | 시리즈 기준이 된 기상 포즈. 초기안·비율 수정안·원래 프롬프트 기반 수정안 보존 |
| [암흑 사제](heroic-resolve-darkpriest/preview.html) | 암흑 사제 외형을 유지한 영웅의 기상 |
| [프리스트](heroic-resolve-priest/preview.html) | 프리스트 외형을 유지한 영웅의 기상 |
| [드루이드 V1](heroic-resolve-druid/preview.html) | 손을 펼쳐 자연의 힘을 부르는 결의 |
| [드루이드 V2](heroic-resolve-druid-v2/preview.html) | 두 눈을 감고 가슴 앞에 손을 모아 영창에 집중 |
| [소드맨](heroic-resolve-sword/preview.html) | 짧은 검을 세우고 원형 방패를 든 자세 |
| [몽크 V1](heroic-resolve-monk/preview.html) | 두 주먹을 쥐고 자세를 바로잡는 결의 |
| [몽크 V2](heroic-resolve-monk-v2/preview.html) | 싸움이 즐거운 듯 활짝 웃으며 무릎을 들고 주먹을 내지르는 도약 |
| [닌자](heroic-resolve-ninja/preview.html) | 쿠나이를 낮게 쥐고 다른 손으로 인을 맺음 |
| [바드](heroic-resolve-bard/preview.html) | 눈을 감고 하프를 연주하며 선율을 타는 포즈, 가벼운 흔들림 |
| [아처](heroic-resolve-archer/preview.html) | 한쪽 눈을 감고 시위를 뺨까지 당긴 정밀 조준 |
| [인챈터](heroic-resolve-enchanter/preview.html) | 열린 마도서를 받치고 손을 뻗어 마력을 집중 |
| [타임 매지션](heroic-resolve-timemage/preview.html) | 앞으로 가속하는 도약, 시계 궤도와 속도 궤적 |
| [거너](heroic-resolve-gunner/preview.html) | 뒤로 피하며 팔을 교차하고 쌍권총을 겨눔 |
| [마법검사 V1](heroic-resolve-spellsword/preview.html) | 한쪽 눈을 감고 검을 가슴 앞에 세운 서약 자세 |
| [마법검사 V2](heroic-resolve-spellsword-v2/preview.html) | 동일한 서약 컨셉의 재제작 |
| [마법검사 V3](heroic-resolve-spellsword-v3/preview.html) | 살짝 즐거운 미소로 검을 앞으로 내지름 |
| [로그](heroic-resolve-rogue/preview.html) | 낮게 웅크려 쌍단검을 쥐고 그림자로 사라지기 직전, 이동·페이드 |
| [배틀메이지](heroic-resolve-forcemage/preview.html) | '다시 달려볼까!' 하는 밝은 미소와 경쾌한 무릎 들기 |
| [마법사](heroic-resolve-wizard/preview.html) | 모자챙을 들어 눈빛을 드러내고 지팡이를 세운 자신감 |

## 목업 확인 방법

각 폴더의 preview.html을 브라우저에서 연다. 이미지 파일은 HTML과 같은 폴더에 유지해야 한다. 기본 화면은 발동 포즈를 정지해서 보여준다.

- 발동 연출 재생: 피격부터 복귀까지 재생.
- 발동 포즈 보기: 기상 장면 정지.
- 기존 전투 포즈: 참고 전투 시트 표시.
- 뒤쪽 후광 / 앞쪽 입자 / 주변 암전 / 발동 순간 확대: 요소별 표시 비교.
- 반복 재생: 전체 시퀀스 반복.
- 현재 장면 PNG 저장: 브라우저 로컬 파일 보안 정책에 따라 제한될 수 있다.

공통 시간 흐름은 대략 대기 0~480ms, 피격 480~850ms, 기상 850~3750ms, 이후 전투 복귀이며 전체 약 4.8초다. 클래스별 이동·도약·소멸은 HTML에서 단일 원화를 이동하거나 투명도를 바꾸는 방식이다. 손발이 프레임별로 움직이는 완성 애니메이션 시트는 아니다.

캔버스는 960×540이며 생성 이미지는 목업에서 축소하여 그린다. 다수 목업은 원화를 256×256 중간 캔버스로 축소하고, 일부는 종횡비 유지 처리를 추가했다. 따라서 원화 파일을 최종 제작의 기준으로 삼고 목업 캡처를 원본으로 쓰지 않는 편이 좋다.

## 게임 적용 전에 남은 작업

1. 클래스별 채택 버전을 정한다.
2. 실제 게임의 셀 크기·캐릭터 크기·발 기준점에 맞춰 원화를 정리한다. 2.5등신과 128×128은 프롬프트 방향이며 현재 생성 PNG가 그 규격이라는 의미는 아니다.
3. 외곽 픽셀 밀도, 무기와 손의 형태, 알파 가장자리, 여백을 검수한다. 원화를 보존한 채 Aseprite 작업본과 내보내기 파일을 별도로 만든다.
4. 캐릭터·후광·앞쪽 효과의 표시 범위 및 발동·복귀 프레임을 정리한다.
5. 실제 전투에서 피격·기절·기상 판정 우선순위와 효과를 구현한다.
6. 화면 경계 잘림, 인접 프레임 노출, 클래스별 크기 차이, 중복 발동과 전투 복귀를 확인한다.

특히 마법검사 V3의 캐릭터 원화에는 주변 광채가 남아 있다. 완전히 분리된 투명 스프라이트로 간주하지 말고 배경·광채 정리를 거친 후 사용해야 한다. 다른 원화도 투명 배경 요청만으로 검수가 끝난 것은 아니다.

## 보관 정책

기존 작업 폴더는 변경하지 않고 복사했다. 이 폴더는 원화·프롬프트·목업 보관용이며 게임이 자동으로 읽는 에셋 등록 경로가 아니다. 원본 작업 폴더와 자동 동기화되지 않으므로 이후 수정 시 어떤 사본을 갱신했는지 기록한다.


## 이후 작업 보관 규칙 (2026-10-15)
사용자 요청에 따라 앞으로 영웅의 기상 신규·수정 작업은 작업 공간뿐 아니라 이 herospirit 폴더에도 원화·프롬프트·목업·설명 문서를 함께 추가한다. 기존 버전을 보존하고 새 버전 폴더를 사용한다.

추가: [팔라딘 V4](heroic-resolve-paladin-v4/README.md) — 두 손에 든 흰빛을 아련하게 내려다보는 포즈. [목업](heroic-resolve-paladin-v4/preview.html). 초기 보관은 20개 폴더였으며 현재 21개다.


추가: [마법검사 V4](heroic-resolve-spellsword-v4/README.md) — 눈을 감고 한 팔과 검지를 높이 세워 묵상하는 열혈의 축적. [목업](heroic-resolve-spellsword-v4/preview.html). 현재 22개 작업 폴더.


추가: [마법검사 V5](heroic-resolve-spellsword-v5/README.md) — 묵상·검지 상승 포즈 유지, 브라운 가죽 장화로 변경. [목업](heroic-resolve-spellsword-v5/preview.html).


추가: [마법검사 V6](heroic-resolve-spellsword-v6/README.md) — 손가락 다섯 개 조건으로 손 모양 수정, 묵상 포즈와 브라운 장화 유지. [목업](heroic-resolve-spellsword-v6/preview.html).


추가: [전투 연출 목업 V1 — 정신력 시험](heroic-resolve-battle-v1/README.md) — 의식 저하 선 아래 피격 때 기절 · 영웅의 기상 판정, 시험 줌인과 네 가지 기상 이름 · 대사. [목업](heroic-resolve-battle-v1/heroic_resolve_mockup.html). 원본과 만드는 스크립트는 D:/heroschool/mockups/heroic-resolve/.


추가: [전투 연출 목업 V2 — 정신력 시험](heroic-resolve-battle-v2/README.md) — V1 을 고친 판: 기상 원화 · 후광 1.5배 (V1 은 1.8배), 기상은 학생마다 한 전투에 한 번 · 기상 확률은 체력과 상관없음 확정. [목업](heroic-resolve-battle-v2/heroic_resolve_mockup.html). V1 은 그대로 둔다.


추가: [전투 연출 목업 V3 — 정신력 시험](heroic-resolve-battle-v3/README.md) — V2 를 고친 판: 기상 원화 · 후광을 아래로 (캐릭터 가운데 전투판 높이의 43% → 59% · 발끝이 아래 글 띠 뒤로 조금 숨는다 · 사용자 그림대로). [목업](heroic-resolve-battle-v3/heroic_resolve_mockup.html). V1 · V2 는 그대로 둔다.


추가: [전투 연출 목업 V4 — 정신력 시험](heroic-resolve-battle-v4/README.md) — V3 를 고친 판: 기절한 학생에게도 같은 편 동료 반응 대사 (성격 아홉 × 셋 = 27 · 한국어 · 영어 · lines.json 의 reactFaint). [목업](heroic-resolve-battle-v4/heroic_resolve_mockup.html). V1 ~ V3 는 그대로 둔다.


추가: [게임 적용 V1 — 기술 선택 · 정신력 시험](heroic-resolve-game-v1/README.md) — 스타일리시 전투 체크포인트 ①(기술 선택 · 설정 '기술 선택 연출') · ②(정신력 시험 · 영웅의 기상 — 규칙 8)를 게임에 넣은 판. 원화는 직업별 최신 판을 WebP 품질 90 으로(assets/heroic/ 32장), 효과음 열한 개(bgm/pick_* · test_*), 대사 한국어 · 영어 · 일본어([lines.json](heroic-resolve-game-v1/lines.json)) · 게임 스크린숏 일곱. 목업 V1 ~ V4 는 그대로 둔다.


추가: [게임 적용 V2 — 기절 두 번 쓰러짐 고침 · 전투 대사와 정신력 시험](heroic-resolve-game-v2/README.md) — 시험에서 기절한 학생이 대사 뒤 한 번 더 쓰러지던 것을 고침 · 같은 빌드의 전투 대사(첫 치명타를 맞고 버틴 대사는 기절 · 기상이 나온 차례엔 없음 · 줌아웃 뒤 치명타 대사 → 기상 · 기절 대사 순). V1 은 그대로 둔다.


추가: [게임 적용 V3 — 후광이 돌지 않게](heroic-resolve-game-v3/README.md) — 기상 장면의 후광이 14초에 한 바퀴씩 돌던 것을 뺐다 (원화 방향 그대로 · 나타나며 커지기와 밝기 숨쉬기는 그대로). V1 · V2 · 목업은 그대로 둔다.

