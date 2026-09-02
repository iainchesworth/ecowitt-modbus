"""Fixtures: supported devices over modbus-connection's in-memory mock backend.

The mock backend and its fixtures ship with ``modbus-connection``. They are
imported explicitly below so the test suite does not depend on pytest
entry-point autoloading. There is no real server, socket, or backend here --
just an address-keyed store loaded with device-shaped register values.
"""

from __future__ import annotations

import pytest
from modbus_connection.mock import MockModbusUnit
from modbus_connection.pytest_plugin import (
    mock_modbus_connection as mock_modbus_connection,
    mock_modbus_unit as mock_modbus_unit,
)

from ecowitt_modbus import WN69LP, WN90LP
from ecowitt_modbus.testing import WN69LP_LIVE_EXAMPLE, WN90LP_LIVE_EXAMPLE


@pytest.fixture
def unit(mock_modbus_unit: MockModbusUnit) -> MockModbusUnit:
    """The mock unit the device fixtures read and write through.

    Request it alongside a device to assert on the register store a write
    landed in, rather than reaching for the unit a component holds.
    """
    return mock_modbus_unit


@pytest.fixture
def wn90lp(unit: MockModbusUnit) -> WN90LP:
    """A WN90LP over the mock unit, preloaded with device values."""
    unit.holding.update(WN90LP_LIVE_EXAMPLE)
    return WN90LP(unit)


@pytest.fixture
def wn69lp(unit: MockModbusUnit) -> WN69LP:
    """A WN69LP over the mock unit, preloaded with device values."""
    unit.holding.update(WN69LP_LIVE_EXAMPLE)
    return WN69LP(unit)
