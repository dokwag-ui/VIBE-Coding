# 자재단가 대시보드 GitHub Pages 배포 방법

## 준비된 파일

- `index.html`: GitHub Pages에서 열릴 자재단가 대시보드입니다.
- `.nojekyll`: GitHub Pages의 Jekyll 처리를 끄는 빈 파일입니다.

## 1. GitHub에서 새 저장소 만들기

1. GitHub에 로그인합니다.
2. 오른쪽 위 `+` 버튼을 누르고 `New repository`를 선택합니다.
3. 저장소 이름을 `material-price-dashboard`처럼 입력합니다.
4. `Public`을 선택합니다.
5. `Create repository`를 누릅니다.

## 2. 파일 업로드

1. 새 저장소 화면에서 `uploading an existing file`을 선택합니다.
2. 이 폴더 안의 `index.html`과 `.nojekyll`을 업로드합니다.
3. 커밋 메시지는 `Add material price dashboard`로 입력합니다.
4. `Commit changes`를 누릅니다.

## 3. GitHub Pages 켜기

1. 저장소의 `Settings` 탭으로 이동합니다.
2. 왼쪽 메뉴에서 `Pages`를 선택합니다.
3. `Build and deployment`의 `Source`를 `Deploy from a branch`로 선택합니다.
4. `Branch`는 `main`, 폴더는 `/root`를 선택하고 `Save`를 누릅니다.
5. 몇 분 후 Pages 화면에 게시 주소가 표시됩니다.

게시 주소는 보통 아래 형식입니다.

```text
https://<GitHub아이디>.github.io/<저장소이름>/
```

예를 들어 GitHub 아이디가 `myname`이고 저장소 이름이 `material-price-dashboard`이면 아래와 같습니다.

```text
https://myname.github.io/material-price-dashboard/
```

## 4. 수정 후 다시 올리기

대시보드를 수정한 뒤에는 새 `index.html` 파일을 같은 저장소에 다시 업로드하고 커밋하면 됩니다. GitHub Pages는 새 커밋을 기준으로 다시 배포합니다.

## 주의

이 방식은 비밀번호가 없는 공개 웹사이트입니다. 링크를 따로 배포하지 않아도 저장소나 Pages 주소를 아는 사람은 내용을 볼 수 있습니다.

또한 차트는 Chart.js CDN을 사용하므로, 접속 환경에서 인터넷 연결이 가능해야 차트가 정상 표시됩니다.
