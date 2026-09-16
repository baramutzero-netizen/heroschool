# 용사 학원 운영기 — 배포 안내

`index.html` 한 개로 완결된 정적 사이트입니다. 빌드 과정도, 서버도 필요 없습니다.
같은 폴더의 `og.png`는 링크를 채팅이나 SNS에 붙였을 때 뜨는 미리보기 이미지입니다.

## Netlify Drop — 가장 빠름 (1분)

1. https://app.netlify.com/drop 접속 (로그인 없이도 임시 배포 가능, 계정이 있으면 영구 유지)
2. 이 `site` 폴더를 통째로 드래그해서 놓기
3. 바로 `https://무작위이름.netlify.app` 주소가 생성됩니다
4. Site settings → Change site name 에서 원하는 이름으로 변경 가능

수정본을 올릴 때는 같은 자리에 폴더를 다시 드래그하면 됩니다.

## GitHub Pages — 주소를 오래 유지하고 싶을 때

1. GitHub에서 새 저장소 생성 (예: `heroschool`, Public)
2. 이 폴더의 `index.html`과 `og.png`를 저장소 루트에 업로드
   - 웹에서 할 경우: 저장소 첫 화면 → "uploading an existing file" → 두 파일 드래그 → Commit
3. 저장소 Settings → Pages → Source를 `Deploy from a branch`, 브랜치 `main` / 폴더 `/ (root)` 로 지정 후 Save
4. 1~2분 뒤 `https://<아이디>.github.io/heroschool/` 에서 열립니다

이후 파일을 교체해 커밋하면 자동으로 반영됩니다.

## Vercel

1. https://vercel.com 에서 Add New → Project
2. 위 GitHub 저장소를 선택하고 Framework Preset은 `Other`로 두고 Deploy
3. 빌드 설정은 비워두면 됩니다 (정적 파일 그대로 서빙)

## 알아둘 점

- 세이브는 방문자의 브라우저(localStorage)에 저장됩니다. 서버가 없으므로 기기·브라우저마다 진행이 따로 갑니다.
- 폰트는 Google Fonts에서 불러옵니다. 네트워크가 막힌 환경에서는 시스템 폰트로 대체되어 표시만 조금 달라집니다.
- 파일을 열어보면 전투 수치, 성장 계수, 대회 보상이 모두 상단 데이터 블록에 상수로 모여 있습니다. 밸런스를 바꾸려면 그 부분만 고치면 됩니다.
