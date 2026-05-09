#!/usr/bin/env python3
import argparse
import logging
import signal
import time

import yaml

from .modbus_client import SungrowModbusClient
from .mqtt_publisher import MqttPublisher
from .registers import REGISTERS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
_LOGGER = logging.getLogger(__name__)

_running = True


def _handle_signal(*_):
    global _running
    _running = False


def main():
    parser = argparse.ArgumentParser(description="Sungrow Modbus to MQTT bridge")
    parser.add_argument(
        "-c", "--config", default="config.yaml", help="Path to config file"
    )
    args = parser.parse_args()

    with open(args.config) as f:
        config = yaml.safe_load(f)

    inv = config["inverter"]
    mq = config["mqtt"]

    modbus = SungrowModbusClient(inv["host"], inv.get("port", 502), inv.get("slave", 1))
    if not modbus.connect():
        _LOGGER.error("Failed to connect to inverter at %s:%d", inv["host"], inv.get("port", 502))
        return

    publisher = MqttPublisher(
        host=mq["host"],
        port=mq.get("port", 1883),
        username=mq.get("username", ""),
        password=mq.get("password", ""),
        topic_prefix=mq.get("topic_prefix", "sungrow/sg10rt"),
        ha_discovery=mq.get("ha_discovery", True),
        ha_discovery_prefix=mq.get("ha_discovery_prefix", "homeassistant"),
    )

    device_id = f"sungrow_sg10rt_{inv['host'].replace('.', '_')}"
    scan_interval = inv.get("scan_interval", 10)

    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    _LOGGER.info("Bridge started — polling every %ds", scan_interval)

    while _running:
        for reg in REGISTERS:
            publisher.publish_discovery(reg, device_id)
            value = modbus.read_register(reg)
            if value is not None:
                publisher.publish_value(reg, value)
        time.sleep(scan_interval)

    _LOGGER.info("Shutting down")
    publisher.stop()
    modbus.close()


if __name__ == "__main__":
    main()
