#!/bin/bash
# Run the robot server with proper Python environment
cd "$(dirname "$0")"
sudo ./venv/bin/python main.py "$@"

