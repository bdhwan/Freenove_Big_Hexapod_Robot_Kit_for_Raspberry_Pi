# Sequential Command API - curl Examples

순차 명령 실행 API (`/api/commands/sequence`)를 사용하는 curl 예제 모음입니다.

## 기본 사용법

```bash
curl -X POST http://localhost:8000/api/commands/sequence \
  -H "Content-Type: application/json" \
  -d '{ ... }'
```

## 예제 1: 이동 → 대기 → POST → 머리 이동 → POST

사용자가 요청한 시나리오: x축, y축으로 3초간 이동 → 완료 POST → 머리 각도 변경 → 완료 POST

```bash
curl -X POST http://localhost:8000/api/commands/sequence \
  -H "Content-Type: application/json" \
  -d '{
    "commands": [
      {
        "id": "cmd1",
        "type": "move",
        "params": {
          "mode": 1,
          "x": 10,
          "y": 5,
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
      },
      {
        "id": "cmd3",
        "type": "post",
        "params": {
          "url": "http://example.com/complete"
        }
      },
      {
        "id": "cmd4",
        "type": "head",
        "params": {
          "servo_id": 0,
          "angle": 45
        }
      },
      {
        "id": "cmd5",
        "type": "post",
        "params": {
          "url": "http://example.com/complete"
        }
      }
    ]
  }'
```

## 예제 2: 간단한 이동 및 대기

```bash
curl -X POST http://localhost:8000/api/commands/sequence \
  -H "Content-Type: application/json" \
  -d '{
    "commands": [
      {
        "id": "move_forward",
        "type": "move",
        "params": {
          "mode": 1,
          "x": 15,
          "y": 0,
          "speed": 6,
          "angle": 0
        }
      },
      {
        "id": "wait_2sec",
        "type": "wait",
        "params": {
          "seconds": 2
        }
      }
    ]
  }'
```

## 예제 3: 복합 시퀀스

```bash
curl -X POST http://localhost:8000/api/commands/sequence \
  -H "Content-Type: application/json" \
  -d '{
    "commands": [
      {
        "id": "move_left",
        "type": "move",
        "params": {
          "mode": 1,
          "x": 0,
          "y": 10,
          "speed": 5,
          "angle": 0
        }
      },
      {
        "id": "wait_3sec",
        "type": "wait",
        "params": {
          "seconds": 3
        }
      },
      {
        "id": "head_left",
        "type": "head",
        "params": {
          "servo_id": 0,
          "angle": -45
        }
      },
      {
        "id": "head_up",
        "type": "head",
        "params": {
          "servo_id": 1,
          "angle": 30
        }
      },
      {
        "id": "led_red",
        "type": "led",
        "params": {
          "r": 255,
          "g": 0,
          "b": 0
        }
      },
      {
        "id": "post_complete",
        "type": "post",
        "params": {
          "url": "http://example.com/task_complete"
        }
      }
    ]
  }'
```

## 예제 4: 여러 이동과 완료 알림

```bash
curl -X POST http://localhost:8000/api/commands/sequence \
  -H "Content-Type: application/json" \
  -d '{
    "commands": [
      {
        "id": "move1",
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
        "id": "wait1",
        "type": "wait",
        "params": {
          "seconds": 2
        }
      },
      {
        "id": "post1",
        "type": "post",
        "params": {
          "url": "http://example.com/move1_complete"
        }
      },
      {
        "id": "move2",
        "type": "move",
        "params": {
          "mode": 1,
          "x": 0,
          "y": 10,
          "speed": 5,
          "angle": 0
        }
      },
      {
        "id": "wait2",
        "type": "wait",
        "params": {
          "seconds": 2
        }
      },
      {
        "id": "post2",
        "type": "post",
        "params": {
          "url": "http://example.com/move2_complete"
        }
      }
    ]
  }'
```

## 예제 5: 머리 스캔 시퀀스

```bash
curl -X POST http://localhost:8000/api/commands/sequence \
  -H "Content-Type: application/json" \
  -d '{
    "commands": [
      {
        "id": "head_center",
        "type": "head",
        "params": {
          "servo_id": 0,
          "angle": 0
        }
      },
      {
        "id": "head_right",
        "type": "head",
        "params": {
          "servo_id": 0,
          "angle": 45
        }
      },
      {
        "id": "wait_head",
        "type": "wait",
        "params": {
          "seconds": 1
        }
      },
      {
        "id": "head_left",
        "type": "head",
        "params": {
          "servo_id": 0,
          "angle": -45
        }
      },
      {
        "id": "post_head_done",
        "type": "post",
        "params": {
          "url": "http://example.com/head_scan_complete"
        }
      }
    ]
  }'
```

## 지원되는 명령 타입

### move
로봇 이동 제어
```json
{
  "id": "move_cmd",
  "type": "move",
  "params": {
    "mode": 1,      // 1=모션 모드, 2=보행 모드
    "x": 10,        // -35 ~ 35 (mm)
    "y": 5,         // -35 ~ 35 (mm)
    "speed": 5,     // 2 ~ 10
    "angle": 0      // -10 ~ 10 (degrees)
  }
}
```

### wait
대기 시간
```json
{
  "id": "wait_cmd",
  "type": "wait",
  "params": {
    "seconds": 3.0  // 대기 시간 (초)
  }
}
```

### post
외부 URL로 POST 요청 (command_id 포함)
```json
{
  "id": "post_cmd",
  "type": "post",
  "params": {
    "url": "http://example.com/complete"
  }
}
```
POST 요청 본문: `{"command_id": "post_cmd"}`

### head
머리 서보 제어
```json
{
  "id": "head_cmd",
  "type": "head",
  "params": {
    "servo_id": 0,  // 0=수평, 1=수직
    "angle": 45     // -90 ~ 90 (degrees)
  }
}
```

### led
LED 색상 설정
```json
{
  "id": "led_cmd",
  "type": "led",
  "params": {
    "r": 255,      // 0 ~ 255
    "g": 0,        // 0 ~ 255
    "b": 0         // 0 ~ 255
  }
}
```

### led_mode
LED 모드 설정
```json
{
  "id": "led_mode_cmd",
  "type": "led_mode",
  "params": {
    "mode": 1      // 0=꺼짐, 1=지정 색상, 2=추적, 3=깜빡임, 4=호흡, 5=무지개 호흡
  }
}
```

### buzzer
부저 제어
```json
{
  "id": "buzzer_cmd",
  "type": "buzzer",
  "params": {
    "state": true  // true=켜기, false=끄기
  }
}
```

### attitude
자세 각도 제어
```json
{
  "id": "attitude_cmd",
  "type": "attitude",
  "params": {
    "roll": 0,     // -15 ~ 15 (degrees)
    "pitch": 0,    // -15 ~ 15 (degrees)
    "yaw": 0       // -15 ~ 15 (degrees)
  }
}
```

### position
위치 제어
```json
{
  "id": "position_cmd",
  "type": "position",
  "params": {
    "x": 0,        // -40 ~ 40 (mm)
    "y": 0,        // -40 ~ 40 (mm)
    "z": 0         // -20 ~ 20 (mm)
  }
}
```

### camera
카메라 뷰 제어
```json
{
  "id": "camera_cmd",
  "type": "camera",
  "params": {
    "x": 0,        // -90 ~ 90 (degrees)
    "y": 90        // -90 ~ 90 (degrees)
  }
}
```

### balance
밸런스 기능 제어
```json
{
  "id": "balance_cmd",
  "type": "balance",
  "params": {
    "enable": true  // true=활성화, false=비활성화
  }
}
```

### servo_power
서보 전원 제어
```json
{
  "id": "servo_power_cmd",
  "type": "servo_power",
  "params": {
    "power_on": true  // true=켜기, false=끄기
  }
}
```

## 응답 형식

### 성공 응답
```json
{
  "status": "success",
  "executed_commands": 5,
  "results": [
    {
      "id": "cmd1",
      "status": "success",
      "command": "move"
    },
    {
      "id": "cmd2",
      "status": "success",
      "command": "wait"
    },
    {
      "id": "cmd3",
      "status": "success",
      "command": "post",
      "response_status": 200
    },
    {
      "id": "cmd4",
      "status": "success",
      "command": "head"
    },
    {
      "id": "cmd5",
      "status": "success",
      "command": "post",
      "response_status": 200
    }
  ]
}
```

### 오류 응답
```json
{
  "status": "error",
  "executed_commands": 2,
  "results": [
    {
      "id": "cmd1",
      "status": "success",
      "command": "move"
    },
    {
      "id": "cmd2",
      "status": "success",
      "command": "wait"
    }
  ],
  "error": {
    "message": "Failed to execute command cmd3: HTTP request failed",
    "status_code": 500
  }
}
```

## 중요 사항

1. **move + wait 조합**: move 명령 다음에 wait 명령이 오면, 자동으로 이동을 시작하고 대기한 후 정지합니다.
2. **POST 명령 ID**: POST 요청의 본문에 `{"command_id": "<id>"}` 형식으로 명령 ID가 포함됩니다.
3. **순차 실행**: 모든 명령은 순차적으로 실행되며, 한 명령이 실패하면 실행이 중단됩니다.
4. **서버 IP 변경**: 다른 서버를 사용하려면 `localhost`를 실제 IP 주소로 변경하세요.

## 스크립트 실행

예제 스크립트를 실행하려면:

```bash
# 기본 (localhost 사용)
./sequence_command_examples.sh

# 특정 서버 IP 사용
./sequence_command_examples.sh 192.168.1.100
```


