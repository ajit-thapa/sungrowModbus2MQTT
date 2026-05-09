from dataclasses import dataclass


@dataclass
class Register:
    address: int
    name: str
    reg_type: str
    scale: float = 1.0
    unit: str = ""
    device_class: str = ""
    state_class: str = "measurement"
    writable: bool = False


REGISTERS = [
    Register(5031, "total_active_power", "uint32", unit="W", device_class="power"),
    Register(5003, "daily_yield", "uint16", scale=0.1, unit="kWh", device_class="energy", state_class="total_increasing"),
    Register(5004, "total_yield", "uint32", scale=0.1, unit="kWh", device_class="energy", state_class="total_increasing"),
    Register(5008, "internal_temperature", "int16", scale=0.1, unit="°C", device_class="temperature"),
    Register(5006, "total_running_time", "uint32", unit="h", device_class="duration"),
    Register(5011, "mppt1_voltage", "uint16", scale=0.1, unit="V", device_class="voltage"),
    Register(5012, "mppt1_current", "uint16", scale=0.1, unit="A", device_class="current"),
    Register(5013, "mppt2_voltage", "uint16", scale=0.1, unit="V", device_class="voltage"),
    Register(5014, "mppt2_current", "uint16", scale=0.1, unit="A", device_class="current"),
    Register(5036, "grid_frequency", "uint16", scale=0.1, unit="Hz", device_class="frequency"),
    Register(5033, "reactive_power", "int32", unit="var", device_class="reactive_power"),
    Register(5035, "power_factor", "int16", scale=0.001, device_class="power_factor"),
    Register(5019, "phase_a_voltage", "uint16", scale=0.1, unit="V", device_class="voltage"),
    Register(5022, "phase_a_current", "uint16", scale=0.1, unit="A", device_class="current"),
    Register(5001, "nominal_active_power", "uint16", scale=100, unit="W", device_class="power"),
]
