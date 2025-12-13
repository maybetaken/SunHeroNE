"""SunHeroNE device factory for integration.

SunHeroNE or sunherone © 2025 by @maybetaken is
licensed under Creative Commons
Attribution-NonCommercial-NoDerivatives 4.0 International.
"""

from .modbus_device import SunHeroModbusDevice
from .impl.makeskyblue_mppt import SunHeroMakeSkyBlueMPPTDevice
from .impl.makeskyblue_wifi import SunHeroMakeSkyBlueWifiDevice

def get_device_instance(hass, device_id, model, config_json):
    model_lower = model.lower()
    if "makeskyblue_mppt" in model_lower:
        return SunHeroMakeSkyBlueMPPTDevice(hass, device_id, model, config_json)
    if "makeskyblue" in model_lower:
        return SunHeroMakeSkyBlueWifiDevice(hass, device_id, model, config_json)
    return SunHeroModbusDevice(hass, device_id, model, config_json)
