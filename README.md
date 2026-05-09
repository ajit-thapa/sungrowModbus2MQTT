# Sungrow Modbus2MQTT Integration

Comprehensive integration for Sungrow inverters with Home Assistant using Modbus TCP.

⚠️ **CRITICAL FOR SG10RT**: This inverter requires **WiNet-S dongle** for Modbus TCP, not the internal LAN port.

## 🎯 Recommended Path: mkaiser Integration (HACS)

For **full control** including export curtailment, use the battle-tested production integration:

### **[mkaiser/Sungrow-SHx-Inverter-Modbus-Home-Assistant](https://github.com/mkaiser/Sungrow-SHx-Inverter-Modbus-Home-Assistant)**

✅ **Why this approach**:
- 5+ years production-tested
- Full SG10RT support via WiNet-S
- Write capabilities (export limiting, curtailment)
- Active maintenance
- Available via HACS

**Quick install via HACS**:
1. Home Assistant → HACS → Integrations
2. Click "Custom repositories" (⋮ menu)
3. Add: `https://github.com/mkaiser/Sungrow-SHx-Inverter-Modbus-Home-Assistant`
4. Category: Integration
5. Search "Sungrow" and install
6. Restart Home Assistant
7. Settings → Devices & Services → Create Integration

See [MKAISER_SETUP.md](MKAISER_SETUP.md) for detailed guide.

## Alternative: This Repository (HACS-Ready Custom Component)

Use this if you want:
- Simple read-only monitoring
- Custom Modbus bridge + MQTT
- Docker deployment

### Option 1A: HACS Installation (Recommended for component)

1. Home Assistant → HACS → Integrations
2. Click "Custom repositories" (⋮ menu)
3. Add: `https://github.com/ajit-thapa/sungrowModbus2MQTT`
4. Category: Integration
5. Search "Sungrow SG10RT" and install
6. Restart Home Assistant
7. Settings → Devices & Services → Create Integration → Enter inverter IP

### Option 1B: Manual Installation (No HACS)

1. Copy `custom_components/sungrow_sg10rt/` to your HA `custom_components` folder
2. Restart Home Assistant
3. Settings → Devices & Services → Create Integration → "Sungrow SG10RT"
4. Enter inverter IP, port (502), slave ID (1)

### Option 2: Modbus2MQTT Bridge

1. Install: `pip install -r requirements.txt`
2. Edit `sungrow_modbus2mqtt/config.yaml`
3. Run: `python -m sungrow_modbus2mqtt.bridge`

### Option 3: Docker (All-in-one)

```bash
docker-compose up -d
```

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
