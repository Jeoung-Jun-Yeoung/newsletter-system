# app/ai_utils.py

import os
import time
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
client = None

if api_key:
    client = genai.Client(api_key=api_key)

def generate_with_retry(prompt, model_name="gemini-flash-latest", retries=3):
    """
    [유틸리티] 429(Too Many Requests) 에러 발생 시 대기 후 재시도하는 함수
    """
    if not client:
        return "API Key 누락"
    
    time.sleep(2)

    for attempt in range(retries):
        try:
            # API 호출
            response = client.models.generate_content(
                model=model_name,
                contents=prompt
            )
            # [수정 2] 경고 제거를 위한 안전한 텍스트 추출 로직
            # response.text 대신 parts를 직접 확인하여 텍스트만 합칩니다.
            extracted_text = ""
            if response.candidates and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    # 텍스트가 있는 파트만 가져옴 (thought_signature 등 제외)
                    if part.text:
                        extracted_text += part.text
            
            # 만약 위 방식으로 안 잡히면 기존 방식 시도 (비상용)
            if not extracted_text and response.text:
                extracted_text = response.text

            return extracted_text.strip()
            
        except Exception as e:
            error_msg = str(e)
            print(f"\n[ 에러 분석] 시도 {attempt+1}/{retries}")
            print(f" - 모델: {model_name}")
            print(f" - 메시지: {error_msg}")
            
            # 429 에러(Resource Exhausted)가 뜨면 대기
            if "429" in error_msg or "429" in str(e):
                print(" -> 구글 서버 과부하 또는 할당량 초과. 60초 대기합니다.")
                time.sleep(60) # 확실하게 1분 쉽니다.
            else:
                # 429가 아닌 다른 에러면 바로 중단 (불필요한 재시도 방지)
                return f"에러 발생: {e}"
    
    return "요약 실패 (재시도 초과)"

def generate_3_line_summary(full_text):
    if not full_text or len(full_text) < 50:
        return "본문 내용이 너무 짧아 요약할 수 없습니다."

    prompt = f"""
    너는 뉴스레터 에디터야. 아래 뉴스 기사 본문을 읽고, 바쁜 현대인을 위해 핵심 내용만 딱 3줄로 요약해줘.
    [작성 규칙]
    1. 한국어로 작성.
    2. 명사형 종결어미("~함") 사용.
    3. 각 줄의 시작은 적절한 이모지로 시작할 것.
    4. [중요] 각 문장은 반드시 줄바꿈(\\n)으로 구분해서 출력할 것. (한 줄로 붙이지 말 것)
    [기사 본문]
    {full_text[:1000]} 
    """
    
    # 여기서 위에서 만든 재시도 함수를 호출합니다.
    return generate_with_retry(prompt)

def generate_daily_insight(article_titles):
    if not article_titles:
        return "분석할 기사가 충분하지 않습니다."

    titles_text = "\n".join(f"- {t}" for t in article_titles)
    
    prompt = f"""
    너는 수석 애널리스트야. 아래 기사 제목들을 보고 '오늘의 인더스트리 브리핑'을 10줄 내외로 작성해줘.
    [형식]
    🌤️ 오늘의 분위기:
    🔍 주요 키워드:
    💡 인사이트:
    [기사 목록]
    {titles_text}
    """

    return generate_with_retry(prompt)