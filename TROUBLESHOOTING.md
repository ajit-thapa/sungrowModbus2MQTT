# Troubleshooting Guide

## Common Issues and Solutions

### Connection Issues

#### "Connection refused" or "Connection timeout"

**Cause**: Modbus TCP not enabled on inverter.

**Solution**:
1. Press OK on inverter display
2. Navigate: **Advanced Settings** → **Communication** → **Modbus TCP**
3. Ensure status shows **Enabled**
4. Restart inverter if needed
5. Test with: `nmap -p 502 <inverter_ip>`

#### "Failed to connect to inverter at 192.168.x.x:502"

**Causes and solutions**:

| Check | Command |
|-------|---------|
| Network connectivity | `ping 192.168.1.100` |
| Port open | `nmap -p 502 192.168.1.100` |
| Correct IP | Check inverter display → Settings → Network |
| Correct port | Default is 502, verify in inverter settings |
| Firewall | Disable temporarily, then add rule for port 502 |
| WiNet vs LAN | **Use internal LAN port, not WiNet dongle** (WiNet blocks Modbus) |

#### "Errno 111 - Connection refused"

**Solution**: Same as above — Modbus TCP disabled or using wrong port/IP.

---

### Modbus Read Issues

#### "Exception code 4 - Server device failure"

**Cause**: Inverter rejected Modbus request, often due to:
- Encryption enabled (newer SG models)
- Invalid register address for your model
- Incorrect data type

**Solution**:
1. Verify register address is correct for your model:
   - https://github.com/bohdan-s/Sungrow-Inverter/tree/main/Modbus%20Information
2. Check data type (uint16 vs uint32)
3. If using SG5K-D or newer SG, may need encrypted Modbus handling

#### "No data returned" or "None/null values"

**Causes**:
1. Wrong register address
2. Wrong slave ID
3. Inverter in standby (no generation)
4. Incorrect data type configuration

**Solution**:
```python
# Test with Python to find correct addresses
from pymodbus.client import ModbusTcpClient
client = ModbusTcpClient("192.168.9.106", port=502)
client.connect()

# Test different slave IDs
for slave in [1, 2, 3, 100, 247]:
    try:
        result = client.read_input_registers(5031, 2, slave=slave)
        if not result.isError():
            print(f"Slave {slave}: {result.registers}")
    except:
        pass

client.close()
```

#### "Modbus timeout"

**Cause**: Inverter not responding, network issues.

**Solution**:
1. Use **Ethernet cable** instead of WiNet Wi-Fi dongle
2. Verify network is stable: `ping -c 100 192.168.9.106`
3. Check if inverter rebooting (often happens during software updates)
4. Increase timeout in configuration (if supported)

#### "Register addresses don't match my inverter"

**Solution**: Register addresses vary by model and firmware version.

1. Find your model's register map:
   - https://github.com/bohdan-s/Sungrow-Inverter/tree/main/Modbus%20Information
   - Look for your model (SG5K-D, SH10RT, etc.)

2. Update `const.py` or `registers.py` with correct addresses

3. Common addresses to test:
   ```python
   5031  # Total Active Power (most common)
   5001  # Nominal Power
   5003  # Daily Yield
   5004  # Total Yield
   5008  # Temperature
   ```

---

### MQTT Issues

#### "MQTT broker not found" or "Connection refused"

**Cause**: MQTT broker unreachable.

**Solution**:
1. Verify broker is running:
   ```bash
   # Check if Mosquitto running
   ps aux | grep mosquitto

   # Or for Docker
   docker ps | grep mosquitto

   # Test connection
   mosquitto_sub -h 192.168.1.50 -u ha_user -P password -t "test"
   ```

2. Check credentials in config:
   ```yaml
   mqtt:
     host: 192.168.1.50      # Correct IP?
     port: 1883
     username: ha_user        # Correct username?
     password: your_password  # Correct password?
   ```

3. Verify firewall allows port 1883:
   ```bash
   nmap -p 1883 192.168.1.50
   ```

#### "Authentication failed" (MQTT)

**Cause**: Wrong username/password.

**Solution**:
1. Test with MQTT client:
   ```bash
   mosquitto_pub -h 192.168.1.50 -u ha_user -P password -t "test" -m "hello"
   ```

2. If fails, recreate password file:
   ```bash
   mosquitto_passwd -c -b passwd ha_user new_password
   ```

3. Update config with new password

#### "Topics not appearing in Home Assistant"

**Cause**: MQTT discovery disabled or incorrect topic prefix.

**Solution**:
1. Check config has `ha_discovery: true`:
   ```yaml
   mqtt:
     ha_discovery: true
     ha_discovery_prefix: homeassistant
   ```

2. Check expected topics are published:
   ```bash
   mosquitto_sub -h 192.168.1.50 -u ha_user -P password -t "homeassistant/#" -v
   ```

3. Verify MQTT integration added to Home Assistant

4. Check Home Assistant MQTT logs:
   - Settings → Devices & Services → MQTT
   - Click "Diagnostics"

---

### Home Assistant Issues

#### "No entities created" after adding integration

**Cause**: Integration not fully loaded or coordinator failed.

**Solution**:
1. Check HA logs:
   - Settings → System → Logs
   - Search for "sungrow" or "Modbus"

2. Restart Home Assistant:
   - Settings → System → Restart

3. Verify inverter is reachable:
   ```bash
   ping 192.168.9.106
   ```

4. Check device is created:
   - Settings → Devices & Services
   - Filter by "Sungrow"

#### "Unavailable" sensors

**Cause**: Coordinator failed to fetch data.

**Solution**:
1. Check Home Assistant logs for error messages
2. Verify Modbus connection still working
3. If inverter in standby, sensor values may be unavailable
4. Restart Home Assistant

#### "Cannot write to number entity" (export limit)

**Cause**: Write register address incorrect.

**Solution**:
1. Find correct write register for your model
2. Update register address in `const.py` or `number.py`
3. Test with Python:
   ```python
   from pymodbus.client import ModbusTcpClient
   client = ModbusTcpClient("192.168.9.106", port=502)
   client.connect()
   result = client.write_register(address=0, value=5000, slave=1)
   print(result)  # Should show success
   client.close()
   ```

---

### Performance Issues

#### "High CPU usage" from bridge

**Cause**: Scan interval too short or many registers.

**Solution**:
1. Increase scan interval:
   ```yaml
   inverter:
     scan_interval: 30  # Default 10, increase to 30-60
   ```

2. Reduce number of registers:
   - Edit `registers.py` to remove unused sensors

#### "Inverter connection drops"

**Cause**: Network instability or inverter auto-disconnecting idle clients.

**Solution**:
1. Use Ethernet instead of WiNet
2. Increase keep-alive ping
3. Add reconnection logic to bridge (already included)
4. Check inverter network settings for idle timeout

---

### Model-Specific Issues

#### SG5K-D shows "Exception code 4"

**Cause**: SG5K-D has encrypted Modbus.

**Solution**: Use `pysungrow` library which handles encryption:
```python
from pysungrow import identify, SungrowClient

client = AsyncModbusTcpClient("192.168.9.106", port=502)
await client.connect()
serial_number, device, output_type = await identify(client)
sungrow = SungrowClient(client, device, output_type)
data = await sungrow.get_all()
```

#### SHxxRS series not recognized

**Cause**: Register map differs from older SH series.

**Solution**:
1. Find SHxxRS register map
2. Update register addresses in configuration
3. Test addresses with Python client
4. Report issue with register map to GitHub

#### "No PV data" on hybrid inverter (SH series)

**Cause**: Register addresses different for battery-related sensors.

**Solution**:
1. Add battery registers to `registers.py`:
   ```python
   Register(13004, "battery_soc", "uint16", scale=0.1, unit="%", device_class="battery")
   Register(13005, "battery_power", "int32", unit="W", device_class="power")
   ```

2. Test addresses match your inverter model

---

### Docker-Specific Issues

#### "mosquitto exited with code 0"

**Cause**: Container crashed, usually config error.

**Solution**:
1. Check logs: `docker logs mosquitto`
2. Verify config file format: `mosquitto -c config/mosquitto.conf -t` (test)
3. Verify password file exists: `docker exec mosquitto ls /mosquitto/config/passwd`

#### "Bridge keeps restarting"

**Cause**: Config error or inverter unreachable.

**Solution**:
1. Check logs: `docker logs sungrow_bridge`
2. Verify config.yaml is valid YAML
3. Test inverter IP: `docker exec sungrow_bridge ping 192.168.9.106`
4. Verify MQTT credentials correct

#### "Permission denied" on docker compose

**Solution**:
```bash
sudo usermod -aG docker $USER
# Log out and back in
newgrp docker
docker-compose up -d
```

---

## Diagnostic Commands

### Modbus Diagnostics

```bash
# Test Modbus connectivity
python3 << 'EOF'
from pymodbus.client import ModbusTcpClient
client = ModbusTcpClient("192.168.9.106", port=502)
if client.connect():
    result = client.read_input_registers(5031, 2, slave=1)
    print(f"Success: {result.registers}")
else:
    print("Failed to connect")
client.close()
EOF
```

### MQTT Diagnostics

```bash
# Subscribe and watch for messages
mosquitto_sub -h 192.168.1.50 -u ha_user -P password -t "sungrow/#" -v

# Publish test message
mosquitto_pub -h 192.168.1.50 -u ha_user -P password -t "test/message" -m "hello"

# Check broker status
mosquitto_passwd -c /tmp/testpass testuser testpass
mosquitto -c /tmp/mosquitto.conf
```

### Network Diagnostics

```bash
# Check if inverter reachable
ping -c 4 192.168.9.106

# Check port open
nmap -p 502 192.168.9.106
nmap -p 1883 192.168.1.50

# Check routing
traceroute 192.168.9.106

# Monitor network traffic
tcpdump -i en0 host 192.168.9.106 -v
```

### Home Assistant Logs

**CLI access**:
```bash
# SSH into HA host
ssh homeassistant@192.168.1.50

# Check logs
cat /home/homeassistant/.homeassistant/home-assistant.log | grep -i sungrow
```

---

## Getting Help

1. **Check GitHub issues** - Your model may have known issues
2. **Find register map** - https://github.com/bohdan-s/Sungrow-Inverter
3. **Test with Python** - Narrow down if issue is Modbus or MQTT
4. **Check inverter firmware** - Update to latest if available
5. **Use wired connection** - Eliminate Wi-Fi as variable

---

## Still Stuck?

Provide:
- Inverter model (SG5K-D, SH10RT, etc.)
- Firmware version (Settings → Information)
- Error message or logs
- Network topology (DHCP, static IP, Wi-Fi/Ethernet)
- Steps you've already tried
