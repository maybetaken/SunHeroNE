import json

class SystemJsonCodec:
    @staticmethod
    def decode(payload: bytes) -> dict:
        try:
            if len(payload) > 0 and payload[0] == 0x7B:
                return json.loads(payload.decode("utf-8"))
        except Exception:
            pass
        return {}

    @staticmethod
    def encode_command(cmd_payload: dict) -> str:
        return json.dumps(cmd_payload)
