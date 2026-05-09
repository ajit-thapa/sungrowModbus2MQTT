# Setup Guide

Complete step-by-step instructions for all three integration methods.

## Prerequisites

### 1. Enable Modbus TCP on Inverter

**Via Inverter Display:**
1. Press OK on inverter
2. Navigate to: **Advanced Settings** → **Communication** → **Modbus TCP**
3. Set to **Enabled**
4. Note the IP address and port (usually `192.168.9.x:502`)

**Via iSolarCloud App:**
1. Open app
2. Go to **Settings** → **Device Settings** → **Communication**
3. Enable Modbus TCP

### 2. Assign Static IP

Assign a static IP to your inverter (e.g., `192.168.9.106`):

**Option A: DHCP reservation** (easiest)
- Log into router
- Find inverter's MAC address
- Reserve IP address for that MAC

**Option B: Inverter display**
- Settings → Network → IPv4 → Set static IP

### 3. Verify Connectivity

```bash
# Test network connectivity
ping 192.168.9.106

# Test Modbus TCP port (requires nmap)
nmap -p 502 192.168.9.106

# Expected output: port 502 open
```

---

## Method 1: Home Assistant Custom Component

### Installation

1. **Copy component files:**
   ```bash
   cp -r custom_components/sungrow_sg10rt /path/to/homeassistant/custom_components/
   ```

2. **Restart Home Assistant:**
   - Settings → System → Restart

3. **Add integration:**
   - Settings → Devices & Services
   - Click "Create Integration"
   - Search for "Sungrow SG10RT"
   - Enter inverter IP (e.g., `192.168.9.106`)
   - Port: `502` (default)
   - Slave ID: `1` (default)

4. **Verify:**
   - Settings → Devices & Services → Sungrow SG10RT
   - Should see 15+ sensors listed

### Configuration Options

**Via Config Flow (UI):**
- IP Address: `192.168.9.106`
- Port: `502`
- Slave ID: `1`

**Via YAML** (optional):
```yaml
# configuration.yaml
sungrow_sg10rt:
  - host: 192.168.9.106
    port: 502
    slave: 1
```

### Entities Created

**Sensors (read-only):**
- `sensor.sungrow_total_active_power` (W)
- `sensor.sungrow_daily_yield` (kWh)
- `sensor.sungrow_total_yield` (kWh)
- `sensor.sungrow_internal_temperature` (°C)
- `sensor.sungrow_total_running_time` (h)
- `sensor.sungrow_mppt1_voltage` (V)
- `sensor.sungrow_mppt1_current` (A)
- `sensor.sungrow_mppt2_voltage` (V)
- `sensor.sungrow_mppt2_current` (A)
- `sensor.sungrow_grid_frequency` (Hz)
- `sensor.sungrow_reactive_power` (var)
- `sensor.sungrow_power_factor`
- `sensor.sungrow_phase_a_voltage` (V)
- `sensor.sungrow_phase_a_current` (A)
- `sensor.sungrow_nominal_active_power` (W)

**Number Controls (writable):**
- `number.sungrow_export_limit_percent` (0-100%)

---

## Method 2: Modbus2MQTT Bridge

### Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure MQTT broker:**

   **Option A: Use Home Assistant MQTT Add-on**
   - Settings → Add-ons → Install "Mosquitto broker"
   - Note: broker address = Home Assistant IP (e.g., `192.168.1.50`)

   **Option B: Docker Mosquitto (see Method 3)**

   **Option C: Standalone Mosquitto**
   ```bash
   # macOS
   brew install mosquitto
   mosquitto -c /usr/local/etc/mosquitto/mosquitto.conf

   # Linux
   sudo apt install mosquitto
   sudo systemctl start mosquitto
   ```

3. **Update configuration:**
   ```yaml
   # sungrow_modbus2mqtt/config.yaml
   inverter:
     host: 192.168.9.106
     port: 502
     slave: 1
     scan_interval: 10

   mqtt:
     host: 192.168.1.50  # Your MQTT broker IP
     port: 1883
     username: ha_user
     password: your_password
     topic_prefix: sungrow/sg10rt
     ha_discovery: true
   ```

4. **Run the bridge:**
   ```bash
   python -m sungrow_modbus2mqtt.bridge -c sungrow_modbus2mqtt/config.yaml
   ```

5. **Add MQTT integration to Home Assistant:**
   - Settings → Devices & Services
   - Click "Create Integration"
   - Search for "MQTT"
   - Enter broker IP and credentials

### MQTT Topics

Published to `sungrow/sg10rt/`:
```
sungrow/sg10rt/total_active_power → "4250"
sungrow/sg10rt/daily_yield → "12.45"
sungrow/sg10rt/total_yield → "1234.56"
sungrow/sg10rt/internal_temperature → "38.5"
...
```

### HA Discovery Configuration

Sensors auto-appear in Home Assistant as `sensor.total_active_power`, etc. if `ha_discovery: true`.

---

## Method 3: Docker Compose (All-in-One)

### Requirements

- Docker and Docker Compose installed
- See [docker-compose.yml](docker-compose.yml)

### Installation

1. **Copy Docker config:**
   ```bash
   cp docker-compose.yml docker-compose.override.yml
   ```

2. **Edit configuration:**
   ```yaml
   # docker-compose.override.yml
   services:
     bridge:
       environment:
         - INVERTER_HOST=192.168.9.106
         - INVERTER_PORT=502
         - MQTT_HOST=mosquitto  # Or your broker IP
         - MQTT_USERNAME=ha_user
         - MQTT_PASSWORD=your_password
   ```

3. **Start services:**
   ```bash
   docker-compose up -d
   ```

4. **Verify:**
   ```bash
   # Check Mosquitto
   docker logs mosquitto

   # Check bridge
   docker logs sungrow_bridge

   # Test MQTT connection
   docker exec mosquitto mosquitto_sub -h localhost -u ha_user -P your_password -t "sungrow/#"
   ```

### Docker Services

**mosquitto** - MQTT broker on ports 1883 (TCP) and 9001 (WebSocket)

**sungrow_bridge** - Modbus2MQTT bridge polling every 10 seconds

### Stopping Services

```bash
docker-compose down
```

---

## Mosquitto Configuration (for Docker/Standalone)

### Create password file:

```bash
mosquitto_passwd -c -b passwd ha_user your_password
```

### mosquitto.conf:

```conf
# Allow anonymous for local testing (disable in production)
allow_anonymous false

# Authentication
password_file /mosquitto/config/passwd

# Listener
listener 1883 0.0.0.0
socket_domain ipv4

# WebSocket support
listener 9001 0.0.0.0
protocol websockets
socket_domain ipv4

# Persistence
persistence true
persistence_location /mosquitto/data/

# Logging
log_dest file /mosquitto/log/mosquitto.log
log_dest stdout
```

---

## Home Assistant Configuration

See [CONFIG.md](CONFIG.md) for complete `configuration.yaml` examples and automations.

### Minimal Setup (MQTT sensors only):

```yaml
mqtt:
  broker: 192.168.1.50
  port: 1883
  username: ha_user
  password: your_password
  discovery: true
```

---

## Testing & Verification

### Test Modbus Connection:

```python
from pymodbus.client import ModbusTcpClient

client = ModbusTcpClient("192.168.9.106", port=502)
client.connect()
result = client.read_input_registers(5031, 2, slave=1)
print(result.registers)  # Should return values
client.close()
```

### Test MQTT Publishing:

```bash
# Subscribe to all topics
mosquitto_sub -h 192.168.1.50 -u ha_user -P your_password -t "sungrow/#" -v

# Should see messages like:
# sungrow/sg10rt/total_active_power 4250
# sungrow/sg10rt/daily_yield 12.45
```

### Check HA Entities:

1. Settings → Devices & Services
2. Filter by "MQTT" or "Sungrow"
3. Should see sensors listed

---

## Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for detailed diagnostics.

### Common Issues:

| Issue | Solution |
|-------|----------|
| "Connection refused" | Enable Modbus TCP on inverter display |
| "No data returned" | Verify slave ID (try 1, 2, or 3) |
| "MQTT connection failed" | Check broker IP and credentials |
| "Modbus timeout" | Use Ethernet cable instead of WiNet |

---

## Next Steps

1. **Set up automations** - See CONFIG.md for export limiting examples
2. **Monitor in Home Assistant** - Create dashboards for solar data
3. **Add battery integration** - If using hybrid inverter (SH series)
4. **Set up notifications** - Alert on inverter errors or low generation

## Support

- Check register addresses at: https://github.com/bohdan-s/Sungrow-Inverter
- Community discussion: Home Assistant forums
- Issues with specific models documented in GitHub issues
