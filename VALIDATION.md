# Prerequisite Validation Checklist

**Before attempting ANY integration, you MUST validate these prerequisites.**

This checklist ensures your system is ready and prevents common setup failures.

---

## 1️⃣ Network Accessibility

### 1.1: Inverter Reachability
```bash
ping -c 4 192.168.9.106
```

Expected output:
```
PING 192.168.9.106 (192.168.9.106): 56 data bytes
64 bytes from 192.168.9.106: icmp_seq=0 ttl=64 time=2.3 ms
```

✅ **Success**: Got ping replies  
❌ **Failure**: "No route to host" or timeout → Check network connectivity

### 1.2: Port 502 Open
```bash
nc -zv 192.168.9.106 502
# or
nmap -p 502 192.168.9.106
```

Expected output:
```
Connection to 192.168.9.106 port 502 [tcp/modbus-tcp] succeeded!
# or
502/tcp open  modbus-tcp
```

✅ **Success**: Port open  
❌ **Failure**: "Connection refused" → **Modbus TCP NOT enabled** on inverter

### 1.3: IP Address Confirmed

Go to your inverter's LCD display:
- Settings → Network → IPv4
- Note the IP address displayed
- Verify it matches what you're using (should be `192.168.9.106`)

✅ **Checklist**: 
- [ ] I can ping the inverter
- [ ] Port 502 is open
- [ ] IP address in configuration matches inverter display

---

## 2️⃣ Inverter Configuration Validation

### ⚠️ CRITICAL: Modbus TCP Must Be Enabled

This is **disabled by default** on Sungrow inverters.

**How to enable** (choose one method):

#### Method A: Via Inverter LCD Display

1. Press **OK** button on inverter front panel
2. Navigate: **Settings** → **Advanced Settings** → **Communication** → **Modbus TCP**
3. Change to **Enabled**
4. Press **OK** to confirm
5. Power cycle the inverter (turn off/on) or restart via iSolarCloud

#### Method B: Via iSolarCloud App

1. Open iSolarCloud app
2. Click your inverter
3. Settings → Device Settings → Communication
4. Find "Modbus TCP" toggle
5. Switch to **ON**
6. Wait 2 minutes for changes to apply

#### Method C: Via WiNet-S Web Interface (if available)

1. Open browser: `http://192.168.9.106:8080`
2. Login (default: admin/admin, varies by firmware)
3. Find Communication or Protocol settings
4. Toggle Modbus TCP: OFF → Save → ON → Save
5. Wait 2 minutes

### 2.1: Verify Modbus Settings

After enabling, verify these are set correctly:

| Setting | Required Value | How to Check |
|---------|----------------|-------------|
| Modbus TCP | **ENABLED** | Inverter LCD or app |
| Port | 502 | Do NOT change (standard) |
| Slave ID | 1 (or 2/3 if fails) | Modbus setting on inverter |
| Protocol | MODBUS | Should be selected, not "SunSpec" |

### 2.2: Run Diagnostic After Enabling

```bash
python3 scripts/diagnose_sg10rt.py -i 192.168.9.106
```

This will test connectivity after Modbus is enabled.

✅ **Checklist**:
- [ ] Modbus TCP is **ENABLED** on inverter
- [ ] Port is **502** (not changed)
- [ ] Slave ID is **1** (default)
- [ ] Diagnostic test shows "✅ Modbus Connection"

---

## 3️⃣ Hardware Connection Validation

### 3.1: Verify Hardware Setup

⚠️ **For SG10RT (String inverter)**:

| Connection Type | Status |
|-----------------|--------|
| WiNet-S Dongle | ✅ **REQUIRED** |
| Internal LAN Port | ⚠️ May not work for SG series |
| Wi-Fi Only (no WiNet) | ❌ Not supported |

**You MUST have**: WiNet-S dongle connected to your network

Verify:
1. WiNet-S dongle is physically connected to inverter
2. Dongle has power (LED lit)
3. Dongle is connected to same network as Home Assistant
4. Dongle has static IP or DHCP reservation: `192.168.9.106`

### 3.2: Test Connection via Diagnostic

```bash
python3 scripts/diagnose_sg10rt.py
```

✅ **All tests pass** → Ready for integration  
❌ **Any test fails** → See troubleshooting section below

✅ **Checklist**:
- [ ] WiNet-S dongle is connected
- [ ] Dongle has power
- [ ] Dongle is on same network
- [ ] Diagnostic shows all tests passing

---

## 4️⃣ Home Assistant Environment Validation

### 4.1: Verify Home Assistant Access

```bash
# Should be accessible at:
http://localhost:8123
# or
http://192.168.1.50:8123  # Your HA IP
```

✅ **Checklist**:
- [ ] Home Assistant is running
- [ ] I can access the UI
- [ ] I have admin credentials

### 4.2: Verify Python/Dependencies

If using the Python bridge:

```bash
python3 --version  # Should be 3.8 or higher
pip3 install -r requirements.txt
```

✅ **Checklist**:
- [ ] Python 3.8+ installed
- [ ] All dependencies install without errors

---

## 5️⃣ Quick Validation Script

Run this to validate all prerequisites at once:

```bash
#!/bin/bash
echo "🌞 SG10RT Validation Checklist"
echo "=============================="

# Test 1: Ping
if ping -c 1 192.168.9.106 > /dev/null 2>&1; then
    echo "✅ Network connectivity"
else
    echo "❌ Network connectivity - cannot ping 192.168.9.106"
    exit 1
fi

# Test 2: Port 502
if nc -zv 192.168.9.106 502 > /dev/null 2>&1; then
    echo "✅ Modbus TCP port open"
else
    echo "❌ Port 502 closed - enable Modbus TCP on inverter"
    exit 1
fi

# Test 3: Python
if python3 --version > /dev/null 2>&1; then
    echo "✅ Python installed"
else
    echo "❌ Python not found"
    exit 1
fi

# Test 4: Home Assistant reachable
if curl -s http://localhost:8123 > /dev/null 2>&1; then
    echo "✅ Home Assistant accessible"
else
    echo "⚠️  Home Assistant not at localhost:8123 (might be different IP)"
fi

echo ""
echo "✅ All prerequisites validated!"
echo "Ready to proceed with integration setup"
```

---

## Troubleshooting Prerequisites

### ❌ Cannot Ping Inverter

**Cause**: Network connectivity issue or wrong IP

**Solutions**:
1. Verify IP: Check inverter display (Settings → Network → IPv4)
2. Check network: Both HA and inverter on same subnet?
3. Check firewall: Any blocks on port 502?
4. Restart inverter: Power off 30 seconds, power on

### ❌ Port 502 Closed

**Cause**: Modbus TCP not enabled

**Solution** (MUST DO THIS):
1. Press OK on inverter → Settings → Communication → Modbus TCP
2. Change to **ENABLED**
3. Confirm and restart inverter
4. Wait 2 minutes
5. Test again: `nc -zv 192.168.9.106 502`

### ❌ Modbus Read Fails (Exception Code 4)

**Cause**: Connection working but register access denied

**Solutions**:
1. Try different slave ID:
   ```bash
   python3 -c "
   from pymodbus.client import ModbusTcpClient
   for slave in [1, 2, 3, 100, 247]:
       client = ModbusTcpClient('192.168.9.106', 502)
       if client.connect():
           result = client.read_holding_registers(5003, 1, slave=slave)
           print(f'Slave {slave}: {result}')
           client.close()
   "
   ```

2. Verify firmware version supports register
3. Check register address (SG vs SH series use different addresses)

### ❌ WiNet-S Not Responding

**Cause**: Dongle needs reset or firmware issue

**Solutions**:
1. Unplug WiNet-S for 30 seconds
2. Plug back in and wait for LED
3. Check dongle has internet connection
4. Access web interface: `http://192.168.9.106:8080`
5. If web UI works: Toggle Modbus TCP OFF → ON

---

## Final Validation Checklist

Before proceeding with integration setup, verify **ALL** of these:

### Network
- [ ] Can ping inverter: `ping 192.168.9.106`
- [ ] Port 502 open: `nc -zv 192.168.9.106 502`
- [ ] Network is stable (no frequent disconnects)

### Inverter
- [ ] Modbus TCP is **ENABLED** (via LCD or app)
- [ ] Port is **502**
- [ ] Slave ID is **1** (default)
- [ ] Inverter is online and showing power generation

### Hardware
- [ ] WiNet-S dongle connected (for SG10RT)
- [ ] Dongle has power (LED lit)
- [ ] Dongle IP is `192.168.9.106` or similar
- [ ] Connection is wired Ethernet (if possible)

### Home Assistant
- [ ] Home Assistant is running
- [ ] UI is accessible
- [ ] Admin user available
- [ ] Python 3.8+ installed (if using Python bridge)

### Diagnostics
- [ ] Run: `python3 scripts/diagnose_sg10rt.py`
- [ ] All tests show ✅ PASS

---

**Once all items are checked**, proceed to:
- **Full control + export limiting**: [MKAISER_SETUP.md](MKAISER_SETUP.md)
- **Simple component**: [INSTALL_COMPONENT.md](INSTALL_COMPONENT.md)
- **MQTT bridge**: [SETUP.md](SETUP.md)
