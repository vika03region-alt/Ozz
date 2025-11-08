#!/bin/bash

echo "=================================================="
echo "  GuideFarm Bot - Starting Services"
echo "  DOBRO. Precision. Reliability. Excellence."
echo "=================================================="
echo ""

# Install dependencies if needed
if [ ! -d "venv" ]; then
    echo "Installing Python dependencies..."
    pip install -r requirements.txt
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "WARNING: .env file not found!"
    echo "Please create .env from .env.example"
    echo ""
    echo "Quick setup:"
    echo "  cp .env.example .env"
    echo "  # Then edit .env with your keys"
    exit 1
fi

echo "Starting Telegram Bot..."
python main.py
