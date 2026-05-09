# Project Structure

Complete overview of files and directories.

## File Organization

```
sungrowModbus2MQTT/
├── README.md                          # Main overview
├── QUICKSTART.md                      # 5-minute setup guide
├── SETUP.md                           # Detailed setup instructions
├── TROUBLESHOOTING.md                 # Diagnostics & solutions
├── CONFIG.md                          # HA configuration examples
├── PROJECT_STRUCTURE.md               # This file
├── LICENSE                            # License
├── requirements.txt                   # Python dependencies
├── Dockerfile                         # Docker image for bridge
├── docker-compose.yml                 # All-in-one Docker setup
├── .env.example                       # Environment variables template

# Home Assistant Custom Component
├── custom_components/
│   └── sungrow_sg10rt/
│       ├── __init__.py                # Core integration
│       ├── config_flow.py             # UI configuration
│       ├── const.py                   # Modbus register definitions
│       ├── sensor.py                  # Sensor entities
│       ├── number.py                  # Number entities (export limit)
│       ├── manifest.json              # Integration metadata
│       └── strings.json               # UI strings/translations

# Standalone Modbus2MQTT Bridge
├── sungrow_modbus2mqtt/
│   ├── __init__.py                    # Python package init
│   ├── bridge.py                      # Main bridge executable
│   ├── config.yaml                    # Configuration file
│   ├── registers.py                   # Modbus register definitions
│   ├── modbus_client.py               # Modbus TCP client
│   └── mqtt_publisher.py              # MQTT publishing

# Configuration Templates
├── config_templates/
│   ├── configuration.yaml.template    # HA config examples
│   └── solar_dashboard.yaml           # Lovelace dashboard

# Utility Scripts
├── scripts/
│   ├── install.sh                     # Installation script
│   ├── start_bridge.sh                # Start bridge with tests
│   ├── test_connection.py             # Connectivity tester
│   └── sungrow-bridge.service         # Systemd service file

# Docker Configuration
├── docker/
│   └── mosquitto/
│       ├── config/
│       │   ├── mosquitto.conf         # MQTT broker config
│       │   └── passwd                 # MQTT credentials
│       ├── data/                      # MQTT data (persistent)
│       └── log/                       # MQTT logs
```

## Key Files

### Integration Files

| File | Purpose |
|------|---------|
| `custom_components/sungrow_sg10rt/__init__.py` | Core integration logic (DataUpdateCoordinator, Modbus client setup) |
| `custom_components/sungrow_sg10rt/const.py` | Register addresses and sensor definitions |
| `custom_components/sungrow_sg10rt/sensor.py` | Sensor entity implementations |
| `custom_components/sungrow_sg10rt/number.py` | Number entity for export limiting |
| `custom_components/sungrow_sg10rt/config_flow.py` | UI configuration flow |

### Bridge Files

| File | Purpose |
|------|---------|
| `sungrow_modbus2mqtt/bridge.py` | Main MQTT bridge (entry point) |
| `sungrow_modbus2mqtt/modbus_client.py` | Low-level Modbus TCP communication |
| `sungrow_modbus2mqtt/mqtt_publisher.py` | MQTT publishing with HA discovery |
| `sungrow_modbus2mqtt/registers.py` | Modbus register definitions |
| `sungrow_modbus2mqtt/config.yaml` | Bridge configuration |

### Documentation

| File | Purpose |
|------|---------|
| `README.md` | Overview and quick links |
| `QUICKSTART.md` | 5-minute setup for each method |
| `SETUP.md` | Detailed step-by-step instructions |
| `TROUBLESHOOTING.md` | Diagnostics and solutions |
| `CONFIG.md` | HA configuration examples |
| `PROJECT_STRUCTURE.md` | This file |

### Configuration & Deployment

| File | Purpose |
|------|---------|
| `requirements.txt` | Python package dependencies |
| `docker-compose.yml` | Docker services (Mosquitto + bridge) |
| `Dockerfile` | Docker image for Python bridge |
| `.env.example` | Environment variables template |
| `docker/mosquitto/config/mosquitto.conf` | MQTT broker configuration |

### Scripts

| File | Purpose |
|------|---------|
| `scripts/install.sh` | One-time setup script |
| `scripts/start_bridge.sh` | Run bridge with connectivity tests |
| `scripts/test_connection.py` | Diagnose Modbus/MQTT issues |
| `scripts/sungrow-bridge.service` | Systemd service for Linux |

### Templates

| File | Purpose |
|------|---------|
| `config_templates/configuration.yaml.template` | HA configuration examples |
| `config_templates/solar_dashboard.yaml` | Lovelace dashboard YAML |

## Integration Methods

### Method 1: Home Assistant Custom Component
- **Entry point**: `custom_components/sungrow_sg10rt/__init__.py`
- **Entities**: Auto-created via `sensor.py` and `number.py`
- **Communication**: Direct Modbus TCP via `pysungrow`
- **Config**: UI-based (config_flow.py)
- **MQTT**: Optional

### Method 2: Standalone MQTT Bridge
- **Entry point**: `sungrow_modbus2mqtt/bridge.py`
- **Communication**: Modbus TCP → MQTT → HA
- **Config**: YAML (`sungrow_modbus2mqtt/config.yaml`)
- **MQTT**: Required
- **HA Discovery**: Automatic if enabled

### Method 3: Docker All-in-One
- **Entry point**: `docker-compose.yml`
- **Services**: Mosquitto + bridge
- **Config**: Environment variables (`.env`)
- **Network**: Internal Docker network

## Data Flow

### Method 1: Component
```
Sungrow Inverter
    ↓ (Modbus TCP)
pysungrow client
    ↓ (DataUpdateCoordinator)
sensor.py / number.py
    ↓ (state_changed)
Home Assistant State Machine
    ↓ (MQTT integration optional)
MQTT Broker
```

### Method 2/3: Bridge
```
Sungrow Inverter
    ↓ (Modbus TCP)
modbus_client.py
    ↓ (read_register)
mqtt_publisher.py
    ↓ (publish_value)
MQTT Broker
    ↓ (MQTT discovery)
Home Assistant
```

## Dependencies

### Python Packages
```
pymodbus>=3.5.0          # Modbus TCP client
pysungrow>=1.0.0         # Sungrow library (component only)
paho-mqtt>=2.0.0         # MQTT client
pyyaml>=6.0              # YAML parsing
```

### System Services
- **Python 3.8+**
- **MQTT broker** (Mosquitto) - if using bridge
- **Docker/Docker Compose** - if using containers

## Configuration Files

### config.yaml (Bridge)
```yaml
inverter:
  host: 192.168.9.106      # Inverter IP
  port: 502                 # Modbus port
  slave: 1                  # Modbus slave ID
  scan_interval: 10         # Poll interval (seconds)

mqtt:
  host: localhost           # MQTT broker IP
  port: 1883                # MQTT port
  username: ha_user         # MQTT username
  password: password        # MQTT password
  topic_prefix: sungrow/sg10rt
  ha_discovery: true        # Enable HA discovery
```

### mosquitto.conf (MQTT)
```conf
allow_anonymous false           # Disable anonymous access
password_file /mosquitto/config/passwd
listener 1883 0.0.0.0           # TCP listener
listener 9001 0.0.0.0 websockets # WebSocket listener
persistence true
```

## Entity Mapping

### Sensors (Read-only)
All sensor entities prefixed with `sensor.sungrow_`:
- `total_active_power` (W)
- `daily_yield` (kWh)
- `total_yield` (kWh)
- `internal_temperature` (°C)
- `total_running_time` (h)
- `mppt1_voltage`, `mppt1_current` (V, A)
- `mppt2_voltage`, `mppt2_current` (V, A)
- `grid_frequency` (Hz)
- `reactive_power` (var)
- `power_factor`
- `phase_a_voltage`, `phase_a_current` (V, A)
- `nominal_active_power` (W)

### Controls (Writable)
- `number.sungrow_export_limit_percent` (0-100%)

## Register Addresses

All registers defined in:
- **Component**: `custom_components/sungrow_sg10rt/const.py`
- **Bridge**: `sungrow_modbus2mqtt/registers.py`

Common addresses:
- `5001`: Nominal active power
- `5003`: Daily yield
- `5004`: Total yield
- `5006`: Total running time
- `5008`: Internal temperature
- `5031`: Total active power (32-bit)
- `5033`: Reactive power
- `5035`: Power factor
- `5036`: Grid frequency

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for address verification.

## Troubleshooting Reference

Quick links to common issues:
- **Connection issues**: [TROUBLESHOOTING.md#connection-issues](TROUBLESHOOTING.md#connection-issues)
- **Modbus errors**: [TROUBLESHOOTING.md#modbus-read-issues](TROUBLESHOOTING.md#modbus-read-issues)
- **MQTT issues**: [TROUBLESHOOTING.md#mqtt-issues](TROUBLESHOOTING.md#mqtt-issues)
- **HA issues**: [TROUBLESHOOTING.md#home-assistant-issues](TROUBLESHOOTING.md#home-assistant-issues)
- **Docker issues**: [TROUBLESHOOTING.md#docker-specific-issues](TROUBLESHOOTING.md#docker-specific-issues)

## Installation Paths

**Windows/macOS/Linux:**
1. Component: `~/.homeassistant/custom_components/sungrow_sg10rt/`
2. Bridge: `/opt/sungrow-modbus2mqtt/`
3. Docker: `/path/to/docker-compose.yml`

**Docker:**
- Bridge: `/app/`
- Mosquitto: `/mosquitto/`

## Next Steps

1. **Start here**: [QUICKSTART.md](QUICKSTART.md)
2. **Detailed setup**: [SETUP.md](SETUP.md)
3. **Troubleshooting**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
4. **HA config**: [CONFIG.md](CONFIG.md)
5. **Source code**: Browse individual files above
