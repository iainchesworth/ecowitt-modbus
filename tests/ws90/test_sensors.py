"""Tests for Sensors."""

from __future__ import annotations

from modbus_connection.mock import MockModbusUnit

from ecowitt_modbus import WS90


async def test_decodes_live_readings(ws90: WS90) -> None:
    await ws90.sensors.async_update()

    assert ws90.sensors.light == 17670
    assert ws90.sensors.uv_index == 1.3
    assert ws90.sensors.temperature == 26.2
    assert ws90.sensors.humidity == 60
    assert ws90.sensors.wind_speed == 0.0
    assert ws90.sensors.gust_speed == 0.0
    assert ws90.sensors.wind_direction == 150
    assert ws90.sensors.rainfall == 0.0
    assert ws90.sensors.absolute_pressure == 1001.0
    assert ws90.sensors.rain_counter == 0.18


async def test_sentinel_decodes_to_none(ws90: WS90, unit: MockModbusUnit) -> None:
    unit.holding[0x167] = 0xFFFF
    await ws90.sensors.async_update()

    assert ws90.sensors.temperature is None
