"""Tests for History."""

from __future__ import annotations

import pytest
from modbus_connection.mock import MockModbusUnit

from ecowitt_modbus import WN90LP


def _fill(unit: MockModbusUnit, start: int, values: list[int]) -> None:
    for offset, value in enumerate(values):
        unit.holding[start + offset] = value


async def test_decodes_most_recent_minute(wn90lp: WN90LP, unit: MockModbusUnit) -> None:
    _fill(unit, 0x9B14, [1767, *[0] * 29])  # max_light
    _fill(unit, 0x9C22, [320, *[0] * 29])  # avg_battery_voltage -> 3.20V
    _fill(unit, 0x9C40, [50, *[0] * 29])  # avg_capacitance_voltage -> 5.0V

    await wn90lp.history.async_update()

    assert len(wn90lp.history.max_light) == 30
    assert wn90lp.history.max_light[0].value == 17670
    assert wn90lp.history.battery_voltage == pytest.approx(3.2)
    assert wn90lp.history.capacitance_voltage == pytest.approx(5.0)


async def test_thirtieth_sample_is_thirty_minutes_ago(
    wn90lp: WN90LP, unit: MockModbusUnit
) -> None:
    _fill(unit, 0x9B50, list(range(30)))  # avg_temperature, offset -40 applied

    await wn90lp.history.async_update()

    assert wn90lp.history.avg_temperature[0].value == pytest.approx(-40.0)
    assert wn90lp.history.avg_temperature[29].value == pytest.approx(29 * 0.1 - 40)


async def test_rainfall_sentinel_decodes_to_none(
    wn90lp: WN90LP, unit: MockModbusUnit
) -> None:
    """The spec doesn't document a rainfall sentinel, but 0xFFFF is applied
    defensively anyway -- see the comment in history.py."""
    _fill(unit, 0x9BE6, [0xFFFF, *[0] * 29])

    await wn90lp.history.async_update()

    assert wn90lp.history.rainfall[0].value is None
