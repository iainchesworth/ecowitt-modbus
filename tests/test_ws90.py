"""Tests for the top-level WS90 device object."""

from __future__ import annotations

from modbus_connection.mock import MockModbusUnit

from ecowitt_ws90_modbus import WS90


async def test_async_update_reads_info_and_sensors_together(
    ws90: WS90, unit: MockModbusUnit
) -> None:
    await ws90.async_update()

    assert ws90.info.model == "WS90"
    assert ws90.sensors.temperature == 26.2


async def test_history_is_not_touched_by_async_update(ws90: WS90) -> None:
    """History's 30 instances exist immediately (a fixed-count repeating_group
    builds eagerly), but async_update() must not read their registers."""
    await ws90.async_update()

    assert len(ws90.history.max_light) == 30
    assert ws90.history.max_light[0].value is None


async def test_async_update_history_is_independent(
    ws90: WS90, unit: MockModbusUnit
) -> None:
    unit.holding[0x9B14] = 100

    await ws90.async_update_history()

    assert ws90.history.max_light[0].value == 1000
