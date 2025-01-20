"""Support for Snoo Sensors."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Coroutine

from python_snoo.containers import SnooData, SnooStates, SnooDevice
from python_snoo.snoo import Snoo

from homeassistant.components.switch import (
    SwitchDeviceClass,
    SwitchEntity,
    SwitchEntityDescription,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import SnooConfigEntry
from .entity import SnooDescriptionEntity


@dataclass(frozen=True, kw_only=True)
class SnooSwitchEntityDescription(SwitchEntityDescription):
    """Describes a Snoo sensor."""

    value_fn: Callable[[SnooData], bool]
    set_value_fn: Callable[[Snoo, SnooDevice, bool], None]


BINARY_SENSOR_DESCRIPTIONS: list[SnooSwitchEntityDescription] = [
    SnooSwitchEntityDescription(
        key="sticky_white_noise",
        translation_key="sticky_white_noise",
        value_fn=lambda data: data.state_machine.sticky_white_noise == "on",
        set_value_fn=lambda snoo_api, device, state: snoo_api.set_sticky_white_noise(
            device, state
        ),
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: SnooConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Snoo device."""
    coordinators = entry.runtime_data
    async_add_entities(
        SnooSwitch(coordinator, description)
        for coordinator in coordinators.values()
        for description in BINARY_SENSOR_DESCRIPTIONS
    )


class SnooSwitch(SnooDescriptionEntity, SwitchEntity):
    """A sensor using Snoo coordinator."""

    entity_description: SnooSwitchEntityDescription

    @property
    def is_on(self) -> bool | None:
        """Return True if entity is on."""
        return self.entity_description.value_fn(self.coordinator.data)

    async def async_turn_on(self) -> None:
        """Turn the entity on."""
        await self.entity_description.set_value_fn(
            self.coordinator.snoo, self.coordinator.device, True
        )

    async def async_turn_off(self) -> None:
        """Turn the entity off."""
        await self.entity_description.set_value_fn(
            self.coordinator.snoo, self.coordinator.device, False
        )
