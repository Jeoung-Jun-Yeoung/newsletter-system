import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
TEST_RECEIVER = os.getenv("TEST_RECEIVER")

def send_newsletter():
    print("📮 이메일 발송을 준비합니다...")

    # 1. HTML 파일 읽기
    file_path = "newsletter_preview.html"
    if not os.path.exists(file_path):
        print(f"❌ '{file_path}' 파일이 없습니다. app.generator를 먼저 실행하세요.")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    # 2. 이메일 객체 생성
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "📢 [Weekly Fashion] 이번 주 핫 트렌드 뉴스레터"
    msg["From"] = SMTP_USER
    msg["To"] = TEST_RECEIVER

    # 3. 본문 탑재 (HTML)
    # plain text 버전도 넣으면 좋지만, 지금은 HTML만 넣습니다.
    part = MIMEText(html_content, "html")
    msg.attach(part)

    try:
        # 4. SMTP 서버 연결 및 발송
        print(f"🔗 SMTP 서버({SMTP_SERVER})에 연결 중...")
        
        # 보안 연결 (TLS)
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls() 
        
        # 로그인
        server.login(SMTP_USER, SMTP_PASSWORD)
        
        # 전송
        server.sendmail(SMTP_USER, TEST_RECEIVER, msg.as_string())
        server.quit()
        
        print(f"✅ 발송 성공! '{TEST_RECEIVER}' 메일함을 확인해보세요.")

    except Exception as e:
        print(f"❌ 발송 실패: {e}")
        print("💡 팁: Gmail을 쓴다면 '앱 비밀번호'를 사용했는지 확인하세요.")

if __name__ == "__main__":
    send_newsletter()