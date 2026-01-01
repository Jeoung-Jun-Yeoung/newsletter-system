# newsletter-system 📰✨  
뉴스사이트 **크롤링 → 본문 파싱 → AI 3줄 요약 → 오늘의 산업 인사이트 생성** 까지 자동으로 처리하는 뉴스레터 파이프라인.

> “면접 대비 관심 산업군 뉴스를 메일로 받아보고, 제미나이 요약 제공”

> 크롤링할 url에 따른 셀렉터 구조 파악하여 크롤러 파일 수정 요망.


## ✅ What it does

### 1) 기사 수집 (Crawler)
- 네이버 속보 섹션에서 기사 목록을 수집
- `link / title / lede(summary)`를 DB에 저장
- 상태값: `PENDING`

### 2) 본문 수집 + 3줄 요약 (Processor)
- `PENDING` 기사만 조회
- 기사 상세 페이지에 접속해 본문 컨테이너에서 텍스트 추출
- AI로 **3줄 요약 생성**
- 성공: `APPROVED`, 실패: `REJECTED`

### 3) 오늘의 산업 인사이트 생성 (Daily Insight)
- 오늘 생성된 기사들 중 요약이 있는 것 기반으로
- 제목들을 묶어 **오늘의 인사이트** 생성
- `daily_insights` 테이블에 저장


## 🗂️ Structure
```
newsletter-system/
├─ app/
│  ├─ crawler.py              # 기사 목록 수집 → DB 저장 (PENDING)
│  ├─ processor.py            # 본문 추출 + 3줄 요약 → APPROVED/REJECTED
│  ├─ ai_utils.py             # AI 요약/인사이트 생성 유틸
│  ├─ database.py             # SQLAlchemy 엔진/세션(SessionLocal)
│  ├─ models.py               # CrawledArticle, DailyInsight ORM 모델
│  └─ ...
├─ run.sh                     # 파이프라인 실행 스크립트
├─ requirements.txt
├─ newsletter_preview.html    # (옵션) 미리보기/결과 확인용
└─ README.md
```

## ⚙️ Tech Stack
```
> Python
> requests / BeautifulSoup (크롤링/HTML 파싱)
> SQLAlchemy (ORM)
> SQLite (기본 로컬 DB, 필요 시 PostgreSQL 교체 가능)
> LLM API (요약 + 인사이트 생성)
```

## 🚀 Quickstart

1. 설치
```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. 루트에 .env를 만들고 키/설정을 넣기.
```
GEMINI_API_KEY="키값"

이메일 발송 설정 (Gmail 기준)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER="Your's Gmail!"
SMTP_PASSWORD="지메일에서 패스워드 발급받은 값"

받는 사람 (테스트용)
TEST_RECEIVER="받을 사람의 이메일"
```

3. 실행
```
bash run.sh
```
