"""The WS90 as a single Modbus device object."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from modbus_connection.model import ComponentGroup

from ..device import EcowittDevice, NotThisDeviceError
from .device_info import DEVICE_CODE, DeviceInfo
from .history import History
from .sensors import Sensors

if TYPE_CHECKING:
    from modbus_connection import ModbusUnit


class WS90(EcowittDevice):
    """A Fine Offset / Ecowitt WS90 weather sensor array on Modbus."""

    MODEL: ClassVar[str] = "WS90"
    DEFAULT_UNIT_ID: ClassVar[int] = 0x90

    def __init__(self, unit: ModbusUnit) -> None:
        """Model the WS90 answering on ``unit``."""
        super().__init__(unit)
        self.info = DeviceInfo(unit)
        self.sensors = Sensors(unit)
        self.history = History(unit)
        # Identity (5 registers) and live readings (10 registers) sit right
        # next to each other on the device -- pool them into one read.
        self._live = ComponentGroup(unit, [self.info, self.sensors])

    async def async_probe(self) -> None:
        """Confirm a WS90 answers, by reading its fixed device code.

        Register 0x160 reads back a constant 0x90 on a WS90, so unlike some
        models this is a positive identification rather than a plausibility
        check.

        Raises :exc:`~..device.NotThisDeviceError` if it reads back anything
        else, or ``ModbusExceptionError`` if the device rejects the read.
        """
        await self.async_update()
        if self.info.device_code != DEVICE_CODE:
            raise NotThisDeviceError(
                f"expected a WS90 (device code 0x{DEVICE_CODE:02x}) but the "
                f"device reports {self.info.model}"
            )

    async def async_update(self) -> None:
        """Refresh identity and live sensor readings in one pooled read.

        Raises ``ModbusExceptionError`` if the device rejects a block.
        """
        await self._live.async_update()

    async def async_update_history(self) -> None:
        """Refresh the last 30 minutes of archived readings.

        Polled separately from :meth:`async_update`: the history block is
        330 registers wide and changes only once a minute, so there is no
        reason to re-read it on every live poll.

        Raises ``ModbusExceptionError`` if the device rejects a block.
        """
        await self.history.async_update()

    @property
    def serial_number(self) -> str | None:
        """The WS90's device ID, stable across host/port/address changes."""
        if (device_id := self.info.device_id) is None:
            return None
        return f"{device_id:08x}"
