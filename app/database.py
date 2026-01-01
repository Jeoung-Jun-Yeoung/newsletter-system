# app/database.py

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# -----------------------------------------------------------
# 1. 데이터베이스 주소 설정
# -----------------------------------------------------------
# 지금은 개발 편의를 위해 파일 기반의 'SQLite'를 사용.
# 현재 폴더에 'newsletter.db'라는 파일이 생성되어 DB 역할
# 나중에 배포할 때는 PostgreSQL 주소로 변경 해야함. 현재는 로컬에서만 사용
SQLALCHEMY_DATABASE_URL = "sqlite:///./newsletter.db"

# -----------------------------------------------------------
# 2. 엔진(Engine) 생성
# -----------------------------------------------------------
# 엔진은 DB와의 실제 연결을 담당하는 핵심 객체.
# connect_args={"check_same_thread": False} 옵션은 SQLite에서만 필요
# (한 스레드에서 만든 커넥션을 다른 스레드에서 공유할 수 있게 허용하는 옵션)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# -----------------------------------------------------------
# 3. 세션 공장(SessionLocal) 생성
# -----------------------------------------------------------
# DB 세션을 생성해주는 클래스입니다.
# autocommit=False: 데이터를 변경하고 commit()을 명시적으로 호출해야 저장. 롤백 혹은 타임아웃 대비용
# 대고객용도는 아님
# autoflush=False: 세션에 변경사항이 있어도 명시적으로 호출하기 전까지는 DB에 반영하지 않음
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# -----------------------------------------------------------
# 4. Base 클래스 생성
# -----------------------------------------------------------
# 앞으로 만들 모든 모델(테이블)은 이 Base 클래스를 상속. 필수임.
# SQLAlchemy가 이 Base를 상속받은 클래스들을 추적하여 테이블을 생성함.
Base = declarative_base()

# -----------------------------------------------------------
# 5. DB 세션 의존성 함수 (Dependency)
# -----------------------------------------------------------
# FastAPI의 강력한 기능인 Dependency Injection(의존성 주입)에 사용
# API 요청이 들어오면 db 세션을 만들고, 처리가 끝나면 자동으로 닫기(close).
def get_db():
    db = SessionLocal()
    try:
        yield db      # 요청 처리 중에 이 db 세션을 사용하고,
    finally:
        db.close()    # 요청 처리가 끝나면 반드시 세션을 닫아 리소스를 반환해야함.