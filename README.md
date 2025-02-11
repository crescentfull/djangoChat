# DjangoChat프로그램 

## 프로젝트 개요
이 프로젝트는 [실시간 웹채팅 시스템을 구현하는 것을 통해 네트워크 프로그래밍의 기본 개념과 WebSoket, 비동기 프로그래밍 숙달]을 목표로 합니다.

## 기능
- 기능 1: [기능 설명]
- 기능 2: [기능 설명]
- 기능 3: [기능 설명]

## 설치 방법

### 필수 조건
- Python 3.10
- 가상환경 설정을 위한 `venv` 또는 `virtualenv`

### 설치 단계
1. 저장소를 클론합니다.
   ```bash
   git clone https://github.com/사용자명/프로젝트명.git
   cd 프로젝트명
   ```

2. 가상환경을 생성하고 활성화합니다.
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows의 경우 `venv\Scripts\activate`
   ```

3. 필요한 패키지를 설치합니다.
   ```bash
   pip install -r requirements.txt
   ```

4. 데이터베이스를 마이그레이션합니다.
   ```bash
   python manage.py migrate
   ```

5. 개발 서버를 시작합니다.
   ```bash
   python manage.py runserver
   ```

6. 웹 브라우저에서 `http://localhost:8000`을 엽니다.

## 사용 방법
1. 애플리케이션을 시작합니다.
   ```bash
   python manage.py runserver
   ```
2. 웹 브라우저에서 `http://localhost:8000`을 엽니다.

## 기여 방법
1. 이 저장소를 포크합니다.
2. 새로운 브랜치를 만듭니다.
   ```bash
   git checkout -b feature/새로운기능
   ```
3. 변경 사항을 커밋합니다.
   ```bash
   git commit -m 'feat: 새로운 기능 추가'
   git commit -m 'fix: 버그 수정'
   git commit -m 'docs: 문서 추가'
   git commit -m 'refactor: 코드 리팩토링'
   git commit -m 'style: 코드 스타일 수정'
   git commit -m 'test: 테스트 추가'
   git commit -m 'chore: 기타 변경 사항'
   ```
4. 브랜치에 푸시합니다.
   ```bash
   git push origin feature/새로운기능
   ```
5. 풀 리퀘스트를 생성합니다.

## 라이선스
이 프로젝트는 MIT 라이선스를 따릅니다. 자세한 내용은 `LICENSE` 파일을 참조하세요. 