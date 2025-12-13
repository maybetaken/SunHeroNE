"""SunHeroNE binary sensor for integration.

SunHeroNE or sunherone © 2025 by @maybetaken is
licensed under Creative Commons
Attribution-NonCommercial-NoDerivatives 4.0 International.
"""

from homeassistant.components.binary_sensor import BinarySensorEntity
from .base import SunHeroBaseEntity

class SunHeroBinarySensor(SunHeroBaseEntity, BinarySensorEntity):
    def __init__(self, device, config, entry_id):
        self._attr_device_class = config.get("device_class")
        super().__init__(device, config, entry_id)

    @property
    def is_on(self):
        return bool(self._value)
