"""SunHeroNE const for integration.

SunHeroNE or sunherone © 2025 by @maybetaken is
licensed under Creative Commons
Attribution-NonCommercial-NoDerivatives 4.0 International.
"""

DOMAIN = "SunHeroNE"

# Device Configuration Keys
CONF_DEVICE_ID = "device_id"
CONF_MODEL = "model"

# Hub/MQTT Configuration Keys
CONF_MQTT_HOST = "mqtt_host"
CONF_MQTT_PORT = "mqtt_port"
CONF_MQTT_USER = "mqtt_user"
CONF_MQTT_PASS = "mqtt_pass"

TOPIC_GLOBAL_HEARTBEAT = "SunHeroNE/system/heartbeat"

# Timers (Seconds)
INTERVAL_SSDP_BROADCAST = 5
INTERVAL_MQTT_HEARTBEAT = 5
