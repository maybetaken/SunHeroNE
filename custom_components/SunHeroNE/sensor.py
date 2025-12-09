from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN
from .entities.sensor import SunHeroSensorData, SunHeroSensorMapping

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    if "device" not in hass.data[DOMAIN][entry.entry_id]: return
    device = hass.data[DOMAIN][entry.entry_id]["device"]
    entities = []
    
    for config in device.entities_by_platform.get("sensor", []):
        t = config.get("type")
        if t == "sensor_data":
            entities.append(SunHeroSensorData(device, config, entry.entry_id))
        elif t == "sensor_mapping":
            entities.append(SunHeroSensorMapping(device, config, entry.entry_id))
            
    async_add_entities(entities)
