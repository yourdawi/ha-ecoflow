"""EcoFlow number platform — charge/discharge limits, custom power, etc."""
from __future__ import annotations

import logging
from typing import Callable

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DEVICE_NUMBERS, DOMAIN
from .coordinator import EcoFlowCoordinator
from .entity_base import EcoFlowEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    entities: list[EcoFlowNumberEntity] = []

    for sn, device_data in hass.data[DOMAIN][entry.entry_id].items():
        coordinator: EcoFlowCoordinator = device_data["coordinator"]
        device_type: str = device_data["device_type"]
        number_defs = DEVICE_NUMBERS.get(device_type, [])

        for quota_key, name, unit, min_val, max_val, step, icon, set_fn in number_defs:
            entities.append(
                EcoFlowNumberEntity(
                    coordinator=coordinator,
                    device_type=device_type,
                    quota_key=quota_key,
                    name=name,
                    unit=unit,
                    min_val=min_val,
                    max_val=max_val,
                    step=step,
                    icon=icon,
                    set_fn=set_fn,
                )
            )

    async_add_entities(entities)


class EcoFlowNumberEntity(EcoFlowEntity, NumberEntity):
    """A number entity that controls a single settable quota value."""

    def __init__(
        self,
        coordinator: EcoFlowCoordinator,
        device_type: str,
        quota_key: str,
        name: str,
        unit: str | None,
        min_val: float,
        max_val: float,
        step: float,
        icon: str | None,
        set_fn: Callable[[int, str], dict],
    ) -> None:
        super().__init__(coordinator, device_type)
        self._quota_key = quota_key
        self._set_fn = set_fn

        slug = quota_key.replace(".", "_").replace("-", "_").lower()
        self._attr_unique_id = f"{coordinator.sn}_{slug}_number"
        self._attr_name = f"{coordinator.device_name} {name}"
        self._attr_native_unit_of_measurement = unit
        self._attr_native_min_value = min_val
        self._attr_native_max_value = max_val
        self._attr_native_step = step
        self._attr_mode = NumberMode.SLIDER
        self._attr_icon = icon

    @property
    def native_value(self) -> float | None:
        raw = self._get(self._quota_key)
        if raw is None:
            return None
        try:
            return float(raw)
        except (TypeError, ValueError):
            return None

    async def async_set_native_value(self, value: float) -> None:
        params = self._set_fn(int(value), self.coordinator.sn)
        await self.coordinator.async_send_command(params)
