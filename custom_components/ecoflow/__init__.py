"""EcoFlow Home Assistant Integration."""
from __future__ import annotations

import logging

import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import EcoFlowApiClient, EcoFlowApiError
from .const import (
    API_HOSTS,
    API_REGION_EU,
    API_REGION_US,
    CONF_ACCESS_KEY,
    CONF_API_HOST,
    CONF_SECRET_KEY,
    DEVICE_UNKNOWN,
    DOMAIN,
    SN_PREFIX_MAP,
)
from .coordinator import EcoFlowCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.SWITCH, Platform.NUMBER, Platform.BINARY_SENSOR]


def _detect_device_type(sn: str) -> str:
    """Detect device type from serial number prefix."""
    for prefix, device_type in SN_PREFIX_MAP.items():
        if sn.startswith(prefix):
            return device_type
    return DEVICE_UNKNOWN


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up EcoFlow from a config entry."""
    session = async_get_clientsession(hass)
    api_host = entry.data.get(CONF_API_HOST) or API_HOSTS["eu"]

    client = EcoFlowApiClient(
        access_key=entry.data[CONF_ACCESS_KEY],
        secret_key=entry.data[CONF_SECRET_KEY],
        session=session,
        api_host=api_host,
    )

    # Fetch device list to create one coordinator per device
    try:
        devices = await client.get_device_list()
    except EcoFlowApiError as err:
        raise ConfigEntryNotReady(f"Cannot connect to EcoFlow API: {err}") from err
    except aiohttp.ClientError as err:
        raise ConfigEntryNotReady(f"Network error: {err}") from err

    if not devices:
        _LOGGER.warning("No EcoFlow devices found for this account")

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {}

    coordinators: list[EcoFlowCoordinator] = []
    for device in devices:
        sn = device.get("sn", "")
        name = device.get("deviceName") or sn
        device_type = _detect_device_type(sn)
        online = device.get("online") == 1

        _LOGGER.debug("Setting up EcoFlow device: %s (%s) type=%s online=%s", name, sn, device_type, online)

        coordinator = EcoFlowCoordinator(hass, client, sn, name, initial_online=online)

        # Initial data fetch
        await coordinator.async_config_entry_first_refresh()

        # Start MQTT for real-time updates
        await coordinator.async_start_mqtt()

        hass.data[DOMAIN][entry.entry_id][sn] = {
            "coordinator": coordinator,
            "device_type": device_type,
            "device_info": device,
        }
        coordinators.append(coordinator)

    # Forward to platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok and DOMAIN in hass.data and entry.entry_id in hass.data[DOMAIN]:
        for device_data in hass.data[DOMAIN][entry.entry_id].values():
            coordinator: EcoFlowCoordinator = device_data["coordinator"]
            await coordinator.async_stop_mqtt()
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
