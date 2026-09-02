"""Tests for the top-level WN69LP device object."""

from __future__ import annotations

import pytest
from modbus_connection import IllegalDataAddressError, ModbusTimeoutError
from modbus_connection.mock import MockModbusUnit

from ecowitt_modbus import WN69LP, EcowittDevice, NotThisDeviceError


async def test_implements_the_shared_device_interface(wn69lp: WN69LP) -> None:
    assert isinstance(wn69lp, EcowittDevice)
    assert WN69LP.MODEL == "WN69LP"
    assert WN69LP.DEFAULT_UNIT_ID == 0x24
    assert wn69lp.manufacturer == "Ecowitt"


async def test_reports_no_serial_number(wn69lp: WN69LP) -> None:
    """The WN69LP has no identity register, before or after a read.

    Callers rely on this being None to know they must fall back to
    addressing the device by where it is rather than what it is.
    """
    assert wn69lp.serial_number is None

    await wn69lp.async_probe()

    assert wn69lp.serial_number is None


async def test_async_update_leaves_the_configuration_block_alone(
    wn69lp: WN69LP, unit: MockModbusUnit
) -> None:
    """The two blocks are 24 registers apart with a reserved gap between.

    Reading them together would span registers the spec marks reserved, so
    a live poll must touch only 0x180-0x18B.
    """
    unit.fail_read(0x160, IllegalDataAddressError())
    unit.fail_read(0x167, IllegalDataAddressError())

    await wn69lp.async_update()

    assert wn69lp.sensors.temperature == 26.2


class TestProbe:
    """Confirming the readings are consistent with a WN69LP."""

    async def test_accepts_a_genuine_wn69lp(self, wn69lp: WN69LP) -> None:
        await wn69lp.async_probe()

        assert wn69lp.sensors.temperature == 26.2

    async def test_reads_the_configuration_block_too(self, wn69lp: WN69LP) -> None:
        """A caller that probes should not need a second call for the firmware."""
        await wn69lp.async_probe()

        assert wn69lp.info.device_address == 0x24
        assert wn69lp.sw_version == "1.0.0"

    @pytest.mark.parametrize(
        ("field", "address", "raw"),
        [
            ("uv_index", 0x181, 16),  # spec caps the index at 15
            ("temperature", 0x182, 1001),  # 60.1 C, above the sensor's range
            ("humidity", 0x183, 101),  # over 100% relative humidity
            ("wind_speed", 0x184, 501),  # 50.1 m/s, above the sensor's range
            ("gust_speed", 0x185, 501),
            ("wind_direction", 0x186, 360),  # a bearing only goes to 359
            ("absolute_pressure", 0x188, 2999),  # 299.9 hPa, below the range
            ("absolute_pressure", 0x188, 11001),  # 1100.1 hPa, above the range
        ],
    )
    async def test_rejects_a_physically_impossible_reading(
        self, wn69lp: WN69LP, unit: MockModbusUnit, field: str, address: int, raw: int
    ) -> None:
        """Whatever answered cannot be a weather sensor, so refuse it."""
        unit.holding[address] = raw

        with pytest.raises(NotThisDeviceError, match=field):
            await wn69lp.async_probe()

    @pytest.mark.parametrize(
        ("field", "address", "raw"),
        [
            ("uv_index", 0x181, 15),
            ("temperature", 0x182, 0),  # -40.0 C
            ("temperature", 0x182, 1000),  # 60.0 C
            ("humidity", 0x183, 0),
            ("humidity", 0x183, 100),
            ("wind_speed", 0x184, 500),  # 50.0 m/s
            ("wind_direction", 0x186, 359),
            ("absolute_pressure", 0x188, 3000),  # 300.0 hPa
            ("absolute_pressure", 0x188, 11000),  # 1100.0 hPa
        ],
    )
    async def test_accepts_readings_at_the_edge_of_the_range(
        self, wn69lp: WN69LP, unit: MockModbusUnit, field: str, address: int, raw: int
    ) -> None:
        """The documented bounds are inclusive; an extreme is not a fault."""
        unit.holding[address] = raw

        await wn69lp.async_probe()

        assert getattr(wn69lp.sensors, field) is not None

    async def test_an_unavailable_reading_is_not_a_rejection(
        self, wn69lp: WN69LP, unit: MockModbusUnit
    ) -> None:
        """0xFFFF means "this sensor has no reading", not "wrong device"."""
        unit.holding[0x183] = 0xFFFF

        await wn69lp.async_probe()

        assert wn69lp.sensors.humidity is None

    async def test_a_silent_device_raises_the_transport_error(
        self, wn69lp: WN69LP, unit: MockModbusUnit
    ) -> None:
        """Nothing answering is a different failure from the wrong thing answering."""
        unit.fail_requests(ModbusTimeoutError("no answer"))

        with pytest.raises(ModbusTimeoutError):
            await wn69lp.async_probe()
