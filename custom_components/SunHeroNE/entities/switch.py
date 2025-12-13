"""SunHeroNE switch entity for integration.

SunHeroNE or sunherone © 2025 by @maybetaken is
licensed under Creative Commons
Attribution-NonCommercial-NoDerivatives 4.0 International.
"""

from homeassistant.components.switch import SwitchEntity
from .base import SunHeroBaseEntity

class SunHeroSwitch(SunHeroBaseEntity, SwitchEntity):
    @property
    def is_on(self):
        val = self._value
        if val is None: return None
        if isinstance(val, str):
            v = val.lower()
            if v in ("on", "true", "1", "yes"): return True
            if v in ("off", "false", "0", "no"): return False
        return bool(val)

    async def async_turn_on(self, **kwargs):
        await self._send(1)

    async def async_turn_off(self, **kwargs):
        await self._send(0)

    async def _send(self, val):
        if self._source == "json":
            key = self._config.get("json_key", self._key)
            await self._device.async_send_json_command(self._key, {key: val})
        else:
            await self._device.async_write_modbus(
                self._config.get('slave', 1),
                self._config['register'],
                val,
                self._config.get('data_type', 'uint16')
            )
