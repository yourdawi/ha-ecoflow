"""EcoFlow data coordinator — combines MQTT push with HTTP polling fallback."""
from __future__ import annotations

import asyncio
import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import EcoFlowApiClient, EcoFlowApiError, EcoFlowMQTTClient
from .const import DOMAIN, UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)


class EcoFlowCoordinator(DataUpdateCoordinator):
    """Manages data for a single EcoFlow device.

    Strategy:
    • MQTT pushes real-time updates (quota reports) → merged into self.data
    • HTTP polling every UPDATE_INTERVAL seconds ensures we don't miss state
      after reconnects or transient MQTT gaps.
    """

    def __init__(
        self,
        hass: HomeAssistant,
        client: EcoFlowApiClient,
        sn: str,
        device_name: str,
        initial_online: bool = False,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{sn}",
            update_interval=timedelta(seconds=UPDATE_INTERVAL),
        )
        self._client = client
        self._sn = sn
        self.device_name = device_name
        self.online: bool = initial_online
        self._mqtt: EcoFlowMQTTClient | None = None

        # Initialize data with the online status
        self.data = {"online": 1 if initial_online else 0}

    # ── DataUpdateCoordinator interface ───────────────────────────────────────

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch full quota snapshot via HTTP (polling fallback)."""
        try:
            data = await self._client.get_all_quota(self._sn)
        except EcoFlowApiError as err:
            raise UpdateFailed(f"EcoFlow API error for {self._sn}: {err}") from err
        except Exception as err:
            raise UpdateFailed(f"Unexpected error: {err}") from err

        # Merge with any existing data so MQTT-only fields survive a poll cycle
        merged = {**(self.data or {}), **data, "online": 1 if self.online else 0}
        return merged

    # ── MQTT lifecycle ────────────────────────────────────────────────────────

    async def async_start_mqtt(self) -> None:
        """Fetch MQTT credentials and connect."""
        try:
            cert = await self._client.get_mqtt_cert()
        except Exception as err:  # noqa: BLE001
            _LOGGER.warning("Could not get MQTT cert for %s: %s — using HTTP polling only", self._sn, err)
            return

        self._mqtt = EcoFlowMQTTClient(
            cert=cert,
            sn=self._sn,
            on_data=self._on_mqtt_data,
            on_status=self._on_mqtt_status,
        )
        loop = asyncio.get_event_loop()
        await self.hass.async_add_executor_job(self._mqtt.start, loop)
        _LOGGER.info("EcoFlow MQTT started for %s", self._sn)

    async def async_stop_mqtt(self) -> None:
        if self._mqtt:
            await self.hass.async_add_executor_job(self._mqtt.stop)
            self._mqtt = None

    # ── MQTT callbacks (called from executor thread via run_coroutine_threadsafe) ──

    def _on_mqtt_data(self, params: dict) -> None:
        """Merge incoming MQTT quota data and notify listeners."""
        merged = {**(self.data or {}), **params, "online": 1 if self.online else 0}
        self.async_set_updated_data(merged)

    def _on_mqtt_status(self, online: bool) -> None:
        self.online = online
        _LOGGER.debug("EcoFlow device %s online=%s", self._sn, online)
        
        # Inject online status into data so listeners are notified
        if self.data is not None:
            new_data = {**self.data, "online": 1 if online else 0}
            self.async_set_updated_data(new_data)

        # Trigger a data refresh when coming back online
        if online:
            self.hass.async_create_task(self.async_request_refresh())

    # ── Command helpers (used by switch / number entities) ────────────────────

    async def async_send_command(self, params: dict) -> None:
        """Send a set command — prefers HTTP, MQTT as optional side-channel."""
        try:
            await self._client.set_quota(self._sn, params)
        except EcoFlowApiError as err:
            _LOGGER.error("Failed to set quota on %s: %s", self._sn, err)
            raise
        # Request an immediate refresh so state reflects the change
        await self.async_request_refresh()

    @property
    def sn(self) -> str:
        return self._sn
