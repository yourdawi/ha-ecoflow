"""EcoFlow binary sensor platform."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DEVICE_BINARY_SENSORS, DOMAIN
from .coordinator import EcoFlowCoordinator
from .entity_base import EcoFlowEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up EcoFlow binary sensors from a config entry."""
    entities: list[EcoFlowBinarySensorEntity] = []

    for sn, device_data in hass.data[DOMAIN][entry.entry_id].items():
        coordinator: EcoFlowCoordinator = device_data["coordinator"]
        device_type: str = device_data["device_type"]
        binary_defs = DEVICE_BINARY_SENSORS.get(device_type, [])

        for quota_key, name, dev_class, icon in binary_defs:
            entities.append(
                EcoFlowBinarySensorEntity(
                    coordinator=coordinator,
                    device_type=device_type,
                    quota_key=quota_key,
                    name=name,
                    dev_class=dev_class,
                    icon=icon,
                )
            )

    async_add_entities(entities)


class EcoFlowBinarySensorEntity(EcoFlowEntity, BinarySensorEntity):
    """A binary sensor that reads a single quota value from coordinator data."""

    def __init__(
        self,
        coordinator: EcoFlowCoordinator,
        device_type: str,
        quota_key: str,
        name: str,
        dev_class: BinarySensorDeviceClass | str | None,
        icon: str | None,
    ) -> None:
        super().__init__(coordinator, device_type)
        self._quota_key = quota_key

        slug = quota_key.replace(".", "_").replace("-", "_").lower()
        self._attr_unique_id = f"{coordinator.sn}_{slug}"
        self._attr_name = f"{coordinator.device_name} {name}"
        self._attr_device_class = dev_class
        self._attr_icon = icon

    @property
    def is_on(self) -> bool | None:
        raw = self._get(self._quota_key)
        if raw is None:
            return None
        return bool(raw)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {"quota_key": self._quota_key, "device_sn": self.coordinator.sn}
