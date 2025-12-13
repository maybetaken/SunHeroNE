"""SunHeroNE number entity for integration.

SunHeroNE or sunherone © 2025 by @maybetaken is
licensed under Creative Commons
Attribution-NonCommercial-NoDerivatives 4.0 International.
"""

from homeassistant.components.number import NumberEntity
from .base import SunHeroBaseEntity

class SunHeroNumber(SunHeroBaseEntity, NumberEntity):
    def __init__(self, device, config, entry_id):
        self._attr_mode = "box"
        self._attr_native_min_value = config.get("min_value")
        self._attr_native_max_value = config.get("max_value")
        self._attr_native_step = config.get("step")
        self._attr_native_unit_of_measurement = config.get("unit")
        super().__init__(device, config, entry_id)

    @property
    def native_value(self):
        return self._value

    async def async_set_native_value(self, value: float) -> None:
        await self._device.async_write_modbus(
            self._config.get('slave', 1),
            self._config['register'],
            value,
            self._config.get('data_type', 'uint16'),
            config=self._config
        )
