import voluptuous as vol
from homeassistant import config_entries
from pymodbus.client import AsyncModbusTcpClient

from .const import DOMAIN, DEFAULT_NAME, DEFAULT_PORT, DEFAULT_SLAVE

DATA_SCHEMA = vol.Schema(
    {
        vol.Required("host"): str,
        vol.Optional("port", default=DEFAULT_PORT): int,
        vol.Optional("slave", default=DEFAULT_SLAVE): int,
    }
)


class SungrowConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            try:
                client = AsyncModbusTcpClient(
                    user_input["host"], port=user_input["port"]
                )
                await client.connect()
                if not client.connected:
                    raise ConnectionError("Failed to connect")
                await client.close()
                return self.async_create_entry(title=DEFAULT_NAME, data=user_input)
            except Exception:
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )
