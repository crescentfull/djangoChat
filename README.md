# DjangoChat프로그램 

## 프로젝트 개요
이 프로젝트는 [실시간 웹채팅 시스템을 구현하는 것을 통해 네트워크 프로그래밍의 기본 개념과 WebSoket, 비동기 프로그래밍 숙달]을 목표로 합니다.

## 기능
- 기능 1: 채팅방 목록 조회, 생성, 삭제
- 기능 2: 회원가입, 본인 프로필 조회
- 기능 3: 실시간 채팅

## 설치 방법

### 필수 조건
- Python 3.10.X
- 가상환경 설정을 위한 `venv` 또는 `virtualenv`

### 설치 단계
1. 저장소를 클론합니다.
   ```bash
   git clone https://github.com/crescentfull/djangoChat.git
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

5. sample.env 파일의 환경변수를 설정하고 .env로 파일명을 변경하여줍니다.
    유저 간 채팅을 위해 redis 서버 설치가 필요합니다.
    [Redis 공식 홈페이지](https://redis.io/)

    ```bash
    #django secret_KEY
    SECRET_KEY=""

    #redis
    # 하나의 환경변수로 HOST/PORT/PASSWORD 
    CHANNEL_LAYER_REDIS_URL="redis://[PASSWORD]@[HOST]:[PORT]"


    # 허용할 호스트
    ALLOWED_HOSTS="*"
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

## 추가 기능 보완 (진행 중)
* 채팅 로비에서 유저수 노출 ✅
* 채팅방에서 마지막 유저가 나가면 채팅방 자동 삭제 ✅
* 각 메세지에 시각 노출 
* 채팅방에 새로운 유저가 들어오면, 최근 메세지 5개 출력
* 메세지 수정/삭제
* 메세지 입력 중에 "{유저명}님이 메세지 입력 중입니다." 메세지
* 메세지 리액션 : 좋아요.
* 파일/사진 업로드
* 채팅방에 비밀번호 설정하기
* 입장신청하고, 허용한 유저만 입장하기
* 유저 로그아웃 시에, 참여 중인 채팅방에서 자동 나가기


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
이 프로젝트는 인프런의 [파이썬/장고로 웹채팅 서비스 만들기 (Feat. Channels)] 강의를 참고하여 만들었습니다.
