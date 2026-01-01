# app/main.py

from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from .database import engine, get_db
from . import models

# -----------------------------------------------------------
# 1. DB 테이블 자동 생성
# -----------------------------------------------------------
# models.py에 정의된 Base 클래스를 상속받은 모든 클래스를 찾아서
# 실제 DB에 테이블이 없으면 생성(CREATE TABLE)합니다.
# 이미 테이블이 있다면 아무 일도 하지 않습니다.
models.Base.metadata.create_all(bind=engine)

# -----------------------------------------------------------
# 2. FastAPI 앱 인스턴스 생성
# -----------------------------------------------------------
app = FastAPI(
    title="Newsletter System",
    description="뉴스레터 자동화 시스템 API",
    version="0.1.0"
)

# -----------------------------------------------------------
# 3. 기본 라우터 (API 엔드포인트)
# -----------------------------------------------------------
@app.get("/")
def read_root():
    """
    서버 상태 확인용 루트 API
    """
    return {"status": "ok", "message": "뉴스레터 시스템이 정상 작동 중입니다."}

# 테스트용: 현재 DB에 저장된 구독자가 몇 명인지 확인하는 API
@app.get("/subscribers/count")
def read_subscribers_count(db: Session = Depends(get_db)):
    """
    Dependency Injection(get_db)을 통해 db 세션을 주입받습니다.
    """
    count = db.query(models.Subscriber).count()
    return {"count": count}