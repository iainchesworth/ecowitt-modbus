"""Tests for the top-level WS90 device object."""

from __future__ import annotations

import pytest
from modbus_connection.mock import MockModbusUnit

from ecowitt_modbus import WS90, EcowittDevice, NotThisDeviceError


async def test_async_update_reads_info_and_sensors_together(ws90: WS90) -> None:
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


async def test_implements_the_shared_device_interface(ws90: WS90) -> None:
    assert isinstance(ws90, EcowittDevice)
    assert WS90.MODEL == "WS90"
    assert WS90.DEFAULT_UNIT_ID == 0x90
    assert ws90.manufacturer == "Ecowitt"


async def test_serial_number_is_the_device_id(ws90: WS90) -> None:
    await ws90.async_update()

    assert ws90.serial_number == "12345678"


async def test_serial_number_is_none_before_the_first_update(
    unit: MockModbusUnit,
) -> None:
    assert WS90(unit).serial_number is None


async def test_the_ws90_reports_no_firmware_version(ws90: WS90) -> None:
    """Unlike the WN69LP, the WS90 has no firmware-version register."""
    await ws90.async_update()

    assert ws90.sw_version is None


class TestProbe:
    """Confirming a WS90 is what answered."""

    async def test_accepts_a_genuine_ws90(self, ws90: WS90) -> None:
        await ws90.async_probe()

        assert ws90.info.model == "WS90"

    async def test_leaves_the_readings_populated(self, ws90: WS90) -> None:
        """A caller that probes should not have to poll again straight away."""
        await ws90.async_probe()

        assert ws90.sensors.temperature == 26.2

    async def test_rejects_another_device_at_the_same_address(
        self, ws90: WS90, unit: MockModbusUnit
    ) -> None:
        unit.holding[0x160] = 0x42

        with pytest.raises(NotThisDeviceError, match="unknown"):
            await ws90.async_probe()
