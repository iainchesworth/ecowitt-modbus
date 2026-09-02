"""Values shared by every modelled device."""

from __future__ import annotations

from enum import IntEnum

#: Both modelled sensors are Fine Offset designs sold under the Ecowitt brand.
MANUFACTURER = "Ecowitt"


class BaudRate(IntEnum):
    """Serial baud rates, as encoded in the RS-485 baud-rate register.

    The same 1-4 encoding is used by every device modelled here.
    """

    BAUD_4800 = 1
    BAUD_9600 = 2
    BAUD_19200 = 3
    BAUD_115200 = 4


def validate_device_address(value: int) -> int:
    """Reject a device (slave) address outside the accepted range.

    Both modelled devices accept 1-252. Raises ``ValueError`` otherwise.
    """
    if not 1 <= value <= 252:
        raise ValueError(f"device address must be between 1 and 252, got {value}")
    return value
