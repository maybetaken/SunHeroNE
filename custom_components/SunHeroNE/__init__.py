import os
import json
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import (
    DOMAIN, 
    CONF_DEVICE_ID, 
    CONF_MODEL, 
    CONF_MQTT_HOST
)
from .manager import CentralMqttManager
from .devices import get_device_instance
from .broadcaster import SunHeroBroadcaster 

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor", "switch", "button", "number", "select", "binary_sensor"]

def load_json_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    hass.data.setdefault(DOMAIN, {})

    if "manager" not in hass.data[DOMAIN]:
        manager = CentralMqttManager(hass)
        await manager.async_start()
        hass.data[DOMAIN]["manager"] = manager
    else:
        manager = hass.data[DOMAIN]["manager"]

    if CONF_MQTT_HOST in entry.data:
        _LOGGER.info("Setting up SunHero Hub & SSDP Broadcaster")
        broadcaster = SunHeroBroadcaster(hass, entry.data)
        await broadcaster.async_start()
        hass.data[DOMAIN]["broadcaster"] = broadcaster
        return True

    device_id = entry.data.get(CONF_DEVICE_ID)
    model = entry.data.get(CONF_MODEL, "default")
    
    if not device_id: return False

    _LOGGER.info(f"Setting up SunHero Device: {model} ({device_id})")

    json_path = os.path.join(os.path.dirname(__file__), "device_definitions", f"{model}.json")
    if not os.path.exists(json_path):
        json_path = os.path.join(os.path.dirname(__file__), "device_definitions", "makeskyblue_mppt.json")

    try:
        config_json = await hass.async_add_executor_job(load_json_file, json_path)
    except Exception as e:
        _LOGGER.error(f"Failed to load device definition for {model}: {e}")
        return False

    device = get_device_instance(hass, device_id, model, config_json)
    manager.register_device(device)

    hass.data[DOMAIN][entry.entry_id] = {"device": device}

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    # Unload Hub
    if CONF_MQTT_HOST in entry.data:
        if "broadcaster" in hass.data[DOMAIN]:
            await hass.data[DOMAIN]["broadcaster"].async_stop()
            hass.data[DOMAIN].pop("broadcaster")
        return True

    # Unload Device
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        data = hass.data[DOMAIN].pop(entry.entry_id)
        device = data["device"]
        
        manager = hass.data[DOMAIN].get("manager")
        if manager:
            manager.unregister_device(device.device_id)
            
    return unload_ok
