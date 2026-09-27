# 공통 아바타 샘플 v2

설정 → 애니메이션 테스트 → 테스트 열기. 기존 직업 스프라이트와 전투에는 영향을 주지 않는 별도 샘플입니다.
Aseprite 1.3.18.5에서 Lua로 픽셀과 레이어/셀을 작성했습니다. 이미지 생성 모델은 사용하지 않았습니다.
거너의 256px 프레임과 약 90~100px 캐릭터 높이, 큰 머리 비율을 참고한 간단한 구조 검증용 디자인입니다. 기존 거너 아트를 분해한 완성품은 아닙니다.

## 파일
- common-avatar-sample.aseprite: 실제 편집 원본, 36프레임, 13개 그림 레이어 + 숨김/잠금 기준선
- sample-sheet.png / sample-sheet.json: Aseprite 통합 내보내기
- 부위명.png: 같은 좌표/프레임으로 내보낸 각 레이어
- manifest.json: 공통 규격
- preview.html: 이미지가 포함된 단독 테스트 화면
- build.lua: Aseprite 생성 및 내보내기
- pack.py: 테스트 화면과 게임 설정 항목에 포함

## 공통 규칙
256×256 셀, 6열, 전체 1536×1536. trim 금지. 발 기준점 (128,171), 머리 (130,100), 앞손 기본 (147,141).
대기 0–2 / 공격 3–6 / 피격 7–9 / 쓰러짐 10–12 / 승리 13–15 / 한손 휘두르기 16–19 / 양손 휘두르기 20–23 / 총쏘기 24–27 / 활쏘기 28–31 / 눕기 32–35.
프레임 시간은 JSON에 저장. 모든 동작은 준비·중간·마무리 중심의 3~4프레임입니다.
표시 순서: cape_back, hair_back, body, pants, shoes, top, arm_back, head, face, arm_front, gloves, hair_front, hat.
공통 body/head/arm은 유지하고 나머지를 교체합니다. 눈+입은 face 하나로 묶었습니다.
장비 하나도 전체 36프레임의 같은 좌표로 그려야 합니다. 동작별로 다른 프레임 수를 쓰지 않습니다.
가이드 레이어는 렌더에 포함하지 않습니다. 원본의 동작 태그를 유지하세요.
현재 모자는 헤어를 누르지 않는 액세서리 유형입니다. 큰 모자/후드 추가 시 눌린 헤어 및 숨김 규칙을 추가해야 합니다.
현재 상의는 민소매 샘플입니다. 긴소매/복잡한 무기는 front/back/over-head 레이어를 추가해 가림 순서를 정의해야 합니다.
한손/양손/총/활 동작은 공통 몸체 포즈로 제공하며 무기 그림은 아직 장착하지 않았습니다. 걷기와 후면 방향은 포함하지 않았습니다.

## 확인한 공식 가이드와 반영점
공식 PSD 파일을 그대로 사용하는 MSW 업로드 파일이 아니라, 구조를 참고한 이 게임 전용 Aseprite 규격입니다.
- [기본 개념](https://maplestoryworlds-creators.nexon.com/ko/docs/?postId=588): 몸/머리/팔 구분, 기준점 및 레이어 순서 → 공통 베이스와 동일 좌표 채택.
- [망토](https://maplestoryworlds-creators.nexon.com/ko/docs?postId=585): 몸 뒤/앞 표현 구분 → 뒤 망토 슬롯.
- [하의](https://maplestoryworlds-creators.nexon.com/ko/docs?postId=584), [신발](https://maplestoryworlds-creators.nexon.com/ko/docs?postId=583): 발 기준으로 매 동작에 맞춰 제작 → 기준선 고정.
- [상의](https://maplestoryworlds-creators.nexon.com/ko/docs?postId=586), [장갑](https://maplestoryworlds-creators.nexon.com/ko/docs?postId=587): 팔/손의 앞뒤 및 동작별 겹침이 중요 → 앞팔/뒤팔 분리, 같은 모션 좌표로 장갑 변환.
- [헤어](https://maplestoryworlds-creators.nexon.com/ko/docs?postId=657): 앞/뒤/눌린 헤어 구분 → 앞뒤 레이어 연동 토글, 눌린 헤어는 후속 장비 규칙으로 명시.
- [모자](https://maplestoryworlds-creators.nexon.com/ko/docs?postId=592): 유형별 헤어 숨김 → 샘플은 액세서리 유형.
- [한벌옷](https://maplestoryworlds-creators.nexon.com/ko/docs?postId=1042): 상하 연결과 소매 가림 순서 → 확장 시 상하의 슬롯 동시 대체.
- [등록/미리보기](https://maplestoryworlds-creators.nexon.com/ko/docs?postId=590): 동작 선택/프레임 확인 → 테스트 화면에 재생, 프레임 이동, 레이어 장착 확인 추가.

## 재생성
프로젝트 루트에서 Aseprite -b --script sprites/avatar-lab/build.lua 실행 후 Python으로 sprites/avatar-lab/pack.py, wrap.py, wrap_site.py 순으로 실행합니다.
주의: build.lua는 생성기이므로 원본 수작업 수정 후 다시 실행하면 샘플 파일을 덮어씁니다. 수작업 버전은 별도 이름으로 보관하고 내보낸 PNG/JSON만 갱신하세요.

장갑 수정: 화면 좌표에 따른 조건부 회전 대신 좌우 손의 원본 픽셀을 미리 분리한 후 해당 팔과 동일한 회전을 적용합니다. 모든 프레임에서 두 개를 넘는 장갑 덩어리가 없는지 검사했습니다.
