# Production Integration: mkaiser Setup Guide

**Official recommended method for SG10RT with full export control.**

This guide follows the proven 5+ year community-tested approach.

---

## 🚨 Prerequisite Validation Checklist

### Hardware Requirements

- [ ] **SG10RT inverter** accessible on network
- [ ] **WiNet-S dongle** installed (⚠️ NOT internal LAN port for SG series)
- [ ] **Ethernet or strong Wi-Fi** connection to WiNet-S (lag matters)
- [ ] **Home Assistant** running and accessible

### Inverter Configuration - MUST BE ENABLED

⚠️ **These must be set on the physical inverter via LCD screen or iSolarCloud app:**

| Setting | Required | How to Verify |
|---------|----------|---------------|
| Modbus TCP | ✅ ENABLED | Inverter LCD: Settings → Communication → Modbus TCP |
| Port | 502 | Default (do not change) |
| Slave ID | 1 | Default (try 2 or 3 if 1 fails) |
| WiNet-S IP | Static recommended | e.g., `192.168.9.106` |

**⚠️ CRITICAL**: Modbus TCP is **disabled by default**. You must physically enable it on the inverter display or via iSolarCloud app.

### Network Verification

Test connectivity before proceeding:

```bash
# Test 1: Ping inverter
ping -c 4 192.168.9.106

# Test 2: Port availability
nc -zv 192.168.9.106 502

# Test 3: Modbus connection (Python)
python3 << 'EOF'
from pymodbus.client import ModbusTcpClient
client = ModbusTcpClient('192.168.9.106', 502)
if client.connect():
    print('✅ Modbus connection OK')
    client.close()
else:
    print('❌ Cannot connect - check Modbus TCP enabled')
EOF
```

**If all tests pass**: Proceed to Phase 1.  
**If any test fails**: See [Troubleshooting](#troubleshooting) before continuing.

---

## Phase 1: Install via HACS

### Step 1.1: Verify HACS Installed

In Home Assistant:
1. Settings → Devices & Services
2. Look for "HACS"
3. If missing: Install from official docs: https://hacs.xyz/

### Step 1.2: Add Custom Repository

1. **HACS** → Click three dots (top right) → **Custom repositories**
2. Repository URL: `https://github.com/mkaiser/Sungrow-SHx-Inverter-Modbus-Home-Assistant`
3. Category: **Integration**
4. Click **Create**

### Step 1.3: Download Integration

1. **HACS** → **Integrations**
2. Search: "Sungrow"
3. Click **Download**
4. Restart Home Assistant (Settings → System → Restart)

### Step 1.4: Verify Installation

After restart, check:
```bash
ls -la ~/.homeassistant/custom_components/sungrow_modbus/
# Should show: __init__.py, manifest.json, etc.
```

---

## Phase 2: Create Configuration Files

### Step 2.1: Create secrets.yaml Entry

Edit `~/.homeassistant/secrets.yaml`:

```yaml
# Sungrow Modbus Configuration
sungrow_modbus_host_ip: 192.168.9.106
sungrow_modbus_port: 502
sungrow_modbus_slave: 1

# ⚠️ CRITICAL: Wait milliseconds for response
# - LAN connection: 5ms
# - WiNet-S dongle: 20-30ms (most common)
sungrow_modbus_wait_milliseconds: 20

# Optional: Scan interval (seconds)
sungrow_modbus_scan_interval: 10
```

### Step 2.2: Get Latest Register Configuration

The `modbus_sungrow.yaml` file contains all register definitions and must be the **latest version**:

```bash
# Download latest from GitHub
curl -o modbus_sungrow.yaml \
  https://raw.githubusercontent.com/mkaiser/Sungrow-SHx-Inverter-Modbus-Home-Assistant/main/modbus_sungrow.yaml

# Move to HA config directory
mv modbus_sungrow.yaml ~/.homeassistant/
```

### Step 2.3: Update configuration.yaml

Add this to `~/.homeassistant/configuration.yaml`:

```yaml
# Sungrow Modbus Integration
homeassistant:
  packages:
    modbus_sungrow: !include modbus_sungrow.yaml
```

**Alternative** (if packages not preferred):

```yaml
modbus:
  - name: "Sungrow SG10RT"
    type: tcp
    host: !secret sungrow_modbus_host_ip
    port: !secret sungrow_modbus_port
    delay: !secret sungrow_modbus_wait_milliseconds
    timeout: 5
    slave: !secret sungrow_modbus_slave
    # Include sensor definitions (see modbus_sungrow.yaml)
```

---

## Phase 3: SG10RT-Specific Configuration

### Register Address Mapping for SG Series

SG series uses **different registers** than SH series. The mkaiser integration handles this via variant detection.

⚠️ **If you customize registers, use these addresses for SG10RT**:

| Sensor | SG10RT Address | Data Type | Scale | Unit |
|--------|---------------|-----------|-------|------|
| Daily Yield | 5003 | uint16 | 0.1 | kWh |
| Total Yield | 5004-5005 | uint32 | 0.1 | kWh |
| Active Power | 5031-5032 | uint32 | 1 | W |
| Temperature | 5008 | int16 | 0.1 | °C |
| Running Time | 5006-5007 | uint32 | 1 | h |
| Grid Frequency | 5036 | uint16 | 0.01 | Hz |

### WiNet-S Dongle Timing

The WiNet-S dongle adds latency. If experiencing timeouts:

1. Increase `sungrow_modbus_wait_milliseconds` to **30-50ms**
2. Increase `scan_interval` to **30+ seconds**
3. Restart Home Assistant

---

## Phase 4: Configure Export Limiting

### Understanding Sungrow Export Limit Quirk

⚠️ **CRITICAL**: On Sungrow inverters:
- **0 kW** = **Unlimited export** (NOT zero)
- **10 W** = Actual zero export
- **5000 W** = 5 kW export limit

### Add to configuration.yaml

```yaml
number:
  - platform: modbus
    name: "Sungrow Export Limit"
    unique_id: sungrow_export_limit
    command_type: holding
    data_type: uint16
    slave: !secret sungrow_modbus_slave
    address: 0  # ⚠️ Verify correct register (may differ by firmware)
    min: 0
    max: 10000  # 10 kW
    step: 100
    unit_of_measurement: "W"
    persistence: true
```

### Automation: Dynamic Export Limiting

```yaml
automation:
  # Limit export during high grid prices
  - alias: "Curtail Solar Export - High Price"
    trigger:
      - platform: numeric_state
        entity_id: sensor.electricity_price
        above: 0.50  # Your price threshold
    action:
      - service: number.set_value
        target:
          entity_id: number.sungrow_export_limit
        data:
          value: 10  # Zero export (10W minimum)

  # Restore unlimited export
  - alias: "Restore Solar Export - Normal Price"
    trigger:
      - platform: numeric_state
        entity_id: sensor.electricity_price
        below: 0.30
    action:
      - service: number.set_value
        target:
          entity_id: number.sungrow_export_limit
        data:
          value: 0  # Unlimited

  # Alert if export limit reached
  - alias: "Export Limit Active Alert"
    trigger:
      - platform: numeric_state
        entity_id: sensor.sungrow_export_limit
        above: 0
        for:
          minutes: 5
    action:
      - service: persistent_notification.create
        data:
          title: "⚠️ Solar Export Limited"
          message: "Export limit is active: {{ states('number.sungrow_export_limit') }} W"
```

---

## Phase 5: Verify Integration

### Check Home Assistant Logs

```bash
# SSH into HA and check logs
tail -f ~/.homeassistant/home-assistant.log | grep -i sungrow
```

Expected output:
```
2024-01-15 14:32:10 INFO (MainThread) [homeassistant.setup] Setting up sungrow_modbus
2024-01-15 14:32:12 INFO Connected to Sungrow inverter at 192.168.9.106
```

### Verify Entities Created

1. Settings → Devices & Services → Integrations
2. Click "Sungrow Modbus"
3. Should show **20-30 entities**

Key entities to check:
- `sensor.sg10rt_power_current` (should show current power in W)
- `sensor.sg10rt_daily_energy` (should show today's yield in kWh)
- `sensor.sg10rt_temperature` (should show 20-80°C range)
- `number.sungrow_export_limit` (should be adjustable 0-10000)

### Test Data Values

1. Click on `sensor.sg10rt_power_current`
2. Should show **live data** (not `unavailable` or constant 0)
3. Should match iSolarCloud app within ±5%

---

## Troubleshooting

### Error: Connection Refused

**Cause**: Modbus TCP not enabled on inverter.

**Solution**:
1. Access inverter via LCD or iSolarCloud
2. Settings → Communication → Modbus TCP → **Enable**
3. If using WiNet-S web interface:
   - Access: `http://192.168.9.106:8080`
   - Toggle Modbus TCP OFF → Save
   - Toggle Modbus TCP ON → Save
   - Wait 2 minutes
4. Retry connection test

### Error: Read Timeout / No Data

**Cause**: WiNet-S response delays (common).

**Solution**:
1. Increase `sungrow_modbus_wait_milliseconds` to **30-50ms**
2. Increase `scan_interval` to **30-60 seconds**
3. Restart Home Assistant
4. Monitor logs for improvement

### Error: Register Read Failed (Exception Code 4)

**Cause**: Invalid register address or wrong variant.

**Solution**:
1. Verify you're using SG series addresses (not SH)
2. Check inverter firmware version (Settings → Information)
3. Try different slave ID (2 or 3 instead of 1)
4. Refer to [Register Address Mapping](#register-address-mapping-for-sg-series)

### Entities Show 0xFFFF or Unavailable

**Cause**: Register not supported by firmware version or dongle issue.

**Solution**:
1. Check inverter firmware supports the register
2. Restart WiNet-S dongle (unplug 30 seconds)
3. Restart Home Assistant
4. If persists, edit `modbus_sungrow.yaml` to remove unsupported registers

### Write Operations Fail (Export Limit Won't Change)

**Cause**: SG series write limitations via WiNet-S.

**Solution**:
1. Verify register address is correct (may differ by firmware)
2. Test with simple 10 value first (zero export)
3. Check HA logs for specific error
4. If consistent failures, SG series may have limited write support
5. Alternative: Contact mkaiser repository for variant-specific write registers

---

## Multi-Inverter Setup

If you have **2+ Sungrow inverters**:

### Create separate files:

**`modbus_sungrow_1.yaml`**: First inverter
```yaml
modbus:
  - name: "Sungrow 1"
    host: !secret sungrow1_host
    port: !secret sungrow1_port
    # ... register definitions
```

**`modbus_sungrow_2.yaml`**: Second inverter
```yaml
modbus:
  - name: "Sungrow 2"
    host: !secret sungrow2_host
    port: !secret sungrow2_port
    # ... register definitions
```

**In configuration.yaml**:
```yaml
homeassistant:
  packages:
    modbus_sungrow_1: !include modbus_sungrow_1.yaml
    modbus_sungrow_2: !include modbus_sungrow_2.yaml
```

**In secrets.yaml**:
```yaml
sungrow1_host: 192.168.9.106
sungrow1_port: 502
sungrow2_host: 192.168.9.107
sungrow2_port: 502
```

---

## Success Criteria

Your integration is successful when:

✅ **Data accuracy**: Solar production matches iSolarCloud within ±5%  
✅ **Update frequency**: Entities refresh every 10-30 seconds reliably  
✅ **Export limit**: Can set and change values (0-10000 W)  
✅ **No timeouts**: Logs show no connection errors  
✅ **All entities**: 20+ entities show valid numeric values (not `unavailable` or `0xFFFF`)

---

## Maintenance

### Regular Checks

- **Monthly**: Compare HA data vs iSolarCloud app
- **After firmware update**: Re-verify Modbus TCP enabled
- **Quarterly**: Check GitHub repo for `modbus_sungrow.yaml` updates

### Update Integration

```bash
# Via HACS: Check for updates regularly
# Manual: Download latest modbus_sungrow.yaml
curl -o ~/homeassistant/modbus_sungrow.yaml \
  https://raw.githubusercontent.com/mkaiser/Sungrow-SHx-Inverter-Modbus-Home-Assistant/main/modbus_sungrow.yaml

# Restart HA
```

---

## Resources

- **mkaiser Repository**: https://github.com/mkaiser/Sungrow-SHx-Inverter-Modbus-Home-Assistant
- **Sungrow Register Map**: https://github.com/Gnarfoz/Sungrow-Inverter
- **Home Assistant Modbus**: https://www.home-assistant.io/integrations/modbus/
- **Community Discussions**: Home Assistant Forums → Search "Sungrow"

---

**Next**: Set up automations and dashboards. See [CONFIG.md](CONFIG.md) for examples.
