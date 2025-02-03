"""Support for Snoo Sensors."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from python_snoo.containers import SnooData, SnooLevels

from homeassistant.components.select import (
    SelectEntityDescription,
    SelectEntity,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import SnooConfigEntry
from .entity import SnooDescriptionEntity
from python_snoo.snoo import Snoo
from python_snoo.containers import SnooDevice


@dataclass(frozen=True, kw_only=True)
class SnooSwitchEntityDescription(SelectEntityDescription):
    """Describes a Snoo sensor."""

    value_fn: Callable[[SnooData], str]
    set_value_fn: Callable[[Snoo, SnooDevice, str], None]


SWITCH_DESCRIPTIONS: list[SnooSwitchEntityDescription] = [
    SnooSwitchEntityDescription(
        key="intensity",
        translation_key="intensity",
        value_fn=lambda data: data.state_machine.level.value,
        set_value_fn=lambda snoo_api, device, state: snoo_api.set_level(
            device, SnooLevels(state)
        ),
        options=[
            SnooLevels.baseline.value,
            SnooLevels.level1.value,
            SnooLevels.level2.value,
            SnooLevels.level3.value,
            SnooLevels.level4.value,
            SnooLevels.stop.value,
        ],
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
        SnooSelect(coordinator, description)
        for coordinator in coordinators.values()
        for description in SWITCH_DESCRIPTIONS
    )


class SnooSelect(SnooDescriptionEntity, SelectEntity):
    """A sensor using Snoo coordinator."""

    entity_description: SnooSwitchEntityDescription

    @property
    def current_option(self) -> str | None:
        """Return the selected entity option to represent the entity state."""
        return self.entity_description.value_fn(self.coordinator.data)

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        await self.entity_description.set_value_fn(
            self.coordinator.snoo, self.device, option
        )
