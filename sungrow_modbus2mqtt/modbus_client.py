import logging
import struct

from pymodbus.client import ModbusTcpClient

from .registers import Register

_LOGGER = logging.getLogger(__name__)


class SungrowModbusClient:
    def __init__(self, host: str, port: int = 502, slave: int = 1):
        self._host = host
        self._port = port
        self._slave = slave
        self._client = ModbusTcpClient(host, port=port)

    def connect(self) -> bool:
        return self._client.connect()

    def close(self):
        self._client.close()

    def read_register(self, reg: Register) -> float | None:
        count = 2 if "32" in reg.reg_type else 1
        result = self._client.read_input_registers(
            address=reg.address, count=count, slave=self._slave
        )
        if result.isError():
            _LOGGER.warning("Failed to read %s at %d", reg.name, reg.address)
            return None

        regs = result.registers
        if reg.reg_type == "uint16":
            raw = regs[0]
        elif reg.reg_type == "int16":
            raw = struct.unpack(">h", struct.pack(">H", regs[0]))[0]
        elif reg.reg_type == "uint32":
            raw = (regs[0] << 16) | regs[1]
        elif reg.reg_type == "int32":
            raw = struct.unpack(">i", struct.pack(">HH", regs[0], regs[1]))[0]
        else:
            return None

        return round(raw * reg.scale, 3)

    def write_register(self, address: int, value: int) -> bool:
        result = self._client.write_register(
            address=address, value=value, slave=self._slave
        )
        return not result.isError()
