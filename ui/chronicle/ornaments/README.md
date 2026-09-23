# 양피지 장식과 훈련 삽화

내장 image_gen 사용. 사용자 제공 문장/훈련 아이콘/편지 그림을 참고해 투명 배경 에셋 제작. source.png는 3×3 아틀라스, letter-source.png는 편지 원본. prepare-ornaments.py에서 연결된 개체 단위로 분리해 WebP로 최적화한다.

## 아틀라스 프롬프트

Create a single transparent production UI icon atlas, exactly 3 columns by 3 rows of equally sized square cells, one fully separate small ornament per cell with 20% empty transparent margin. Reference1 navy gold heraldic shield style, reference2 small hand-drawn training icon style. Warm brown pen outlines, restrained muted watercolor fill, ivory antique gold/navy, like illustrations in a handwritten parchment academy journal, NOT glossy modern emoji. True alpha transparent background, no paper rectangles, no checkerboard, no text, no grid lines. Row1 left: ornate navy heraldic shield with gold tree and tiny crown; middle: simple two-leaf olive sprig diagonal upward; right: small tied golden coin purse. Row2 left: antique metal dumbbell; middle: stack of three old books; right: circular archery target with one arrow. Row3 left: two crossed short swords; middle: steaming cream ceramic cup; right: little rolled expedition map with brass compass. Each icon centered inside its cell, no touching or crossing cell boundaries. Readable at small scale, matching attached vintage journal drawings. Equal size cells, clean transparent isolated objects.

## 편지 프롬프트

Extract and redraw this small parchment letter and envelope as ONE high quality isolated game UI decoration with true transparent background. Preserve its composition: weathered warm beige envelope diagonally behind a small handwritten note, navy gold heraldic tree shield printed on envelope corner, delicate paper creases, slightly rotated rectangle paper. Brown Korean handwriting EXACT '언제나,\n더 좋은 용사를 위해.\n— 교장으로서.' Keep whole letter/envelope visible, transparent padding all sides, same cozy hand-painted fantasy journal style. No extra background table, no book edge, no white rectangular backing, no other objects, no other text. Intended as a small decoration overlapping the lower left edge of an open book.

## 폰트

Google Fonts 공식 저장소의 Nanum Pen Script / Nanum Brush Script. 라이선스 원문은 ../fonts/OFL-NanumPenScript.txt와 OFL-NanumBrushScript.txt에 보관. 브라우저에서 외부 요청 없이 사용하도록 WOFF2로 변환해 게임에 포함. 목업의 생성형 글자와 동일한 폰트는 아니며 실제 동적 UI에서 비슷한 손글씨 분위기를 구현한다. 주요 제목은 Nanum Pen Script의 굵은 스타일, 날짜/메모/훈련 문구는 일반 스타일. 조작 버튼과 학생 수치는 기존 가독성 유지.

출처: https://github.com/google/fonts/tree/main/ofl/nanumpenscript 및 https://github.com/google/fonts/tree/main/ofl/nanumbrushscript
