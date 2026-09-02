"""Live weather readings from the WN69LP sensor array.

Registers 0x180-0x18B. How often the device refreshes them is set by its own
sampling-period register (0x163, default 16s) rather than being fixed in
firmware -- polling faster than that returns the same values again. Battery
and supply voltage are re-measured every 60s regardless.
"""

from __future__ import annotations

from modbus_connection.model import Component, gauge, integer

#: Documented by the spec as the invalid-reading sentinel for every field
#: below except the two rainfall totals.
_INVALID = 0xFFFF

#: Rainfall is counted in 0.01in tips and reported in millimetres, so it
#: advances in steps of 0.254mm rather than a round metric figure.
_MM_PER_TIP = 0.254


class Sensors(Component):
    """The WN69LP's live weather readings."""

    light = gauge(0x180, 10, signed=False, nan=_INVALID, unit="lx")
    # Reported as a whole number, unlike the WS90's tenths.
    uv_index = integer(0x181, signed=False, nan=_INVALID)
    temperature = gauge(0x182, 0.1, offset=-40, signed=False, nan=_INVALID, unit="°C")
    humidity = integer(0x183, signed=False, nan=_INVALID, unit="%")
    wind_speed = gauge(0x184, 0.1, signed=False, nan=_INVALID, unit="m/s")
    gust_speed = gauge(0x185, 0.1, signed=False, nan=_INVALID, unit="m/s")
    wind_direction = integer(0x186, signed=False, nan=_INVALID, unit="°")
    # Cumulative since the last "clear rainfall" command (register 0x164).
    rainfall = gauge(0x187, _MM_PER_TIP, signed=False, unit="mm")
    absolute_pressure = gauge(0x188, 0.1, signed=False, nan=_INVALID, unit="hPa")
    # The WS90 archives these two in its history block instead; here they are
    # live registers, re-measured every 60s.
    battery_voltage = gauge(0x189, 0.01, signed=False, nan=_INVALID, unit="V")
    supply_voltage = gauge(0x18A, 0.1, signed=False, nan=_INVALID, unit="V")
    # Cleared by the same command as `rainfall`. The spec names it "latest"
    # (V1.0.2) and "recent" (V1.0.0) rainfall without defining the window it
    # covers, so it is exposed as reported and left uninterpreted.
    recent_rainfall = gauge(0x18B, _MM_PER_TIP, signed=False, unit="mm")


#: Hard bounds each reading must fall within on a genuine WN69LP, from the
#: spec's own documented ranges. The device reports no model or serial
#: register, so checking these is the only confirmation available that the
#: responder is really a WN69LP rather than an unrelated device that happens
#: to answer at the same address; see :meth:`~.wn69lp.WN69LP.async_probe`.
PLAUSIBLE_RANGES: dict[str, tuple[float, float]] = {
    "uv_index": (0, 15),
    "temperature": (-40.0, 60.0),
    "humidity": (0, 100),
    "wind_speed": (0.0, 50.0),
    "gust_speed": (0.0, 50.0),
    "wind_direction": (0, 359),
    "absolute_pressure": (300.0, 1100.0),
}
