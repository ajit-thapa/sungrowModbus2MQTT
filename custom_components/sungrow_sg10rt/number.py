from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, CONTROL_REGISTERS


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
):
    data = hass.data[DOMAIN][entry.entry_id]
    modbus_client = data["modbus_client"]
    device_info = data["device_info"]
    slave = entry.data.get("slave", 1)

    async_add_entities(
        SungrowNumber(modbus_client, entry, key, cfg, device_info, slave)
        for key, cfg in CONTROL_REGISTERS.items()
    )


class SungrowNumber(NumberEntity):
    _attr_has_entity_name = True

    def __init__(self, client, entry, key, cfg, device_info, slave):
        self._client = client
        self._slave = slave
        self._address = cfg["address"]
        self._scale = cfg.get("scale", 1)
        self._value = None
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_name = key.replace("_", " ").title()
        self._attr_native_min_value = cfg.get("min", 0)
        self._attr_native_max_value = cfg.get("max", 100)
        self._attr_native_step = cfg.get("scale", 0.1)
        self._attr_native_unit_of_measurement = cfg.get("unit")
        self._attr_device_info = device_info

    @property
    def native_value(self):
        return self._value

    async def async_set_native_value(self, value: float):
        raw = int(value / self._scale)
        await self._client.write_register(
            address=self._address, value=raw, slave=self._slave
        )
        self._value = value
        self.async_write_ha_state()
