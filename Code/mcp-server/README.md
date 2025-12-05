# Hexapod Robot MCP Server (Node.js)

이 문서는 헥사포드 로봇을 제어하기 위한 Node.js 기반 MCP (Model Context Protocol) 서버에 대한 설명입니다.

## 개요

MCP 서버는 AI 모델이 헥사포드 로봇을 직접 제어할 수 있도록 하는 인터페이스를 제공합니다. 이 서버는 원격 REST API를 호출하여 로봇을 제어합니다.

## 설치

### 1. 필수 패키지 설치

```bash
cd mcp-server
npm install
```

또는 yarn을 사용하는 경우:

```bash
cd mcp-server
yarn install
```

### 2. MCP 서버 설정

Cursor나 다른 MCP 호환 클라이언트에서 MCP 서버를 설정합니다.

#### Cursor 설정

Cursor의 설정 파일 (`~/.cursor/mcp.json` 또는 프로젝트별 설정)에 다음을 추가:

```json
{
  "mcpServers": {
    "hexapod-robot": {
      "command": "node",
      "args": [
        "--loader",
        "tsx/esm",
        "/path/to/Code/mcp-server/mcp_server.ts"
      ],
      "env": {
        "ROBOT_REST_API_URL": "http://raspberry-pi-ip:8000"
      }
    }
  }
}
```

**설정 항목 설명:**

- `command`: Node.js 실행 파일 경로 (일반적으로 `node`)
- `args`: 
  - `--loader tsx/esm`: TypeScript 파일을 직접 실행하기 위한 로더
  - 마지막 인자는 MCP 서버 TypeScript 파일의 절대 경로
- `env.ROBOT_REST_API_URL`: 원격 로봇의 REST API URL
  - 예: `http://192.168.1.100:8000`
  - 기본값: `http://localhost:8000`

**경로 수정 필요**: 
- MCP 서버 파일 경로를 실제 프로젝트 경로로 변경하세요.
- `ROBOT_REST_API_URL`을 실제 로봇 서버의 IP 주소와 포트로 변경하세요.

## 사용 가능한 도구 (Tools)

MCP 서버는 다음 도구들을 제공합니다:

### 1. `robot_move`
로봇을 이동시킵니다.

**파라미터:**
- `mode` (integer, 1-2): 이동 모드 (1=모션 모드, 2=보행 모드)
- `x` (integer, -35~35): X축 스텝 길이 (mm)
- `y` (integer, -35~35): Y축 스텝 길이 (mm)
- `speed` (integer, 2-10): 속도
- `angle` (integer, -10~10, optional): 이동 각도 (도)

**예시:**
```json
{
  "mode": 1,
  "x": 10,
  "y": 0,
  "speed": 5,
  "angle": 0
}
```

### 2. `robot_set_led_color`
LED 색상을 설정합니다.

**파라미터:**
- `r` (integer, 0-255): 빨강 값
- `g` (integer, 0-255): 초록 값
- `b` (integer, 0-255): 파랑 값

### 3. `robot_set_led_mode`
LED 모드를 설정합니다.

**파라미터:**
- `mode` (integer, 0-5): LED 모드
  - 0: 꺼짐
  - 1: 지정 색상
  - 2: 추적 모드
  - 3: 깜빡임 모드
  - 4: 호흡 모드
  - 5: 무지개 호흡 모드

### 4. `robot_set_head`
머리 서보를 제어합니다.

**파라미터:**
- `servo_id` (integer, 0-1): 서보 ID (0=수평, 1=수직)
- `angle` (integer, -90~90): 각도 (도)

### 5. `robot_set_attitude`
로봇의 자세 각도를 설정합니다.

**파라미터:**
- `roll` (integer, -15~15): 롤 각도 (도)
- `pitch` (integer, -15~15): 피치 각도 (도)
- `yaw` (integer, -15~15): 요 각도 (도)

### 6. `robot_set_position`
로봇의 몸체 위치를 이동시킵니다.

**파라미터:**
- `x` (integer, -40~40): X축 위치 오프셋 (mm)
- `y` (integer, -40~40): Y축 위치 오프셋 (mm)
- `z` (integer, -20~20): Z축 위치 오프셋 (mm)

### 7. `robot_set_camera`
카메라 뷰를 제어합니다.

**파라미터:**
- `x` (integer, -90~90): 수평 각도 (도)
- `y` (integer, -90~90): 수직 각도 (도)

### 8. `robot_set_buzzer`
부저를 켜거나 끕니다.

**파라미터:**
- `state` (boolean): 부저 상태 (true=켜기, false=끄기)

### 9. `robot_set_balance`
밸런스 기능을 활성화하거나 비활성화합니다.

**파라미터:**
- `enable` (boolean): 밸런스 기능 (true=활성화, false=비활성화)

### 10. `robot_set_servo_power`
서보 전원을 켜거나 끕니다.

**파라미터:**
- `power_on` (boolean): 서보 전원 (true=켜기, false=끄기)

### 11. `robot_get_ultrasonic`
초음파 센서로 거리를 측정합니다.

**파라미터:** 없음

**반환값:**
```json
{
  "command": "CMD_SONIC",
  "distance": 25.5
}
```

### 12. `robot_get_power`
배터리 전압을 조회합니다.

**파라미터:** 없음

**반환값:**
```json
{
  "command": "CMD_POWER",
  "load_battery": 7.2,
  "raspberry_pi_battery": 5.1
}
```

### 13. `robot_get_status`
로봇의 현재 상태를 조회합니다.

**파라미터:** 없음

**반환값:**
```json
{
  "status": "online",
  "servo_relaxed": false,
  "tcp_active": false
}
```

### 14. `robot_execute_sequence`
여러 명령을 순차적으로 실행합니다.

**파라미터:**
- `commands` (array): 실행할 명령어 배열

**예시:**
```json
{
  "commands": [
    {
      "id": "cmd1",
      "type": "move",
      "params": {
        "mode": 1,
        "x": 10,
        "y": 0,
        "speed": 5,
        "angle": 0
      }
    },
    {
      "id": "cmd2",
      "type": "wait",
      "params": {
        "seconds": 3
      }
    }
  ]
}
```

## 사용 예시

### AI 모델과의 대화 예시

```
사용자: 로봇을 앞으로 10mm 이동시켜줘

AI: 로봇을 앞으로 이동시키겠습니다.
    [robot_move 호출: mode=1, x=10, y=0, speed=5, angle=0]
    
사용자: LED를 빨간색으로 바꿔줘

AI: LED를 빨간색으로 설정하겠습니다.
    [robot_set_led_color 호출: r=255, g=0, b=0]
    
사용자: 거리를 측정해줘

AI: 초음파 센서로 거리를 측정하겠습니다.
    [robot_get_ultrasonic 호출]
    측정된 거리: 25.5cm
```

## 아키텍처

```
┌─────────────┐         HTTP/REST API         ┌──────────────┐
│   AI Model  │ ────────────────────────────> │  MCP Server │
│  (Cursor)   │                               │  (Node.js)  │
└─────────────┘                               └──────────────┘
                                                      │
                                                      │ HTTP Request
                                                      ▼
                                              ┌──────────────┐
                                              │ REST API     │
                                              │ (FastAPI)    │
                                              └──────────────┘
                                                      │
                                                      │ Hardware Control
                                                      ▼
                                              ┌──────────────┐
                                              │   Robot      │
                                              │  Hardware    │
                                              └──────────────┘
```

## 주의사항

1. **REST API URL 설정**: MCP 설정 파일의 `ROBOT_REST_API_URL` 환경 변수를 올바르게 설정해야 합니다.

2. **네트워크 연결**: MCP 서버가 실행되는 머신에서 로봇의 REST API 서버에 접근할 수 있어야 합니다.

3. **REST API 서버 실행**: 로봇에서 REST API 서버가 실행 중이어야 합니다. (`Server/main.py`를 통해 시작)

4. **포트 확인**: 기본 포트는 8000입니다. 다른 포트를 사용하는 경우 URL에 포트 번호를 포함하세요.

5. **방화벽 설정**: 로봇 서버의 방화벽에서 포트 8000이 열려있는지 확인하세요.

## 문제 해결

### MCP 서버가 시작되지 않는 경우

1. Node.js 버전 확인:
   ```bash
   node --version  # v18 이상 필요
   ```

2. 패키지 설치 확인:
   ```bash
   npm list @modelcontextprotocol/sdk axios
   ```

3. TypeScript 실행 확인:
   ```bash
   npx tsx mcp_server.ts
   ```

### REST API 연결 실패

1. REST API URL 확인:
   ```bash
   curl http://raspberry-pi-ip:8000/
   ```

2. 네트워크 연결 확인:
   ```bash
   ping raspberry-pi-ip
   ```

3. 로봇 서버 상태 확인:
   ```bash
   curl http://raspberry-pi-ip:8000/api/status
   ```

### 도구 실행이 실패하는 경우

1. REST API 서버 로그 확인:
   - 로봇 서버의 콘솔 출력 확인
   - 에러 메시지 확인

2. 요청 형식 확인:
   - MCP 서버는 REST API 문서에 따라 요청을 보냅니다
   - REST API 문서: `Server/REST_API_DOCUMENTATION.md`

## 개발

### 로컬 개발

```bash
# 개발 모드로 실행 (파일 변경 시 자동 재시작)
npm run dev

# 일반 실행
npm start
```

### 빌드

```bash
npm run build
```

빌드된 파일은 `dist/` 디렉토리에 생성됩니다.

## 추가 정보

- REST API 문서: `../Server/REST_API_DOCUMENTATION.md`
- 통신 프로토콜: `../robot_control_communication_protocol.md`
- MCP SDK 문서: https://modelcontextprotocol.io/

