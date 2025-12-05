# Hexapod Robot REST API 문서

## 개요

이 문서는 헥사포드 로봇을 제어하기 위한 REST API에 대한 설명입니다. API는 FastAPI를 기반으로 구현되었으며, HTTP 요청을 통해 로봇의 다양한 기능을 제어할 수 있습니다.

## 기본 정보

- **Base URL**: `http://<raspberry-pi-ip>:8000`
- **포트**: `8000`
- **프로토콜**: HTTP/HTTPS
- **데이터 형식**: JSON
- **인코딩**: UTF-8

## API 엔드포인트

### 1. API 상태 확인

#### `GET /`

API 서버의 기본 상태를 확인합니다.

**응답 예시:**
```json
{
  "message": "Hexapod Robot Control API",
  "version": "1.0.0",
  "status": "running"
}
```

---

### 2. 로봇 이동 제어

#### `POST /api/move`

로봇의 이동을 제어합니다. 두 가지 보행 모드를 지원하며, 각 모드는 다른 보행 패턴과 속도 특성을 가집니다.

**요청 본문:**
```json
{
  "mode": 1,
  "x": 10,
  "y": 0,
  "speed": 5,
  "angle": 0
}
```

**파라미터 상세 설명:**

##### `mode` (integer, required)
- **범위**: `1` ~ `2`
- **설명**: 이동 모드를 선택합니다.
  - **`1` (모션 모드 / 트로트 보행)**: 
    - 빠르고 부드러운 이동에 적합합니다.
    - 대각선 다리 쌍이 동시에 움직이는 트로트 보행 패턴을 사용합니다.
    - 보행 주기 프레임 수: 속도 2일 때 126프레임, 속도 10일 때 22프레임
    - 빠른 이동이나 역동적인 동작에 적합합니다.
  - **`2` (보행 모드 / 순차 보행)**:
    - 안정적이고 정확한 이동에 적합합니다.
    - 한 번에 하나의 다리씩 순차적으로 움직이는 보행 패턴을 사용합니다.
    - 보행 주기 프레임 수: 속도 2일 때 171프레임, 속도 10일 때 45프레임
    - 정밀한 위치 제어나 불안정한 지면에서 이동할 때 적합합니다.

##### `x` (integer, required)
- **범위**: `-35` ~ `35` (단위: 미리미터)
- **설명**: X축 방향의 스텝 길이를 설정합니다.
  - **양수 값 (`1` ~ `35`)**: 앞으로 이동하는 스텝 길이
    - 값이 클수록 더 큰 스텝을 의미합니다.
    - 예: `x: 10` = 작은 스텝으로 앞으로 이동, `x: 35` = 큰 스텝으로 앞으로 이동
  - **음수 값 (`-35` ~ `-1`)**: 뒤로 이동하는 스텝 길이
    - 절댓값이 클수록 더 큰 스텝을 의미합니다.
    - 예: `x: -10` = 작은 스텝으로 뒤로 이동, `x: -35` = 큰 스텝으로 뒤로 이동
  - **`0`**: 앞뒤 이동 없음 (좌우 이동만 수행)

##### `y` (integer, required)
- **범위**: `-35` ~ `35` (단위: 미리미터)
- **설명**: Y축 방향의 스텝 길이를 설정합니다.
  - **양수 값 (`1` ~ `35`)**: 왼쪽으로 이동하는 스텝 길이
    - 값이 클수록 더 큰 스텝을 의미합니다.
    - 예: `y: 10` = 작은 스텝으로 왼쪽 이동, `y: 35` = 큰 스텝으로 왼쪽 이동
  - **음수 값 (`-35` ~ `-1`)**: 오른쪽으로 이동하는 스텝 길이
    - 절댓값이 클수록 더 큰 스텝을 의미합니다.
    - 예: `y: -10` = 작은 스텝으로 오른쪽 이동, `y: -35` = 큰 스텝으로 오른쪽 이동
  - **`0`**: 좌우 이동 없음 (앞뒤 이동만 수행)

##### `speed` (integer, required)
- **범위**: `2` ~ `10`
- **설명**: 이동 속도를 설정합니다. 내부적으로 보행 주기 프레임 수로 변환됩니다.
  - **낮은 값 (`2` ~ `4`)**: 느리고 안정적인 이동
    - 모드 1: 126프레임 (매우 느림) ~ 90프레임
    - 모드 2: 171프레임 (매우 느림) ~ 120프레임
    - 정밀한 제어나 불안정한 지면에서 사용 권장
  - **중간 값 (`5` ~ `7`)**: 보통 속도
    - 모드 1: 약 70프레임 ~ 45프레임
    - 모드 2: 약 90프레임 ~ 60프레임
    - 일반적인 사용에 적합
  - **높은 값 (`8` ~ `10`)**: 빠르고 역동적인 이동
    - 모드 1: 약 35프레임 ~ 22프레임 (매우 빠름)
    - 모드 2: 약 50프레임 ~ 45프레임
    - 빠른 이동이 필요할 때 사용, 안정성은 다소 감소

##### `angle` (integer, optional)
- **범위**: `-10` ~ `10` (단위: 도)
- **기본값**: `0`
- **설명**: 이동 방향의 회전 각도를 설정합니다.
  - **양수 값 (`1` ~ `10`)**: 오른쪽으로 회전하며 이동
    - 값이 클수록 더 큰 회전 각도
    - 예: `angle: 5` = 약간 오른쪽으로 회전하며 이동, `angle: 10` = 크게 오른쪽으로 회전하며 이동
  - **음수 값 (`-10` ~ `-1`)**: 왼쪽으로 회전하며 이동
    - 절댓값이 클수록 더 큰 회전 각도
    - 예: `angle: -5` = 약간 왼쪽으로 회전하며 이동, `angle: -10` = 크게 왼쪽으로 회전하며 이동
  - **`0`**: 직진 (회전 없음)
  - **조합 사용**: `x`, `y`, `angle` 값을 조합하여 곡선 이동을 구현할 수 있습니다.
    - 예: `x: 10, y: 0, angle: 5` = 앞으로 이동하면서 오른쪽으로 회전
    - 예: `x: 0, y: 10, angle: -5` = 왼쪽으로 이동하면서 왼쪽으로 회전

**사용 예시:**

1. **앞으로 직진 (느린 속도)**:
```json
{
  "mode": 1,
  "x": 10,
  "y": 0,
  "speed": 3,
  "angle": 0
}
```

2. **뒤로 빠르게 이동**:
```json
{
  "mode": 1,
  "x": -20,
  "y": 0,
  "speed": 8,
  "angle": 0
}
```

3. **왼쪽으로 이동**:
```json
{
  "mode": 1,
  "x": 0,
  "y": 15,
  "speed": 5,
  "angle": 0
}
```

4. **오른쪽으로 회전하며 앞으로 이동**:
```json
{
  "mode": 1,
  "x": 15,
  "y": 0,
  "speed": 6,
  "angle": 5
}
```

5. **안정적인 보행 모드로 정밀 이동**:
```json
{
  "mode": 2,
  "x": 5,
  "y": 0,
  "speed": 3,
  "angle": 0
}
```

**응답 예시:**
```json
{
  "status": "success",
  "command": "CMD_MOVE"
}
```

**사용 예시:**
```bash
curl -X POST http://localhost:8000/api/move \
  -H "Content-Type: application/json" \
  -d '{
    "mode": 1,
    "x": 10,
    "y": 0,
    "speed": 5,
    "angle": 0
  }'
```

---

### 3. LED 색상 설정

#### `POST /api/led`

RGB 값을 사용하여 LED의 색상을 설정합니다. 이 엔드포인트는 LED 모드가 1(지정 색상) 또는 3(깜빡임 모드)일 때만 효과가 있습니다.

**요청 본문:**
```json
{
  "r": 255,
  "g": 0,
  "b": 0
}
```

**파라미터 상세 설명:**

##### `r` (integer, required)
- **범위**: `0` ~ `255`
- **설명**: 빨강(Red) 색상 값입니다. RGB 색상 모델의 빨강 채널 강도를 나타냅니다.
  - **`0`**: 빨강 채널 꺼짐
  - **`255`**: 빨강 채널 최대 밝기
  - 중간 값은 빨강의 강도를 조절합니다.

##### `g` (integer, required)
- **범위**: `0` ~ `255`
- **설명**: 초록(Green) 색상 값입니다. RGB 색상 모델의 초록 채널 강도를 나타냅니다.
  - **`0`**: 초록 채널 꺼짐
  - **`255`**: 초록 채널 최대 밝기
  - 중간 값은 초록의 강도를 조절합니다.

##### `b` (integer, required)
- **범위**: `0` ~ `255`
- **설명**: 파랑(Blue) 색상 값입니다. RGB 색상 모델의 파랑 채널 강도를 나타냅니다.
  - **`0`**: 파랑 채널 꺼짐
  - **`255`**: 파랑 채널 최대 밝기
  - 중간 값은 파랑의 강도를 조절합니다.

**색상 조합 예시:**
- 빨강: `{"r": 255, "g": 0, "b": 0}`
- 초록: `{"r": 0, "g": 255, "b": 0}`
- 파랑: `{"r": 0, "g": 0, "b": 255}`
- 흰색: `{"r": 255, "g": 255, "b": 255}`
- 노랑: `{"r": 255, "g": 255, "b": 0}`
- 보라: `{"r": 255, "g": 0, "b": 255}`
- 청록: `{"r": 0, "g": 255, "b": 255}`

**응답 예시:**
```json
{
  "status": "success",
  "command": "CMD_LED"
}
```

**사용 예시:**
```bash
curl -X POST http://localhost:8000/api/led \
  -H "Content-Type: application/json" \
  -d '{
    "r": 255,
    "g": 0,
    "b": 0
  }'
```

---

### 4. LED 모드 설정

#### `POST /api/led/mode`

LED의 동작 모드를 설정합니다.

**요청 본문:**
```json
{
  "mode": 1
}
```

**파라미터 설명:**
- `mode` (integer, required): LED 모드
  - `0`: 꺼짐
  - `1`: 지정 색상
  - `2`: 추적 모드
  - `3`: 깜빡임 모드
  - `4`: 호흡 모드
  - `5`: 무지개 호흡 모드

**응답 예시:**
```json
{
  "status": "success",
  "command": "CMD_LED_MOD"
}
```

**사용 예시:**
```bash
curl -X POST http://localhost:8000/api/led/mode \
  -H "Content-Type: application/json" \
  -d '{"mode": 1}'
```

---

### 5. 초음파 거리 측정

#### `GET /api/ultrasonic`

전방 장애물까지의 거리를 측정합니다.

**응답 예시:**
```json
{
  "command": "CMD_SONIC",
  "distance": 25.5
}
```

**파라미터 설명:**
- `distance` (float): 거리 (단위: 센티미터)

**사용 예시:**
```bash
curl http://localhost:8000/api/ultrasonic
```

---

### 6. 부저 제어

#### `POST /api/buzzer`

부저를 켜거나 끕니다.

**요청 본문:**
```json
{
  "state": true
}
```

**파라미터 설명:**
- `state` (boolean, required): 부저 상태
  - `true`: 켜기
  - `false`: 끄기

**응답 예시:**
```json
{
  "status": "success",
  "command": "CMD_BUZZER"
}
```

**사용 예시:**
```bash
curl -X POST http://localhost:8000/api/buzzer \
  -H "Content-Type: application/json" \
  -d '{"state": true}'
```

---

### 7. 머리 서보 제어

#### `POST /api/head`

로봇의 머리 부분에 장착된 서보 모터를 제어합니다. 머리의 방향을 조절하여 시야각을 변경할 수 있습니다.

**요청 본문:**
```json
{
  "servo_id": 0,
  "angle": 45
}
```

**파라미터 상세 설명:**

##### `servo_id` (integer, required)
- **범위**: `0` ~ `1`
- **설명**: 제어할 서보 모터를 선택합니다.
  - **`0`**: 수평 회전 서보 (좌우 회전)
    - 로봇의 머리를 좌우로 회전시킵니다.
    - 양수 각도는 오른쪽, 음수 각도는 왼쪽을 의미합니다.
  - **`1`**: 수직 회전 서보 (상하 회전)
    - 로봇의 머리를 상하로 회전시킵니다.
    - 양수 각도는 위쪽, 음수 각도는 아래쪽을 의미합니다.

##### `angle` (integer, required)
- **범위**: `-90` ~ `90` (단위: 도)
- **설명**: 서보 모터의 목표 각도입니다.
  - **`0`**: 중앙 위치 (기본 위치)
  - **양수 값 (`1` ~ `90`)**: 
    - 서보 ID 0: 오른쪽으로 회전
    - 서보 ID 1: 위쪽으로 회전
    - 값이 클수록 더 많이 회전합니다.
  - **음수 값 (`-90` ~ `-1`)**: 
    - 서보 ID 0: 왼쪽으로 회전
    - 서보 ID 1: 아래쪽으로 회전
    - 절댓값이 클수록 더 많이 회전합니다.

**응답 예시:**
```json
{
  "status": "success",
  "command": "CMD_HEAD"
}
```

**사용 예시:**
```bash
curl -X POST http://localhost:8000/api/head \
  -H "Content-Type: application/json" \
  -d '{
    "servo_id": 0,
    "angle": 45
  }'
```

---

### 8. 밸런스 기능 제어

#### `POST /api/balance`

로봇의 밸런스 기능을 활성화하거나 비활성화합니다.

**요청 본문:**
```json
{
  "enable": true
}
```

**파라미터 설명:**
- `enable` (boolean, required): 밸런스 기능
  - `true`: 활성화
  - `false`: 비활성화

**응답 예시:**
```json
{
  "status": "success",
  "command": "CMD_BALANCE"
}
```

**사용 예시:**
```bash
curl -X POST http://localhost:8000/api/balance \
  -H "Content-Type: application/json" \
  -d '{"enable": true}'
```

---

### 9. 자세 각도 제어

#### `POST /api/attitude`

로봇의 전체 자세(기울기)를 제어합니다. 각 다리의 위치를 조정하여 로봇의 롤, 피치, 요 각도를 변경합니다. 경사면에서 균형을 맞추거나 특정 자세를 취할 때 사용합니다.

**요청 본문:**
```json
{
  "roll": 0,
  "pitch": 0,
  "yaw": 0
}
```

**파라미터 상세 설명:**

##### `roll` (integer, required)
- **범위**: `-15` ~ `15` (단위: 도)
- **설명**: 롤(Roll) 각도 - 로봇을 좌우로 기울이는 각도입니다.
  - **양수 값 (`1` ~ `15`)**: 오른쪽으로 기울임
    - 값이 클수록 더 많이 기울어집니다.
    - 예: `roll: 5` = 약간 오른쪽으로 기울임, `roll: 15` = 크게 오른쪽으로 기울임
  - **음수 값 (`-15` ~ `-1`)**: 왼쪽으로 기울임
    - 절댓값이 클수록 더 많이 기울어집니다.
    - 예: `roll: -5` = 약간 왼쪽으로 기울임, `roll: -15` = 크게 왼쪽으로 기울임
  - **`0`**: 수평 유지 (기울임 없음)
  - **주의**: 범위를 벗어나면 로봇이 불안정해질 수 있습니다.

##### `pitch` (integer, required)
- **범위**: `-15` ~ `15` (단위: 도)
- **설명**: 피치(Pitch) 각도 - 로봇을 앞뒤로 기울이는 각도입니다.
  - **양수 값 (`1` ~ `15`)**: 앞으로 기울임
    - 값이 클수록 더 많이 기울어집니다.
    - 예: `pitch: 5` = 약간 앞으로 기울임, `pitch: 15` = 크게 앞으로 기울임
  - **음수 값 (`-15` ~ `-1`)**: 뒤로 기울임
    - 절댓값이 클수록 더 많이 기울어집니다.
    - 예: `pitch: -5` = 약간 뒤로 기울임, `pitch: -15` = 크게 뒤로 기울임
  - **`0`**: 수평 유지 (기울임 없음)
  - **사용 예**: 경사면을 오를 때 앞으로 기울여 균형을 맞출 수 있습니다.

##### `yaw` (integer, required)
- **범위**: `-15` ~ `15` (단위: 도)
- **설명**: 요(Yaw) 각도 - 로봇을 좌우로 회전시키는 각도입니다.
  - **양수 값 (`1` ~ `15`)**: 오른쪽으로 회전
    - 값이 클수록 더 많이 회전합니다.
    - 예: `yaw: 5` = 약간 오른쪽으로 회전, `yaw: 15` = 크게 오른쪽으로 회전
  - **음수 값 (`-15` ~ `-1`)**: 왼쪽으로 회전
    - 절댓값이 클수록 더 많이 회전합니다.
    - 예: `yaw: -5` = 약간 왼쪽으로 회전, `yaw: -15` = 크게 왼쪽으로 회전
  - **`0`**: 회전 없음 (정면 유지)
  - **참고**: 이동 명령의 `angle` 파라미터와 달리, 이 값은 로봇의 몸체 자세만 변경합니다.

**응답 예시:**
```json
{
  "status": "success",
  "command": "CMD_ATTITUDE"
}
```

**사용 예시:**
```bash
curl -X POST http://localhost:8000/api/attitude \
  -H "Content-Type: application/json" \
  -d '{
    "roll": 0,
    "pitch": 0,
    "yaw": 0
  }'
```

---

### 10. 위치 제어

#### `POST /api/position`

로봇의 몸체 위치를 상대적으로 이동시킵니다. 모든 다리의 기준점을 동시에 이동시켜 로봇의 중심 위치를 변경합니다. 이동 명령과 달리 한 번의 명령으로 즉시 위치를 변경합니다.

**요청 본문:**
```json
{
  "x": 0,
  "y": 0,
  "z": 0
}
```

**파라미터 상세 설명:**

##### `x` (integer, required)
- **범위**: `-40` ~ `40` (단위: 미리미터)
- **설명**: X축 방향의 몸체 위치 오프셋입니다.
  - **양수 값 (`1` ~ `40`)**: 몸체를 앞으로 이동
    - 값이 클수록 더 많이 앞으로 이동합니다.
    - 예: `x: 10` = 약간 앞으로 이동, `x: 40` = 크게 앞으로 이동
  - **음수 값 (`-40` ~ `-1`)**: 몸체를 뒤로 이동
    - 절댓값이 클수록 더 많이 뒤로 이동합니다.
    - 예: `x: -10` = 약간 뒤로 이동, `x: -40` = 크게 뒤로 이동
  - **`0`**: 앞뒤 이동 없음
  - **참고**: 이동 명령(`/api/move`)과 달리 보행 없이 즉시 위치를 변경합니다.

##### `y` (integer, required)
- **범위**: `-40` ~ `40` (단위: 미리미터)
- **설명**: Y축 방향의 몸체 위치 오프셋입니다.
  - **양수 값 (`1` ~ `40`)**: 몸체를 왼쪽으로 이동
    - 값이 클수록 더 많이 왼쪽으로 이동합니다.
    - 예: `y: 10` = 약간 왼쪽으로 이동, `y: 40` = 크게 왼쪽으로 이동
  - **음수 값 (`-40` ~ `-1`)**: 몸체를 오른쪽으로 이동
    - 절댓값이 클수록 더 많이 오른쪽으로 이동합니다.
    - 예: `y: -10` = 약간 오른쪽으로 이동, `y: -40` = 크게 오른쪽으로 이동
  - **`0`**: 좌우 이동 없음

##### `z` (integer, required)
- **범위**: `-20` ~ `20` (단위: 미리미터)
- **설명**: Z축 방향의 몸체 높이 오프셋입니다. 기본 높이는 -25mm입니다.
  - **양수 값 (`1` ~ `20`)**: 몸체를 올림
    - 값이 클수록 더 많이 올립니다.
    - 예: `z: 10` = 약간 올림, `z: 20` = 크게 올림
    - 몸체를 높이면 다리가 더 펴지고 안정성이 증가할 수 있습니다.
  - **음수 값 (`-20` ~ `-1`)**: 몸체를 내림
    - 절댓값이 클수록 더 많이 내립니다.
    - 예: `z: -10` = 약간 내림, `z: -20` = 크게 내림
    - 몸체를 낮추면 무게 중심이 낮아져 안정성이 증가할 수 있습니다.
  - **`0`**: 높이 변경 없음 (기본 높이 유지)
  - **주의**: 너무 높이거나 낮추면 다리의 동작 범위를 벗어날 수 있습니다.

**응답 예시:**
```json
{
  "status": "success",
  "command": "CMD_POSITION"
}
```

**사용 예시:**
```bash
curl -X POST http://localhost:8000/api/position \
  -H "Content-Type: application/json" \
  -d '{
    "x": 0,
    "y": 0,
    "z": 0
  }'
```

---

### 11. 카메라 뷰 제어

#### `POST /api/camera`

카메라가 장착된 서보 모터를 제어하여 카메라의 시야각을 조절합니다. 머리 서보 제어와 유사하지만 카메라 전용 서보를 제어합니다.

**요청 본문:**
```json
{
  "x": 0,
  "y": 90
}
```

**파라미터 상세 설명:**

##### `x` (integer, required)
- **범위**: `-90` ~ `90` (단위: 도)
- **설명**: 카메라의 수평 각도입니다.
  - **양수 값 (`1` ~ `90`)**: 오른쪽으로 회전
    - 값이 클수록 더 많이 오른쪽으로 회전합니다.
    - 내부적으로 50~180 범위로 변환되어 서보 0번에 적용됩니다.
  - **음수 값 (`-90` ~ `-1`)**: 왼쪽으로 회전
    - 절댓값이 클수록 더 많이 왼쪽으로 회전합니다.
  - **`0`**: 중앙 (정면)
  - **참고**: 실제 서보 각도는 입력값에 따라 50~180도 범위로 매핑됩니다.

##### `y` (integer, required)
- **범위**: `-90` ~ `90` (단위: 도)
- **설명**: 카메라의 수직 각도입니다.
  - **양수 값 (`1` ~ `90`)**: 위쪽으로 회전
    - 값이 클수록 더 많이 위쪽으로 회전합니다.
    - 내부적으로 0~180 범위로 변환되어 서보 1번에 적용됩니다.
  - **음수 값 (`-90` ~ `-1`)**: 아래쪽으로 회전
    - 절댓값이 클수록 더 많이 아래쪽으로 회전합니다.
  - **`0`**: 중앙 (수평)
  - **참고**: 실제 서보 각도는 입력값에 따라 0~180도 범위로 매핑됩니다.

**응답 예시:**
```json
{
  "status": "success",
  "command": "CMD_CAMERA"
}
```

**사용 예시:**
```bash
curl -X POST http://localhost:8000/api/camera \
  -H "Content-Type: application/json" \
  -d '{
    "x": 0,
    "y": 90
  }'
```

---

### 12. 서보 릴렉스 토글

#### `POST /api/relax`

서보의 릴렉스 상태를 토글합니다. (권장하지 않음, `/api/servo/power` 사용 권장)

**응답 예시:**
```json
{
  "status": "success",
  "command": "CMD_RELAX"
}
```

**사용 예시:**
```bash
curl -X POST http://localhost:8000/api/relax \
  -H "Content-Type: application/json"
```

---

### 13. 배터리 전압 조회

#### `GET /api/power`

배터리 전압을 조회합니다.

**응답 예시:**
```json
{
  "command": "CMD_POWER",
  "load_battery": 7.2,
  "raspberry_pi_battery": 5.1
}
```

**파라미터 설명:**
- `load_battery` (float): 부하 배터리 전압 (V)
- `raspberry_pi_battery` (float): 라즈베리파이 배터리 전압 (V)

**사용 예시:**
```bash
curl http://localhost:8000/api/power
```

**참고:** 배터리 전압이 낮을 경우 (부하 배터리 < 5.5V 또는 라즈베리파이 배터리 < 6V) 부저가 자동으로 경고음을 울립니다.

---

### 14. 서보 전원 제어

#### `POST /api/servo/power`

서보의 전원을 켜거나 끕니다.

**요청 본문:**
```json
{
  "power_on": true
}
```

**파라미터 설명:**
- `power_on` (boolean, required): 서보 전원 상태
  - `true`: 전원 켜기
  - `false`: 전원 끄기

**응답 예시:**
```json
{
  "status": "success",
  "command": "CMD_SERVOPOWER"
}
```

**사용 예시:**
```bash
curl -X POST http://localhost:8000/api/servo/power \
  -H "Content-Type: application/json" \
  -d '{"power_on": true}'
```

---

### 15. 로봇 상태 조회

#### `GET /api/status`

로봇의 현재 상태를 조회합니다.

**응답 예시:**
```json
{
  "status": "online",
  "servo_relaxed": false,
  "tcp_active": false
}
```

**파라미터 설명:**
- `status` (string): 로봇 상태 (`"online"` 또는 `"offline"`)
- `servo_relaxed` (boolean): 서보 릴렉스 상태
- `tcp_active` (boolean): TCP 연결 활성 상태

**사용 예시:**
```bash
curl http://localhost:8000/api/status
```

---

## 에러 응답

API 요청이 실패할 경우 다음과 같은 형식의 에러 응답이 반환됩니다:

**에러 응답 형식:**
```json
{
  "detail": "에러 메시지"
}
```

**주요 HTTP 상태 코드:**
- `200 OK`: 요청 성공
- `400 Bad Request`: 잘못된 요청 파라미터
- `422 Unprocessable Entity`: 요청 본문 검증 실패
- `503 Service Unavailable`: 로봇 서버가 초기화되지 않음
- `500 Internal Server Error`: 서버 내부 오류

**에러 예시:**
```json
{
  "detail": "Robot server not initialized"
}
```

---

## Swagger UI

FastAPI는 자동으로 Swagger UI를 제공합니다. 브라우저에서 다음 URL을 방문하여 대화형 API 문서를 확인할 수 있습니다:

- **Swagger UI**: `http://<raspberry-pi-ip>:8000/docs`
- **ReDoc**: `http://<raspberry-pi-ip>:8000/redoc`

---

## Python 클라이언트 예제

```python
import requests

BASE_URL = "http://localhost:8000"

# 로봇 이동
def move_robot(mode=1, x=0, y=0, speed=5, angle=0):
    response = requests.post(
        f"{BASE_URL}/api/move",
        json={
            "mode": mode,
            "x": x,
            "y": y,
            "speed": speed,
            "angle": angle
        }
    )
    return response.json()

# LED 색상 설정
def set_led_color(r, g, b):
    response = requests.post(
        f"{BASE_URL}/api/led",
        json={"r": r, "g": g, "b": b}
    )
    return response.json()

# 초음파 거리 측정
def get_distance():
    response = requests.get(f"{BASE_URL}/api/ultrasonic")
    return response.json()

# 배터리 전압 조회
def get_battery_voltage():
    response = requests.get(f"{BASE_URL}/api/power")
    return response.json()

# 사용 예시
if __name__ == "__main__":
    # 로봇을 앞으로 이동
    move_robot(mode=1, x=10, y=0, speed=5, angle=0)
    
    # LED를 빨간색으로 설정
    set_led_color(255, 0, 0)
    
    # 거리 측정
    distance = get_distance()
    print(f"Distance: {distance['distance']} cm")
    
    # 배터리 전압 확인
    battery = get_battery_voltage()
    print(f"Load Battery: {battery['load_battery']}V")
    print(f"Raspberry Pi Battery: {battery['raspberry_pi_battery']}V")
```

---

## JavaScript/TypeScript 클라이언트 예제

```javascript
const BASE_URL = 'http://localhost:8000';

// 로봇 이동
async function moveRobot(mode = 1, x = 0, y = 0, speed = 5, angle = 0) {
  const response = await fetch(`${BASE_URL}/api/move`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ mode, x, y, speed, angle }),
  });
  return await response.json();
}

// LED 색상 설정
async function setLEDColor(r, g, b) {
  const response = await fetch(`${BASE_URL}/api/led`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ r, g, b }),
  });
  return await response.json();
}

// 초음파 거리 측정
async function getDistance() {
  const response = await fetch(`${BASE_URL}/api/ultrasonic`);
  return await response.json();
}

// 사용 예시
(async () => {
  // 로봇을 앞으로 이동
  await moveRobot(1, 10, 0, 5, 0);
  
  // LED를 빨간색으로 설정
  await setLEDColor(255, 0, 0);
  
  // 거리 측정
  const distance = await getDistance();
  console.log(`Distance: ${distance.distance} cm`);
})();
```

---

## 주의사항

1. **포트 충돌**: REST API는 기본적으로 포트 8000을 사용합니다. 다른 서비스와 충돌하지 않는지 확인하세요.

2. **동시 요청**: 여러 명령을 동시에 보낼 경우, 로봇의 하드웨어 제한으로 인해 일부 명령이 무시될 수 있습니다.

3. **배터리 모니터링**: 배터리 전압이 낮을 경우 로봇이 자동으로 경고음을 울립니다. 정기적으로 배터리 상태를 확인하세요.

4. **서보 전원**: 서보 전원을 끄면 로봇이 움직이지 않습니다. 전원을 끄기 전에 로봇이 안전한 위치에 있는지 확인하세요.

5. **CORS**: 현재 모든 origin에서의 요청을 허용하도록 설정되어 있습니다. 프로덕션 환경에서는 보안을 위해 특정 origin만 허용하도록 설정하는 것을 권장합니다.

---

## 버전 정보

- **API 버전**: 1.0.0
- **FastAPI 버전**: 최신 버전
- **Python 버전**: 3.x 이상

---

## 문의 및 지원

문제가 발생하거나 추가 기능이 필요한 경우, 프로젝트 저장소의 이슈 트래커를 통해 문의해주세요.

