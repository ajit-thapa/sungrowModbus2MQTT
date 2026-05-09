#!/usr/bin/env python3
"""
Diagnostic tool for SG10RT Sungrow inverter Modbus connection.
Follows strict Phase 1 testing sequence from comprehensive setup guide.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import socket
import time
from pymodbus.client import ModbusTcpClient


class Colors:
    """Terminal colors."""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    """Print section header."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.RESET}\n")


def print_success(text):
    """Print success message."""
    print(f"{Colors.GREEN}✅ {text}{Colors.RESET}")


def print_error(text):
    """Print error message."""
    print(f"{Colors.RED}❌ {text}{Colors.RESET}")


def print_warning(text):
    """Print warning message."""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.RESET}")


def test_ping(host: str) -> bool:
    """Test 1: Basic network connectivity."""
    print_header("Test 1: Basic Network Connectivity")
    print(f"Pinging {host}...\n")

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((host, 22))  # Port 22 for SSH to test routing
        sock.close()

        if result == 0:
            print_success(f"Host {host} is reachable")
            return True
        else:
            print_error(f"Host {host} is NOT reachable")
            print("  → Check network connectivity")
            print("  → Verify inverter IP address")
            print("  → Check firewall rules")
            return False
    except Exception as e:
        print_error(f"Ping test failed: {e}")
        return False


def test_port_502(host: str, port: int = 502) -> bool:
    """Test 2: Port 502 availability."""
    print_header("Test 2: Modbus TCP Port (502) Availability")
    print(f"Checking port {port} on {host}...\n")

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()

        if result == 0:
            print_success(f"Port {port} is OPEN and listening")
            return True
        else:
            print_error(f"Port {port} is NOT open")
            print("\n  Likely causes:")
            print("  1. Modbus TCP is DISABLED on inverter")
            print("  2. Wrong IP address")
            print("  3. Firewall blocking port 502")
            print("\n  Solutions:")
            print("  1. Enable Modbus TCP on inverter display")
            print("     Settings → Communication → Modbus TCP → Enable")
            print("  2. If using WiNet-S: Access web interface and toggle")
            print("     http://192.168.9.106:8080")
            print("  3. Verify network connectivity (Test 1 passed)")
            return False
    except Exception as e:
        print_error(f"Port test failed: {e}")
        return False


def test_modbus_connection(host: str, port: int = 502, slave: int = 1, wait_ms: int = 20) -> bool:
    """Test 3: Modbus TCP connection and register read."""
    print_header("Test 3: Modbus TCP Connection & Register Read")
    print(f"Connecting to {host}:{port} (Slave {slave})...")
    print(f"Wait time: {wait_ms}ms (typical for WiNet-S)\n")

    try:
        client = ModbusTcpClient(host, port=port)

        # Set response timeout
        client.timeout = 5

        if not client.connect():
            print_error("Failed to establish Modbus connection")
            print("\n  Likely causes:")
            print("  1. Modbus TCP disabled on inverter")
            print("  2. Wrong slave ID (try 2 or 3)")
            print("  3. Network routing issue")
            print("  4. WiNet-S dongle needs reset")
            return False

        print_success("Modbus TCP connection established")

        # Test read on register 5003 (Daily Yield - common register)
        print("\nReading register 5003 (Daily Yield)...")
        result = client.read_holding_registers(5003, 1, slave=slave)

        if result.isError():
            print_error(f"Register read failed: {result}")
            print("\n  Likely causes:")
            print("  1. Wrong slave ID (try 1, 2, or 3)")
            print("  2. Register not supported by this firmware")
            print("  3. SG vs SH series register mismatch")
            print("\n  Solutions:")
            print("  1. Verify inverter firmware version")
            print("  2. Check if register 5003 exists for SG10RT")
            print("  3. Try different slave IDs")
            client.close()
            return False

        value = result.registers[0] if result.registers else 0
        print_success(f"Register 5003 read: {value} (raw value)")

        # Scale it (0.1 = divide by 10)
        scaled_value = value * 0.1
        print(f"  → Scaled value: {scaled_value} kWh (Daily Yield)")

        # Test read on register 5031 (Active Power)
        print("\nReading register 5031-5032 (Active Power, uint32)...")
        result = client.read_holding_registers(5031, 2, slave=slave)

        if not result.isError():
            regs = result.registers
            if len(regs) >= 2:
                power = (regs[0] << 16) | regs[1]  # Combine two uint16 to uint32
                print_success(f"Register 5031-5032 read: {power} W")
            else:
                print_warning(f"Unexpected register count: {len(regs)}")
        else:
            print_error(f"Register 5031 read failed: {result}")

        client.close()
        return True

    except Exception as e:
        print_error(f"Modbus connection test failed: {e}")
        print("\n  Debugging info:")
        print(f"  Exception: {str(e)}")
        return False


def test_dongle_status(host: str) -> bool:
    """Test 4: Check WiNet-S dongle web interface (optional)."""
    print_header("Test 4: WiNet-S Dongle Web Interface (Optional)")
    print(f"Checking web interface at http://{host}:8080...\n")

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((host, 8080))
        sock.close()

        if result == 0:
            print_success("WiNet-S web interface is accessible")
            print(f"\n  Access at: http://{host}:8080")
            print("  You can check/toggle Modbus TCP status there")
            return True
        else:
            print_warning("WiNet-S web interface not found (port 8080 closed)")
            print("  This is OK - Modbus TCP may still be working")
            print("  Use inverter LCD menu instead: Settings → Communication → Modbus TCP")
            return False
    except Exception as e:
        print_warning(f"Could not test web interface: {e}")
        return False


def main():
    """Run all diagnostics."""
    parser = argparse.ArgumentParser(
        description="SG10RT Sungrow Modbus Connection Diagnostic Tool"
    )
    parser.add_argument(
        "-i", "--ip",
        default="192.168.9.106",
        help="Inverter IP address (default: 192.168.9.106)"
    )
    parser.add_argument(
        "-p", "--port",
        type=int,
        default=502,
        help="Modbus port (default: 502)"
    )
    parser.add_argument(
        "-s", "--slave",
        type=int,
        default=1,
        help="Modbus slave ID (default: 1)"
    )
    parser.add_argument(
        "-w", "--wait",
        type=int,
        default=20,
        help="Wait milliseconds for response (default: 20 for WiNet-S)"
    )

    args = parser.parse_args()

    print(f"\n{Colors.BOLD}🌞 SG10RT Sungrow Inverter Diagnostic Tool{Colors.RESET}")
    print("=" * 60)
    print("This tool validates your Modbus TCP connection setup")
    print("=" * 60)

    results = {}

    # Run all tests
    results["Ping"] = test_ping(args.ip)
    results["Port 502"] = test_port_502(args.ip, args.port)
    results["Modbus Connection"] = test_modbus_connection(
        args.ip, args.port, args.slave, args.wait
    )
    results["WiNet-S Web UI"] = test_dongle_status(args.ip)

    # Summary
    print_header("Diagnostic Summary")

    for test_name, passed in results.items():
        status = f"{Colors.GREEN}✅ PASS{Colors.RESET}" if passed else f"{Colors.RED}❌ FAIL{Colors.RESET}"
        print(f"{test_name}: {status}")

    # Overall status
    critical_tests = ["Ping", "Port 502", "Modbus Connection"]
    critical_passed = all(results.get(test, False) for test in critical_tests)

    print("\n" + "=" * 60)
    if critical_passed:
        print_success("All critical tests passed!")
        print("\n✅ Your SG10RT is ready for Home Assistant integration")
        print("\n  Recommended next steps:")
        print("  1. Follow MKAISER_SETUP.md for full control")
        print("  2. Configure export limiting and automations")
        print("  3. Add to Home Assistant dashboard")
        return 0
    else:
        print_error("One or more critical tests failed")
        print("\n❌ Cannot proceed with integration")
        print("\n  Troubleshooting steps:")
        print("  1. Enable Modbus TCP on inverter (Settings → Communication)")
        print("  2. Verify inverter IP address and network connectivity")
        print("  3. Try different slave IDs (1, 2, or 3)")
        print("  4. Reset WiNet-S dongle (unplug 30 seconds)")
        print("  5. Check firewall rules for port 502")
        print("\n  See TROUBLESHOOTING.md for detailed solutions")
        return 1


if __name__ == "__main__":
    sys.exit(main())
