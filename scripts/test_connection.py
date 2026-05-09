#!/usr/bin/env python3
"""Test Modbus and MQTT connectivity."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import yaml
from pymodbus.client import ModbusTcpClient
import paho.mqtt.client as mqtt


def test_modbus(host: str, port: int = 502, slave: int = 1):
    """Test Modbus TCP connection."""
    print(f"\n📡 Testing Modbus connection to {host}:{port}...")

    try:
        client = ModbusTcpClient(host, port=port)
        if not client.connect():
            print("  ✗ Failed to connect")
            return False

        print("  ✓ Connected")

        # Try reading a register
        result = client.read_input_registers(5031, 2, slave=slave)
        if result.isError():
            print(f"  ✗ Read failed: {result}")
            client.close()
            return False

        print(f"  ✓ Read register 5031: {result.registers}")
        client.close()
        return True

    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def test_mqtt(host: str, port: int = 1883, username: str = "", password: str = ""):
    """Test MQTT broker connection."""
    print(f"\n📮 Testing MQTT connection to {host}:{port}...")

    def on_connect(client, userdata, flags, rc, properties=None):
        if rc == 0:
            print("  ✓ Connected")
            client.connected_flag = True
        else:
            print(f"  ✗ Connection failed: code {rc}")
            client.connected_flag = False

    def on_disconnect(client, userdata, rc, properties=None):
        client.connected_flag = False

    try:
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        client.connected_flag = False
        client.on_connect = on_connect
        client.on_disconnect = on_disconnect

        if username:
            client.username_pw_set(username, password)

        client.connect(host, port, keepalive=10)
        client.loop_start()

        import time
        timeout = 5
        start = time.time()
        while not client.connected_flag and (time.time() - start) < timeout:
            time.sleep(0.1)

        if not client.connected_flag:
            print(f"  ✗ Connection timeout after {timeout}s")
            client.loop_stop()
            return False

        # Try publishing
        result = client.publish("test/sungrow", "hello")
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            print("  ✓ Published test message")
        else:
            print(f"  ✗ Publish failed: {result.rc}")

        client.loop_stop()
        client.disconnect()
        return True

    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Test Sungrow integration connectivity")
    parser.add_argument("-c", "--config", default="sungrow_modbus2mqtt/config.yaml")
    parser.add_argument("--modbus-only", action="store_true")
    parser.add_argument("--mqtt-only", action="store_true")
    args = parser.parse_args()

    print("🌞 Sungrow Connection Test")
    print("=" * 40)

    # Load config
    try:
        with open(args.config) as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"✗ Config file not found: {args.config}")
        return 1
    except Exception as e:
        print(f"✗ Failed to read config: {e}")
        return 1

    inv = config.get("inverter", {})
    mq = config.get("mqtt", {})

    results = []

    # Test Modbus
    if not args.mqtt_only:
        modbus_ok = test_modbus(
            inv.get("host", "192.168.9.106"),
            inv.get("port", 502),
            inv.get("slave", 1)
        )
        results.append(("Modbus", modbus_ok))

    # Test MQTT
    if not args.modbus_only:
        mqtt_ok = test_mqtt(
            mq.get("host", "localhost"),
            mq.get("port", 1883),
            mq.get("username", ""),
            mq.get("password", "")
        )
        results.append(("MQTT", mqtt_ok))

    # Summary
    print("\n" + "=" * 40)
    print("📋 Summary:")
    for name, status in results:
        symbol = "✓" if status else "✗"
        print(f"  {symbol} {name}")

    all_ok = all(status for _, status in results)
    if all_ok:
        print("\n✅ All tests passed!")
        return 0
    else:
        print("\n❌ Some tests failed. See above for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
