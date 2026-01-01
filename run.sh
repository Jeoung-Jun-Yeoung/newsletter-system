#!/bin/bash
echo "🗑️  DB 초기화..."
rm -f newsletter.db

echo "🕷️  뉴스 크롤링 중..."
python -m app.crawler

echo "🧠  AI 요약 및 분석 중..."
python -m app.processor

echo "🎨  HTML 생성 중..."
python -m app.generator

echo "📮  이메일 발송 중..."
python -m app.sender

echo "✨  모든 작업 완료!"