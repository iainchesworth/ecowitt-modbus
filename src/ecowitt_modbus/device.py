"""The interface every modelled device presents to a caller.

A caller that only reads weather data can treat any supported device
identically: construct it, :meth:`~EcowittDevice.async_probe` it once to
confirm the right model answered, then :meth:`~EcowittDevice.async_update`
it on a schedule and read ``device.sensors``.

Which readings a given model actually exposes differs -- see each model's
``sensors`` component for the definitive list.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, ClassVar

from modbus_connection.model import Component

from .const import MANUFACTURER

if TYPE_CHECKING:
    from modbus_connection import ModbusUnit


class EcowittDeviceError(Exception):
    """Base class for errors raised by this library.

    Transport failures are not wrapped: those surface as the
    ``modbus_connection.ModbusError`` subclasses they already are.
    """


class NotThisDeviceError(EcowittDeviceError):
    """Something answered, but it is not the model that was asked for.

    Raised by :meth:`EcowittDevice.async_probe`.
    """


class EcowittDevice(ABC):
    """One Fine Offset / Ecowitt sensor reachable over Modbus."""

    #: Model name as printed on the device, e.g. ``"WN90LP"``.
    MODEL: ClassVar[str]

    #: The device (slave) address this model ships with.
    DEFAULT_UNIT_ID: ClassVar[int]

    def __init__(self, unit: ModbusUnit) -> None:
        """Model the device answering on ``unit``."""
        self._unit = unit

    @property
    @abstractmethod
    def info(self) -> Component:
        """The device's identity and link settings.

        Which fields this holds is model-specific; each model narrows the
        return type to its own component.
        """

    @property
    @abstractmethod
    def sensors(self) -> Component:
        """The device's live weather readings.

        Which readings this holds is model-specific; each model narrows the
        return type to its own component.
        """

    @abstractmethod
    async def async_probe(self) -> None:
        """Read the device and confirm it is really this model.

        Raises :exc:`NotThisDeviceError` if what answers is inconsistent
        with this model, or a ``modbus_connection.ModbusError`` if it does
        not answer at all. How much confirmation is possible depends on the
        model; see each implementation.
        """

    @abstractmethod
    async def async_update(self) -> None:
        """Refresh the live readings exposed by ``self.sensors``.

        Raises a ``modbus_connection.ModbusError`` if the device does not
        answer or rejects the read.
        """

    @property
    def manufacturer(self) -> str:
        """The name to attribute this sensor to."""
        return MANUFACTURER

    @property
    @abstractmethod
    def serial_number(self) -> str | None:
        """A stable hardware identity, or ``None`` if the model has none.

        Where a device reports one, it is the only identifier that survives
        a change of host, port, or device address. Callers that need to
        recognise a device across address changes have nothing to fall back
        on when this is ``None``.
        """

    @property
    def sw_version(self) -> str | None:
        """The device's firmware version, if it reports one."""
        return None
