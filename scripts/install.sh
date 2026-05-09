#!/bin/bash
set -e

echo "🌞 Sungrow Modbus2MQTT Installation"
echo "===================================="
echo ""

# Check Python version
echo "✓ Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "✗ Python3 not found. Please install Python 3.8+"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "  Found Python $PYTHON_VERSION"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt
echo "✓ Dependencies installed"
echo ""

# Create directories
echo "📁 Creating directories..."
mkdir -p docker/mosquitto/{config,data,log}
echo "✓ Directories created"
echo ""

# Copy config if doesn't exist
if [ ! -f sungrow_modbus2mqtt/config.yaml ]; then
    echo "⚙️  Creating config from template..."
    cp sungrow_modbus2mqtt/config.yaml sungrow_modbus2mqtt/config.yaml.example || true
    echo "   Edit sungrow_modbus2mqtt/config.yaml with your settings"
fi

if [ ! -f .env ]; then
    echo "⚙️  Creating .env from template..."
    cp .env.example .env
    echo "   Edit .env with your settings"
fi

echo ""
echo "✅ Installation complete!"
echo ""
echo "Next steps:"
echo "1. Edit sungrow_modbus2mqtt/config.yaml with your inverter IP"
echo "2. Edit .env with your MQTT broker details (if using Docker)"
echo "3. Run: python -m sungrow_modbus2mqtt.bridge"
echo "   Or:  docker-compose up -d"
echo ""
