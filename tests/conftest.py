"""Fixtures: a WS90 over modbus-connection's in-memory mock backend.

The mock backend and its fixtures ship with ``modbus-connection``. They are
imported explicitly below so the test suite does not depend on pytest entry-point
autoloading. There is no real server, socket, or backend here -- just an
address-keyed store loaded with WS90-shaped register values.
"""

from __future__ import annotations

import pytest
from modbus_connection.mock import MockModbusUnit
from modbus_connection.pytest_plugin import (
    mock_modbus_connection as mock_modbus_connection,
    mock_modbus_unit as mock_modbus_unit,
)

from ecowitt_ws90_modbus import WS90

# Raw register words keyed by their (protocol) address; decoded view inline.
# The live-block values reproduce Example 2 of Ecowitt's WS90ModbusRTU_V1.0.6
# spec verbatim, so they double as a cross-check against the manufacturer's
# own worked example. The rain counter value reproduces that spec's own
# worked example for register 0x16E.
HOLDING: dict[int, int] = {
    0x160: 0x90,  # device_code -> model "WS90"
    0x161: 2,  # baud_rate -> BAUD_9600
    0x162: 0x90,  # device_address (factory default)
    0x163: 0x1234,  # device_id MSB
    0x164: 0x5678,  # device_id LSB -> 0x12345678
    0x165: 1767,  # light -> 17670 lux
    0x166: 13,  # uv_index -> 1.3
    0x167: 662,  # temperature -> 26.2 C
    0x168: 60,  # humidity -> 60%
    0x169: 0,  # wind_speed -> 0.0 m/s
    0x16A: 0,  # gust_speed -> 0.0 m/s
    0x16B: 150,  # wind_direction -> 150 deg
    0x16C: 0,  # rainfall -> 0.0 mm
    0x16D: 10010,  # absolute_pressure -> 1001.0 hPa
    0x16E: 18,  # rain_counter -> 0.18 mm
}


@pytest.fixture
def ws90(mock_modbus_unit: MockModbusUnit) -> WS90:
    """A WS90 over the mock unit, preloaded with device values."""
    mock_modbus_unit.holding.update(HOLDING)
    return WS90(mock_modbus_unit)


@pytest.fixture
def unit(mock_modbus_unit: MockModbusUnit) -> MockModbusUnit:
    """The mock unit the ``ws90`` fixture reads and writes through.

    Request it alongside ``ws90`` to assert on the register store a write
    landed in, rather than reaching for the unit a component holds.
    """
    return mock_modbus_unit
