"""Tests for Sensors."""

from __future__ import annotations

from modbus_connection.mock import MockModbusUnit

from ecowitt_modbus import WN90LP


async def test_decodes_live_readings(wn90lp: WN90LP) -> None:
    await wn90lp.sensors.async_update()

    assert wn90lp.sensors.light == 17670
    assert wn90lp.sensors.uv_index == 1.3
    assert wn90lp.sensors.temperature == 26.2
    assert wn90lp.sensors.humidity == 60
    assert wn90lp.sensors.wind_speed == 0.0
    assert wn90lp.sensors.gust_speed == 0.0
    assert wn90lp.sensors.wind_direction == 150
    assert wn90lp.sensors.rainfall == 0.0
    assert wn90lp.sensors.absolute_pressure == 1001.0
    assert wn90lp.sensors.rain_counter == 0.18


async def test_sentinel_decodes_to_none(wn90lp: WN90LP, unit: MockModbusUnit) -> None:
    unit.holding[0x167] = 0xFFFF
    await wn90lp.sensors.async_update()

    assert wn90lp.sensors.temperature is None
