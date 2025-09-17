# YouTube Trending Streamlit App

간단한 YouTube Data API v3를 사용해 최신 인기 동영상을 보여주는 Streamlit 앱입니다.

- 한 페이지에 인기 동영상 최대 30개 표시 (슬라이더로 1~50 조정 가능)
- 썸네일, 제목, 채널명, 조회수(만/억 단위 축약) 표시
- 사이드바에 새로고침 버튼(캐시 초기화 후 재요청)
- 친화적인 에러 처리 및 도움말

## 파일 구성
- `streamlit_app.py` — 메인 앱 파일
- `requirements.txt` — 의존 패키지 목록
- `.env.example` — 로컬 개발용 환경변수 예시 파일 (복사하여 `.env`로 사용)
- `.streamlit/secrets.example.toml` — 배포/시크릿 예시 파일 (복사하여 `.streamlit/secrets.toml`로 사용)

## 요구사항
- Python 3.9+
- YouTube Data API v3 API Key (Google Cloud Console)

## 설치 및 실행 (로컬)
1) 가상환경(선택) 생성 및 활성화
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2) 의존성 설치
```bash
pip install -r requirements.txt
```

3) 설정 파일 준비 (둘 중 하나 또는 둘 다 가능)
- 로컬 개발: `.env.example`를 복사해 프로젝트 루트에 `.env`로 저장 후 값 설정
```
YOUTUBE_API_KEY=YOUR_YOUTUBE_DATA_API_KEY
REGION_CODE=KR
MAX_RESULTS=30
```
- 배포/로컬 시크릿: `.streamlit/secrets.example.toml`을 복사해 `.streamlit/secrets.toml`로 저장
```toml
YOUTUBE_API_KEY = "YOUR_YOUTUBE_DATA_API_KEY"
REGION_CODE = "KR"
MAX_RESULTS = "30"
```
앱은 설정을 `st.secrets`(있으면 우선) → `.env` 순서로 읽습니다.

4) 앱 실행
```bash
streamlit run streamlit_app.py
```

## 배포 (선택) — Streamlit Community Cloud
1) 이 프로젝트를 GitHub 저장소로 푸시합니다.
2) Streamlit Community Cloud에서 새 앱을 만들고 리포지토리를 연결합니다.
3) App settings의 "Secrets"에 아래 내용을 붙여넣습니다:
```toml
YOUTUBE_API_KEY = "YOUR_YOUTUBE_DATA_API_KEY"
REGION_CODE = "KR"
MAX_RESULTS = "30"
```
4) 배포하면 앱이 자동으로 `st.secrets`에서 값을 읽습니다.

## 사용법
- 사이드바에서 지역 코드와 결과 개수를 조정할 수 있습니다.
- "새로고침" 버튼을 누르면 캐시가 비워지고 API가 다시 호출됩니다.
- 각 항목의 제목을 클릭하면 해당 유튜브 동영상으로 이동합니다.

## 트러블슈팅
- API 키 미설정 오류: 로컬은 `.env`, 배포는 `.streamlit/secrets.toml` 또는 Cloud Secrets에 `YOUTUBE_API_KEY`를 설정하세요.
- HTTP 오류(쿼터 초과, 권한 등): API의 응답 메시지가 함께 표시됩니다. Google Cloud Console에서 쿼터를 확인하세요.
- 네트워크 오류/타임아웃: 네트워크 상태를 확인하고 다시 시도하세요.
- 결과가 비어 있음: 해당 지역/시간대에 인기 동영상 데이터가 없거나 API 제한일 수 있습니다. 지역 코드를 변경해 보세요.

## 참고
- 조회수 표기는 가독성을 위해 `만/억` 단위로 간략 표기합니다.
- YouTube API는 일일 쿼터 제한이 있습니다. 빈번한 새로고침은 쿼터를 소모합니다.

## 라이선스
이 프로젝트는 학습/데모 목적이며 별도의 라이선스 없이 제공합니다.
