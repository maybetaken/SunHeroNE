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
