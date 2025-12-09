from .base import SunHeroBaseDevice
from ..protocol.modbus_codec import ModbusBinaryCodec

class SunHeroModbusDevice(SunHeroBaseDevice):
    def __init__(self, hass, device_id, model, config_json):
        super().__init__(hass, device_id, model, config_json)
        
        # Key: (slave, func_code, register)
        self.modbus_map = {}
        
        for item in config_json.get("entities", []):
            if item.get("source", "modbus") == "modbus":
                slave = item.get('slave', 1)
                register = item['register']
                # Default Read Function is 3
                func = item.get('modbus_func', 3)
                
                key = (slave, func, register)
                
                if key not in self.modbus_map: 
                    self.modbus_map[key] = []
                self.modbus_map[key].append(item)

    def on_protocol_msg(self, msg_type, payload):
        # Decode: [Slave][Func][Start][Count][Data...]
        slave, func_code, start, raw = ModbusBinaryCodec.decode_block(payload)
        if slave is None: return
        
        self._reset_timer("modbus")
        
        total_len = len(raw)
        end = start + (total_len // 2)
        updates = {}

        for reg in range(start, end):
            # Lookup using (slave, func_code, register)
            configs = self.modbus_map.get((slave, func_code, reg))
            
            if configs:
                offset = (reg - start) * 2
                for cfg in configs:
                    req_len = ModbusBinaryCodec.get_byte_length(cfg)
                    if offset + req_len <= total_len:
                        chunk = raw[offset : offset + req_len]
                        val = ModbusBinaryCodec.parse_value(chunk, cfg)
                        
                        if val is not None:
                            if "scale" in cfg and isinstance(val, (int, float)):
                                val *= cfg["scale"]
                            val = self.transform_value(cfg, val)   
                            updates[cfg['key']] = val
        if updates:
            self.apply_updates(updates)

    async def async_write_modbus(self, slave, register, value, dtype, config=None):
        raw_val = value

        if config and "scale" in config and isinstance(value, (int, float)):
             raw_val = int(value / config["scale"])

        write_cmd = 6
        if config:
            write_cmd = config.get("write_command", 6)

        payload = ModbusBinaryCodec.encode_write(slave, register, raw_val, write_cmd)

        if self._mqtt_publish:
            await self._mqtt_publish(self.device_id, slave, "set", payload)

    def get_config_payload(self):
        return self.config.get("modbus_config", {})
    
    def transform_value(self, config, value):
        """
        Hook for subclasses to modify value based on config.
        Default implementation returns value as-is.
        """
        return value
