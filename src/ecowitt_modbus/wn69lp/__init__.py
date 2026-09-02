"""The Fine Offset / Ecowitt WN69LP wired 7-in-1 weather sensor array.

Modelled from Ecowitt's ``WN69LP Modbus RTU V1.0.2`` specification.
"""

from .device_info import DeviceInfo, FirmwareVersion
from .sensors import Sensors
from .wn69lp import WN69LP

__all__ = [
    "WN69LP",
    "DeviceInfo",
    "FirmwareVersion",
    "Sensors",
]
