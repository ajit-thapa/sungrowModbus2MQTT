import json
import logging

import paho.mqtt.client as mqtt

from .registers import Register

_LOGGER = logging.getLogger(__name__)


class MqttPublisher:
    def __init__(
        self,
        host: str,
        port: int = 1883,
        username: str = "",
        password: str = "",
        topic_prefix: str = "sungrow/sg10rt",
        ha_discovery: bool = True,
        ha_discovery_prefix: str = "homeassistant",
    ):
        self._topic_prefix = topic_prefix
        self._ha_discovery = ha_discovery
        self._ha_discovery_prefix = ha_discovery_prefix
        self._client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        if username:
            self._client.username_pw_set(username, password)
        self._client.connect(host, port)
        self._client.loop_start()
        self._discovered: set[str] = set()

    def publish_discovery(self, reg: Register, device_id: str):
        if not self._ha_discovery or reg.name in self._discovered:
            return
        config = {
            "name": reg.name.replace("_", " ").title(),
            "state_topic": f"{self._topic_prefix}/{reg.name}",
            "unique_id": f"{device_id}_{reg.name}",
            "device": {
                "identifiers": [device_id],
                "name": "Sungrow SG10RT",
                "manufacturer": "Sungrow",
                "model": "SG10RT",
            },
        }
        if reg.unit:
            config["unit_of_measurement"] = reg.unit
        if reg.device_class:
            config["device_class"] = reg.device_class
        if reg.state_class:
            config["state_class"] = reg.state_class

        topic = f"{self._ha_discovery_prefix}/sensor/{device_id}/{reg.name}/config"
        self._client.publish(topic, json.dumps(config), retain=True)
        self._discovered.add(reg.name)

    def publish_value(self, reg: Register, value: float):
        self._client.publish(f"{self._topic_prefix}/{reg.name}", str(value), retain=True)

    def stop(self):
        self._client.loop_stop()
        self._client.disconnect()
