"""SunHeroNE select entry for integration.

SunHeroNE or sunherone © 2025 by @maybetaken is
licensed under Creative Commons
Attribution-NonCommercial-NoDerivatives 4.0 International.
"""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN
from .entities.select import SunHeroSelectMapping

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    if "device" not in hass.data[DOMAIN][entry.entry_id]: return
    device = hass.data[DOMAIN][entry.entry_id]["device"]
    entities = []
    for config in device.entities_by_platform.get("select", []):
        if config.get("type") == "select_mapping":
            entities.append(SunHeroSelectMapping(device, config, entry.entry_id))
    async_add_entities(entities)
