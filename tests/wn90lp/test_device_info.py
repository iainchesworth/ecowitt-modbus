"""Tests for DeviceInfo."""

from __future__ import annotations

import pytest
from modbus_connection.mock import MockModbusUnit

from ecowitt_modbus import WN90LP, BaudRate
from ecowitt_modbus.wn90lp import DeviceInfo


async def test_decodes_identity(wn90lp: WN90LP) -> None:
    await wn90lp.info.async_update()

    assert wn90lp.info.device_code == 0x90
    assert wn90lp.info.model == "WN90LP"
    assert wn90lp.info.baud_rate is BaudRate.BAUD_9600
    assert wn90lp.info.device_address == 0x90
    assert wn90lp.info.device_id == 0x12345678


async def test_model_is_none_before_update(unit: MockModbusUnit) -> None:
    info = DeviceInfo(unit)

    assert info.model is None


async def test_unknown_device_code_reports_unknown(
    wn90lp: WN90LP, unit: MockModbusUnit
) -> None:
    unit.holding[0x160] = 0x42
    await wn90lp.info.async_update()

    assert wn90lp.info.model == "unknown (0x42)"


async def test_device_address_rejects_out_of_range_write(wn90lp: WN90LP) -> None:
    with pytest.raises(ValueError, match="between 1 and 252"):
        await wn90lp.info.write("device_address", 0)
