from homeassistant.components.sensor import (
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, SENSOR_REGISTERS


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
):
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    device_info = data["device_info"]

    async_add_entities(
        SungrowSensor(coordinator, entry, key, cfg, device_info)
        for key, cfg in SENSOR_REGISTERS.items()
    )


class SungrowSensor(CoordinatorEntity, SensorEntity):
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_has_entity_name = True

    def __init__(self, coordinator, entry, key, cfg, device_info):
        super().__init__(coordinator)
        self._key = key
        self._scale = cfg.get("scale", 1)
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_translation_key = key
        self._attr_name = key.replace("_", " ").title()
        self._attr_native_unit_of_measurement = cfg.get("unit")
        self._attr_device_class = cfg.get("device_class")
        self._attr_device_info = device_info

    @property
    def native_value(self):
        if self.coordinator.data and self._key in self.coordinator.data:
            return round(self.coordinator.data[self._key] * self._scale, 2)
        return None
