from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN
from .entities.button import SunHeroButton

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    if "device" not in hass.data[DOMAIN][entry.entry_id]: return
    device = hass.data[DOMAIN][entry.entry_id]["device"]
    entities = []
    for config in device.entities_by_platform.get("button", []):
        entities.append(SunHeroButton(device, config, entry.entry_id))
    async_add_entities(entities)
