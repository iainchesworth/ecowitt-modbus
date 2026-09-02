"""Tests for the WN69LP's configuration and firmware registers."""

from __future__ import annotations

import pytest
from modbus_connection import IllegalDataAddressError
from modbus_connection.mock import MockModbusUnit

from ecowitt_modbus import WN69LP, BaudRate


async def test_decodes_the_configuration_block(wn69lp: WN69LP) -> None:
    await wn69lp.async_update_info()

    assert wn69lp.info.device_address == 0x24
    assert wn69lp.info.baud_rate is BaudRate.BAUD_9600
    assert wn69lp.info.sampling_period == 16.0


async def test_auto_reporting_is_disabled_by_default(wn69lp: WN69LP) -> None:
    """This library polls, so it never wants the device pushing reports."""
    await wn69lp.async_update_info()

    assert wn69lp.info.auto_report_interval == 0.0


async def test_intervals_decode_in_quarter_seconds(
    wn69lp: WN69LP, unit: MockModbusUnit
) -> None:
    """The spec's own worked examples: 0x3C -> 15s, 0xF0 -> 60s."""
    unit.holding[0x162] = 0x3C
    unit.holding[0x163] = 0xF0
    await wn69lp.async_update_info()

    assert wn69lp.info.auto_report_interval == 15.0
    assert wn69lp.info.sampling_period == 60.0


async def test_device_address_rejects_an_out_of_range_write(wn69lp: WN69LP) -> None:
    with pytest.raises(ValueError, match="between 1 and 252"):
        await wn69lp.info.write("device_address", 0)


class TestFirmwareVersion:
    """The 0x167 register, added by specification revision V1.0.2."""

    @pytest.mark.parametrize(
        ("raw", "expected"),
        [
            (100, "1.0.0"),  # the spec's own worked example (0x64)
            (103, "1.0.3"),  # the release that added low-power control
            (110, "1.1.0"),
            (204, "2.0.4"),
        ],
    )
    async def test_decodes_a_packed_decimal_version(
        self, wn69lp: WN69LP, unit: MockModbusUnit, raw: int, expected: str
    ) -> None:
        unit.holding[0x167] = raw
        await wn69lp.async_update_info()

        assert wn69lp.sw_version == expected

    async def test_is_none_before_the_first_read(self, unit: MockModbusUnit) -> None:
        assert WN69LP(unit).sw_version is None

    async def test_older_firmware_without_the_register_still_reads_info(
        self, wn69lp: WN69LP, unit: MockModbusUnit
    ) -> None:
        """A device predating V1.0.2 rejects 0x167.

        That must cost the caller the firmware version and nothing else --
        the configuration block was read successfully before it.
        """
        unit.fail_read(0x167, IllegalDataAddressError())

        await wn69lp.async_update_info()

        assert wn69lp.sw_version is None
        assert wn69lp.info.device_address == 0x24
