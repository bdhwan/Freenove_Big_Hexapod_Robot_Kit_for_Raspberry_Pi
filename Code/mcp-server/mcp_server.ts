#!/usr/bin/env node
/**
 * MCP Server for Hexapod Robot Control
 * Node.js based MCP server that calls remote REST API
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  Tool,
} from "@modelcontextprotocol/sdk/types.js";
import axios, { AxiosInstance } from "axios";

// Get REST API URL from environment variable
const REST_API_URL = process.env.ROBOT_REST_API_URL || "http://localhost:8000";

// Create axios instance with base URL
const apiClient: AxiosInstance = axios.create({
  baseURL: REST_API_URL,
  timeout: 10000,
  headers: {
    "Content-Type": "application/json",
  },
});

// MCP Server instance
const server = new Server(
  {
    name: "hexapod-robot-control",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

/**
 * List all available tools
 */
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: "robot_move",
        description:
          "로봇을 이동시킵니다. mode(1=모션모드, 2=보행모드), x(-35~35), y(-35~35), speed(2~10), angle(-10~10) 파라미터를 사용합니다.",
        inputSchema: {
          type: "object",
          properties: {
            mode: {
              type: "integer",
              description: "이동 모드: 1=모션 모드(트로트 보행), 2=보행 모드(순차 보행)",
              minimum: 1,
              maximum: 2,
            },
            x: {
              type: "integer",
              description: "X축 스텝 길이 (mm). 양수=앞으로, 음수=뒤로",
              minimum: -35,
              maximum: 35,
            },
            y: {
              type: "integer",
              description: "Y축 스텝 길이 (mm). 양수=왼쪽으로, 음수=오른쪽으로",
              minimum: -35,
              maximum: 35,
            },
            speed: {
              type: "integer",
              description: "속도 (2=가장 느림, 10=가장 빠름)",
              minimum: 2,
              maximum: 10,
            },
            angle: {
              type: "integer",
              description: "이동 각도 (도). 양수=오른쪽 회전, 음수=왼쪽 회전",
              minimum: -10,
              maximum: 10,
              default: 0,
            },
          },
          required: ["mode", "x", "y", "speed"],
        },
      },
      {
        name: "robot_set_led_color",
        description: "LED 색상을 설정합니다. RGB 값(0-255)을 사용합니다.",
        inputSchema: {
          type: "object",
          properties: {
            r: {
              type: "integer",
              description: "빨강 값 (0-255)",
              minimum: 0,
              maximum: 255,
            },
            g: {
              type: "integer",
              description: "초록 값 (0-255)",
              minimum: 0,
              maximum: 255,
            },
            b: {
              type: "integer",
              description: "파랑 값 (0-255)",
              minimum: 0,
              maximum: 255,
            },
          },
          required: ["r", "g", "b"],
        },
      },
      {
        name: "robot_set_led_mode",
        description:
          "LED 모드를 설정합니다. 0=꺼짐, 1=지정색상, 2=추적, 3=깜빡임, 4=호흡, 5=무지개호흡",
        inputSchema: {
          type: "object",
          properties: {
            mode: {
              type: "integer",
              description:
                "LED 모드: 0=꺼짐, 1=지정색상, 2=추적, 3=깜빡임, 4=호흡, 5=무지개호흡",
              minimum: 0,
              maximum: 5,
            },
          },
          required: ["mode"],
        },
      },
      {
        name: "robot_set_head",
        description:
          "머리 서보를 제어합니다. servo_id(0=수평, 1=수직), angle(-90~90) 파라미터를 사용합니다.",
        inputSchema: {
          type: "object",
          properties: {
            servo_id: {
              type: "integer",
              description: "서보 ID: 0=수평 회전, 1=수직 회전",
              minimum: 0,
              maximum: 1,
            },
            angle: {
              type: "integer",
              description: "각도 (도). -90~90",
              minimum: -90,
              maximum: 90,
            },
          },
          required: ["servo_id", "angle"],
        },
      },
      {
        name: "robot_set_attitude",
        description:
          "로봇의 자세 각도를 설정합니다. roll, pitch, yaw 각도(-15~15도)를 사용합니다.",
        inputSchema: {
          type: "object",
          properties: {
            roll: {
              type: "integer",
              description: "롤 각도 (도). 양수=오른쪽 기울임",
              minimum: -15,
              maximum: 15,
            },
            pitch: {
              type: "integer",
              description: "피치 각도 (도). 양수=앞으로 기울임",
              minimum: -15,
              maximum: 15,
            },
            yaw: {
              type: "integer",
              description: "요 각도 (도). 양수=오른쪽 회전",
              minimum: -15,
              maximum: 15,
            },
          },
          required: ["roll", "pitch", "yaw"],
        },
      },
      {
        name: "robot_set_position",
        description:
          "로봇의 몸체 위치를 이동시킵니다. x(-40~40), y(-40~40), z(-20~20) mm 오프셋을 사용합니다.",
        inputSchema: {
          type: "object",
          properties: {
            x: {
              type: "integer",
              description: "X축 위치 오프셋 (mm). 양수=앞으로",
              minimum: -40,
              maximum: 40,
            },
            y: {
              type: "integer",
              description: "Y축 위치 오프셋 (mm). 양수=왼쪽으로",
              minimum: -40,
              maximum: 40,
            },
            z: {
              type: "integer",
              description: "Z축 위치 오프셋 (mm). 양수=올림",
              minimum: -20,
              maximum: 20,
            },
          },
          required: ["x", "y", "z"],
        },
      },
      {
        name: "robot_set_camera",
        description: "카메라 뷰를 제어합니다. x(-90~90), y(-90~90) 각도를 사용합니다.",
        inputSchema: {
          type: "object",
          properties: {
            x: {
              type: "integer",
              description: "수평 각도 (도). 양수=오른쪽",
              minimum: -90,
              maximum: 90,
            },
            y: {
              type: "integer",
              description: "수직 각도 (도). 양수=위쪽",
              minimum: -90,
              maximum: 90,
            },
          },
          required: ["x", "y"],
        },
      },
      {
        name: "robot_set_buzzer",
        description: "부저를 켜거나 끕니다.",
        inputSchema: {
          type: "object",
          properties: {
            state: {
              type: "boolean",
              description: "부저 상태: true=켜기, false=끄기",
            },
          },
          required: ["state"],
        },
      },
      {
        name: "robot_set_balance",
        description: "밸런스 기능을 활성화하거나 비활성화합니다.",
        inputSchema: {
          type: "object",
          properties: {
            enable: {
              type: "boolean",
              description: "밸런스 기능: true=활성화, false=비활성화",
            },
          },
          required: ["enable"],
        },
      },
      {
        name: "robot_set_servo_power",
        description: "서보 전원을 켜거나 끕니다.",
        inputSchema: {
          type: "object",
          properties: {
            power_on: {
              type: "boolean",
              description: "서보 전원: true=켜기, false=끄기",
            },
          },
          required: ["power_on"],
        },
      },
      {
        name: "robot_get_ultrasonic",
        description: "초음파 센서로 거리를 측정합니다.",
        inputSchema: {
          type: "object",
          properties: {},
        },
      },
      {
        name: "robot_get_power",
        description: "배터리 전압을 조회합니다.",
        inputSchema: {
          type: "object",
          properties: {},
        },
      },
      {
        name: "robot_get_status",
        description: "로봇의 현재 상태를 조회합니다.",
        inputSchema: {
          type: "object",
          properties: {},
        },
      },
      {
        name: "robot_execute_sequence",
        description:
          "여러 명령을 순차적으로 실행합니다. commands 배열에 실행할 명령들을 포함합니다.",
        inputSchema: {
          type: "object",
          properties: {
            commands: {
              type: "array",
              description: "실행할 명령어 배열",
              items: {
                type: "object",
                properties: {
                  id: { type: "string" },
                  type: { type: "string" },
                  params: { type: "object" },
                },
                required: ["id", "type", "params"],
              },
            },
          },
          required: ["commands"],
        },
      },
    ],
  };
});

/**
 * Handle tool calls
 */
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    let response;

    switch (name) {
      case "robot_move":
        response = await apiClient.post("/api/move", {
          mode: args.mode,
          x: args.x,
          y: args.y,
          speed: args.speed,
          angle: args.angle ?? 0,
        });
        break;

      case "robot_set_led_color":
        response = await apiClient.post("/api/led", {
          r: args.r,
          g: args.g,
          b: args.b,
        });
        break;

      case "robot_set_led_mode":
        response = await apiClient.post("/api/led/mode", {
          mode: args.mode,
        });
        break;

      case "robot_set_head":
        response = await apiClient.post("/api/head", {
          servo_id: args.servo_id,
          angle: args.angle,
        });
        break;

      case "robot_set_attitude":
        response = await apiClient.post("/api/attitude", {
          roll: args.roll,
          pitch: args.pitch,
          yaw: args.yaw,
        });
        break;

      case "robot_set_position":
        response = await apiClient.post("/api/position", {
          x: args.x,
          y: args.y,
          z: args.z,
        });
        break;

      case "robot_set_camera":
        response = await apiClient.post("/api/camera", {
          x: args.x,
          y: args.y,
        });
        break;

      case "robot_set_buzzer":
        response = await apiClient.post("/api/buzzer", {
          state: args.state,
        });
        break;

      case "robot_set_balance":
        response = await apiClient.post("/api/balance", {
          enable: args.enable,
        });
        break;

      case "robot_set_servo_power":
        response = await apiClient.post("/api/servo/power", {
          power_on: args.power_on,
        });
        break;

      case "robot_get_ultrasonic":
        response = await apiClient.get("/api/ultrasonic");
        break;

      case "robot_get_power":
        response = await apiClient.get("/api/power");
        break;

      case "robot_get_status":
        response = await apiClient.get("/api/status");
        break;

      case "robot_execute_sequence":
        response = await apiClient.post("/api/commands/sequence", {
          commands: args.commands,
        });
        break;

      default:
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(
                {
                  error: `Unknown tool: ${name}`,
                },
                null,
                2
              ),
            },
          ],
          isError: true,
        };
    }

    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(response.data, null, 2),
        },
      ],
    };
  } catch (error: any) {
    const errorMessage =
      error.response?.data?.detail ||
      error.message ||
      "Unknown error occurred";
    const statusCode = error.response?.status || 500;

    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(
            {
              error: errorMessage,
              statusCode: statusCode,
              tool: name,
              arguments: args,
              apiUrl: REST_API_URL,
            },
            null,
            2
          ),
        },
      ],
      isError: true,
    };
  }
});

/**
 * Main function
 */
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);

  console.error(`Hexapod Robot MCP Server started`);
  console.error(`REST API URL: ${REST_API_URL}`);
}

main().catch((error) => {
  console.error("Fatal error:", error);
  process.exit(1);
});

