#!/bin/bash
# Start the Sungrow Modbus2MQTT bridge

set -e

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

# Check config exists
if [ ! -f "sungrow_modbus2mqtt/config.yaml" ]; then
    echo "❌ Config file not found: sungrow_modbus2mqtt/config.yaml"
    echo "   Copy .env.example to .env and edit with your settings"
    exit 1
fi

# Run tests first
echo "🧪 Running connectivity tests..."
python3 scripts/test_connection.py -c sungrow_modbus2mqtt/config.yaml || {
    echo ""
    echo "⚠️  Some tests failed. Check TROUBLESHOOTING.md"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    [[ ! $REPLY =~ ^[Yy]$ ]] && exit 1
}

echo ""
echo "🌞 Starting Sungrow Modbus2MQTT Bridge..."
echo "Press Ctrl+C to stop"
echo ""

python3 -m sungrow_modbus2mqtt.bridge -c sungrow_modbus2mqtt/config.yaml
