# 새로운 스킬 아이콘 리소스

정리일: 2026-10-15

16개 직업의 최신 스킬 아이콘 80종과 공용 정사각 테두리를 모은 패키지입니다. 원본 작업 폴더는 보존했습니다. 이 패키지 생성만으로 게임 코드나 기존 자산을 교체하지는 않았습니다.

## 폴더 구성

- icons/<직업>/: 적용 대상으로 선별한 최신 96×96 PNG. 직업당 5종.
- source/<작업 폴더>/: ImageGen 원화, 프롬프트, Aseprite 편집 파일, PNG, 확대 이미지, 미리보기, 제작 스크립트 및 개별 설명.
- frame/square-frame-96.aseprite: 공용 정사각 테두리 편집 파일.
- frame/square-frame-96.png: 중앙이 투명한 공용 테두리 PNG.
- manifest.json: 적용 대상 PNG와 Aseprite 파일 경로 목록. 모든 경로는 이 폴더 기준 상대 경로.

## 제작 규격

- 최종 아이콘은 96×96 픽셀, 투명 배경이며 테두리와 분리되어 있습니다.
- 프롬프트의 90% canvas fill을 기준으로 구성했습니다. Aseprite에서는 일반적으로 심볼의 긴 쪽을 86px(89.6%)에 맞추고 비율을 유지하여 중앙 배치했습니다. 비정사각형 심볼은 짧은 쪽 점유율이 다릅니다.
- 원화 생성 후 Aseprite에서 알파 경계 여백 정리, 최근접 축소와 배치, 레이어 정리 및 내보내기를 수행했습니다. 전체 픽셀을 수작업으로 다시 그린 방식은 아닙니다.
- RGB/RGBA 색상과 투명도를 유지하며 별도 36색 또는 256색 제한을 적용하지 않았습니다.

## 버전 선택

- 팔라딘, 소드맨, 프리스트, 암흑 사제는 최신 투명 배경 v2를 사용합니다.
- 나머지 11개 직업은 현재 최신 v1을 사용합니다.
- 마법검사의 삼연격은 triple-v2를 선택했습니다. 검이나 대상 없이 세 방향의 보라색 참격이 모이는 수정본입니다. 이전 triple 파일은 source 안에만 참고용으로 남아 있으며 적용 목록에서 제외했습니다.
- 아처는 화살 디자인을 통일한 작업 폴더를 포함했습니다.
- source 내부의 개별 README는 당시 제작 기록입니다. 실제 적용 파일 선택은 icons와 manifest.json을 기준으로 하세요.

## 테두리 적용

테두리는 앞서 성역 선포에서 분리한 공용 정사각 리소스를 그대로 포함했습니다. 새 테두리를 다시 그리지 않았습니다. 아이콘 위에 동일한 96×96 좌표와 크기로 겹쳐 표시하면 됩니다. Aseprite에서는 테두리를 별도 레이어로 가져와 표시 여부를 전환할 수 있습니다. 테두리 미사용 시 아이콘 PNG만 사용하세요.

픽셀 표현을 유지하려면 최근접 보간 또는 CSS image-rendering: pixelated를 사용하고, 가능하면 정수 배율로 표시하세요.

## 직업별 미리보기

- [archer — 5종](source/archer-square-v2/preview.html)
- [bard — 5종](source/bard-square-v1/preview.html)
- [darkpriest — 5종](source/darkpriest-square-v2/preview.html)
- [druid — 5종](source/druid-square-v1/preview.html)
- [enchanter — 5종](source/enchanter-square-v1/preview.html)
- [forcemage — 5종](source/forcemage-square-v1/preview.html)
- [gunner — 5종](source/gunner-square-v1/preview.html)
- [monk — 5종](source/monk-square-v1/preview.html)
- [ninja — 5종](source/ninja-square-v1/preview.html)
- [paladin — 5종](source/paladin-square-v2/preview.html)
- [priest — 5종](source/priest-square-v2/preview.html)
- [rogue — 5종](source/rogue-square-v1/preview.html)
- [spellsword — 5종](source/spellsword-square-v1/preview.html)
- [swordsman — 5종](source/swordsman-square-v2/preview.html)
- [timemage — 5종](source/timemage-square-v1/preview.html)
- [wizard — 5종](source/wizard-square-v1/preview.html)

## 검증

선별된 아이콘 80종의 96×96 크기와 대응 Aseprite 파일 존재를 확인했습니다. manifest.json에는 이전 삼연격이 포함되지 않습니다.


## 아처 v2 업데이트
아처 적용 PNG와 manifest를 v2로 갱신했습니다. 저격 자세는 치비 소드맨과 조준선, 매의 눈은 매의 얼굴, 유성 화살은 화살비로 재제작했습니다. 이전 v1은 source에 보존했습니다.

