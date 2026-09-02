"""The WN69LP as a single Modbus device object."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, ClassVar

from modbus_connection import ModbusError

from ..device import EcowittDevice, NotThisDeviceError
from .device_info import DEFAULT_UNIT_ID, DeviceInfo, FirmwareVersion
from .sensors import PLAUSIBLE_RANGES, Sensors

if TYPE_CHECKING:
    from modbus_connection import ModbusUnit

_LOGGER = logging.getLogger(__name__)


class WN69LP(EcowittDevice):
    """A Fine Offset / Ecowitt WN69LP weather sensor array on Modbus."""

    MODEL: ClassVar[str] = "WN69LP"
    DEFAULT_UNIT_ID: ClassVar[int] = DEFAULT_UNIT_ID

    def __init__(self, unit: ModbusUnit) -> None:
        """Model the WN69LP answering on ``unit``."""
        super().__init__(unit)
        self._info = DeviceInfo(unit)
        self._sensors = Sensors(unit)
        self.firmware = FirmwareVersion(unit)

    @property
    def info(self) -> DeviceInfo:
        """The WN69LP's RS-485 and sampling configuration."""
        return self._info

    @property
    def sensors(self) -> Sensors:
        """The WN69LP's live weather readings."""
        return self._sensors

    async def async_probe(self) -> None:
        """Check the readings at 0x180 are consistent with a WN69LP.

        The WN69LP reports no model or serial register, so unlike the WS90
        there is nothing to identify positively against. What this can do is
        reject a responder whose readings fall outside the physical ranges
        the specification documents -- a real sensor cannot report 130%
        humidity or a 700 hPa pressure. That rules out most unrelated
        devices, but it cannot distinguish a WN69LP from another device
        whose registers happen to decode plausibly at the same addresses.

        Also reads the configuration block, so a caller that probes need not
        call :meth:`async_update_info` as well.

        Raises :exc:`~..device.NotThisDeviceError` if a reading is out of
        range, or ``ModbusExceptionError`` if the device rejects a read.
        """
        await self.async_update()
        await self.async_update_info()

        for field, (low, high) in PLAUSIBLE_RANGES.items():
            # None is the documented invalid-reading sentinel, not a fault:
            # a sensor can legitimately report one field as unavailable.
            if (value := getattr(self.sensors, field)) is None:
                continue
            if not low <= value <= high:
                raise NotThisDeviceError(
                    f"the device reports {field}={value}, outside the "
                    f"{low}-{high} a WN69LP can measure"
                )

    async def async_update(self) -> None:
        """Refresh the live weather readings.

        Raises ``ModbusExceptionError`` if the device rejects the block.
        """
        await self.sensors.async_update()

    async def async_update_info(self) -> None:
        """Refresh the configuration block, and the firmware version if present.

        Read separately from :meth:`async_update`: the two blocks are 24
        registers apart with a documented reserved gap between them, and
        this one only changes when the device is reconfigured.

        A device on firmware older than V1.0.2 has no firmware-version
        register and rejects that read; this logs and continues rather than
        failing, leaving :attr:`sw_version` as ``None``.

        Raises ``ModbusExceptionError`` if the device rejects the
        configuration block itself.
        """
        await self.info.async_update()
        try:
            await self.firmware.async_update()
        except ModbusError:
            _LOGGER.debug(
                "No firmware-version register (0x167); the device predates "
                "specification V1.0.2",
                exc_info=True,
            )

    @property
    def serial_number(self) -> str | None:
        """Always ``None`` -- the WN69LP reports no stable hardware identity."""
        return None

    @property
    def sw_version(self) -> str | None:
        """The firmware version, if the device is new enough to report one."""
        return self.firmware.version
