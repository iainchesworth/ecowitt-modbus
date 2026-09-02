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
from ecowitt_ws90_modbus.testing import WS90_LIVE_EXAMPLE


@pytest.fixture
def ws90(mock_modbus_unit: MockModbusUnit) -> WS90:
    """A WS90 over the mock unit, preloaded with device values."""
    mock_modbus_unit.holding.update(WS90_LIVE_EXAMPLE)
    return WS90(mock_modbus_unit)


@pytest.fixture
def unit(mock_modbus_unit: MockModbusUnit) -> MockModbusUnit:
    """The mock unit the ``ws90`` fixture reads and writes through.

    Request it alongside ``ws90`` to assert on the register store a write
    landed in, rather than reaching for the unit a component holds.
    """
    return mock_modbus_unit
