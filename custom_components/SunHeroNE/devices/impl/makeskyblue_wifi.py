from ..modbus_device import SunHeroModbusDevice

class SunHeroMakeSkyBlueWifiDevice(SunHeroModbusDevice):
    def transform_value(self, config, value):
        """Handle custom data transformations."""

        if config.get("key") == "sw_version" and isinstance(value, int):

            minor = value & 0x3F
            middle = (value >> 6) & 0x0F
            major = (value >> 10) & 0x3F
            return f"V{major}.{middle}.{minor}"
            
        return value
