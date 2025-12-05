#!/bin/bash
# LLM 로봇 제어기 사용 예시

# 환경 변수 설정 (필요에 따라 수정)
export ROBOT_REST_API_URL="http://localhost:8000"

# Ollama 사용 예시
echo "=== Ollama를 사용한 예시 ==="
export LLM_PROVIDER=ollama
export LLM_MODEL=llama3.2

# 예시 1: 앞으로 이동
echo "예시 1: 앞으로 이동"
npm run llm-controller "앞으로 이동해줘"

sleep 2

# 예시 2: LED 제어
echo "예시 2: LED를 빨간색으로 설정"
npm run llm-controller "LED를 빨간색으로 바꿔줘"

sleep 2

# 예시 3: 거리 측정
echo "예시 3: 거리 측정"
npm run llm-controller "앞에 있는 물체까지의 거리를 측정해줘"

sleep 2

# 예시 4: 복합 명령
echo "예시 4: 복합 명령"
npm run llm-controller "앞으로 이동하고 LED를 파란색으로 바꾸고 부저를 켜줘"

# OpenAI 사용 예시 (주석 해제하여 사용)
# echo "=== OpenAI를 사용한 예시 ==="
# export LLM_PROVIDER=openai
# export OPENAI_API_KEY="your-api-key-here"
# export OPENAI_MODEL="gpt-4o-mini"
# 
# npm run llm-controller "앞으로 이동해줘"

