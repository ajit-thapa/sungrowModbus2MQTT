# Installing Home Assistant Custom Component

Complete setup guide for the direct Modbus TCP integration.

## Prerequisites

✅ **Modbus TCP enabled** on your inverter (Settings → Communication → Modbus TCP)  
✅ **Static IP assigned** (recommended: `192.168.9.106:502`)  
✅ **Network connectivity** verified:
```bash
ping 192.168.9.106
nmap -p 502 192.168.9.106  # Port should show "open"
```

## Step 1: Prepare Home Assistant

### Determine Your HA Configuration Path

**Home Assistant OS (Supervisor):**
```bash
/root/config/custom_components/
```

**Home Assistant Core (Docker):**
```bash
/path/to/config/custom_components/
```

**Home Assistant Container:**
```bash
~/.homeassistant/custom_components/
```

**Home Assistant on Linux:**
```bash
/home/username/.homeassistant/custom_components/
```

### Create Directory

```bash
mkdir -p /path/to/config/custom_components/
```

## Step 2: Install Component Files

### Option A: Copy from This Repository

```bash
cp -r custom_components/sungrow_sg10rt /path/to/config/custom_components/
```

### Option B: Manual Setup (if git not available)

Create the directory structure:
```
custom_components/
└── sungrow_sg10rt/
    ├── __init__.py
    ├── config_flow.py
    ├── const.py
    ├── sensor.py
    ├── number.py
    ├── manifest.json
    └── strings.json
```

Copy each file from this repository into the corresponding location.

### Verify Installation

```bash
ls -la /path/to/config/custom_components/sungrow_sg10rt/
# Should show:
# __init__.py
# config_flow.py
# const.py
# manifest.json
# number.py
# sensor.py
# strings.json
```

## Step 3: Restart Home Assistant

### Via Home Assistant UI:
1. Settings → System → **Restart**
2. Wait 2-3 minutes for restart to complete

### Via Command Line:
```bash
curl -X POST http://localhost:8123/api/services/homeassistant/restart \
  -H "Authorization: Bearer YOUR_LONG_LIVED_TOKEN"
```

### Via SSH (if available):
```bash
docker restart homeassistant  # If using Docker
# Or
systemctl restart homeassistant  # If using systemd
```

## Step 4: Add Integration via UI

### In Home Assistant:
1. Go to **Settings** → **Devices & Services**
2. Click **"Create Integration"** (bottom right)
3. Search for **"Sungrow SG10RT"**
4. Fill in the form:
   - **IP Address:** `192.168.9.106` (your inverter IP)
   - **Port:** `502` (default Modbus port)
   - **Slave ID:** `1` (default, try 2 or 3 if doesn't work)
5. Click **"Create"**

### Via YAML Configuration (Optional)

Edit `configuration.yaml`:

```yaml
sungrow_sg10rt:
  - host: 192.168.9.106
    port: 502
    slave: 1
```

Then restart Home Assistant.

## Step 5: Verify Installation

### Check Entities Created

1. Settings → Devices & Services
2. Look for "Sungrow SG10RT" integration
3. Click to expand
4. Should see **15+ entities** listed:
   - `sensor.sungrow_total_active_power`
   - `sensor.sungrow_daily_yield`
   - `sensor.sungrow_total_yield`
   - `sensor.sungrow_internal_temperature`
   - `sensor.sungrow_grid_frequency`
   - `number.sungrow_export_limit_percent`
   - (and more...)

### View Live Data

1. Settings → Devices & Services → Sungrow SG10RT
2. Click on one of the entities (e.g., "Total Active Power")
3. Should see:
   - Current value
   - Last updated timestamp
   - State history graph

### Check Logs

If integration doesn't appear:

1. Settings → System → **Logs**
2. Search for "sungrow" or "Modbus"
3. Look for error messages

Common errors:
- **"Cannot connect to inverter"** → Modbus TCP not enabled or wrong IP
- **"Exception code 4"** → Wrong register address for your model
- **"No module named 'pysungrow'"** → Missing dependency

## Step 6: Optional - Create Dashboard

### Add to Energy Dashboard

1. Settings → Dashboards → Energy
2. Click **"Solar production"**
3. Select: `sensor.sungrow_total_yield`
4. Now tracks daily, monthly, yearly generation

### Create Custom Dashboard

1. Create new dashboard
2. Add cards for:
   - `sensor.sungrow_total_active_power` (Gauge card)
   - `sensor.sungrow_daily_yield` (Statistic card)
   - `sensor.sungrow_total_yield` (History graph)
   - `number.sungrow_export_limit_percent` (Number input)

Example card YAML:
```yaml
type: gauge
entity: sensor.sungrow_total_active_power
title: Solar Power
min: 0
max: 10000
unit: W
```

## Step 7: Optional - Set Up Export Limiting

### Create Automation

1. Settings → Automations & Scenes → **Create Automation**
2. Trigger: **Numeric state** (e.g., grid frequency)
3. Condition: When frequency > 50.05 Hz for 5 minutes
4. Action: **Call service** → `number.set_value`
   - Entity: `number.sungrow_export_limit_percent`
   - Value: `50` (50% export)

Or via YAML:

```yaml
automation:
  - alias: "Limit Solar Export"
    trigger:
      - platform: numeric_state
        entity_id: sensor.sungrow_grid_frequency
        above: 50.05
        for:
          minutes: 5
    action:
      - service: number.set_value
        target:
          entity_id: number.sungrow_export_limit_percent
        data:
          value: 50
```

## Troubleshooting

### Integration Doesn't Appear

**Check logs:**
```bash
# In HA logs, search for: "sungrow"
```

**Verify files:**
```bash
ls -la /path/to/config/custom_components/sungrow_sg10rt/
# Should have 7 files
```

**Check Python version:**
```bash
# Requires Python 3.8+
python3 --version
```

### Connection Errors

**Error: "Cannot connect to inverter"**

1. Verify Modbus TCP enabled on inverter
2. Check inverter IP is correct
3. Test connectivity:
   ```bash
   ping 192.168.9.106
   nmap -p 502 192.168.9.106
   ```
4. Try different slave ID (2 or 3 instead of 1)

**Error: "Exception code 4 - Server device failure"**

1. Wrong slave ID
2. Wrong register addresses for your model
3. Inverter doesn't support Modbus on that register

Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for solutions.

### Entities Show "Unavailable"

**Cause**: Coordinator failed to fetch data.

**Solution**:
1. Check Home Assistant logs for errors
2. Verify inverter is online and not rebooting
3. Restart Home Assistant
4. If still unavailable, run diagnostic:
   ```python
   from pymodbus.client import ModbusTcpClient
   client = ModbusTcpClient("192.168.9.106", port=502)
   client.connect()
   result = client.read_input_registers(5031, 2, slave=1)
   print(result.registers)
   client.close()
   ```

### Missing Dependencies

**Error: "No module named 'pysungrow'"**

**Solution**:
1. SSH into Home Assistant host
2. Install package:
   ```bash
   pip install pysungrow>=1.0.0
   ```
3. Restart Home Assistant

## Support

### Check register addresses

If you have a different Sungrow model (not SG10RT), register addresses may differ:

1. Find your model's register map:
   - https://github.com/bohdan-s/Sungrow-Inverter/tree/main/Modbus%20Information

2. Update `const.py` with correct addresses

3. Restart Home Assistant

### Report Issues

If integration still doesn't work:

1. Collect diagnostics:
   - Inverter model
   - Firmware version
   - Error messages from logs
   - Network setup (IP, port, slave ID)

2. Check GitHub issues for your model

3. See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for detailed diagnostics

## What's Included

After successful installation, you'll have:

### Read-Only Sensors (15)
- Power generation (W)
- Daily/total yield (kWh)
- Inverter temperature (°C)
- Operating time (h)
- PV voltage/current (V, A)
- Grid frequency (Hz)
- Power factor
- And more...

### Controls
- Export limit percentage (0-100%)

### Automatic
- HA Energy Dashboard support
- MQTT discovery (if enabled)
- Device grouping
- History tracking

## Next Steps

1. **Add to dashboard** - Create visualizations
2. **Set up automations** - Export limiting, alerts
3. **Monitor energy** - Use Energy Dashboard
4. **Troubleshoot** - See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

Need help? Check:
- [QUICKSTART.md](QUICKSTART.md) - 5-minute overview
- [CONFIG.md](CONFIG.md) - HA configuration examples
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Diagnostics
