"""EcoFlow switch platform."""
from __future__ import annotations

import logging
from typing import Any, Callable

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DEVICE_SWITCHES, DOMAIN
from .coordinator import EcoFlowCoordinator
from .entity_base import EcoFlowEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    entities: list[EcoFlowSwitchEntity] = []

    for sn, device_data in hass.data[DOMAIN][entry.entry_id].items():
        coordinator: EcoFlowCoordinator = device_data["coordinator"]
        device_type: str = device_data["device_type"]
        switch_defs = DEVICE_SWITCHES.get(device_type, [])

        for quota_key, name, icon, set_fn in switch_defs:
            entities.append(
                EcoFlowSwitchEntity(
                    coordinator=coordinator,
                    device_type=device_type,
                    quota_key=quota_key,
                    name=name,
                    icon=icon,
                    set_fn=set_fn,
                )
            )

    async_add_entities(entities)


class EcoFlowSwitchEntity(EcoFlowEntity, SwitchEntity):
    """A switch that toggles a single quota value."""

    def __init__(
        self,
        coordinator: EcoFlowCoordinator,
        device_type: str,
        quota_key: str,
        name: str,
        icon: str | None,
        set_fn: Callable[[bool, str], dict],
    ) -> None:
        super().__init__(coordinator, device_type)
        self._quota_key = quota_key
        self._set_fn = set_fn

        slug = quota_key.replace(".", "_").replace("-", "_").lower()
        self._attr_unique_id = f"{coordinator.sn}_{slug}_switch"
        self._attr_name = f"{coordinator.device_name} {name}"
        self._attr_icon = icon

    @property
    def is_on(self) -> bool | None:
        raw = self._get(self._quota_key)
        if raw is None:
            return None
        # Handle bool / int / string truthy values
        if isinstance(raw, bool):
            return raw
        try:
            return int(raw) != 0
        except (TypeError, ValueError):
            return str(raw).lower() in ("true", "1", "on")

    async def async_turn_on(self, **kwargs: Any) -> None:
        params = self._set_fn(True, self.coordinator.sn)
        await self.coordinator.async_send_command(params)

    async def async_turn_off(self, **kwargs: Any) -> None:
        params = self._set_fn(False, self.coordinator.sn)
        await self.coordinator.async_send_command(params)
