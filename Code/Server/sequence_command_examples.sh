#!/bin/bash
# Sequential Command API curl examples
# Usage: ./sequence_command_examples.sh [server_ip]
# Default server IP: localhost

SERVER_IP=${1:-localhost}
BASE_URL="http://${SERVER_IP}:8000"

echo "=== Sequential Command API Examples ==="
echo "Server: ${BASE_URL}"
echo ""


# Example 3: Complex sequence with multiple actions
echo "Example 3: Complex sequence - Move, wait, head movement, LED, POST"
curl -X POST "${BASE_URL}/api/commands/sequence" \
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
        "id": "move_right",
        "type": "move",
        "params": {
          "mode": 1,
          "x": 0,
          "y": 0,
          "speed": 5,
          "angle": 0
        }
      },
      {
        "id": "head_left",
        "type": "head",
        "params": {
          "servo_id": 0,
          "angle": 0
        }
      }
    ]
  }'

echo ""
echo ""
echo "=========================================="
echo ""
exit 0



# Example 3: Complex sequence with multiple actions
echo "Example 3: Complex sequence - Move, wait, head movement, LED, POST"
curl -X POST "${BASE_URL}/api/commands/sequence" \
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

echo ""
echo ""
echo "=========================================="
echo ""
exit 0
# Example 4: Multiple movements with completion posts
echo "Example 4: Multiple movements with completion notifications"
curl -X POST "${BASE_URL}/api/commands/sequence" \
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

echo ""
echo ""
echo "=========================================="
echo ""

# Example 5: Head movement sequence
echo "Example 5: Head movement sequence"
curl -X POST "${BASE_URL}/api/commands/sequence" \
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

echo ""
echo ""
echo "=========================================="
echo ""

# Example 6: Using localhost webhook for testing
echo "Example 6: Using localhost webhook (for testing)"
echo "Note: This will fail if webhook server is not running, but demonstrates the concept"
curl -X POST "${BASE_URL}/api/commands/sequence" \
  -H "Content-Type: application/json" \
  -d '{
    "commands": [
      {
        "id": "test_move",
        "type": "move",
        "params": {
          "mode": 1,
          "x": 5,
          "y": 0,
          "speed": 5,
          "angle": 0
        }
      },
      {
        "id": "test_wait",
        "type": "wait",
        "params": {
          "seconds": 1
        }
      },
      {
        "id": "test_webhook",
        "type": "post",
        "params": {
          "url": "http://localhost:3000/webhook"
        }
      }
    ]
  }'

echo ""
echo ""
echo "=== All examples completed ==="


