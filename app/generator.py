import os
import sys
from jinja2 import Template
from mjml import mjml2html
from datetime import datetime
from app.database import SessionLocal, engine
from app import models
from app.models import CrawledArticle, DailyInsight

# DB 테이블 확인
models.Base.metadata.create_all(bind=engine)

def create_preview_html():
    output_filename = "newsletter_preview.html"

    # 1. 기존 파일 삭제 (Clean Start)
    if os.path.exists(output_filename):
        try:
            os.remove(output_filename)
            print(f"🗑️ 기존 '{output_filename}' 파일을 삭제했습니다.")
        except Exception as e:
            print(f" 기존 파일 삭제 실패 (파일이 열려있을 수 있음): {e}")

    print("뉴스레터 HTML 생성을 시작합니다...")
    
    db = SessionLocal()
    
    # [공통] 오늘 날짜 기준점 (오늘 00시 00분 00초)
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    # =========================================================
    # 2. 기사 가져오기
    # =========================================================
    articles = db.query(CrawledArticle).filter(
        CrawledArticle.summary.isnot(None),       # 요약이 완료된 것
        CrawledArticle.created_at >= today_start  # 오늘 생성된 것만
    ).order_by(CrawledArticle.created_at.desc()).all() # .limit(5) 제거함. 다 해보기
    
    if not articles:
        print("오늘 요약된 기사가 없습니다. app.processor를 먼저 실행해주세요.")
        db.close()
        return
    else:
        print(f"오늘 요약된 기사 총 {len(articles)}개를 모두 뉴스레터에 담습니다.")

    # 3. 오늘의 인사이트 가져오기
    insight_entry = db.query(DailyInsight).filter(
        DailyInsight.created_at >= today_start
    ).order_by(DailyInsight.created_at.desc()).first()
    
    if insight_entry:
        final_insight = insight_entry.content
        print(f"오늘의 AI 인사이트를 반영합니다.")
    else:
        final_insight = "아직 오늘의 AI 분석 결과가 도착하지 않았습니다."
        print("주의: 오늘 생성된 인사이트가 없습니다.")

    # 4. MJML 템플릿 로딩
    template_path = os.path.join(os.path.dirname(__file__), "templates", "newsletter.mjml")
    
    if not os.path.exists(template_path):
        print(f"❌ 템플릿 파일을 찾을 수 없습니다: {template_path}")
        db.close()
        return

    with open(template_path, "r", encoding="utf-8") as f:
        mjml_template = f.read()

    # 5. Jinja2 렌더링
    template = Template(mjml_template)
    rendered_mjml = template.render(
        today_date=datetime.now().strftime("%Y년 %m월 %d일"),
        insight=final_insight, 
        articles=articles  # 제한 없이 모든 기사가 들어갑니다
    )

    # 6. MJML -> HTML 변환
    print("MJML을 HTML로 변환 중...")
    result = mjml2html(rendered_mjml)
    
    html_content = ""
    if hasattr(result, 'html'):
        html_content = result.html
    elif isinstance(result, dict) and 'html' in result:
        html_content = result['html']
    else:
        html_content = str(result)

    # 7. 파일 저장
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    print(f"성공! '{output_filename}' 파일이 새로 생성되었습니다.")
    
    db.close()

if __name__ == "__main__":
    create_preview_html()