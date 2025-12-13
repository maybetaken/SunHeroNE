import time
import json
import logging
import asyncio
from datetime import timedelta
from ..protocol.json_codec import SystemJsonCodec
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.event import async_track_time_interval
from ..const import DOMAIN

_LOGGER = logging.getLogger(__name__)

class SunHeroBaseDevice:
    def __init__(self, hass, device_id, model, config_json):
        self.hass = hass
        self.device_id = device_id
        self.model = model
        self.config = config_json
        
        self.data_cache = {}
        self._last_seen = { "json": 0, "modbus": 0 }
        self._available_state = { "json": False, "modbus": False }
        self._timeout = 120 
        self._callbacks = {}
        self._mqtt_publish = None
        self.entities_by_platform = { 
            "sensor": [], "switch": [], "button": [], 
            "number": [], "select": [], "binary_sensor": [] 
        }
        self.json_map = {} 
        self.buttons_map = {}
        
        for item in config_json.get("entities", []):
            e_type = item.get("type", "sensor_data")
            ha_plat = "sensor"
            if "switch" in e_type: ha_plat = "switch"
            elif "button" in e_type: ha_plat = "button"
            elif "number" in e_type: ha_plat = "number"
            elif "select" in e_type: ha_plat = "select"
            elif "binary" in e_type: ha_plat = "binary_sensor"
            
            if ha_plat in self.entities_by_platform:
                self.entities_by_platform[ha_plat].append(item)
            
            if item.get("source") == "json":
                if "json_key" in item:
                    jk = item['json_key']
                    if jk not in self.json_map: self.json_map[jk] = []
                    self.json_map[jk].append(item)
                if e_type == "button" or e_type == "switch":
                    self.buttons_map[item['key']] = item

        self._remove_timer = async_track_time_interval(
            self.hass, self.check_availability, timedelta(seconds=10)
        )

    def stop(self):
        if self._remove_timer: self._remove_timer()

    def set_mqtt_publisher(self, func):
        self._mqtt_publish = func

    def register_callback(self, key, cb):
        if key not in self._callbacks: self._callbacks[key] = set()
        self._callbacks[key].add(cb)

    def remove_callback(self, key, cb):
        if key in self._callbacks: self._callbacks[key].discard(cb)

    def _reset_timer(self, source_type):
        self._last_seen[source_type] = int(time.time())
        if not self._available_state[source_type]:
            self._available_state[source_type] = True
            self._notify_source_status(source_type)

    def check_availability(self, now=None):
        current_time = time.time()
        for source in ["json", "modbus"]:
            if self._available_state[source]:
                if (current_time - self._last_seen[source]) > self._timeout:
                    self._available_state[source] = False
                    self._notify_source_status(source)

    def is_source_available(self, source_type):
        return self._available_state.get(source_type, False)

    def _notify_source_status(self, source_type):
        all_cbs = [cb for cbs in self._callbacks.values() for cb in cbs]
        for cb in set(all_cbs):
            try: cb(None)
            except: pass

    def apply_updates(self, updates: dict):
        for key, new_val in updates.items():
            old_val = self.data_cache.get(key)
            if old_val != new_val:
                self.data_cache[key] = new_val
                
                if key == "sys_version": 
                    self._update_registry_version(new_val)
                
                if key in self._callbacks:
                    for cb in self._callbacks[key]:
                        try: cb(new_val)
                        except: pass

    async def _send_config_on_version_report(self):
        await asyncio.sleep(1) 
        await self.async_send_config_to_device()

    def on_message_received(self, msg_type, payload):
        if msg_type == "info" or (len(payload) > 0 and payload[0] == 0x7B):
             self._handle_json_msg(payload)
        elif msg_type == "sys_version":
             try:
                 ver_str = payload.decode("utf-8")
                 self._handle_json_msg(json.dumps({"ver": ver_str}).encode())
                 self.hass.async_create_task(self._send_config_on_version_report())
             except: pass
        else:
             self.on_protocol_msg(msg_type, payload)

    def _handle_json_msg(self, payload):
        data = SystemJsonCodec.decode(payload)
        if not data: return
        self._reset_timer("json")
        
        updates = {}
        for k, v in data.items():
            if k in self.json_map:
                for config in self.json_map[k]:
                    key = config['key']
                    updates[key] = v

        if updates:
            self.apply_updates(updates)           

    def on_protocol_msg(self, msg_type, payload):
        pass

    def get_value_by_key(self, key):
        return self.data_cache.get(key)
    
    def get_version(self):
        return self.data_cache.get("sys_version", "1.0.0")

    def _update_registry_version(self, version):
        dev_reg = dr.async_get(self.hass)
        device = dev_reg.async_get_device(identifiers={(DOMAIN, self.device_id)})
        if device and device.sw_version != version:
            dev_reg.async_update_device(device.id, sw_version=version)

    async def async_send_json_command(self, key_name, custom_payload=None):
        if key_name in self.buttons_map:
            cfg = self.buttons_map[key_name]
            payload = custom_payload if custom_payload else cfg.get("command_payload", {})
            if self._mqtt_publish:
                await self._mqtt_publish(
                    self.device_id, None, "cmd", 
                    SystemJsonCodec.encode_command(payload)
                )

    async def async_send_config_to_device(self):
        payload = self.get_config_payload()
        if self._mqtt_publish and payload:
            await self._mqtt_publish(self.device_id, None, "config", json.dumps(payload))

    async def async_request_initial_status(self):
        """Send a command to device asking for immediate status report."""
        if self._mqtt_publish:
            await self._mqtt_publish(
                self.device_id, None, "cmd", 
                json.dumps({"cmd": "report_status"})
            )

    def get_config_payload(self):
        return {}
