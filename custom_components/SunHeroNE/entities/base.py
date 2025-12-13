"""SunHeroNE base entity for integration.

SunHeroNE or sunherone © 2025 by @maybetaken is
licensed under Creative Commons
Attribution-NonCommercial-NoDerivatives 4.0 International.
"""

from homeassistant.helpers.entity import Entity, EntityCategory
from ..const import DOMAIN

entityMap = {"diagnostic": EntityCategory.DIAGNOSTIC,
                "config": EntityCategory.CONFIG}


class SunHeroBaseEntity(Entity):
    """
    Base class for all SunHero entities.
    Handles common attributes: name, icon, device_class, entity_category.
    """
    def __init__(self, device, config, entry_id):
        self._device = device
        self._config = config
        self._key = config['key']
        self._source = config.get("source", "modbus")
        
        self._attr_unique_id = f"{device.device_id}_{self._key}"
        self._attr_has_entity_name = True
        self._attr_translation_key = self._key
        self._attr_entity_category = entityMap.get(config.get("entity_category"), None)
        self._attr_device_class = config.get("device_class", None)
        if "icon" in config:
            self._attr_icon = config["icon"]
        
        self._value = self._device.get_value_by_key(self._key)
        if self._value is not None:
            self._value = self._process_raw_value(self._value)

    @property
    def available(self):
        return self._device.is_source_available(self._source)

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._device.device_id)},
            "name": f"{self._device.device_id} {self._device.model}",
            "model": self._device.model,
            "manufacturer": self._device.config.get("manufacturer", "SunHero"),
            "sw_version": self._device.get_version(),
        }

    async def async_added_to_hass(self):
        self._device.register_callback(self._key, self._handle_update)

    async def async_will_remove_from_hass(self):
        self._device.remove_callback(self._key, self._handle_update)

    def _handle_update(self, new_value=None):
        if new_value is not None:
            self._value = self._process_raw_value(new_value)
        self.schedule_update_ha_state()

    def _process_raw_value(self, value):
        return value
