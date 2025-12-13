"""SunHeroNE config flow for integration.

SunHeroNE or sunherone © 2025 by @maybetaken is
licensed under Creative Commons
Attribution-NonCommercial-NoDerivatives 4.0 International.
"""

import logging
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.components.network import async_get_source_ip
import voluptuous as vol
from .const import (
    DOMAIN, 
    CONF_DEVICE_ID, 
    CONF_MODEL, 
    CONF_MQTT_HOST, 
    CONF_MQTT_PORT, 
    CONF_MQTT_USER, 
    CONF_MQTT_PASS
)

_LOGGER = logging.getLogger(__name__)

class SunHeroFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle manual configuration (Hub Setup)."""

        if not self.hass.config_entries.async_entries("mqtt"):
            return self.async_abort(reason="mqtt_required")

        current_entries = self._async_current_entries()
        for entry in current_entries:
            if CONF_MQTT_HOST in entry.data:
                return self.async_abort(reason="hub_already_configured")

        if user_input is not None:
            return self.async_create_entry(title="SunHeroNE System Hub", data=user_input)

        default_host = "127.0.0.1"
        try:
            default_host = await async_get_source_ip(self.hass, target_ip="8.8.8.8")
        except Exception:
            pass

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_MQTT_HOST, default=default_host): str,
                vol.Required(CONF_MQTT_PORT, default=1883): int,
                vol.Optional(CONF_MQTT_USER): str,
                vol.Optional(CONF_MQTT_PASS): str,
            })
        )

    async def async_step_zeroconf(self, discovery_info):
        """Handle zeroconf discovery."""
        props = discovery_info.properties
        sn = props.get("sn", "unknown")
        dtype = props.get("device_type", "default")

        await self.async_set_unique_id(sn)
        self._abort_if_unique_id_configured()

        self.d_data = {CONF_DEVICE_ID: sn, CONF_MODEL: dtype}
        self.context["title_placeholders"] = {"name": f"{dtype} ({sn})"}
        return await self.async_step_discovery_confirm()

    async def async_step_discovery_confirm(self, user_input=None):
        """Confirm discovery."""
        if user_input is not None:
            return self.async_create_entry(
                title=f"{self.d_data[CONF_MODEL]} {self.d_data[CONF_DEVICE_ID]}",
                data=self.d_data
            )
        return self.async_show_form(step_id="discovery_confirm",    
            description_placeholders={
            "name": self.context["title_placeholders"]["name"]
            }
        )
    

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return SunHeroOptionsFlowHandler()

class SunHeroOptionsFlowHandler(config_entries.OptionsFlow):
    async def async_step_init(self, user_input=None):
        # Only show options for the Hub entry
        if CONF_MQTT_HOST in self.config_entry.data:
            if user_input is not None:
                self.hass.config_entries.async_update_entry(self.config_entry, data=user_input)
                await self.hass.config_entries.async_reload(self.config_entry.entry_id)
                return self.async_create_entry(title="", data={})

            return self.async_show_form(
                step_id="init",
                data_schema=vol.Schema({
                    vol.Required(CONF_MQTT_HOST, default=self.config_entry.data.get(CONF_MQTT_HOST)): str,
                    vol.Required(CONF_MQTT_PORT, default=self.config_entry.data.get(CONF_MQTT_PORT)): int,
                    vol.Optional(CONF_MQTT_USER, default=self.config_entry.data.get(CONF_MQTT_USER)): str,
                    vol.Optional(CONF_MQTT_PASS, default=self.config_entry.data.get(CONF_MQTT_PASS)): str,
                })
            )
        return self.async_create_entry(title="", data={})
