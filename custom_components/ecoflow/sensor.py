"""EcoFlow sensor platform."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DEVICE_SENSORS, DOMAIN
from .coordinator import EcoFlowCoordinator
from .entity_base import EcoFlowEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up EcoFlow sensors from a config entry."""
    entities: list[EcoFlowSensorEntity] = []

    for sn, device_data in hass.data[DOMAIN][entry.entry_id].items():
        coordinator: EcoFlowCoordinator = device_data["coordinator"]
        device_type: str = device_data["device_type"]
        sensor_defs = DEVICE_SENSORS.get(device_type, [])

        for quota_key, name, unit, dev_class, state_class, icon, factor in sensor_defs:
            entities.append(
                EcoFlowSensorEntity(
                    coordinator=coordinator,
                    device_type=device_type,
                    quota_key=quota_key,
                    name=name,
                    unit=unit,
                    dev_class=dev_class,
                    state_class=state_class,
                    icon=icon,
                    factor=factor,
                )
            )

    async_add_entities(entities)


class EcoFlowSensorEntity(EcoFlowEntity, SensorEntity):
    """A sensor that reads a single quota value from coordinator data."""

    def __init__(
        self,
        coordinator: EcoFlowCoordinator,
        device_type: str,
        quota_key: str,
        name: str,
        unit: str | None,
        dev_class: SensorDeviceClass | None,
        state_class: SensorStateClass | None,
        icon: str | None,
        factor: float,
    ) -> None:
        super().__init__(coordinator, device_type)
        self._quota_key = quota_key
        self._factor = factor

        slug = quota_key.replace(".", "_").replace("-", "_").lower()
        self._attr_unique_id = f"{coordinator.sn}_{slug}"
        self._attr_name = f"{coordinator.device_name} {name}"
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = dev_class
        self._attr_state_class = state_class
        self._attr_icon = icon

    @property
    def native_value(self) -> float | str | None:
        raw = self._get(self._quota_key)
        if raw is None:
            return None
        try:
            return round(float(raw) * self._factor, 3)
        except (TypeError, ValueError):
            return str(raw)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {"quota_key": self._quota_key, "device_sn": self.coordinator.sn}
