import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from datetime import datetime
import time
from app.database import SessionLocal
from app.models import CrawledArticle, DailyInsight
from app.ai_utils import generate_3_line_summary, generate_daily_insight

def process_articles():
    db: Session = SessionLocal()
    
    # ====================================================
    # 1. 기사 상세 처리 (요약 안 된 것들 요약하기)
    # ====================================================
    articles = db.query(CrawledArticle).filter(
        CrawledArticle.status == "PENDING"
    ).all()

    print(f" 미처리 기사 {len(articles)}건의 요약 작업을 시작")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    if articles:
        total_count = len(articles)
        for index, article in enumerate(articles, 1):
            try:
                print(f"[{index}/{total_count}] Processing: {article.title[:15]}...")
                
                resp = requests.get(article.link, headers=headers)
                soup = BeautifulSoup(resp.text, "html.parser")
                
                content_tag = soup.select_one("#dic_area") or soup.select_one("#newsct_article")
                
                if content_tag:
                    for tag in content_tag.select(".img_desc, .byline, .f_share"):
                        tag.decompose()
                    
                    full_text = content_tag.get_text(strip=True)
                    
                    summary = generate_3_line_summary(full_text)
                    
                    article.summary = summary
                    article.status = "APPROVED" 
                    
                    print(f"  -> 요약 완료: {summary[:20]}...")
                else:
                    print("  -> 본문 태그를 찾을 수 없음 (Skip)")
                    article.status = "REJECTED" 
                
                db.commit()
                # 속도를 위해 대기시간 1초로 단축
                time.sleep(1)

            except Exception as e:
                print(f"  -> 에러: {e}")
                db.rollback()
    else:
        print(" 모든 기사가 이미 요약되어 있습니다.")

    # ====================================================
    # 2.오늘의 인사이트 생성 및 'DB 저장'
    # ====================================================
    print("\n [2단계] 오늘의 산업 인사이트를 생성합니다...")

    # 이미 처리된(APPROVED) 기사라도 '오늘' 생성된 거라면 모두 가져옵니다.
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    today_articles = db.query(CrawledArticle).filter(
        CrawledArticle.created_at >= today_start,
        CrawledArticle.summary.isnot(None)
    ).all()
    
    if not today_articles:
        print(" 분석할 오늘의 기사가 없습니다.")
        db.close()
        return

    titles = [article.title for article in today_articles]
    print(f" 총 {len(titles)}개의 기사 제목을 기반으로 분석 중...")

    # AI 분석 요청
    insight_text = generate_daily_insight(titles)
    
    print("="*50)
    print("[생성된 인사이트]")
    print(insight_text)
    print("="*50)

    # DB에 저장하는 로직
    new_insight = DailyInsight(
        content=insight_text
    )
    db.add(new_insight)
    db.commit()
    print(" DB 저장 완료 (테이블: daily_insights)")

    db.close()

if __name__ == "__main__":
    process_articles()