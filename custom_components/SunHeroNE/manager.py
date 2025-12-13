"""SunHeroNE Manager for integration.

SunHeroNE or sunherone © 2025 by @maybetaken is
licensed under Creative Commons
Attribution-NonCommercial-NoDerivatives 4.0 International.
"""

import asyncio
import logging
import time
import json
from homeassistant.core import HomeAssistant
from homeassistant.components import mqtt
from .const import TOPIC_GLOBAL_HEARTBEAT

_LOGGER = logging.getLogger(__name__)

class CentralMqttManager:
    def __init__(self, hass: HomeAssistant):
        self.hass = hass
        self._devices = {}
        self._unsub = None
        self._hb_task = None
        self._background_tasks = set()

    async def async_start(self):
        if self._unsub: return
        topic = "SunHeroNE/#"
        self._unsub = await mqtt.async_subscribe(self.hass, topic, self._mqtt_callback, qos=0, encoding=None)
        _LOGGER.info(f"SunHeroNE Manager subscribed to {topic}")
        self._hb_task = asyncio.create_task(self._heartbeat_loop())

    async def async_stop(self):
        if self._unsub:
            self._unsub()
            self._unsub = None
        if self._hb_task: self._hb_task.cancel()
        for task in self._background_tasks:
            task.cancel()
        self._background_tasks.clear()

    def register_device(self, device):
        self._devices[device.device_id] = device
        device.set_mqtt_publisher(self.publish_to_device)
        task = asyncio.create_task(self._send_init_commands(device))
        self._background_tasks.add(task)
        task.add_done_callback(self._background_tasks.discard)

    def unregister_device(self, device_id):
        if device_id in self._devices:
            self._devices[device_id].stop()
            del self._devices[device_id]

    async def _send_init_commands(self, device):
        """Send Config and ask for Status immediately."""
        try:
            await asyncio.sleep(2) 
            await device.async_send_config_to_device()
            await asyncio.sleep(1)
            await device.async_request_initial_status()
        except Exception as e:
            _LOGGER.error(f"Failed to send init commands to {device.device_id}: {e}")

    async def _mqtt_callback(self, msg):
        try:
            parts = msg.topic.split('/')
            length = len(parts)
            if length < 3: return
            sn = parts[1]

            msg_type = parts[-1]
            if msg_type in ["cmd", "set", "config", "ota"]: return
            
            if sn in self._devices:
                if length == 4:
                    self._devices[sn].on_message_received(parts[3], msg.payload)
                elif length == 3:
                    self._devices[sn].on_message_received(parts[2], msg.payload)
        except Exception:
            pass

    async def publish_to_device(self, sn, slave_id, type_str, payload):
        if slave_id == None:
             topic = f"SunHeroNE/{sn}/" + type_str
        else:
             topic = f"SunHeroNE/{sn}/{slave_id}/{type_str}"
        await mqtt.async_publish(self.hass, topic, payload, qos=1)

    async def _heartbeat_loop(self):
        while True:
            await mqtt.async_publish(self.hass, TOPIC_GLOBAL_HEARTBEAT, str(time.time()), qos=0)
            await asyncio.sleep(5)
