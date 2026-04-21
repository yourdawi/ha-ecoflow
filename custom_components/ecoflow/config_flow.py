"""Config flow for EcoFlow integration."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import EcoFlowApiClient
from .const import (
    API_HOSTS,
    API_REGION_CUSTOM,
    API_REGION_EU,
    API_REGION_US,
    CONF_ACCESS_KEY,
    CONF_API_HOST,
    CONF_REGION,
    CONF_SECRET_KEY,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_ACCESS_KEY, description={"suggested_value": ""}): str,
        vol.Required(CONF_SECRET_KEY, description={"suggested_value": ""}): str,
        vol.Required(CONF_REGION, default=API_REGION_EU): vol.In(
            {
                API_REGION_EU: "Europe (api-e)",
                API_REGION_US: "Americas (api-a)",
                API_REGION_CUSTOM: "Custom / Other",
            }
        ),
    }
)

CUSTOM_HOST_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_API_HOST, description={"suggested_value": "https://"}): str,
    }
)


async def _validate_credentials(hass: HomeAssistant, data: dict, api_host: str) -> dict[str, str]:
    """Validate credentials and return errors dict (empty = success)."""
    session = async_get_clientsession(hass)
    client = EcoFlowApiClient(
        access_key=data[CONF_ACCESS_KEY],
        secret_key=data[CONF_SECRET_KEY],
        session=session,
        api_host=api_host,
    )
    errors: dict[str, str] = {}
    try:
        ok = await client.test_credentials()
        if not ok:
            errors["base"] = "invalid_auth"
    except aiohttp.ClientConnectorError:
        errors["base"] = "cannot_connect"
    except Exception:  # noqa: BLE001
        _LOGGER.exception("Unexpected error validating EcoFlow credentials")
        errors["base"] = "unknown"
    return errors


class EcoFlowConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for EcoFlow."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            # Avoid duplicate entries for same access key
            await self.async_set_unique_id(user_input[CONF_ACCESS_KEY])
            self._abort_if_unique_id_configured()

            self._temp_data = user_input

            if user_input[CONF_REGION] == API_REGION_CUSTOM:
                return await self.async_step_custom_host()

            api_host = API_HOSTS[user_input[CONF_REGION]]
            errors = await _validate_credentials(self.hass, user_input, api_host)
            if not errors:
                user_input[CONF_API_HOST] = api_host
                return self.async_create_entry(
                    title=f"EcoFlow ({user_input[CONF_ACCESS_KEY][:8]}…)",
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
            description_placeholders={
                "portal_eu": "https://developer-eu.ecoflow.com",
                "portal_us": "https://developer.ecoflow.com/us/",
            },
        )

    async def async_step_custom_host(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle custom API host input."""
        errors: dict[str, str] = {}

        if user_input is not None:
            api_host = user_input[CONF_API_HOST]
            errors = await _validate_credentials(self.hass, self._temp_data, api_host)
            if not errors:
                full_data = {**self._temp_data, **user_input}
                return self.async_create_entry(
                    title=f"EcoFlow ({self._temp_data[CONF_ACCESS_KEY][:8]}…)",
                    data=full_data,
                )

        return self.async_show_form(
            step_id="custom_host",
            data_schema=CUSTOM_HOST_SCHEMA,
            errors=errors,
        )

    async def async_step_reauth(self, entry_data: dict[str, Any]) -> FlowResult:
        """Handle re-authentication."""
        return await self.async_step_user()
