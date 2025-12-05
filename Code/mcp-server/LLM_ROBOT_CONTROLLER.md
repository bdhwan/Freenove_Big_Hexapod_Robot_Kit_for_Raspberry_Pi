# LLM 로봇 제어기 사용 가이드

LLM(Large Language Model)을 사용하여 자연어로 헥사포드 로봇을 제어하는 도구입니다.

## 개요

이 도구는 사용자의 자연어 명령을 LLM이 해석하여 MCP(Model Context Protocol)를 통해 로봇을 제어합니다. Ollama 또는 OpenAI API를 사용할 수 있습니다.

## 기능

- 🤖 자연어 명령 해석
- 📊 실시간 로봇 상태 조회
- ⚙️ MCP를 통한 로봇 제어
- 🔄 대화형 모드 지원
- 📝 명령줄 인자 모드 지원

## 설치

### 1. 의존성 설치

```bash
cd mcp-server
npm install
```

### 2. MCP 서버 빌드

```bash
npm run build
```

## 설정

### 환경 변수

다음 환경 변수를 설정할 수 있습니다:

#### 필수 설정

- `ROBOT_REST_API_URL`: 로봇 REST API URL (기본값: `http://localhost:8000`)

#### LLM 프로바이더 설정

**Ollama 사용 시:**
```bash
export LLM_PROVIDER=ollama
export LLM_MODEL=llama3.2  # 사용할 Ollama 모델명
export OLLAMA_BASE_URL=http://localhost:11434  # Ollama 서버 URL (선택사항)
```

**OpenAI 사용 시:**
```bash
export LLM_PROVIDER=openai
export OPENAI_API_KEY=your-api-key-here
export OPENAI_MODEL=gpt-4o-mini  # 사용할 모델 (선택사항, 기본값: gpt-4o-mini)
```

#### MCP 서버 설정 (선택사항)

```bash
export MCP_SERVER_COMMAND=node  # MCP 서버 실행 명령
export MCP_SERVER_PATH=./dist/mcp_server.js  # MCP 서버 경로
```

## 사용법

### 1. 대화형 모드

환경 변수를 설정한 후 실행:

```bash
# Ollama 사용
LLM_PROVIDER=ollama LLM_MODEL=llama3.2 npm run llm-controller

# OpenAI 사용
LLM_PROVIDER=openai OPENAI_API_KEY=your-key npm run llm-controller
```

대화형 모드에서는 자연어 명령을 입력하면 로봇이 제어됩니다.

**예시 명령:**
- "앞으로 이동해줘"
- "LED를 빨간색으로 바꿔줘"
- "거리를 측정해줘"
- "머리를 왼쪽으로 45도 회전시켜줘"
- "부저를 켜줘"
- "배터리 상태를 확인해줘"

종료하려면 `exit` 또는 `quit`를 입력하세요.

### 2. 명령줄 인자 모드

한 번의 명령만 실행하고 종료:

```bash
# Ollama 사용
LLM_PROVIDER=ollama LLM_MODEL=llama3.2 npm run llm-controller "앞으로 이동해줘"

# OpenAI 사용
LLM_PROVIDER=openai OPENAI_API_KEY=your-key npm run llm-controller "LED를 파란색으로 설정해줘"
```

## 작동 원리

1. **로봇 상태 조회**: 현재 로봇의 상태(배터리, 거리, 서보 상태 등)를 조회합니다.

2. **LLM 호출**: 사용자의 자연어 명령과 현재 로봇 상태를 LLM에 전달합니다.

3. **명령 해석**: LLM이 자연어 명령을 분석하여 적절한 로봇 제어 명령(JSON 형식)을 생성합니다.

4. **명령 실행**: 생성된 명령을 MCP를 통해 로봇에 전달하여 실행합니다.

## LLM 응답 형식

LLM은 다음 형식으로 응답해야 합니다:

**단일 명령:**
```json
{
  "tool": "robot_move",
  "args": {
    "mode": 1,
    "x": 10,
    "y": 0,
    "speed": 5,
    "angle": 0
  },
  "explanation": "앞으로 이동합니다"
}
```

**여러 명령:**
```json
{
  "commands": [
    {
      "tool": "robot_move",
      "args": {
        "mode": 1,
        "x": 10,
        "y": 0,
        "speed": 5,
        "angle": 0
      }
    },
    {
      "tool": "robot_set_led_color",
      "args": {
        "r": 255,
        "g": 0,
        "b": 0
      }
    }
  ],
  "explanation": "앞으로 이동하고 LED를 빨간색으로 설정합니다"
}
```

## 사용 가능한 로봇 제어 명령

- `robot_move`: 로봇 이동
- `robot_set_led_color`: LED 색상 설정
- `robot_set_led_mode`: LED 모드 설정
- `robot_set_head`: 머리 서보 제어
- `robot_set_attitude`: 자세 각도 설정
- `robot_set_position`: 몸체 위치 이동
- `robot_set_camera`: 카메라 뷰 제어
- `robot_set_buzzer`: 부저 제어
- `robot_set_balance`: 밸런스 기능 제어
- `robot_set_servo_power`: 서보 전원 제어
- `robot_get_ultrasonic`: 거리 측정
- `robot_get_power`: 배터리 전압 조회
- `robot_get_status`: 로봇 상태 조회

자세한 내용은 `REST_API_DOCUMENTATION.md`를 참조하세요.

## 문제 해결

### Ollama 연결 오류

```
Ollama API 오류: connect ECONNREFUSED
```

**해결 방법:**
1. Ollama가 실행 중인지 확인: `ollama list`
2. `OLLAMA_BASE_URL` 환경 변수가 올바른지 확인
3. Ollama 서버를 시작: `ollama serve`

### OpenAI API 오류

```
OpenAI API 오류: Invalid API key
```

**해결 방법:**
1. `OPENAI_API_KEY` 환경 변수가 올바르게 설정되었는지 확인
2. API 키가 유효한지 확인

### MCP 서버 연결 오류

```
MCP 클라이언트가 초기화되지 않았습니다
```

**해결 방법:**
1. MCP 서버가 빌드되었는지 확인: `npm run build`
2. `MCP_SERVER_PATH`가 올바른지 확인
3. 로봇 REST API 서버가 실행 중인지 확인

### 로봇 상태 조회 실패

**해결 방법:**
1. 로봇 REST API 서버가 실행 중인지 확인
2. `ROBOT_REST_API_URL` 환경 변수가 올바른지 확인
3. 네트워크 연결 확인

## 예시

### 예시 1: 기본 이동

```bash
LLM_PROVIDER=ollama LLM_MODEL=llama3.2 npm run llm-controller "앞으로 천천히 이동해줘"
```

### 예시 2: LED 제어

```bash
LLM_PROVIDER=ollama LLM_MODEL=llama3.2 npm run llm-controller "LED를 초록색으로 바꾸고 깜빡이게 해줘"
```

### 예시 3: 복합 명령

```bash
LLM_PROVIDER=ollama LLM_MODEL=llama3.2 npm run llm-controller "앞으로 이동하고 LED를 빨간색으로 바꾸고 부저를 켜줘"
```

### 예시 4: 상태 확인

```bash
LLM_PROVIDER=ollama LLM_MODEL=llama3.2 npm run llm-controller "배터리 상태와 거리를 확인해줘"
```

## 주의사항

1. **안전**: 로봇이 안전한 위치에 있는지 확인한 후 명령을 실행하세요.
2. **배터리**: 배터리 상태를 정기적으로 확인하세요.
3. **네트워크**: 로봇과의 네트워크 연결이 안정적인지 확인하세요.
4. **LLM 응답**: LLM이 생성한 명령이 올바른지 확인하세요. 잘못된 명령은 로봇에 손상을 줄 수 있습니다.

## 라이선스

MIT License

