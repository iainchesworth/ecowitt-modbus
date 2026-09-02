"""Tests for DeviceInfo."""

from __future__ import annotations

import pytest
from modbus_connection.mock import MockModbusUnit

from ecowitt_ws90_modbus import WS90, BaudRate
from ecowitt_ws90_modbus.device_info import DeviceInfo


async def test_decodes_identity(ws90: WS90) -> None:
    await ws90.info.async_update()

    assert ws90.info.device_code == 0x90
    assert ws90.info.model == "WS90"
    assert ws90.info.manufacturer == "Ecowitt"
    assert ws90.info.baud_rate is BaudRate.BAUD_9600
    assert ws90.info.device_address == 0x90
    assert ws90.info.device_id == 0x12345678


async def test_model_is_none_before_update(unit: MockModbusUnit) -> None:
    info = DeviceInfo(unit)

    assert info.model is None


async def test_unknown_device_code_reports_unknown(
    ws90: WS90, unit: MockModbusUnit
) -> None:
    unit.holding[0x160] = 0x42
    await ws90.info.async_update()

    assert ws90.info.model == "unknown (0x42)"


async def test_device_address_rejects_out_of_range_write(ws90: WS90) -> None:
    with pytest.raises(ValueError, match="between 1 and 252"):
        await ws90.info.write("device_address", 0)
