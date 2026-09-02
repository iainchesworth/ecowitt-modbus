"""ecowitt-modbus -- read Fine Offset / Ecowitt weather sensors over Modbus.

Construct the model you have with a ``modbus_connection.ModbusUnit``, probe
it once to confirm the right device answered, then poll it::

    device = WS90(unit)
    await device.async_probe()
    await device.async_update()

    device.sensors.temperature
    device.sensors.wind_speed

Callers that let a user pick the model can look the class up by name rather
than branching::

    device = SUPPORTED_MODELS["WN69LP"](unit)

Every model exposes the same :class:`EcowittDevice` interface, but not the
same readings -- see each model's ``sensors`` component for what it measures.
"""

from .const import MANUFACTURER, BaudRate
from .device import EcowittDevice, EcowittDeviceError, NotThisDeviceError
from .wn69lp import WN69LP
from .ws90 import WS90

#: Every model this library can talk to, keyed by the name printed on the
#: device. Callers that offer a model picker should drive it from this.
SUPPORTED_MODELS: dict[str, type[EcowittDevice]] = {
    WS90.MODEL: WS90,
    WN69LP.MODEL: WN69LP,
}

__all__ = [
    "MANUFACTURER",
    "SUPPORTED_MODELS",
    "WN69LP",
    "WS90",
    "BaudRate",
    "EcowittDevice",
    "EcowittDeviceError",
    "NotThisDeviceError",
]
