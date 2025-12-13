"""SunHeroNE select entity for integration.

SunHeroNE or sunherone © 2025 by @maybetaken is
licensed under Creative Commons
Attribution-NonCommercial-NoDerivatives 4.0 International.
"""

from homeassistant.components.select import SelectEntity
from .base import SunHeroBaseEntity

class SunHeroSelectMapping(SunHeroBaseEntity, SelectEntity):
    def __init__(self, device, config, entry_id):
        self._map = config.get("map", {})
        self._attr_options = list(self._map.values())
        super().__init__(device, config, entry_id)

    def _process_raw_value(self, raw):
        val_str = str(raw)
        return self._map.get(val_str)

    @property
    def current_option(self):
        return self._value

    async def async_select_option(self, option: str) -> None:
        val_to_send = None
        for k, v in self._map.items():
            if v == option:
                try: val_to_send = int(k)
                except: val_to_send = k
                break
        
        if val_to_send is not None:
            await self._device.async_write_modbus(
                self._config.get('slave', 1),
                self._config['register'],
                val_to_send,
                self._config.get('data_type', 'uint16'),
                config=self._config
            )
