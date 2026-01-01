'''
FileName : crawler.py 
#2025-12-26 : 정준영
'''
import requests # 웹페이지 접속 처리를 위한 request import
from requests.exceptions import RequestException # RequestException 처리를 위한 선언
from bs4 import BeautifulSoup # BeatifulSoup 모듈 import https://pypi.org/project/beautifulsoup4/ 참고
from sqlalchemy.orm import Session # Python ORM 사용을 위한 sqlalchemy import
from app import models
from app.database import SessionLocal, engine
from app.models import CrawledArticle

def crawl_fashion_breaking_news():
    """
    Need: 하드코딩된 url에 접속하여 크롤링.

    Args:

    Returns:
        크롤링 요소들
    """

    models.Base.metadata.create_all(bind=engine)
    # model 파일에 정의된 table 정보를 바탕으로 engine에 연결된 DB 테이블 유/무에 따른 생성
    # DB 테이블이 없으면 생성

    print("🚀 [패션/뷰티] 실시간 뉴스 크롤링 시작...")


    # 요청정보 디폴트 세팅
    #url = "https://news.naver.com/breakingnews/section/103/376"
    url = "크롤링할 url"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language" : "ko-KR,ko;q=0.9,en;q=0.8",
        "Referer": "https://news.naver.com/"
    }
    # User-Agent : **“이 요청을 보낸 클라이언트가 누구인지(브라우저/앱/봇 등)”**를 서버에 알려주는 문자열.
    # Accept : 클라이언트가 어떤 MIME 타입을 받을 수 있는지 서버에 전달

    # request 실행
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except RequestException as exc:
        print(f"❌ 요청 실패: {exc}")
        return

    soup = BeautifulSoup(response.text, "html.parser")
    
    list_selectors = [
        "ul.sa_list_news > li.sa_item",
        "div.sa_list_news > ul > li.sa_item",
        "div.sa_list > ul > li.sa_item",
        "div.sa_list .sa_item",
        "li.sa_item",
        ".sa_item",
    ]

    matched_selector = None
    news_items = []
    for selector in list_selectors:
        news_items = soup.select(selector)
        if news_items:
            matched_selector = selector
            break

    print(f"🔎 매칭된 selector: {matched_selector} / items: {len(news_items)}")

    if not news_items:
        print(f"⚠️ 기사 리스트를 찾지 못했습니다. (HTML 길이: {len(response.text)})")
        return

    print(f"✅ 기사 아이템 {len(news_items)}개를 발견했습니다. DB 저장을 시작합니다...")

    db: Session = SessionLocal()
    count = 0

    try:
        for item in news_items:
            # 제목 및 링크 추출
            title_tag = item.select_one(".sa_text_title")
            if not title_tag:
                title_tag = item.select_one("a[href*='/article/']")
            
            if not title_tag:
                continue

            if title_tag.name == 'a':
                link = title_tag['href']
            else:
                parent_a = title_tag.find_parent('a')
                link = parent_a['href'] if parent_a else ""

            title = title_tag.get_text(strip=True)

            if link and link.startswith("/"):
                link = f"https://news.naver.com{link}"

            if not link:
                continue

            summary_tag = item.select_one(".sa_text_lede")
            summary = summary_tag.get_text(strip=True) if summary_tag else ""

            # source_tag는 모델에 저장할 곳이 없으므로 추출만 하고 저장은 안함
            # source_tag = item.select_one(".sa_text_press")
            # source = source_tag.get_text(strip=True) if source_tag else "Unknown"

            # 26일 수정 original_url -> link 로 변경
            exists = db.query(CrawledArticle).filter(CrawledArticle.link == link).first()
            if exists:
                continue

            # 26일 수정 모델에 있는 컬럼만 사용하여 ORM 처리
            new_article = CrawledArticle(
                link=link,          # original_url -> link
                title=title,
                summary=summary,
                content="",         # 현재 리스트에서는 본문이 없으므로 빈 문자열 처리
                status="PENDING"
            )

            db.add(new_article)
            count += 1
            print(f"  - 저장: {title[:20]}...")

        db.commit() # 한번에 커밋
        print(f"\n🎉 총 {count}개의 기사가 저장되었습니다.")

    except Exception as e:
        print(f"처리 중 에러 발생: {e} rollback 처리")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    crawl_fashion_breaking_news() # 함수 호출

#  Flow
# ┌──────────────────────────────────────────┐
# │ crawl_fashion_breaking_news() 호출        │
# └──────────────────────────────────────────┘
#                  │
#                  ▼
# ┌──────────────────────────────────────────┐
# │ 1) 테이블 생성 안전장치                   │
# │    models.Base.metadata.create_all(...)   │
# └──────────────────────────────────────────┘
#                  │
#                  ▼
# ┌──────────────────────────────────────────┐
# │ 2) 네이버 속보 URL / headers 준비         │
# └──────────────────────────────────────────┘
#                  │
#                  ▼
# ┌──────────────────────────────────────────┐
# │ 3) HTTP 요청                              │
# │    response = requests.get(..., timeout)  │
# │    response.raise_for_status()            │
# └──────────────────────────────────────────┘
#         │성공                         │실패(RequestException)
#         ▼                             ▼
# ┌───────────────────────────┐   ┌─────────────────────────┐
# │ 4) BeautifulSoup 파싱       │   │ "요청 실패" 출력 후 return│
# │    soup = BeautifulSoup(...)│   └─────────────────────────┘
# └───────────────────────────┘
#         │
#         ▼
# ┌──────────────────────────────────────────┐
# │ 5) 기사 리스트 선택자 탐색                │
# │    for selector in list_selectors:        │
# │        news_items = soup.select(selector) │
# │        있으면 break                        │
# └──────────────────────────────────────────┘
#         │있음                         │없음
#         ▼                             ▼
# ┌───────────────────────────┐   ┌──────────────────────────┐
# │ 6) DB 세션 생성             │   │ "기사 리스트 못 찾음" 출력│
# │    db = SessionLocal()      │   │ 후 return                 │
# └───────────────────────────┘   └──────────────────────────┘
#         │
#         ▼
# ┌──────────────────────────────────────────┐
# │ 7) 기사 아이템 루프                        │
# │    for item in news_items:                │
# │      - 제목/링크 추출                      │
# │      - 링크 정규화                         │
# │      - 요약 추출                           │
# │      - 중복 체크(select)                   │
# │      - 새 객체 생성 + db.add()             │
# └──────────────────────────────────────────┘
#         │
#         ▼
# ┌──────────────────────────────────────────┐
# │ 8) db.commit()                            │
# │    "총 N개 저장" 출력                     │
# └──────────────────────────────────────────┘
#         │
#         ▼
# ┌──────────────────────────────────────────┐
# │ 9) finally: db.close()                    │
# └──────────────────────────────────────────┘