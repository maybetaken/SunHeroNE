"""SunHeroNE sensor entity for integration.

SunHeroNE or sunherone © 2025 by @maybetaken is
licensed under Creative Commons
Attribution-NonCommercial-NoDerivatives 4.0 International.
"""

from homeassistant.components.sensor import SensorEntity
from .base import SunHeroBaseEntity

class SunHeroSensorData(SunHeroBaseEntity, SensorEntity):
    """Numeric Sensor (Voltage, Power, Energy, etc.)"""
    def __init__(self, device, config, entry_id):
        super().__init__(device, config, entry_id)
        self._attr_native_unit_of_measurement = config.get("unit")
        self._attr_state_class = config.get("state_class")
        
        if "precision" in config:
            self._attr_suggested_display_precision = config["precision"]
        self._scale = config.get("scale", 1.0)
        self._offset = config.get("offset", 0.0)
        self._precision = config.get("precision", 0)
        self._data_type = config.get("data_type", "uint16")

    def _process_raw_value(self, raw):
        if self._data_type in ["string", "ipv4"]:
            return str(raw)

        try:
            val = (float(raw) - self._offset) * self._scale
            if self._precision == 0:
                return int(round(val))
            return round(val, self._precision)
        except (ValueError, TypeError):
            return raw

    @property
    def native_value(self):
        return self._value

class SunHeroSensorMapping(SunHeroBaseEntity, SensorEntity):
    """Enum/Text Sensor (Status, Errors)"""
    def __init__(self, device, config, entry_id):
        super().__init__(device, config, entry_id)
        self._map = config.get("map", {})
        self._attr_device_class = "enum"
        self._attr_options = list(self._map.values())

    def _process_raw_value(self, raw):
        val_str = str(raw)
        return self._map.get(val_str, None)

    @property
    def native_value(self):
        return self._value
