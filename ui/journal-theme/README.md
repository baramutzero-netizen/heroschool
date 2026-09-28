# 일지 UI 컨셉

설정 → UI 컨셉 → 기본 / 일지에서 즉시 전환합니다. 기본값은 기본이며 선택은 기존 브라우저 설정 `heroschool_pref_v1.uiConcept`에 저장됩니다. 게임 세이브는 바꾸지 않습니다.

`theme.css`는 `html[data-ui-concept="journal"]`에만 적용됩니다. 회흑색 배경 위에 독립적인 양피지 패널, 책 표지 색상의 강조 버튼, 금속 느낌 초상화 테두리를 표시합니다. 기존 진행 페이지 책 테스트 모드와 별개이며 배포 빌드에도 포함됩니다. 이미지 파일 없이 CSS 질감으로 화면 크기에 대응합니다.

수정 후 실행:

```sh
python ui/journal-theme/pack.py
python wrap.py
python wrap_site.py
```

`pack.py`는 game.html의 JOURNAL_THEME 블록만 교체합니다. wrap 과정의 리소스 분리 방식은 그대로 유지됩니다.

`check.cjs`: Edge/Playwright, PC 1440px·휴대폰 390px에서 전환·저장·복귀, 주요 페이지 가로 넘침, JS 오류 검사. 테스트는 별도 브라우저 컨텍스트를 사용합니다. 스크린샷 촬영 전에 초기 로딩 화면을 종료하고 테스트 학원을 생성합니다.
