"""Tests for the WN69LP's live weather readings."""

from __future__ import annotations

import pytest
from modbus_connection.mock import MockModbusUnit

from ecowitt_modbus import WN69LP


async def test_decodes_the_specs_worked_example(wn69lp: WN69LP) -> None:
    """Every value here is the one Example 1 of the V1.0.2 spec prints."""
    await wn69lp.async_update()

    assert wn69lp.sensors.light == 17670
    assert wn69lp.sensors.uv_index == 1
    assert wn69lp.sensors.temperature == 26.2
    assert wn69lp.sensors.humidity == 60
    assert wn69lp.sensors.wind_speed == 1.2
    assert wn69lp.sensors.gust_speed == 2.8
    assert wn69lp.sensors.wind_direction == 150
    assert wn69lp.sensors.rainfall == pytest.approx(35.306)
    assert wn69lp.sensors.absolute_pressure == 1001.5
    assert wn69lp.sensors.battery_voltage == 3.12
    assert wn69lp.sensors.supply_voltage == 12.0
    assert wn69lp.sensors.recent_rainfall == pytest.approx(1.27)


async def test_uv_index_is_not_scaled_like_the_wn90lps(wn69lp: WN69LP) -> None:
    """The WN90LP reports tenths here; the WN69LP reports whole numbers.

    Getting this wrong would silently report a tenth of the real UV index,
    so it is pinned separately from the worked example above.
    """
    await wn69lp.async_update()

    assert wn69lp.sensors.uv_index == 1


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (0, 0.0),
        (1, 0.254),
        (4, 1.016),
        (139, 35.306),
    ],
)
async def test_rainfall_counts_in_imperial_tips(
    wn69lp: WN69LP, unit: MockModbusUnit, raw: int, expected: float
) -> None:
    """Rainfall advances in 0.254mm (0.01in) steps, not round metric ones."""
    unit.holding[0x187] = raw
    await wn69lp.async_update()

    assert wn69lp.sensors.rainfall == pytest.approx(expected)


@pytest.mark.parametrize(
    ("field", "address"),
    [
        ("light", 0x180),
        ("uv_index", 0x181),
        ("temperature", 0x182),
        ("humidity", 0x183),
        ("wind_speed", 0x184),
        ("gust_speed", 0x185),
        ("wind_direction", 0x186),
        ("absolute_pressure", 0x188),
        ("battery_voltage", 0x189),
        ("supply_voltage", 0x18A),
    ],
)
async def test_sentinel_decodes_to_none(
    wn69lp: WN69LP, unit: MockModbusUnit, field: str, address: int
) -> None:
    unit.holding[address] = 0xFFFF
    await wn69lp.async_update()

    assert getattr(wn69lp.sensors, field) is None


@pytest.mark.parametrize("address", [0x187, 0x18B])
async def test_the_rainfall_totals_have_no_sentinel(
    wn69lp: WN69LP, unit: MockModbusUnit, address: int
) -> None:
    """The spec documents no invalid value for the two rainfall registers.

    0xFFFF is a reachable (if implausible) total there rather than a
    sentinel, so it must decode as a number instead of silently vanishing.
    """
    unit.holding[address] = 0xFFFF
    await wn69lp.async_update()

    assert wn69lp.sensors.rainfall is not None
    assert wn69lp.sensors.recent_rainfall is not None


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (0, -40.0),  # bottom of the measurable range
        (105, -29.5),
        (295, -10.5),  # the spec's own worked example
        (400, 0.0),
        (505, 10.5),  # the spec's own worked example
        (1000, 60.0),  # top of the measurable range
    ],
)
async def test_temperature_offset_spans_below_freezing(
    wn69lp: WN69LP, unit: MockModbusUnit, raw: int, expected: float
) -> None:
    """Sub-zero readings come from the 400-count offset, not a signed word."""
    unit.holding[0x182] = raw
    await wn69lp.async_update()

    assert wn69lp.sensors.temperature == pytest.approx(expected)
