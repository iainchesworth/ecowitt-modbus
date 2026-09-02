"""Tests for the top-level WN90LP device object."""

from __future__ import annotations

import pytest
from modbus_connection.mock import MockModbusUnit

from ecowitt_modbus import WN90LP, EcowittDevice, NotThisDeviceError


async def test_async_update_reads_info_and_sensors_together(wn90lp: WN90LP) -> None:
    await wn90lp.async_update()

    assert wn90lp.info.model == "WN90LP"
    assert wn90lp.sensors.temperature == 26.2


async def test_history_is_not_touched_by_async_update(wn90lp: WN90LP) -> None:
    """History's 30 instances exist immediately (a fixed-count repeating_group
    builds eagerly), but async_update() must not read their registers."""
    await wn90lp.async_update()

    assert len(wn90lp.history.max_light) == 30
    assert wn90lp.history.max_light[0].value is None


async def test_async_update_history_is_independent(
    wn90lp: WN90LP, unit: MockModbusUnit
) -> None:
    unit.holding[0x9B14] = 100

    await wn90lp.async_update_history()

    assert wn90lp.history.max_light[0].value == 1000


async def test_implements_the_shared_device_interface(wn90lp: WN90LP) -> None:
    assert isinstance(wn90lp, EcowittDevice)
    assert WN90LP.MODEL == "WN90LP"
    assert WN90LP.DEFAULT_UNIT_ID == 0x90
    assert wn90lp.manufacturer == "Ecowitt"


async def test_serial_number_is_the_device_id(wn90lp: WN90LP) -> None:
    await wn90lp.async_update()

    assert wn90lp.serial_number == "12345678"


async def test_serial_number_is_none_before_the_first_update(
    unit: MockModbusUnit,
) -> None:
    assert WN90LP(unit).serial_number is None


async def test_the_wn90lp_reports_no_firmware_version(wn90lp: WN90LP) -> None:
    """Unlike the WN69LP, the WN90LP has no firmware-version register."""
    await wn90lp.async_update()

    assert wn90lp.sw_version is None


class TestProbe:
    """Confirming a WN90LP is what answered."""

    async def test_accepts_a_genuine_wn90lp(self, wn90lp: WN90LP) -> None:
        await wn90lp.async_probe()

        assert wn90lp.info.model == "WN90LP"

    async def test_leaves_the_readings_populated(self, wn90lp: WN90LP) -> None:
        """A caller that probes should not have to poll again straight away."""
        await wn90lp.async_probe()

        assert wn90lp.sensors.temperature == 26.2

    async def test_rejects_another_device_at_the_same_address(
        self, wn90lp: WN90LP, unit: MockModbusUnit
    ) -> None:
        unit.holding[0x160] = 0x42

        with pytest.raises(NotThisDeviceError, match="unknown"):
            await wn90lp.async_probe()
