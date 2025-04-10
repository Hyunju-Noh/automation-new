# Whatap-e2e

[![Python](https://img.shields.io/badge/Python-3.x-blue)](https://www.python.org/)

## 개요

이 프로젝트는 Playwright와 Python을 사용한 웹 서비스 자동화 테스트 코드 레포지토리입니다. 
이 리포지토리에는 웹 애플리케이션의 UI 테스트를 자동화하는 스크립트가 포함되어 있습니다. (Teatrail 연동 예정)

## 기능

- Playwright를 사용한 웹 애플리케이션의 UI 자동화 테스트
- 최신 테스트 구조 및 전략 적용
- Page Object Model(POM) 설계
- 테스트 데이터/유틸리티 모듈화
- TestRail과 연동하여 테스트 케이스 결과 보고 (예정)

## 브랜치 전략
|브랜치|설명|
|---|---|
|main|최신 구조의 정리된 자동화 코드|
|legacy-code|초기 레거시 코드 보관용 브랜치|

## 요구 사항

- Python 3.x
- `playwright` 라이브러리
- `pytest` 라이브러리

## 설치 방법

1. Python 3.x 설치

2. 프로젝트 클론

   ```bash
   git clone https://github.com/whatap/whatap-e2e.git
   cd whatap-e2e

3. 가상 환경 생성 및 활성화

   ```bash
   python -m venv myenv
   source myenv/bin/activate  
   # Windows에서는 `venv\Scripts\activate`
   ```
4. 필수 패키지 설치
   ```bash
   pip install -r requirements.txt
   ```
5. Playwright 브라우저 설치
   ```bash
   playwright install
   ```
6. 파일 구조
   ```bash
   .
   ├── src/                   # Git 추적 포함 디렉토리
   │   ├── data               # 테스트에 필요한 데이터 (로그인 정보, 프로젝트 정보 등)
   │   ├── reports            # 테스트 실행 후 생성된 결과 리포트
   │   ├── pages              # 테스트에서 사용하는 모든 UI 페이지 객체를 정의하는 디렉토리
   │   ├── testcases          # 작성된 테스트 케이스를 포함하는 디렉토리
   │   └── util_tools         # 유틸리티 함수 디렉토리
   ├── venv                   # 가상 환경 파일
   ├── requirements.txt       # 프로젝트에 필요한 패키지 목록 및 버전
   ├── .gitignore             # Git이 추적하지 않을 파일 및 디렉토리 목록
   ├── .cz.toml               # Commitizen 설정 파일 (커밋 메시지 규칙 관리)
   └── README.md              # 프로젝트 설명 문서

   ```
