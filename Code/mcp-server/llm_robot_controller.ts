#!/usr/bin/env node
/**
 * LLM Robot Controller
 * 자연어 명령을 LLM을 통해 해석하고 MCP를 통해 로봇을 제어합니다.
 * 
 * 사용법:
 *   - Ollama 사용: LLM_PROVIDER=ollama LLM_MODEL=llama3.2 npm run llm-controller
 *   - OpenAI 사용: LLM_PROVIDER=openai LLM_API_KEY=your-key npm run llm-controller
 */

import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";
import axios from "axios";
import * as readline from "readline";

// 환경 변수 설정
const LLM_PROVIDER = process.env.LLM_PROVIDER || "ollama"; // "ollama" or "openai"
const LLM_MODEL = process.env.LLM_MODEL || "llama3.2"; // Ollama 모델명
const OPENAI_API_KEY = process.env.OPENAI_API_KEY || "";
const OPENAI_MODEL = process.env.OPENAI_MODEL || "gpt-4o-mini";
const OLLAMA_BASE_URL = process.env.OLLAMA_BASE_URL || "http://localhost:11434";
const MCP_SERVER_COMMAND = process.env.MCP_SERVER_COMMAND || "node";
const MCP_SERVER_PATH = process.env.MCP_SERVER_PATH || "./dist/mcp_server.js";

// MCP 클라이언트 초기화
let mcpClient: Client | null = null;

/**
 * MCP 클라이언트 초기화
 */
async function initializeMCPClient(): Promise<Client> {
  const transport = new StdioClientTransport({
    command: MCP_SERVER_COMMAND,
    args: [MCP_SERVER_PATH],
    env: {
      ROBOT_REST_API_URL: process.env.ROBOT_REST_API_URL || "http://localhost:8000",
    },
  });

  const client = new Client(
    {
      name: "llm-robot-controller",
      version: "1.0.0",
    },
    {
      capabilities: {},
    }
  );

  await client.connect(transport);
  console.log("✓ MCP 클라이언트 연결됨");
  return client;
}

/**
 * 로봇 상태 조회
 */
async function getRobotStatus(): Promise<any> {
  if (!mcpClient) {
    throw new Error("MCP 클라이언트가 초기화되지 않았습니다");
  }

  try {
    // 여러 상태 정보를 조회
    const [statusResult, powerResult, ultrasonicResult] = await Promise.all([
      mcpClient.callTool({
        name: "robot_get_status",
        arguments: {},
      }),
      mcpClient.callTool({
        name: "robot_get_power",
        arguments: {},
      }),
      mcpClient.callTool({
        name: "robot_get_ultrasonic",
        arguments: {},
      }),
    ]);

    const status = JSON.parse(statusResult.content[0].text);
    const power = JSON.parse(powerResult.content[0].text);
    const ultrasonic = JSON.parse(ultrasonicResult.content[0].text);

    return {
      status: status.status || "unknown",
      servo_relaxed: status.servo_relaxed || false,
      tcp_active: status.tcp_active || false,
      battery: {
        load: power.load_battery || 0,
        raspberry_pi: power.raspberry_pi_battery || 0,
      },
      distance: ultrasonic.distance || 0,
    };
  } catch (error: any) {
    console.error("로봇 상태 조회 오류:", error.message);
    return {
      status: "unknown",
      error: error.message,
    };
  }
}

/**
 * Ollama API를 통한 LLM 호출
 */
async function callOllama(prompt: string, systemPrompt: string): Promise<string> {
  try {
    const response = await axios.post(
      `${OLLAMA_BASE_URL}/api/chat`,
      {
        model: LLM_MODEL,
        messages: [
          { role: "system", content: systemPrompt },
          { role: "user", content: prompt },
        ],
        stream: false,
      },
      {
        timeout: 30000,
      }
    );

    return response.data.message.content;
  } catch (error: any) {
    throw new Error(`Ollama API 오류: ${error.message}`);
  }
}

/**
 * OpenAI API를 통한 LLM 호출
 */
async function callOpenAI(prompt: string, systemPrompt: string): Promise<string> {
  if (!OPENAI_API_KEY) {
    throw new Error("OPENAI_API_KEY 환경 변수가 설정되지 않았습니다");
  }

  try {
    const response = await axios.post(
      "https://api.openai.com/v1/chat/completions",
      {
        model: OPENAI_MODEL,
        messages: [
          { role: "system", content: systemPrompt },
          { role: "user", content: prompt },
        ],
        temperature: 0.7,
      },
      {
        headers: {
          Authorization: `Bearer ${OPENAI_API_KEY}`,
          "Content-Type": "application/json",
        },
        timeout: 30000,
      }
    );

    return response.data.choices[0].message.content;
  } catch (error: any) {
    throw new Error(`OpenAI API 오류: ${error.message}`);
  }
}

/**
 * LLM 호출 (프로바이더에 따라 분기)
 */
async function callLLM(prompt: string, systemPrompt: string): Promise<string> {
  if (LLM_PROVIDER === "openai") {
    return await callOpenAI(prompt, systemPrompt);
  } else {
    return await callOllama(prompt, systemPrompt);
  }
}

/**
 * LLM 응답에서 JSON 명령 추출
 */
function extractCommandFromLLMResponse(response: string): any {
  // JSON 코드 블록 찾기
  const jsonMatch = response.match(/```json\n([\s\S]*?)\n```/);
  if (jsonMatch) {
    try {
      return JSON.parse(jsonMatch[1]);
    } catch (e) {
      console.warn("JSON 파싱 실패:", e);
    }
  }

  // 중괄호로 감싸진 JSON 찾기
  const braceMatch = response.match(/\{[\s\S]*\}/);
  if (braceMatch) {
    try {
      return JSON.parse(braceMatch[0]);
    } catch (e) {
      console.warn("JSON 파싱 실패:", e);
    }
  }

  // JSON이 없으면 텍스트 응답 반환
  return { text: response };
}

/**
 * MCP 도구 목록 가져오기
 */
async function getAvailableTools(): Promise<string> {
  if (!mcpClient) {
    throw new Error("MCP 클라이언트가 초기화되지 않았습니다");
  }

  const tools = await mcpClient.listTools();
  return JSON.stringify(
    tools.tools.map((tool) => ({
      name: tool.name,
      description: tool.description,
    })),
    null,
    2
  );
}

/**
 * 자연어 명령을 로봇 제어 명령으로 변환
 */
async function processNaturalLanguageCommand(userRequest: string): Promise<void> {
  try {
    // 1. 로봇 상태 조회
    console.log("\n📊 로봇 상태 조회 중...");
    const robotStatus = await getRobotStatus();
    console.log("✓ 로봇 상태:", JSON.stringify(robotStatus, null, 2));

    // 2. 사용 가능한 도구 목록 가져오기
    const availableTools = await getAvailableTools();

    // 3. LLM 시스템 프롬프트 생성
    const systemPrompt = `당신은 헥사포드 로봇 제어 전문가입니다. 사용자의 자연어 명령을 분석하여 적절한 로봇 제어 명령을 생성해야 합니다.

사용 가능한 로봇 제어 명령:
${availableTools}

⚠️ 중요: 명령 처리 규칙
1. **이동 명령 처리**: 
   - 시간 지속이 필요한 이동 명령(예: "3초간 앞으로 이동")이나 연속된 동작을 요청받으면, 반드시 'robot_execute_sequence' 도구를 사용하여 한 번에 명령을 내리세요.
   - 절대 'robot_move'를 여러 번 따로 호출하거나, 'robot_move' 후 'wait' 도구를 따로 호출하지 마세요.
   - **중요**: 로봇이 실제로 이동하려면 이동 명령 사이에 대기 시간이 필수입니다. 이동 명령 뒤에는 항상 'wait' 명령을 포함해야 합니다. (별도 시간 언급이 없으면 기본 1초 이상)
   - 이동 후 멈추는 동작이 포함되어야 합니다. (마지막에 x=0, y=0 이동 명령 추가)
   - 구조: [이동 명령] -> [wait 명령 (필수)] -> [정지(x=0,y=0) 명령]

2. **기본 파라미터**: 
   - 사용자가 별도로 지정하지 않으면 **mode는 1**, **speed는 10(최대)**을 기본값으로 사용하세요.

명령 형식:
- robot_move: {mode: 1|2, x: -35~35, y: -35~35, speed: 2~10, angle: -10~10}
- robot_execute_sequence: {commands: [{id, type, params}]}
  - type: move, wait, head, led, buzzer, attitude, position, camera, balance, servo_power
  - wait params: {seconds: number}
- robot_set_led_color: {r: 0~255, g: 0~255, b: 0~255}
- robot_set_led_mode: {mode: 0~5}
- robot_set_head: {servo_id: 0|1, angle: -90~90}
- robot_set_attitude: {roll: -15~15, pitch: -15~15, yaw: -15~15}
- robot_set_position: {x: -40~40, y: -40~40, z: -20~20}
- robot_set_camera: {x: -90~90, y: -90~90}
- robot_set_buzzer: {state: true|false}
- robot_set_balance: {enable: true|false}
- robot_set_servo_power: {power_on: true|false}
- robot_get_ultrasonic: {}
- robot_get_power: {}
- robot_get_status: {}

응답 형식:
사용자의 요청을 분석하여 JSON 형식으로 명령을 반환하세요.

예시 1 (단일 명령):
{
  "tool": "robot_move",
  "args": {"mode": 1, "x": 10, "y": 0, "speed": 10, "angle": 0},
  "explanation": "앞으로 이동합니다 (기본 속도 10)"
}

예시 2 (시퀀스 명령 - 3초간 앞으로 이동):
{
  "tool": "robot_execute_sequence",
  "args": {
    "commands": [
      {
        "id": "move_1",
        "type": "move",
        "params": {"mode": 1, "x": 10, "y": 0, "speed": 10, "angle": 0}
      },
      {
        "id": "wait_1",
        "type": "wait",
        "params": {"seconds": 3}
      },
      {
        "id": "stop_1",
        "type": "move",
        "params": {"mode": 1, "x": 0, "y": 0, "speed": 10, "angle": 0}
      }
    ]
  },
  "explanation": "3초간 앞으로 이동 후 정지합니다."
}`;

    // 4. 사용자 프롬프트 생성
    const userPrompt = `현재 로봇 상태:
${JSON.stringify(robotStatus, null, 2)}

사용자 요청: "${userRequest}"

위 요청을 분석하여 적절한 로봇 제어 명령을 JSON 형식으로 생성하세요.`;

    // 5. LLM 호출
    console.log("\n🤖 LLM에 요청 전송 중...");
    const llmResponse = await callLLM(userPrompt, systemPrompt);
    console.log("✓ LLM 응답:", llmResponse);

    // 6. 명령 추출 및 실행
    const command = extractCommandFromLLMResponse(llmResponse);
    console.log("\n📝 추출된 명령:", JSON.stringify(command, null, 2));

    // 7. 명령 실행
    if (command.commands && Array.isArray(command.commands)) {
      // 여러 명령 실행
      console.log(`\n⚙️  ${command.commands.length}개의 명령 실행 중...`);
      for (const cmd of command.commands) {
        await executeMCPCommand(cmd.tool, cmd.args);
      }
    } else if (command.tool) {
      // 단일 명령 실행
      console.log(`\n⚙️  명령 실행 중: ${command.tool}`);
      await executeMCPCommand(command.tool, command.args);
    } else {
      console.log("\n⚠️  명령을 찾을 수 없습니다. LLM 응답을 확인하세요.");
      console.log("응답:", llmResponse);
    }
  } catch (error: any) {
    console.error("\n❌ 오류 발생:", error.message);
    if (error.stack) {
      console.error("스택 트레이스:", error.stack);
    }
  }
}

/**
 * MCP 명령 실행
 */
async function executeMCPCommand(toolName: string, args: any): Promise<void> {
  if (!mcpClient) {
    throw new Error("MCP 클라이언트가 초기화되지 않았습니다");
  }

  try {
    console.log(`  → ${toolName}(${JSON.stringify(args)})`);
    const result = await mcpClient.callTool({
      name: toolName,
      arguments: args || {},
    });

    const resultText = result.content[0].text;
    const resultData = JSON.parse(resultText);

    if (result.isError) {
      console.error(`  ❌ 오류:`, resultData);
    } else {
      console.log(`  ✓ 성공:`, resultData);
    }
  } catch (error: any) {
    console.error(`  ❌ 실행 오류:`, error.message);
    throw error;
  }
}

/**
 * 대화형 모드
 */
function startInteractiveMode(): void {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });

  console.log("\n" + "=".repeat(60));
  console.log("🤖 LLM 로봇 제어기");
  console.log("=".repeat(60));
  console.log(`LLM 프로바이더: ${LLM_PROVIDER}`);
  if (LLM_PROVIDER === "ollama") {
    console.log(`모델: ${LLM_MODEL}`);
  } else {
    console.log(`모델: ${OPENAI_MODEL}`);
  }
  console.log("=".repeat(60));
  console.log("\n자연어로 로봇을 제어할 수 있습니다.");
  console.log("예시: '앞으로 이동해줘', 'LED를 빨간색으로 바꿔줘', '거리를 측정해줘'");
  console.log("\n종료하려면 'exit' 또는 'quit'를 입력하세요.\n");

  const askQuestion = () => {
    rl.question("명령 입력 > ", async (answer) => {
      if (answer.toLowerCase() === "exit" || answer.toLowerCase() === "quit") {
        console.log("\n👋 종료합니다.");
        rl.close();
        if (mcpClient) {
          await mcpClient.close();
        }
        process.exit(0);
      }

      if (answer.trim()) {
        await processNaturalLanguageCommand(answer.trim());
      }

      console.log(""); // 빈 줄 추가
      askQuestion();
    });
  };

  askQuestion();
}

/**
 * 명령줄 인자 모드
 */
async function processCommandLineArgs(): Promise<void> {
  const args = process.argv.slice(2);
  if (args.length === 0) {
    console.error("사용법: npm run llm-controller <자연어 명령>");
    console.error("예시: npm run llm-controller '앞으로 이동해줘'");
    process.exit(1);
  }

  const userRequest = args.join(" ");
  await processNaturalLanguageCommand(userRequest);

  if (mcpClient) {
    await mcpClient.close();
  }
}

/**
 * 메인 함수
 */
async function main() {
  try {
    // MCP 클라이언트 초기화
    console.log("🔌 MCP 서버에 연결 중...");
    mcpClient = await initializeMCPClient();

    // 명령줄 인자가 있으면 실행하고 종료, 없으면 대화형 모드
    if (process.argv.length > 2) {
      await processCommandLineArgs();
    } else {
      startInteractiveMode();
    }
  } catch (error: any) {
    console.error("❌ 치명적 오류:", error.message);
    if (error.stack) {
      console.error("스택 트레이스:", error.stack);
    }
    process.exit(1);
  }
}

// 프로그램 실행
main();

