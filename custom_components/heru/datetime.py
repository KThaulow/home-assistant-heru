"""Date/time platform for HERU."""
import logging

from homeassistant.components.number import NumberEntity, NumberDeviceClass
from homeassistant.components.datetime import DateTimeEntity
from datetime import datetime
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import CoordinatorEntity


from .const import (
    DOMAIN,
    HERU_NUMBERS,
)
from .entity import HeruEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry, async_add_devices):
    """Setup date/time platform."""
    _LOGGER.debug("Heru.date_time.py")
    coordinator = hass.data[DOMAIN]["coordinator"]

    date_times = []
    for date_time in HERU_DATE_TIMES:
        date_times.append(HeruDateTime(coordinator, date_time, entry))
    async_add_devices(date_times)


class HeruDateTime(HeruEntity, DateTimeEntity):
    """HERU date/time class."""

    _attr_device_class = NumberDeviceClass.TEMPERATURE # TODO

    def __init__(self, coordinator: CoordinatorEntity, idx, config_entry):
        _LOGGER.debug("HeruDateTime.__init__()")
        super().__init__(coordinator, idx, config_entry)
        self.coordinator = coordinator
        self.address = self.idx["address"]
        self.scale = self.idx["scale"]
        self._attr_native_value = datetime
        self._attr_native_value = (
            self.coordinator.holding_registers[self.address] * self.scale
        )

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        _LOGGER.debug("HeruNumber._handle_coordinator_update()")
        self._attr_native_value = (
            self.coordinator.holding_registers[self.address] * self.scale
        )
        _LOGGER.debug(
            "%s: %s %s",
            self._attr_name,
            self._attr_native_value
        )
        self.async_write_ha_state()

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        _LOGGER.debug("HeruButton.async_set_native_value()")
        native_value = int(value / self.scale)
        await self.coordinator.write_register(self.address, native_value)
