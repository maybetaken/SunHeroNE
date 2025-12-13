"""SunHeroNE ssdp broadcaster for integration.

SunHeroNE or sunherone © 2025 by @maybetaken is
licensed under Creative Commons
Attribution-NonCommercial-NoDerivatives 4.0 International.
"""

import asyncio
import logging
import socket
from datetime import timedelta
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_time_interval
from .const import INTERVAL_SSDP_BROADCAST

_LOGGER = logging.getLogger(__name__)

SSDP_ADDR = "239.255.255.250"
SSDP_PORT = 1900
SSDP_ST = "urn:sunherone:service:config:1"

class SunHeroBroadcaster:
    """
    Broadcasts MQTT credentials using SSDP via a random source port.
    Target: 239.255.255.250:1900
    """

    def __init__(self, hass: HomeAssistant, config: dict):
        self.hass = hass
        self.config = config
        self._remove_timer = None
        self._transport = None
        self._packet = None

    async def async_start(self):
        """Setup transport and start timer."""
        host = self.config.get("mqtt_host")
        port = self.config.get("mqtt_port", 1883)
        user = self.config.get("mqtt_user", "")
        password = self.config.get("mqtt_pass", "")

        if not host:
            _LOGGER.warning("No MQTT Host configured, skipping SSDP broadcast.")
            return

        # Prepare Payload
        self._packet = (
            "NOTIFY * HTTP/1.1\r\n"
            f"HOST: {SSDP_ADDR}:{SSDP_PORT}\r\n"
            "CACHE-CONTROL: max-age=1800\r\n"
            f"NT: {SSDP_ST}\r\n"
            "NTS: ssdp:alive\r\n"
            "SERVER: HomeAssistant/SunHeroNE\r\n"
            f"X-SunHero-Host: {host}\r\n"
            f"X-SunHero-Port: {port}\r\n"
            f"X-SunHero-User: {user}\r\n"
            f"X-SunHero-Pass: {password}\r\n"
            "\r\n"
        ).encode("utf-8")

        try:
            # Create UDP socket (Random Source Port)
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.setblocking(False)

            # Create Asyncio Transport
            loop = asyncio.get_running_loop()
            self._transport, _ = await loop.create_datagram_endpoint(
                lambda: asyncio.DatagramProtocol(),
                sock=sock
            )
            
            # Start Timer
            self._remove_timer = async_track_time_interval(
                self.hass, 
                self.broadcast_once, 
                timedelta(seconds=INTERVAL_SSDP_BROADCAST)
            )
            
            _LOGGER.info(f"Started SSDP broadcast (Target: {host}:{port})")

        except Exception as e:
            _LOGGER.error(f"Failed to start SSDP broadcaster: {e}")

    async def async_stop(self):
        """Stop timer and close transport."""
        if self._remove_timer:
            self._remove_timer()
            self._remove_timer = None

        if self._transport:
            self._transport.close()
            self._transport = None
            
        _LOGGER.info("Stopped SSDP broadcast.")

    async def broadcast_once(self, now=None):
        """Send a single SSDP packet."""
        if self._transport and self._packet:
            try:
                self._transport.sendto(self._packet, (SSDP_ADDR, SSDP_PORT))
            except Exception as e:
                # Debug level to avoid log spam on transient network issues
                _LOGGER.debug(f"SSDP send failed: {e}")
