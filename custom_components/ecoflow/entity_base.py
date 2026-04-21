"""Shared base entity for all EcoFlow platforms."""
from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER
from .coordinator import EcoFlowCoordinator


class EcoFlowEntity(CoordinatorEntity[EcoFlowCoordinator]):
    """Base class for EcoFlow entities.

    Subclasses only need to set:
      • self._attr_unique_id
      • self._attr_name
      • override native_value / is_on etc.
    """

    def __init__(self, coordinator: EcoFlowCoordinator, device_type: str) -> None:
        super().__init__(coordinator)
        self._device_type = device_type

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.sn)},
            name=self.coordinator.device_name,
            manufacturer=MANUFACTURER,
            model=self._device_type.replace("_", " ").title(),
        )

    @property
    def available(self) -> bool:
        """Mark unavailable when coordinator has no data."""
        return super().available and self.coordinator.data is not None

    def _get(self, key: str, default=None):
        """Safely read a quota value from coordinator data."""
        if not self.coordinator.data:
            return default
        return self.coordinator.data.get(key, default)
