# app/models.py

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from .database import Base


# ========================================================
# 1. 구독자 테이블 (Subscribers)
# ========================================================
class Subscriber(Base):
    __tablename__ = "subscribers" 

    # index 생성 : 처리건수 늘어날수록 효과적.
    id = Column(Integer, primary_key=True, index=True)
    
    # unique=True: 중복된 이메일이 들어오면 에러를 발생시켜 막습니다.
    email = Column(String, unique=True, index=True, nullable=False)
    
    name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True) # 구독 취소 시 False로 변경
    
    # server_default=func.now(): 데이터 생성 시 현재 시간이 자동으로 들어갑니다.
    subscribed_at = Column(DateTime(timezone=True), server_default=func.now())
    unsubscribed_at = Column(DateTime(timezone=True), nullable=True)


# ========================================================
# 2. 크롤링 기사 테이블 (Crawled Articles)
# ========================================================
class CrawledArticle(Base):
    __tablename__ = "crawled_articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    link = Column(String, unique=True, index=True)  # 'original_url' 대신 'link'로 통일
    content = Column(Text)
    summary = Column(Text, nullable=True) # AI가 요약한 내용
    status = Column(String, default="PENDING") # PENDING, DONE, ERROR
    created_at = Column(DateTime, default=datetime.now)


# ========================================================
# 3. 뉴스레터 테이블 (Newsletters) - 1회 발송분
# ========================================================
class Newsletter(Base):
    __tablename__ = "newsletters"

    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String, nullable=False)  # 이메일 제목
    html_content = Column(Text, nullable=True) # 발송된 최종 HTML 원본 저장
    scheduled_at = Column(DateTime(timezone=True), nullable=True) # 예약 발송 시간
    
    # 상태값: DRAFT(작성중), SENDING(발송중), SENT(완료), FAILED(실패)
    status = Column(String, default="DRAFT")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # [관계 설정]
    # NewsletterItem 테이블과 1:N 관계입니다.
    # back_populates는 반대쪽 모델에 있는 변수명과 일치해야 합니다.
    items = relationship("NewsletterItem", back_populates="newsletter")


# ========================================================
# 4. 뉴스레터 구성 아이템 (Mapping Table)
# ========================================================
# 하나의 뉴스레터에는 여러 기사가 포함될 수 있습니다. (N:M 해소용 중간 테이블)
class NewsletterItem(Base):
    __tablename__ = "newsletter_items"

    id = Column(Integer, primary_key=True, index=True)
    
    # ForeignKey: 다른 테이블의 id를 참조합니다.
    newsletter_id = Column(Integer, ForeignKey("newsletters.id"))
    article_id = Column(Integer, ForeignKey("crawled_articles.id"))
    
    sort_order = Column(Integer, default=0) # 뉴스레터 안에서 몇 번째로 보여줄지 순서

    # 관계 설정 (객체처럼 접근하기 위함)
    # 예: newsletter_item.article.title 처럼 접근 가능
    newsletter = relationship("Newsletter", back_populates="items")
    article = relationship("CrawledArticle")


# ========================================================
# 5. 발송 로그 (Send Logs)
# ========================================================
class SendLog(Base):
    __tablename__ = "send_logs"

    id = Column(Integer, primary_key=True, index=True)
    newsletter_id = Column(Integer, ForeignKey("newsletters.id"))
    subscriber_id = Column(Integer, ForeignKey("subscribers.id"))
    
    status = Column(String) # SENT, BOUNCED(반송), OPENED(수신확인)
    message_id = Column(String, nullable=True) # 이메일 서비스(AWS SES 등)에서 주는 고유 ID
    sent_at = Column(DateTime(timezone=True), server_default=func.now())


# ========================================================
# 6. 데일리 인사이트
# ========================================================
class DailyInsight(Base):
    __tablename__ = "daily_insights"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text) # AI가 분석한 오늘의 트렌드
    created_at = Column(DateTime(timezone=True), server_default=func.now())