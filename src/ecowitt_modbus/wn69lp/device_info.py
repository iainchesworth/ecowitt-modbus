"""Configuration and firmware registers of the WN69LP.

Unlike the WS90, the WN69LP has no model or serial-number register: nothing
here identifies the device as a WN69LP, and nothing survives a change of
device address. Everything in this block is settable.
"""

from __future__ import annotations

from modbus_connection.model import Component, enum, gauge, integer

from ..const import BaudRate, validate_device_address

#: The device (slave) address a WN69LP ships with.
DEFAULT_UNIT_ID = 0x24

#: Both interval registers count in units of 250ms.
_SECONDS_PER_STEP = 0.25


class DeviceInfo(Component):
    """The WN69LP's RS-485 and sampling configuration (registers 0x160-0x163).

    Deliberately stops short of 0x164: that register and 0x165 are
    write-only (clear rainfall, software reset), 0x166 exists only on
    firmware V1.0.3 and later, and reading any of them risks an
    illegal-data-address rejection that would fail the whole block.
    :class:`FirmwareVersion` covers 0x167 as a separate, optional read.
    """

    device_address = integer(0x160, signed=False, writable=validate_device_address)
    baud_rate = enum(0x161, BaudRate, writable=True)
    # 0 disables automatic reporting, which is the default and the only mode
    # this library supports -- it polls rather than listening for reports.
    auto_report_interval = gauge(
        0x162, _SECONDS_PER_STEP, signed=False, writable=True, unit="s"
    )
    sampling_period = gauge(
        0x163, _SECONDS_PER_STEP, signed=False, writable=True, unit="s"
    )


class FirmwareVersion(Component):
    """The WN69LP's firmware version register (0x167).

    Added by revision V1.0.2 of the specification, so a device on older
    firmware may reject the read. Kept out of :class:`DeviceInfo` for that
    reason: a failure here must not cost the caller the rest of the block.
    """

    raw = integer(0x167, signed=False)

    @property
    def version(self) -> str | None:
        """The firmware version as ``major.minor.patch``.

        The register packs the three parts as a single decimal number: the
        specification's worked example gives ``Ver1.0.0 = 0x64`` (100), and
        the low-power register is documented as needing "V1.0.3 or later"
        (103).
        """
        if (raw := self.raw) is None:
            return None
        return f"{raw // 100}.{raw // 10 % 10}.{raw % 10}"
