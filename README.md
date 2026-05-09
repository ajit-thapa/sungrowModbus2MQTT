# Sungrow Modbus2MQTT Integration

Comprehensive Modbus TCP integration for Sungrow inverters with Home Assistant.

**Supports**: SG10RT, SG series, SH series, and other Sungrow models

## 📦 Installation Options

### Option 1: Home Assistant Custom Component (Recommended)

#### Via HACS

1. Home Assistant → **HACS** → **Integrations**
2. Click **⋮** (top right) → **Custom repositories**
3. Paste: `https://github.com/ajit-thapa/sungrowModbus2MQTT`
4. Category: **Integration**
5. Click **Create**
6. Search **"Sungrow"** and click **Download**
7. Restart Home Assistant
8. Settings → Devices & Services → **Create Integration** → **Sungrow Inverter**
9. Enter your inverter IP, port (502), and slave ID (1)

#### Manual Installation

1. Copy `custom_components/sungrow/` to `~/.homeassistant/custom_components/`
2. Restart Home Assistant
3. Settings → Devices & Services → Create Integration → Sungrow Inverter

### Option 2: Modbus2MQTT Bridge (Multi-System)

For MQTT-based integration or multiple systems:

```bash
pip install -r requirements.txt
# Edit sungrow_modbus2mqtt/config.yaml with your settings
python -m sungrow_modbus2mqtt.bridge
```

### Option 3: Docker (All-in-One)

```bash
docker-compose up -d
```

Includes Mosquitto MQTT broker + bridge

## Supported Models

- **SH Series**: SH3.0-5.0RT, SH5.0-8.0RT, SH10RT (hybrid inverters)
- **SG Series**: SG3.0-5.0RT, SG5K-D, SG10RT (string inverters)
- **SBH Series**: SBH series (string inverters)
- **SHxxRS Series**: Newer hybrid series
- **Data Logger**: Logger 1000 (COM100)
- **Wallbox**: AC011E-01 Charging station

## Features

✅ **15+ sensors** - Power, energy, voltage, current, temperature, frequency  
✅ **Export limiting** - Control solar curtailment via Home Assistant  
✅ **HA Discovery** - Sensors auto-appear in Home Assistant  
✅ **MQTT native** - Works with any MQTT-compatible system  
✅ **Modbus direct** - Alternative direct connection without MQTT  
✅ **Docker support** - Easy deployment with Mosquitto included  

## Prerequisites

- **Modbus TCP enabled** on inverter (Settings → Communication → Modbus TCP)
- **Static IP** for inverter (recommended: `192.168.9.106:502`)
- **MQTT broker** (Mosquitto) - can use Home Assistant built-in or Docker
- **Python 3.8+** or Docker

## Documentation

- [SETUP.md](SETUP.md) - Detailed setup and configuration
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues and solutions
- [CONFIG.md](CONFIG.md) - Home Assistant configuration examples

## Key Differences: HA Component vs MQTT Bridge

| Feature | HA Component | MQTT Bridge |
|---------|--------------|------------|
| Setup | Via UI | Edit config file |
| Dependencies | HA native | Python + MQTT |
| Modbus reads | Direct (pysungrow) | Direct (pymodbus) |
| MQTT required | Optional | Required |
| HA Discovery | Automatic | Optional |
| Multiple HA instances | ❌ No | ✅ Yes |

## Wiring Checklist

- ✅ Modbus TCP enabled on inverter
- ✅ Static IP assigned to inverter
- ✅ Mosquitto broker running (if using bridge)
- ✅ Network connectivity verified (`ping 192.168.9.106`)
- ✅ Port 502 accessible (`nmap -p 502 192.168.9.106`)

## Support

- **Community Modbus maps**: https://github.com/bohdan-s/Sungrow-Inverter/tree/main/Modbus%20Information
- **Issue tracker**: Check GitHub issues for your specific model

## License

See LICENSE file.
