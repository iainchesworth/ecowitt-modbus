"""Identity and RS-485 communication settings of the WN90LP."""

from __future__ import annotations

from modbus_connection.model import Component, enum, integer, uint32

from ..const import BaudRate, validate_device_address

#: Register 0x160 reports this fixed code on a genuine WN90LP. Kept as a dict
#: (rather than a bare constant) so an OEM variant sharing the register map
#: only needs a new entry here.
MODEL_NAMES: dict[int, str] = {0x90: "WN90LP"}

#: The value register 0x160 holds on a WN90LP.
DEVICE_CODE = 0x90


class DeviceInfo(Component):
    """The WN90LP's identity and RS-485 communication settings.

    Registers 0x160-0x164, immediately below the live readings, so both are
    pooled into a single read (see :class:`~.wn90lp.WN90LP`).
    """

    device_code = integer(0x160, signed=False)
    baud_rate = enum(0x161, BaudRate, writable=True)
    device_address = integer(0x162, signed=False, writable=validate_device_address)
    device_id = uint32(0x163)

    @property
    def model(self) -> str | None:
        """The human-readable model name, or ``None`` before the first update."""
        if self.device_code is None:
            return None
        return MODEL_NAMES.get(self.device_code, f"unknown (0x{self.device_code:02x})")
