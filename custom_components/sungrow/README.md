# Sungrow Inverter Integration

Home Assistant integration for Sungrow inverters using Modbus TCP.

## Supported Models

- SG10RT
- SG series inverters
- SH series inverters
- Other Sungrow models with Modbus TCP support

## Features

- Real-time solar production monitoring
- Daily and lifetime energy yield tracking
- Inverter temperature monitoring
- Grid frequency tracking
- Export limit control (write-capable registers)
- 15+ sensors for comprehensive monitoring

## Installation

### Via HACS (Recommended)

1. Add custom repository in HACS: `https://github.com/ajit-thapa/sungrowModbus2MQTT`
2. Search for "Sungrow" and install
3. Restart Home Assistant
4. Add integration from Settings → Devices & Services

### Manual Installation

1. Copy this folder to `~/.homeassistant/custom_components/`
2. Restart Home Assistant
3. Add integration from Settings → Devices & Services

## Configuration

When adding the integration, provide:
- **IP Address**: Your inverter's IP (e.g., `192.168.9.106`)
- **Port**: 502 (default Modbus port)
- **Slave ID**: 1 (default, try 2-3 if doesn't work)

## Prerequisites

1. **Modbus TCP enabled** on inverter (Settings → Communication → Modbus TCP)
2. **Network connectivity** to inverter
3. For SG series: WiNet-S dongle (NOT internal LAN port)

## Support

See the main repository for:
- [VALIDATION.md](../../VALIDATION.md) - Prerequisite checklist
- [INSTALL_COMPONENT.md](../../INSTALL_COMPONENT.md) - Detailed setup
- [CONFIG.md](../../CONFIG.md) - Configuration examples
- [TROUBLESHOOTING.md](../../TROUBLESHOOTING.md) - Common issues
