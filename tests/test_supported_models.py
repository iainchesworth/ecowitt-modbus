"""Tests for the contract every supported model has to keep.

These run against ``SUPPORTED_MODELS`` rather than a fixed list, so adding a
model to the library without giving it the shared interface fails here
instead of in whatever application consumes it.
"""

from __future__ import annotations

import pytest
from modbus_connection.mock import MockModbusUnit

from ecowitt_modbus import SUPPORTED_MODELS, WN69LP, WS90, EcowittDevice

MODELS = pytest.mark.parametrize(
    "model", SUPPORTED_MODELS.values(), ids=lambda m: str(m.MODEL)
)


def test_every_model_is_registered_under_its_own_name() -> None:
    for name, model in SUPPORTED_MODELS.items():
        assert model.MODEL == name


def test_the_registry_holds_the_models_this_library_documents() -> None:
    """A deliberate tripwire: adding a model should be a visible diff here."""
    assert set(SUPPORTED_MODELS) == {"WS90", "WN69LP"}
    assert SUPPORTED_MODELS["WS90"] is WS90
    assert SUPPORTED_MODELS["WN69LP"] is WN69LP


@MODELS
def test_every_model_implements_the_shared_interface(
    model: type[EcowittDevice], unit: MockModbusUnit
) -> None:
    device = model(unit)

    assert isinstance(device, EcowittDevice)
    assert device.manufacturer == "Ecowitt"
    # Readable before any I/O, so a caller can build a device and inspect it
    # without having reached the hardware yet.
    assert device.serial_number is None
    assert device.sw_version is None


@MODELS
def test_every_model_declares_a_plausible_default_address(
    model: type[EcowittDevice],
) -> None:
    """Modbus RTU addresses run 1-247; 248-252 are reserved."""
    assert 1 <= model.DEFAULT_UNIT_ID <= 247


@MODELS
@pytest.mark.parametrize("address", [1, 128, 252])
async def test_every_model_accepts_a_valid_device_address(
    model: type[EcowittDevice], unit: MockModbusUnit, address: int
) -> None:
    """Test the address validator lets through what the devices accept.

    Both specifications document 1-252 as the settable range. Rejecting a
    valid address would leave a user unable to move a device off a
    conflicting one.
    """
    info = model(unit).info
    await info.write("device_address", address)

    # The two models keep this register at different addresses, so the
    # write is checked where the component says it went.
    register = info.resolved_fields["device_address"].address
    assert unit.holding[register] == address


@MODELS
@pytest.mark.parametrize("address", [0, 253, 65535])
async def test_every_model_rejects_an_invalid_device_address(
    model: type[EcowittDevice], unit: MockModbusUnit, address: int
) -> None:
    """Test an unsettable address is refused before it reaches the wire."""
    with pytest.raises(ValueError, match="between 1 and 252"):
        await model(unit).info.write("device_address", address)


@MODELS
def test_every_model_exposes_the_readings_common_to_all_of_them(
    model: type[EcowittDevice], unit: MockModbusUnit
) -> None:
    """The set an application can rely on without knowing the model.

    Anything beyond this is model-specific and has to be handled per model.
    """
    sensors = model(unit).sensors  # type: ignore[attr-defined]

    for field in (
        "light",
        "uv_index",
        "temperature",
        "humidity",
        "wind_speed",
        "gust_speed",
        "wind_direction",
        "rainfall",
        "absolute_pressure",
    ):
        assert hasattr(sensors, field), f"{model.MODEL} is missing {field}"
