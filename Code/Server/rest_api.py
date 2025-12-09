# -*- coding: utf-8 -*-
"""
REST API server for robot control
Provides HTTP endpoints to control the hexapod robot
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Union, Literal
import threading
import asyncio
import time
try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False
from server import Server
from command import COMMAND as cmd

app = FastAPI(title="Hexapod Robot Control API", version="1.0.0")

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global server instance (will be set by main.py)
robot_server: Optional[Server] = None


def set_server(server: Server):
    """Set the robot server instance"""
    global robot_server
    robot_server = server


def process_command(command_parts: list):
    """
    명령을 처리하는 내부 함수
    
    REST API 요청을 기존 TCP 서버의 명령 처리 로직으로 변환하여 실행합니다.
    각 명령 타입에 따라 적절한 하드웨어 제어 함수를 호출합니다.
    
    Args:
        command_parts: 명령 문자열 리스트. 첫 번째 요소는 명령 타입(CMD_*),
                      이후 요소들은 명령에 필요한 파라미터들입니다.
    
    Returns:
        dict: 명령 처리 결과를 포함한 딕셔너리.
              일부 명령(CMD_POWER, CMD_SONIC)은 추가 정보를 반환합니다.
    
    Raises:
        HTTPException: 로봇 서버가 초기화되지 않았거나 명령 처리 중 오류가 발생한 경우.
    """
    if robot_server is None:
        raise HTTPException(status_code=503, detail="Robot server not initialized")
    
    if cmd.CMD_BUZZER in command_parts:
        robot_server.buzzer_controller.set_state(command_parts[1] == "1")
    elif cmd.CMD_POWER in command_parts:
        try:
            battery_voltage = robot_server.adc_sensor.read_battery_voltage()
            return {
                "command": cmd.CMD_POWER,
                "load_battery": battery_voltage[0],
                "raspberry_pi_battery": battery_voltage[1]
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to read battery voltage: {str(e)}")
    elif cmd.CMD_LED in command_parts:
        try:
            if robot_server.led_thread is not None:
                from Thread import stop_thread
                stop_thread(robot_server.led_thread)
        except:
            pass
        robot_server.led_thread = threading.Thread(
            target=robot_server.led_controller.process_light_command,
            args=(command_parts,)
        )
        robot_server.led_thread.start()
    elif cmd.CMD_LED_MOD in command_parts:
        try:
            if robot_server.led_thread is not None:
                from Thread import stop_thread
                stop_thread(robot_server.led_thread)
        except:
            pass
        robot_server.led_thread = threading.Thread(
            target=robot_server.led_controller.process_light_command,
            args=(command_parts,)
        )
        robot_server.led_thread.start()
    elif cmd.CMD_SONIC in command_parts:
        distance = robot_server.ultrasonic_sensor.get_distance()
        return {
            "command": cmd.CMD_SONIC,
            "distance": distance
        }
    elif cmd.CMD_HEAD in command_parts:
        if len(command_parts) == 3:
            # Fix: Swap servo ID 0 and 1 because they are reversed physically
            # Input: 0=Horizontal, 1=Vertical
            # Hardware: 0=Vertical, 1=Horizontal (based on user report)
            req_id = int(command_parts[1])
            target_id = 1 - req_id if req_id in [0, 1] else req_id
            robot_server.servo_controller.set_servo_angle(
                target_id, int(command_parts[2])
            )
    elif cmd.CMD_CAMERA in command_parts:
        if len(command_parts) == 3:
            x = robot_server.control_system.restrict_value(int(command_parts[1]), 50, 180)
            y = robot_server.control_system.restrict_value(int(command_parts[2]), 0, 180)
            # Fix: Swap servo ID 0 and 1
            # x is Horizontal -> should map to Hardware ID 1
            # y is Vertical -> should map to Hardware ID 0
            robot_server.servo_controller.set_servo_angle(1, x)
            robot_server.servo_controller.set_servo_angle(0, y)
    elif cmd.CMD_RELAX in command_parts:
        if robot_server.is_servo_relaxed == False:
            robot_server.control_system.relax(True)
            robot_server.is_servo_relaxed = True
        else:
            robot_server.control_system.relax(False)
            robot_server.is_servo_relaxed = False
    elif cmd.CMD_SERVOPOWER in command_parts:
        if command_parts[1] == "0":
            robot_server.control_system.servo_power_disable.on()
        else:
            robot_server.control_system.servo_power_disable.off()
    else:
        import time
        robot_server.control_system.command_queue = command_parts
        robot_server.control_system.timeout = time.time()
    
    return {"status": "success", "command": command_parts[0]}


# Request models
class MoveRequest(BaseModel):
    """
    로봇 이동 제어 요청 모델
    
    이 모델은 헥사포드 로봇의 이동을 제어하기 위한 모든 파라미터를 포함합니다.
    각 파라미터는 로봇의 보행 패턴, 방향, 속도, 각도를 결정합니다.
    """
    mode: int = Field(
        ..., 
        ge=1, 
        le=2, 
        description="이동 모드: 1=모션 모드(트로트 보행), 2=보행 모드(순차 보행). "
                   "모드 1은 빠르고 부드러운 이동에 적합하며, 모드 2는 안정적인 이동에 적합합니다."
    )
    x: int = Field(
        ..., 
        ge=-35, 
        le=35, 
        description="X축 스텝 길이 (단위: 미리미터). "
                   "범위: -35 ~ 35. "
                   "양수 값은 앞으로 이동, 음수 값은 뒤로 이동을 의미합니다. "
                   "절댓값이 클수록 더 큰 스텝을 의미합니다."
    )
    y: int = Field(
        ..., 
        ge=-35, 
        le=35, 
        description="Y축 스텝 길이 (단위: 미리미터). "
                   "범위: -35 ~ 35. "
                   "양수 값은 왼쪽으로 이동, 음수 값은 오른쪽으로 이동을 의미합니다. "
                   "0으로 설정하면 좌우 이동 없이 직진/후진만 수행합니다."
    )
    speed: int = Field(
        ..., 
        ge=2, 
        le=10, 
        description="이동 속도. "
                   "범위: 2(가장 느림) ~ 10(가장 빠름). "
                   "낮은 값(2-4)은 느리고 안정적인 이동, 높은 값(7-10)은 빠르고 역동적인 이동을 제공합니다. "
                   "내부적으로 보행 주기 프레임 수로 변환됩니다 (모드 1: 126~22 프레임, 모드 2: 171~45 프레임)."
    )
    angle: int = Field(
        0, 
        ge=-10, 
        le=10, 
        description="이동 각도 (단위: 도). "
                   "범위: -10(왼쪽 회전) ~ 10(오른쪽 회전), 기본값: 0(직진). "
                   "양수 값은 오른쪽으로 회전하며 이동, 음수 값은 왼쪽으로 회전하며 이동합니다. "
                   "각도와 x, y 값을 조합하여 곡선 이동을 구현할 수 있습니다."
    )


class LEDRequest(BaseModel):
    """
    LED 색상 설정 요청 모델
    
    RGB 값을 사용하여 LED의 색상을 설정합니다.
    LED 모드가 1(지정 색상) 또는 3(깜빡임 모드)일 때만 유효합니다.
    """
    r: int = Field(
        ..., 
        ge=0, 
        le=255, 
        description="빨강(Red) 색상 값. "
                   "범위: 0(꺼짐) ~ 255(최대 밝기). "
                   "RGB 색상 모델의 빨강 채널 강도를 나타냅니다."
    )
    g: int = Field(
        ..., 
        ge=0, 
        le=255, 
        description="초록(Green) 색상 값. "
                   "범위: 0(꺼짐) ~ 255(최대 밝기). "
                   "RGB 색상 모델의 초록 채널 강도를 나타냅니다."
    )
    b: int = Field(
        ..., 
        ge=0, 
        le=255, 
        description="파랑(Blue) 색상 값. "
                   "범위: 0(꺼짐) ~ 255(최대 밝기). "
                   "RGB 색상 모델의 파랑 채널 강도를 나타냅니다."
    )


class LEDModeRequest(BaseModel):
    """
    LED 모드 설정 요청 모델
    
    LED의 동작 모드를 설정합니다. 각 모드는 다른 시각적 효과를 제공합니다.
    """
    mode: int = Field(
        ..., 
        ge=0, 
        le=5, 
        description="LED 동작 모드. "
                   "0=꺼짐 (LED 완전히 끄기), "
                   "1=지정 색상 (LEDRequest로 설정한 색상 유지), "
                   "2=추적 모드 (색상이 순차적으로 이동), "
                   "3=깜빡임 모드 (LEDRequest로 설정한 색상을 깜빡임), "
                   "4=호흡 모드 (밝기가 부드럽게 변화), "
                   "5=무지개 호흡 모드 (무지개 색상이 호흡하듯 변화)"
    )


class HeadRequest(BaseModel):
    """
    머리 서보 제어 요청 모델
    
    로봇의 머리 부분에 장착된 서보 모터를 제어합니다.
    """
    servo_id: int = Field(
        ..., 
        ge=0, 
        le=1, 
        description="서보 ID. "
                   "0=수평 회전 서보 (좌우 회전), "
                   "1=수직 회전 서보 (상하 회전). "
                   "로봇의 머리 방향을 제어하는 서보 모터를 선택합니다."
    )
    angle: int = Field(
        ..., 
        ge=-90, 
        le=90, 
        description="서보 각도 (단위: 도). "
                   "범위: -90 ~ 90. "
                   "0도는 중앙 위치를 의미합니다. "
                   "수평 서보(servo_id=0)의 경우: 양수=오른쪽, 음수=왼쪽. "
                   "수직 서보(servo_id=1)의 경우: 양수=위쪽, 음수=아래쪽."
    )


class AttitudeRequest(BaseModel):
    """
    자세 각도 제어 요청 모델
    
    로봇의 전체 자세(기울기)를 제어합니다. 
    각 다리의 위치를 조정하여 로봇의 롤, 피치, 요 각도를 변경합니다.
    """
    roll: int = Field(
        ..., 
        ge=-15, 
        le=15, 
        description="롤(Roll) 각도 (단위: 도). "
                   "범위: -15 ~ 15. "
                   "로봇을 좌우로 기울이는 각도입니다. "
                   "양수 값은 오른쪽으로 기울임, 음수 값은 왼쪽으로 기울임을 의미합니다."
    )
    pitch: int = Field(
        ..., 
        ge=-15, 
        le=15, 
        description="피치(Pitch) 각도 (단위: 도). "
                   "범위: -15 ~ 15. "
                   "로봇을 앞뒤로 기울이는 각도입니다. "
                   "양수 값은 앞으로 기울임, 음수 값은 뒤로 기울임을 의미합니다."
    )
    yaw: int = Field(
        ..., 
        ge=-15, 
        le=15, 
        description="요(Yaw) 각도 (단위: 도). "
                   "범위: -15 ~ 15. "
                   "로봇을 좌우로 회전시키는 각도입니다. "
                   "양수 값은 오른쪽으로 회전, 음수 값은 왼쪽으로 회전을 의미합니다."
    )


class PositionRequest(BaseModel):
    """
    위치 제어 요청 모델
    
    로봇의 몸체 위치를 상대적으로 이동시킵니다.
    모든 다리의 기준점을 동시에 이동시켜 로봇의 중심 위치를 변경합니다.
    """
    x: int = Field(
        ..., 
        ge=-40, 
        le=40, 
        description="X축 위치 오프셋 (단위: 미리미터). "
                   "범위: -40 ~ 40. "
                   "로봇 몸체를 앞뒤로 이동시킵니다. "
                   "양수 값은 앞으로 이동, 음수 값은 뒤로 이동을 의미합니다."
    )
    y: int = Field(
        ..., 
        ge=-40, 
        le=40, 
        description="Y축 위치 오프셋 (단위: 미리미터). "
                   "범위: -40 ~ 40. "
                   "로봇 몸체를 좌우로 이동시킵니다. "
                   "양수 값은 왼쪽으로 이동, 음수 값은 오른쪽으로 이동을 의미합니다."
    )
    z: int = Field(
        ..., 
        ge=-20, 
        le=20, 
        description="Z축 위치 오프셋 (단위: 미리미터). "
                   "범위: -20 ~ 20. "
                   "로봇 몸체의 높이를 조절합니다. "
                   "양수 값은 몸체를 올림, 음수 값은 몸체를 내림을 의미합니다. "
                   "기본 높이는 -25mm입니다."
    )


class CameraRequest(BaseModel):
    """
    카메라 뷰 제어 요청 모델
    
    카메라가 장착된 서보 모터를 제어하여 카메라의 시야각을 조절합니다.
    """
    x: int = Field(
        ..., 
        ge=-90, 
        le=90, 
        description="수평 각도 (단위: 도). "
                   "범위: -90 ~ 90. "
                   "카메라를 좌우로 회전시킵니다. "
                   "내부적으로 50~180 범위로 변환되어 서보 0번에 적용됩니다. "
                   "양수 값은 오른쪽, 음수 값은 왼쪽을 의미합니다."
    )
    y: int = Field(
        ..., 
        ge=-90, 
        le=90, 
        description="수직 각도 (단위: 도). "
                   "범위: -90 ~ 90. "
                   "카메라를 상하로 회전시킵니다. "
                   "내부적으로 0~180 범위로 변환되어 서보 1번에 적용됩니다. "
                   "양수 값은 위쪽, 음수 값은 아래쪽을 의미합니다."
    )


class BuzzerRequest(BaseModel):
    state: bool = Field(..., description="Buzzer state: true=on, false=off")


class BalanceRequest(BaseModel):
    enable: bool = Field(..., description="Balance function: true=enable, false=disable")


class ServoPowerRequest(BaseModel):
    power_on: bool = Field(..., description="Servo power: true=on, false=off")


# Sequential Command Models
class MoveCommandParams(BaseModel):
    mode: int = Field(..., ge=1, le=2)
    x: int = Field(..., ge=-35, le=35)
    y: int = Field(..., ge=-35, le=35)
    speed: int = Field(..., ge=2, le=10)
    angle: int = Field(0, ge=-10, le=10)


class HeadCommandParams(BaseModel):
    servo_id: int = Field(..., ge=0, le=1)
    angle: int = Field(..., ge=-90, le=90)


class WaitCommandParams(BaseModel):
    seconds: float = Field(..., gt=0, description="Wait duration in seconds")


class PostCommandParams(BaseModel):
    url: str = Field(..., description="URL to send POST request to")


class LEDCommandParams(BaseModel):
    r: int = Field(..., ge=0, le=255)
    g: int = Field(..., ge=0, le=255)
    b: int = Field(..., ge=0, le=255)


class LEDModeCommandParams(BaseModel):
    mode: int = Field(..., ge=0, le=5)


class BuzzerCommandParams(BaseModel):
    state: bool


class AttitudeCommandParams(BaseModel):
    roll: int = Field(..., ge=-15, le=15)
    pitch: int = Field(..., ge=-15, le=15)
    yaw: int = Field(..., ge=-15, le=15)


class PositionCommandParams(BaseModel):
    x: int = Field(..., ge=-40, le=40)
    y: int = Field(..., ge=-40, le=40)
    z: int = Field(..., ge=-20, le=20)


class CameraCommandParams(BaseModel):
    x: int = Field(..., ge=-90, le=90)
    y: int = Field(..., ge=-90, le=90)


class BalanceCommandParams(BaseModel):
    enable: bool


class ServoPowerCommandParams(BaseModel):
    power_on: bool


class MoveCommand(BaseModel):
    id: str = Field(..., description="Unique command identifier")
    type: Literal["move"] = "move"
    params: MoveCommandParams


class HeadCommand(BaseModel):
    id: str = Field(..., description="Unique command identifier")
    type: Literal["head"] = "head"
    params: HeadCommandParams


class WaitCommand(BaseModel):
    id: str = Field(..., description="Unique command identifier")
    type: Literal["wait"] = "wait"
    params: WaitCommandParams


class PostCommand(BaseModel):
    id: str = Field(..., description="Unique command identifier")
    type: Literal["post"] = "post"
    params: PostCommandParams


class LEDCommand(BaseModel):
    id: str = Field(..., description="Unique command identifier")
    type: Literal["led"] = "led"
    params: LEDCommandParams


class LEDModeCommand(BaseModel):
    id: str = Field(..., description="Unique command identifier")
    type: Literal["led_mode"] = "led_mode"
    params: LEDModeCommandParams


class BuzzerCommand(BaseModel):
    id: str = Field(..., description="Unique command identifier")
    type: Literal["buzzer"] = "buzzer"
    params: BuzzerCommandParams


class AttitudeCommand(BaseModel):
    id: str = Field(..., description="Unique command identifier")
    type: Literal["attitude"] = "attitude"
    params: AttitudeCommandParams


class PositionCommand(BaseModel):
    id: str = Field(..., description="Unique command identifier")
    type: Literal["position"] = "position"
    params: PositionCommandParams


class CameraCommand(BaseModel):
    id: str = Field(..., description="Unique command identifier")
    type: Literal["camera"] = "camera"
    params: CameraCommandParams


class BalanceCommand(BaseModel):
    id: str = Field(..., description="Unique command identifier")
    type: Literal["balance"] = "balance"
    params: BalanceCommandParams


class ServoPowerCommand(BaseModel):
    id: str = Field(..., description="Unique command identifier")
    type: Literal["servo_power"] = "servo_power"
    params: ServoPowerCommandParams


Command = Union[
    MoveCommand,
    HeadCommand,
    WaitCommand,
    PostCommand,
    LEDCommand,
    LEDModeCommand,
    BuzzerCommand,
    AttitudeCommand,
    PositionCommand,
    CameraCommand,
    BalanceCommand,
    ServoPowerCommand,
]


class CommandSequenceRequest(BaseModel):
    """
    순차 명령 실행 요청 모델
    
    명령어 배열을 받아서 순차적으로 실행합니다.
    각 명령은 고유한 ID를 가지며, POST 명령의 경우 해당 ID가 요청 본문에 포함됩니다.
    """
    commands: List[Command] = Field(..., min_length=1, description="실행할 명령어 배열")


# API Endpoints
@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "Hexapod Robot Control API",
        "version": "1.0.0",
        "status": "running"
    }


@app.post("/api/move")
async def move(request: MoveRequest):
    """
    로봇 이동 제어 엔드포인트
    
    로봇의 이동 방향, 속도, 각도를 제어합니다.
    두 가지 보행 모드를 지원하며, 각 모드는 다른 보행 패턴을 사용합니다.
    
    - 모드 1 (모션 모드): 트로트 보행으로 빠르고 부드러운 이동
    - 모드 2 (보행 모드): 순차 보행으로 안정적인 이동
    
    Args:
        request: MoveRequest 객체. 이동에 필요한 모든 파라미터를 포함합니다.
    
    Returns:
        dict: 명령 처리 결과. {"status": "success", "command": "CMD_MOVE"}
    
    Example:
        앞으로 직진 (속도 5):
        {
            "mode": 1,
            "x": 10,
            "y": 0,
            "speed": 5,
            "angle": 0
        }
        
        오른쪽으로 회전하며 이동:
        {
            "mode": 1,
            "x": 10,
            "y": 0,
            "speed": 5,
            "angle": 5
        }
        
        왼쪽으로 이동:
        {
            "mode": 1,
            "x": 0,
            "y": 10,
            "speed": 5,
            "angle": 0
        }
    """
    command_parts = [
        cmd.CMD_MOVE,
        str(request.mode),
        str(-request.y),
        str(request.x),
        str(request.speed),
        str(request.angle)
    ]
    return process_command(command_parts)


@app.post("/api/led")
async def set_led(request: LEDRequest):
    """
    LED 색상 설정 엔드포인트
    
    RGB 값을 사용하여 LED의 색상을 설정합니다.
    이 엔드포인트는 LED 모드가 1(지정 색상) 또는 3(깜빡임 모드)일 때만 효과가 있습니다.
    다른 모드에서는 LED 모드 설정 API를 먼저 호출해야 합니다.
    
    Args:
        request: LEDRequest 객체. RGB 색상 값을 포함합니다.
    
    Returns:
        dict: 명령 처리 결과. {"status": "success", "command": "CMD_LED"}
    
    Note:
        LED 모드를 먼저 설정하지 않으면 색상이 적용되지 않을 수 있습니다.
    """
    command_parts = [
        cmd.CMD_LED,
        str(request.r),
        str(request.g),
        str(request.b)
    ]
    return process_command(command_parts)


@app.post("/api/led/mode")
async def set_led_mode(request: LEDModeRequest):
    """Set LED mode"""
    command_parts = [cmd.CMD_LED_MOD, str(request.mode)]
    return process_command(command_parts)


@app.get("/api/ultrasonic")
async def get_ultrasonic():
    """Get ultrasonic distance measurement"""
    command_parts = [cmd.CMD_SONIC]
    return process_command(command_parts)


@app.post("/api/buzzer")
async def set_buzzer(request: BuzzerRequest):
    """Control buzzer"""
    command_parts = [cmd.CMD_BUZZER, "1" if request.state else "0"]
    return process_command(command_parts)


@app.post("/api/head")
async def set_head(request: HeadRequest):
    """Control head servos"""
    command_parts = [
        cmd.CMD_HEAD,
        str(request.servo_id),
        str(request.angle)
    ]
    return process_command(command_parts)


@app.post("/api/balance")
async def set_balance(request: BalanceRequest):
    """Enable/disable balance function"""
    command_parts = [cmd.CMD_BALANCE, "1" if request.enable else "0"]
    return process_command(command_parts)


@app.post("/api/attitude")
async def set_attitude(request: AttitudeRequest):
    """
    자세 각도 제어 엔드포인트
    
    로봇의 전체 자세(기울기)를 제어합니다.
    각 다리의 위치를 조정하여 로봇의 롤, 피치, 요 각도를 변경합니다.
    경사면에서 균형을 맞추거나 특정 자세를 취할 때 사용합니다.
    
    Args:
        request: AttitudeRequest 객체. 롤, 피치, 요 각도를 포함합니다.
    
    Returns:
        dict: 명령 처리 결과. {"status": "success", "command": "CMD_ATTITUDE"}
    
    Note:
        각도 범위는 -15도에서 15도로 제한되어 있습니다.
        이 범위를 벗어나면 로봇이 불안정해질 수 있습니다.
    """
    command_parts = [
        cmd.CMD_ATTITUDE,
        str(request.roll),
        str(request.pitch),
        str(request.yaw)
    ]
    return process_command(command_parts)


@app.post("/api/position")
async def set_position(request: PositionRequest):
    """
    로봇 위치 제어 엔드포인트
    
    로봇의 몸체 위치를 상대적으로 이동시킵니다.
    모든 다리의 기준점을 동시에 이동시켜 로봇의 중심 위치를 변경합니다.
    이동 명령과 달리 한 번의 명령으로 즉시 위치를 변경합니다.
    
    Args:
        request: PositionRequest 객체. X, Y, Z 축 위치 오프셋을 포함합니다.
    
    Returns:
        dict: 명령 처리 결과. {"status": "success", "command": "CMD_POSITION"}
    
    Note:
        이 명령은 로봇의 자세를 변경하지 않고 위치만 이동시킵니다.
        몸체를 높이거나 낮추려면 z 값을 조정하세요.
    """
    command_parts = [
        cmd.CMD_POSITION,
        str(-request.y),
        str(request.x),
        str(request.z)
    ]
    return process_command(command_parts)


@app.post("/api/camera")
async def set_camera(request: CameraRequest):
    """Control camera view"""
    command_parts = [
        cmd.CMD_CAMERA,
        str(request.x),
        str(request.y)
    ]
    return process_command(command_parts)


@app.post("/api/relax")
async def toggle_relax():
    """Toggle servo relax state"""
    command_parts = [cmd.CMD_RELAX]
    return process_command(command_parts)


@app.get("/api/power")
async def get_power():
    """Get battery voltage"""
    command_parts = [cmd.CMD_POWER]
    return process_command(command_parts)


@app.post("/api/servo/power")
async def set_servo_power(request: ServoPowerRequest):
    """Control servo power"""
    command_parts = [cmd.CMD_SERVOPOWER, "1" if request.power_on else "0"]
    return process_command(command_parts)


@app.get("/api/status")
async def get_status():
    """Get robot status"""
    return {
        "status": "online",
        "servo_relaxed": robot_server.is_servo_relaxed if robot_server else None,
        "tcp_active": robot_server.is_tcp_active if robot_server else None
    }


async def execute_command(command: Command) -> dict:
    """
    Execute a single command
    
    Args:
        command: Command object to execute
    
    Returns:
        dict: Execution result with status and command info
    
    Raises:
        HTTPException: If command execution fails
    """
    if robot_server is None:
        raise HTTPException(status_code=503, detail="Robot server not initialized")
    
    try:
        if isinstance(command, MoveCommand):
            command_parts = [
                cmd.CMD_MOVE,
                str(command.params.mode),
                str(-command.params.y),
                str(command.params.x),
                str(command.params.speed),
                str(command.params.angle)
            ]
            result = process_command(command_parts)
            return {"id": command.id, "status": "success", "command": "move", **result}
        
        elif isinstance(command, HeadCommand):
            command_parts = [
                cmd.CMD_HEAD,
                str(command.params.servo_id),
                str(command.params.angle)
            ]
            result = process_command(command_parts)
            return {"id": command.id, "status": "success", "command": "head", **result}
        
        elif isinstance(command, WaitCommand):
            await asyncio.sleep(command.params.seconds)
            return {"id": command.id, "status": "success", "command": "wait"}
        
        elif isinstance(command, PostCommand):
            if not HTTPX_AVAILABLE:
                raise HTTPException(
                    status_code=500,
                    detail="httpx library is required for POST commands. Please install it with: pip install httpx"
                )
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    command.params.url,
                    json={"command_id": command.id}
                )
                response.raise_for_status()
            return {
                "id": command.id,
                "status": "success",
                "command": "post",
                "response_status": response.status_code
            }
        
        elif isinstance(command, LEDCommand):
            command_parts = [
                cmd.CMD_LED,
                str(command.params.r),
                str(command.params.g),
                str(command.params.b)
            ]
            result = process_command(command_parts)
            return {"id": command.id, "status": "success", "command": "led", **result}
        
        elif isinstance(command, LEDModeCommand):
            command_parts = [cmd.CMD_LED_MOD, str(command.params.mode)]
            result = process_command(command_parts)
            return {"id": command.id, "status": "success", "command": "led_mode", **result}
        
        elif isinstance(command, BuzzerCommand):
            command_parts = [cmd.CMD_BUZZER, "1" if command.params.state else "0"]
            result = process_command(command_parts)
            return {"id": command.id, "status": "success", "command": "buzzer", **result}
        
        elif isinstance(command, AttitudeCommand):
            command_parts = [
                cmd.CMD_ATTITUDE,
                str(command.params.roll),
                str(command.params.pitch),
                str(command.params.yaw)
            ]
            result = process_command(command_parts)
            return {"id": command.id, "status": "success", "command": "attitude", **result}
        
        elif isinstance(command, PositionCommand):
            command_parts = [
                cmd.CMD_POSITION,
                str(-command.params.y),
                str(command.params.x),
                str(command.params.z)
            ]
            result = process_command(command_parts)
            return {"id": command.id, "status": "success", "command": "position", **result}
        
        elif isinstance(command, CameraCommand):
            command_parts = [
                cmd.CMD_CAMERA,
                str(command.params.x),
                str(command.params.y)
            ]
            result = process_command(command_parts)
            return {"id": command.id, "status": "success", "command": "camera", **result}
        
        elif isinstance(command, BalanceCommand):
            command_parts = [cmd.CMD_BALANCE, "1" if command.params.enable else "0"]
            result = process_command(command_parts)
            return {"id": command.id, "status": "success", "command": "balance", **result}
        
        elif isinstance(command, ServoPowerCommand):
            command_parts = [cmd.CMD_SERVOPOWER, "1" if command.params.power_on else "0"]
            result = process_command(command_parts)
            return {"id": command.id, "status": "success", "command": "servo_power", **result}
        
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown command type: {command.type if hasattr(command, 'type') else 'unknown'}"
            )
    
    except HTTPException:
        raise
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=500,
            detail=f"HTTP request failed for command {command.id}: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to execute command {command.id}: {str(e)}"
        )


async def execute_move_with_wait(move_cmd: MoveCommand, wait_cmd: WaitCommand) -> List[dict]:
    """
    Execute move command followed by wait, then stop movement
    
    Args:
        move_cmd: Move command to execute
        wait_cmd: Wait command with duration
    
    Returns:
        List of execution results
    """
    results = []
    
    # Start movement
    move_result = await execute_command(move_cmd)
    results.append(move_result)
    
    # Wait for duration
    wait_result = await execute_command(wait_cmd)
    results.append(wait_result)
    
    # Stop movement by sending move command with x=0, y=0
    stop_command = MoveCommand(
        id=f"{move_cmd.id}_stop",
        type="move",
        params=MoveCommandParams(
            mode=move_cmd.params.mode,
            x=0,
            y=0,
            speed=move_cmd.params.speed,
            angle=0
        )
    )
    stop_result = await execute_command(stop_command)
    results.append(stop_result)
    
    return results


@app.post("/api/commands/sequence")
async def execute_command_sequence(request: CommandSequenceRequest):
    """
    순차 명령 실행 엔드포인트
    
    명령어 배열을 받아서 순차적으로 실행합니다.
    각 명령은 고유한 ID를 가지며, POST 명령의 경우 해당 ID가 요청 본문에 포함됩니다.
    
    Args:
        request: CommandSequenceRequest 객체. 실행할 명령어 배열을 포함합니다.
    
    Returns:
        dict: 실행 결과. 각 명령의 실행 상태를 포함합니다.
    
    Example:
        {
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
                }
            ]
        }
    """
    if robot_server is None:
        raise HTTPException(status_code=503, detail="Robot server not initialized")
    
    results = []
    i = 0
    
    try:
        while i < len(request.commands):
            command = request.commands[i]
            
            # Check if this is a move command followed by a wait command
            if isinstance(command, MoveCommand) and i + 1 < len(request.commands):
                next_command = request.commands[i + 1]
                if isinstance(next_command, WaitCommand):
                    # Execute move + wait + stop sequence
                    move_wait_results = await execute_move_with_wait(command, next_command)
                    results.extend(move_wait_results)
                    i += 2  # Skip both move and wait commands
                    continue
            
            # Execute single command
            result = await execute_command(command)
            results.append(result)
            i += 1
        
        return {
            "status": "success",
            "executed_commands": len(results),
            "results": results
        }
    
    except HTTPException as e:
        # Return partial results if error occurred
        return {
            "status": "error",
            "executed_commands": len(results),
            "results": results,
            "error": {
                "message": e.detail,
                "status_code": e.status_code
            }
        }

