# Whatap-e2e

[![Python](https://img.shields.io/badge/Python-3.x-blue)](https://www.python.org/)

## 개요

이 프로젝트는 Playwright와 TestRail을 사용한 웹 서비스 자동화 테스트 코드 레포지토리입니다. 이 리포지토리에는 웹 애플리케이션의 UI 테스트를 자동화하는 스크립트와 TestRail 연동을 포함한 테스트 케이스 관리 기능이 포함되어 있습니다.

## 기능

- Playwright를 사용한 웹 애플리케이션의 UI 자동화 테스트
- TestRail과 연동하여 테스트 케이스 결과 보고

## 요구 사항

- Python 3.x
- `playwright` 라이브러리
- `pytest` 라이브러리
- `testrail-api` 또는 `pytastrail` 라이브러리 (TestRail API 사용)

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