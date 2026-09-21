# 원정 몬스터 14종

## 구성
- 학원 지하 수련장: 목검 훈련병, 마력 표적구
- 안개 낀 옛 성터: 안개 창병, 안개 사냥개, 길 잃은 등불
- 무너진 종탑: 금 간 종게, 태엽 까마귀, 종탑 성가석
- 소금 바다의 균열: 염정 소라게, 심해 염수해파리, 침몰한 잠수병
- 용사의 무덤: 맹세의 방패병, 묘실 기록관, 유검의 잔영

앞 구간은 해당 원정의 새 몬스터를 순환하고 마지막 구간은 기존 주인으로 유지한다. 각 몬스터는 기본 공격, 일반 스킬 2개, 필살기 1개를 가진다. 상세 수치와 설명은 runtime.js와 preview.html에서 확인한다. 학생 직업 선택 목록에는 추가하지 않는다.

## 제작 및 프롬프트 구성
내장 image_gen 도구로 생성. 기존 mon_dummy / mon_wraith 그림을 스타일 참고로 사용했다. 다음 공통 조건과 원정별 피사체로 투명 스프라이트 원본 5장을 제작했다.

공통: detailed crisp fantasy RPG pixel-art monster sprite atlas, transparent alpha background, horizontal isolated square cells, entire bodies/weapons/effects visible, generous 12% margins, left-facing three-quarter view, aligned feet at 85%, no text, no scenery. Match existing game monster sprite style.

- d1: two cells; wooden practice automaton with wooden sword, round shield and blue/gold ribbon; floating brass and crystal target orb.
- d2: three cells; fog spear sentry with shield; spectral fog hound; haunted lantern with maroon hanging strips.
- d3: three cells; cracked bronze bell crawler with spider legs; copper clockwork crow with gears; stone choir gargoyle holding a handbell.
- d4: three cells; salt crystal crab with orange claws; purple/teal deep-sea eye jellyfish; drowned knight in corroded green diving armor carrying a trident.
- d5: three cells; hollow oath sentinel in navy/gold armor with tower shield; ivory/gold spectral scribe with open book and quill; floating ancient greatsword spirit surrounded by three shards.

## 파일과 재생
- d1-source.png ~ d5-source.png: 생성 원본 보관.
- mon_*.png: 각각 256×256 RGBA. 하단 기준점 y=236, 최대 몸체 영역 220×220.
- pack.py: 연결된 몸체 단위로 분리하며 떨어진 작은 효과는 가까운 몸체에 귀속. 동일 폭으로 자르지 않아 무기/효과가 옆 칸으로 잘리는 일을 방지한다. 투명 여백 보존. 기존 5종을 유지하면서 MON_IMG와 새 원정 정의를 game.html에 삽입한다.
- 기존 몬스터의 정지 스프라이트 기반 대기 부유·공격 이동·피격·쓰러짐 연출을 사용한다. 별도 프레임 애니메이션 시트는 아니다.
- overview.jpg: 전체 그림 모음.
- preview.html: 실제 게임 정의에서 불러오는 몬스터/스킬 도감. 저장 데이터와 분리.

반영 순서: pack.py → 루트 wrap.py → wrap_site.py.
검사: check.cjs (14종 이미지 디코드, 19종 등장 경로, 학생 목록 분리, 56개 기술 전투 실행 및 유한 HP).
