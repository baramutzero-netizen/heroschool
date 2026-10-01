# 마법사 스타일리시 효과

캐릭터 애니메이션 시트와 분리된 단일 프레임 효과입니다.

- triple-circle.svg: 지팡이 앞에 선으로 그린 파랑·빨강·보라 3중 마법진. 실제 시전자가 마법사일 때 표시.
- fire-explosion.png: 화염 폭발의 각 피해 대상 복부에 표시. 내장 image_gen으로 제작한 투명 PNG. 프롬프트는 prompts.md.
- blizzard-back.svg / blizzard-front.svg: 서리 결계 대상 그룹 전체에 한 쌍의 눈보라. 위·아래 경계선 안에 배치.
- gravity-circle.svg / gravity-beam.svg: 중력 반전 대상 그룹 바닥의 마법진과 상단 경계선까지 이어진 반투명 보라색 빔. 바닥 마법진은 학생 뒤쪽, 빔은 학생과 다른 효과 앞쪽에 배치.

마력탄은 기존 대상 효과를 유지하고 새 직업 효과를 추가합니다. 유성 강림을 중력 반전으로 변경했으며 기존 전체 대상·피해 계수는 유지합니다. 스킬 ID wz_u 유지. 속성 표현은 arcane으로 변경.

선형 도형은 build_vectors.py에서 생성합니다. 런타임은 ../paladin/runtime.js. check.cjs에서 양 진영, 1·3·5 대상, 전수, 종료 및 취소를 검증합니다.

중력 빔은 마법진 외곽에 폭을 맞췄으며, gravity-foot.svg가 앞쪽 반원까지 빛을 이어줍니다. 빔과 반원 모두 최전경입니다.
