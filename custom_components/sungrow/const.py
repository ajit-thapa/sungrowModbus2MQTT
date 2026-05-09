DOMAIN = "sungrow"
DEFAULT_NAME = "Sungrow Inverter"
DEFAULT_PORT = 502
DEFAULT_SLAVE = 1

# ⚠️ CRITICAL NOTES:
# 1. Modbus TCP must be enabled on inverter: Settings → Communication → Modbus TCP
# 2. SG series (SG10RT, etc.): Requires WiNet-S dongle, NOT internal LAN port
# 3. SH series: Can use internal LAN port or WiNet-S
# 4. 0kW export limit = UNLIMITED (not zero). Use 10W for actual zero export.
# 5. Register addresses may vary by model - adjust SENSOR_REGISTERS if needed

SENSOR_REGISTERS = {
    "total_active_power": {
        "address": 5031,
        "type": "uint32",
        "scale": 1,
        "unit": "W",
        "device_class": "power",
    },
    "daily_yield": {
        "address": 5003,
        "type": "uint16",
        "scale": 0.1,
        "unit": "kWh",
        "device_class": "energy",
    },
    "total_yield": {
        "address": 5004,
        "type": "uint32",
        "scale": 0.1,
        "unit": "kWh",
        "device_class": "energy",
    },
    "internal_temperature": {
        "address": 5008,
        "type": "int16",
        "scale": 0.1,
        "unit": "°C",
        "device_class": "temperature",
    },
    "total_running_time": {
        "address": 5006,
        "type": "uint32",
        "scale": 1,
        "unit": "h",
        "device_class": "duration",
    },
    "mppt1_voltage": {
        "address": 5011,
        "type": "uint16",
        "scale": 0.1,
        "unit": "V",
        "device_class": "voltage",
    },
    "mppt1_current": {
        "address": 5012,
        "type": "uint16",
        "scale": 0.1,
        "unit": "A",
        "device_class": "current",
    },
    "mppt2_voltage": {
        "address": 5013,
        "type": "uint16",
        "scale": 0.1,
        "unit": "V",
        "device_class": "voltage",
    },
    "mppt2_current": {
        "address": 5014,
        "type": "uint16",
        "scale": 0.1,
        "unit": "A",
        "device_class": "current",
    },
    "grid_frequency": {
        "address": 5036,
        "type": "uint16",
        "scale": 0.1,
        "unit": "Hz",
        "device_class": "frequency",
    },
    "reactive_power": {
        "address": 5033,
        "type": "int32",
        "scale": 1,
        "unit": "var",
        "device_class": "reactive_power",
    },
    "power_factor": {
        "address": 5035,
        "type": "int16",
        "scale": 0.001,
        "unit": "",
        "device_class": "power_factor",
    },
    "phase_a_voltage": {
        "address": 5019,
        "type": "uint16",
        "scale": 0.1,
        "unit": "V",
        "device_class": "voltage",
    },
    "phase_a_current": {
        "address": 5022,
        "type": "uint16",
        "scale": 0.1,
        "unit": "A",
        "device_class": "current",
    },
    "nominal_active_power": {
        "address": 5001,
        "type": "uint16",
        "scale": 100,
        "unit": "W",
        "device_class": "power",
    },
}

CONTROL_REGISTERS = {
    "export_limit_percent": {
        "address": 5000,
        "type": "uint16",
        "scale": 0.1,
        "min": 0,
        "max": 100,
        "unit": "%",
    },
}
