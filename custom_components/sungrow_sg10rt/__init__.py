import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from pymodbus.client import AsyncModbusTcpClient
from pysungrow import identify, SungrowClient

from .const import DOMAIN, DEFAULT_PORT

_LOGGER = logging.getLogger(__name__)
PLATFORMS = ["sensor", "number"]
SCAN_INTERVAL = timedelta(seconds=10)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})

    client = AsyncModbusTcpClient(
        entry.data["host"],
        port=entry.data.get("port", DEFAULT_PORT),
    )
    await client.connect()

    serial_number, device, output_type = await identify(client)
    sungrow_client = SungrowClient(client, device, output_type)

    coordinator = SungrowDataCoordinator(hass, sungrow_client, entry)
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "client": sungrow_client,
        "modbus_client": client,
        "device_info": DeviceInfo(
            identifiers={(DOMAIN, serial_number)},
            name=f"Sungrow {device.name}",
            manufacturer="Sungrow",
            model=device.name,
            serial_number=serial_number,
        ),
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        data = hass.data[DOMAIN].pop(entry.entry_id)
        await data["modbus_client"].close()
    return unload_ok


class SungrowDataCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, client: SungrowClient, entry: ConfigEntry):
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{entry.entry_id}",
            update_interval=SCAN_INTERVAL,
        )
        self.client = client

    async def _async_update_data(self):
        try:
            return await self.client.get_all()
        except Exception as err:
            raise UpdateFailed(f"Error communicating with inverter: {err}") from err
