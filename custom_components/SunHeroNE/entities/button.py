from homeassistant.components.button import ButtonEntity
from .base import SunHeroBaseEntity

class SunHeroButton(SunHeroBaseEntity, ButtonEntity):
    async def async_press(self) -> None:
        if self._source == "json":
            await self._device.async_send_json_command(self._key)
        elif self._source == "modbus":
            val = self._config.get("write_value", 1)
            await self._device.async_write_modbus(
                self._config.get('slave', 1),
                self._config['register'],
                val,
                self._config.get('data_type', 'uint16'),
                config=self._config
            )
