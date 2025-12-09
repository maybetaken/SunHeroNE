import struct
import socket
import logging

_LOGGER = logging.getLogger(__name__)

class ModbusBinaryCodec:
    @staticmethod
    def decode_block(payload: bytes):
        """
        Decode received block.
        Format: [Slave(1B)][Func(1B)][Start(2B)][Count(2B)][Data...]
        """
        # Ensure minimum length (Header is 6 bytes)
        if len(payload) < 6:
            return None, None, None, None
            
        slave_id, func_code, start_addr, reg_count = struct.unpack_from(">BBHH", payload, 0)
        raw_data = payload[6:]
        return slave_id, func_code, start_addr, raw_data

    @staticmethod
    def get_byte_length(config: dict) -> int:
        dtype = config.get("data_type", "uint16")
        if dtype == "string": return config.get("length", 1) * 2
        if dtype in ["float32", "int32", "uint32", "ipv4"]: return 4
        return 2

    @staticmethod
    def parse_value(data_chunk: bytes, config: dict):
        dtype = config.get("data_type", "uint16")
        try:
            if dtype in ["uint8_low", "uint8_high", "bit"]:
                val_int = struct.unpack(">H", data_chunk)[0]
                
                if dtype == "uint8_low":
                    return val_int & 0xFF
                elif dtype == "uint8_high":
                    return (val_int >> 8) & 0xFF
                elif dtype == "bit":
                    idx = config.get("bit", 0)
                    return bool((val_int >> idx) & 1)

            elif dtype == "string":
                return data_chunk.decode("ascii", errors="ignore").strip('\x00').strip()
            elif dtype == "ipv4":
                if len(data_chunk) >= 4:
                    return socket.inet_ntop(socket.AF_INET, data_chunk[:4])
                return None
            elif dtype == "float32":
                return struct.unpack(">f", data_chunk)[0]
            elif dtype == "int16":
                return struct.unpack(">h", data_chunk)[0]
            elif dtype == "uint32":
                return struct.unpack(">I", data_chunk)[0]
            return struct.unpack(">H", data_chunk)[0]
        except Exception:
            return None

    @staticmethod
    def encode_write(slave: int, register: int, value: int, write_cmd: int = 6) -> bytes:
        """
        Standard Modbus Write Packet.
        Default: Function Code 06 (Write Single Register)
        Format: [Slave(1B)] [Cmd(1B)] [Addr(2B)] [Value(2B)]
        """

        if write_cmd == 6:
            return (
                struct.pack(">B", slave)
                + struct.pack(">B", write_cmd)
                + struct.pack(">H", register)
                + struct.pack(">H", int(value) & 0xFFFF)
            )

        return (
            struct.pack(">B", slave)
            + struct.pack(">B", 6)
            + struct.pack(">H", register)
            + struct.pack(">H", int(value) & 0xFFFF)
        )
