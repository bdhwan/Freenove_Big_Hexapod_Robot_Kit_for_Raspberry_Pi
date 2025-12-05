# -*- coding: utf-8 -*-
"""
MCP Server for Hexapod Robot Control
Provides Model Context Protocol interface for controlling the hexapod robot
"""
import asyncio
import sys
from typing import Any, Optional
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import json

# Import robot control functions from rest_api
try:
    from rest_api import (
        robot_server,
        set_server,
        process_command,
        MoveRequest,
        LEDRequest,
        LEDModeRequest,
        HeadRequest,
        AttitudeRequest,
        PositionRequest,
        CameraRequest,
        BuzzerRequest,
        BalanceRequest,
        ServoPowerRequest,
        CommandSequenceRequest,
        execute_command_sequence,
    )
except ImportError as e:
    print(f"Error importing rest_api: {e}", file=sys.stderr)
    print("Make sure rest_api.py is in the same directory", file=sys.stderr)
    sys.exit(1)
from server import Server as RobotServer
from command import COMMAND as cmd

# Initialize MCP server
mcp_server = Server("hexapod-robot-control")

# Initialize robot server if not already initialized
_robot_server_initialized = False

def ensure_robot_server():
    """Ensure robot server is initialized"""
    global _robot_server_initialized
    if robot_server is None and not _robot_server_initialized:
        try:
            robot_server_instance = RobotServer()
            set_server(robot_server_instance)
            _robot_server_initialized = True
            print("Robot server initialized for MCP", file=sys.stderr)
        except Exception as e:
            print(f"Warning: Could not initialize robot server: {e}", file=sys.stderr)
            print("Some tools may not work properly", file=sys.stderr)

# Try to initialize on import
ensure_robot_server()


@mcp_server.list_tools()
async def list_tools() -> list[Tool]:
    """
    List all available tools for robot control
    """
    return [
        Tool(
            name="robot_move",
            description="로봇을 이동시킵니다. mode(1=모션모드, 2=보행모드), x(-35~35), y(-35~35), speed(2~10), angle(-10~10) 파라미터를 사용합니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "mode": {
                        "type": "integer",
                        "description": "이동 모드: 1=모션 모드(트로트 보행), 2=보행 모드(순차 보행)",
                        "minimum": 1,
                        "maximum": 2
                    },
                    "x": {
                        "type": "integer",
                        "description": "X축 스텝 길이 (mm). 양수=앞으로, 음수=뒤로",
                        "minimum": -35,
                        "maximum": 35
                    },
                    "y": {
                        "type": "integer",
                        "description": "Y축 스텝 길이 (mm). 양수=왼쪽으로, 음수=오른쪽으로",
                        "minimum": -35,
                        "maximum": 35
                    },
                    "speed": {
                        "type": "integer",
                        "description": "속도 (2=가장 느림, 10=가장 빠름)",
                        "minimum": 2,
                        "maximum": 10
                    },
                    "angle": {
                        "type": "integer",
                        "description": "이동 각도 (도). 양수=오른쪽 회전, 음수=왼쪽 회전",
                        "minimum": -10,
                        "maximum": 10,
                        "default": 0
                    }
                },
                "required": ["mode", "x", "y", "speed"]
            }
        ),
        Tool(
            name="robot_set_led_color",
            description="LED 색상을 설정합니다. RGB 값(0-255)을 사용합니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "r": {
                        "type": "integer",
                        "description": "빨강 값 (0-255)",
                        "minimum": 0,
                        "maximum": 255
                    },
                    "g": {
                        "type": "integer",
                        "description": "초록 값 (0-255)",
                        "minimum": 0,
                        "maximum": 255
                    },
                    "b": {
                        "type": "integer",
                        "description": "파랑 값 (0-255)",
                        "minimum": 0,
                        "maximum": 255
                    }
                },
                "required": ["r", "g", "b"]
            }
        ),
        Tool(
            name="robot_set_led_mode",
            description="LED 모드를 설정합니다. 0=꺼짐, 1=지정색상, 2=추적, 3=깜빡임, 4=호흡, 5=무지개호흡",
            inputSchema={
                "type": "object",
                "properties": {
                    "mode": {
                        "type": "integer",
                        "description": "LED 모드: 0=꺼짐, 1=지정색상, 2=추적, 3=깜빡임, 4=호흡, 5=무지개호흡",
                        "minimum": 0,
                        "maximum": 5
                    }
                },
                "required": ["mode"]
            }
        ),
        Tool(
            name="robot_set_head",
            description="머리 서보를 제어합니다. servo_id(0=수평, 1=수직), angle(-90~90) 파라미터를 사용합니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "servo_id": {
                        "type": "integer",
                        "description": "서보 ID: 0=수평 회전, 1=수직 회전",
                        "minimum": 0,
                        "maximum": 1
                    },
                    "angle": {
                        "type": "integer",
                        "description": "각도 (도). -90~90",
                        "minimum": -90,
                        "maximum": 90
                    }
                },
                "required": ["servo_id", "angle"]
            }
        ),
        Tool(
            name="robot_set_attitude",
            description="로봇의 자세 각도를 설정합니다. roll, pitch, yaw 각도(-15~15도)를 사용합니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "roll": {
                        "type": "integer",
                        "description": "롤 각도 (도). 양수=오른쪽 기울임",
                        "minimum": -15,
                        "maximum": 15
                    },
                    "pitch": {
                        "type": "integer",
                        "description": "피치 각도 (도). 양수=앞으로 기울임",
                        "minimum": -15,
                        "maximum": 15
                    },
                    "yaw": {
                        "type": "integer",
                        "description": "요 각도 (도). 양수=오른쪽 회전",
                        "minimum": -15,
                        "maximum": 15
                    }
                },
                "required": ["roll", "pitch", "yaw"]
            }
        ),
        Tool(
            name="robot_set_position",
            description="로봇의 몸체 위치를 이동시킵니다. x(-40~40), y(-40~40), z(-20~20) mm 오프셋을 사용합니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "x": {
                        "type": "integer",
                        "description": "X축 위치 오프셋 (mm). 양수=앞으로",
                        "minimum": -40,
                        "maximum": 40
                    },
                    "y": {
                        "type": "integer",
                        "description": "Y축 위치 오프셋 (mm). 양수=왼쪽으로",
                        "minimum": -40,
                        "maximum": 40
                    },
                    "z": {
                        "type": "integer",
                        "description": "Z축 위치 오프셋 (mm). 양수=올림",
                        "minimum": -20,
                        "maximum": 20
                    }
                },
                "required": ["x", "y", "z"]
            }
        ),
        Tool(
            name="robot_set_camera",
            description="카메라 뷰를 제어합니다. x(-90~90), y(-90~90) 각도를 사용합니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "x": {
                        "type": "integer",
                        "description": "수평 각도 (도). 양수=오른쪽",
                        "minimum": -90,
                        "maximum": 90
                    },
                    "y": {
                        "type": "integer",
                        "description": "수직 각도 (도). 양수=위쪽",
                        "minimum": -90,
                        "maximum": 90
                    }
                },
                "required": ["x", "y"]
            }
        ),
        Tool(
            name="robot_set_buzzer",
            description="부저를 켜거나 끕니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "state": {
                        "type": "boolean",
                        "description": "부저 상태: true=켜기, false=끄기"
                    }
                },
                "required": ["state"]
            }
        ),
        Tool(
            name="robot_set_balance",
            description="밸런스 기능을 활성화하거나 비활성화합니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "enable": {
                        "type": "boolean",
                        "description": "밸런스 기능: true=활성화, false=비활성화"
                    }
                },
                "required": ["enable"]
            }
        ),
        Tool(
            name="robot_set_servo_power",
            description="서보 전원을 켜거나 끕니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "power_on": {
                        "type": "boolean",
                        "description": "서보 전원: true=켜기, false=끄기"
                    }
                },
                "required": ["power_on"]
            }
        ),
        Tool(
            name="robot_get_ultrasonic",
            description="초음파 센서로 거리를 측정합니다.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="robot_get_power",
            description="배터리 전압을 조회합니다.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="robot_get_status",
            description="로봇의 현재 상태를 조회합니다.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="robot_execute_sequence",
            description="여러 명령을 순차적으로 실행합니다. commands 배열에 실행할 명령들을 포함합니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "commands": {
                        "type": "array",
                        "description": "실행할 명령어 배열",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string"},
                                "type": {"type": "string"},
                                "params": {"type": "object"}
                            },
                            "required": ["id", "type", "params"]
                        }
                    }
                },
                "required": ["commands"]
            }
        ),
    ]


@mcp_server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any] | None) -> list[TextContent]:
    """
    Execute robot control tools
    """
    # Ensure robot server is initialized
    ensure_robot_server()
    
    if arguments is None:
        arguments = {}
    
    # Check if robot server is available
    if robot_server is None:
        error_msg = {
            "error": "Robot server not initialized",
            "tool": name,
            "message": "Please ensure the robot hardware is connected and the server can be initialized"
        }
        return [TextContent(type="text", text=json.dumps(error_msg, ensure_ascii=False, indent=2))]
    
    try:
        if name == "robot_move":
            request = MoveRequest(**arguments)
            command_parts = [
                cmd.CMD_MOVE,
                str(request.mode),
                str(request.x),
                str(request.y),
                str(request.speed),
                str(request.angle)
            ]
            result = process_command(command_parts)
            return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
        
        elif name == "robot_set_led_color":
            request = LEDRequest(**arguments)
            command_parts = [
                cmd.CMD_LED,
                str(request.r),
                str(request.g),
                str(request.b)
            ]
            result = process_command(command_parts)
            return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
        
        elif name == "robot_set_led_mode":
            request = LEDModeRequest(**arguments)
            command_parts = [cmd.CMD_LED_MOD, str(request.mode)]
            result = process_command(command_parts)
            return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
        
        elif name == "robot_set_head":
            request = HeadRequest(**arguments)
            command_parts = [
                cmd.CMD_HEAD,
                str(request.servo_id),
                str(request.angle)
            ]
            result = process_command(command_parts)
            return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
        
        elif name == "robot_set_attitude":
            request = AttitudeRequest(**arguments)
            command_parts = [
                cmd.CMD_ATTITUDE,
                str(request.roll),
                str(request.pitch),
                str(request.yaw)
            ]
            result = process_command(command_parts)
            return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
        
        elif name == "robot_set_position":
            request = PositionRequest(**arguments)
            command_parts = [
                cmd.CMD_POSITION,
                str(request.x),
                str(request.y),
                str(request.z)
            ]
            result = process_command(command_parts)
            return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
        
        elif name == "robot_set_camera":
            request = CameraRequest(**arguments)
            command_parts = [
                cmd.CMD_CAMERA,
                str(request.x),
                str(request.y)
            ]
            result = process_command(command_parts)
            return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
        
        elif name == "robot_set_buzzer":
            request = BuzzerRequest(**arguments)
            command_parts = [cmd.CMD_BUZZER, "1" if request.state else "0"]
            result = process_command(command_parts)
            return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
        
        elif name == "robot_set_balance":
            request = BalanceRequest(**arguments)
            command_parts = [cmd.CMD_BALANCE, "1" if request.enable else "0"]
            result = process_command(command_parts)
            return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
        
        elif name == "robot_set_servo_power":
            request = ServoPowerRequest(**arguments)
            command_parts = [cmd.CMD_SERVOPOWER, "1" if request.power_on else "0"]
            result = process_command(command_parts)
            return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
        
        elif name == "robot_get_ultrasonic":
            command_parts = [cmd.CMD_SONIC]
            result = process_command(command_parts)
            return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
        
        elif name == "robot_get_power":
            command_parts = [cmd.CMD_POWER]
            result = process_command(command_parts)
            return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
        
        elif name == "robot_get_status":
            status = {
                "status": "online",
                "servo_relaxed": robot_server.is_servo_relaxed if robot_server else None,
                "tcp_active": robot_server.is_tcp_active if robot_server else None
            }
            return [TextContent(type="text", text=json.dumps(status, ensure_ascii=False, indent=2))]
        
        elif name == "robot_execute_sequence":
            request = CommandSequenceRequest(**arguments)
            try:
                result = await execute_command_sequence(request)
            except Exception as e:
                # Handle HTTPException from execute_command_sequence
                if hasattr(e, 'detail'):
                    result = {
                        "status": "error",
                        "error": {
                            "message": str(e.detail),
                            "status_code": getattr(e, 'status_code', 500)
                        }
                    }
                else:
                    result = {
                        "status": "error",
                        "error": {
                            "message": str(e)
                        }
                    }
            return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
        
        else:
            return [TextContent(type="text", text=json.dumps({"error": f"Unknown tool: {name}"}, ensure_ascii=False, indent=2))]
    
    except Exception as e:
        import traceback
        error_msg = {
            "error": str(e),
            "tool": name,
            "arguments": arguments,
            "traceback": traceback.format_exc() if robot_server is None else None
        }
        return [TextContent(type="text", text=json.dumps(error_msg, ensure_ascii=False, indent=2))]


async def main():
    """
    Main entry point for MCP server
    """
    async with stdio_server() as (read_stream, write_stream):
        await mcp_server.run(
            read_stream,
            write_stream,
            mcp_server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())

