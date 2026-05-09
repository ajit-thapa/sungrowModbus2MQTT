# Quick Start Guide

Get up and running in 5 minutes.

## Prerequisites

- Sungrow inverter with **Modbus TCP enabled**
- Inverter has **static IP** (e.g., `192.168.9.106:502`)
- Python 3.8+ or Docker installed
- MQTT broker available (can use Home Assistant built-in)

## 1. Test Inverter Connectivity

```bash
# Verify network connectivity
ping 192.168.9.106

# Verify Modbus port open
nmap -p 502 192.168.9.106

# Expected output: port 502 open
```

If you get "connection refused," enable Modbus TCP on your inverter (see [TROUBLESHOOTING.md](TROUBLESHOOTING.md)).

## 2. Choose Your Installation Method

### Option A: Home Assistant Component (Easiest)

```bash
# Copy integration to Home Assistant
cp -r custom_components/sungrow_sg10rt ~/.homeassistant/custom_components/

# Restart Home Assistant
# Settings → System → Restart
```

In Home Assistant UI:
1. Settings → Devices & Services
2. Click "Create Integration"
3. Search for "Sungrow SG10RT"
4. Enter IP: `192.168.9.106`
5. ✅ Done!

### Option B: Python Bridge (Advanced)

```bash
# Install dependencies
pip install -r requirements.txt

# Copy config template
cp .env.example .env
cp sungrow_modbus2mqtt/config.yaml.example sungrow_modbus2mqtt/config.yaml

# Edit config with your inverter IP
nano sungrow_modbus2mqtt/config.yaml

# Run the bridge
python -m sungrow_modbus2mqtt.bridge
```

### Option C: Docker (All-in-One)

```bash
# Copy templates
cp .env.example .env

# Edit .env with your settings (inverter IP, MQTT password, etc.)
nano .env

# Start all services (Mosquitto + bridge)
docker-compose up -d

# Check logs
docker logs sungrow_bridge
```

## 3. Verify It's Working

### Option A (HA Component)
- Settings → Devices & Services → Sungrow SG10RT
- Should see 15+ sensors listed
- Check one sensor to see live data

### Option B/C (MQTT Bridge)
```bash
# Subscribe to MQTT topic
mosquitto_sub -h 192.168.1.50 -u ha_user -P password -t "sungrow/#" -v

# Should see:
# sungrow/sg10rt/total_active_power 4250
# sungrow/sg10rt/daily_yield 12.45
# sungrow/sg10rt/... (more sensors)
```

## 4. Add to Home Assistant Dashboard

Edit `configuration.yaml`:

```yaml
# If using MQTT Bridge
mqtt:
  broker: 192.168.1.50
  port: 1883
  username: ha_user
  password: sungrow_password
  discovery: true
```

Then:
1. Create new dashboard
2. Add "Entity" card
3. Select any `sensor.sungrow_*` entity
4. ✅ Done!

## 5. Optional: Set Up Export Limiting

In Home Assistant automations:

```yaml
automation:
  - alias: "Limit Solar Export"
    trigger:
      - platform: numeric_state
        entity_id: sensor.grid_import_price
        above: 0.50
    action:
      - service: number.set_value
        target:
          entity_id: number.sungrow_export_limit_percent
        data:
          value: 50
```

---

## Common Issues

| Issue | Solution |
|-------|----------|
| "Connection refused" | Enable Modbus TCP on inverter display |
| "MQTT connection failed" | Check broker IP/password in config |
| "No data returned" | Verify slave ID = 1 (try others if needed) |
| "Port 502 not open" | Use Ethernet, not WiNet Wi-Fi dongle |

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for detailed diagnostics.

## Next Steps

1. **Add more sensors** - See [CONFIG.md](CONFIG.md) for templates
2. **Create dashboards** - Use [config_templates/solar_dashboard.yaml](config_templates/solar_dashboard.yaml)
3. **Set up automations** - Export limiting, alerts, etc.
4. **Monitor in Home Assistant** - Settings → Dashboards → Energy

---

## Support

- **Modbus register map**: https://github.com/bohdan-s/Sungrow-Inverter
- **Issues**: Check GitHub issues for your model
- **Questions**: See [SETUP.md](SETUP.md) for detailed docs

**Stuck?** Run the diagnostic script:

```bash
python scripts/test_connection.py -c sungrow_modbus2mqtt/config.yaml
```

This will test Modbus and MQTT connectivity and report any issues.
