# `ecowitt-modbus` Python library

[![CI](https://github.com/iainchesworth/ecowitt-modbus/actions/workflows/ci.yml/badge.svg?branch=develop)](https://github.com/iainchesworth/ecowitt-modbus/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/ecowitt-modbus.svg)](https://pypi.org/project/ecowitt-modbus/)
[![Python](https://img.shields.io/pypi/pyversions/ecowitt-modbus.svg)](https://pypi.org/project/ecowitt-modbus/)
[![License](https://img.shields.io/github/license/iainchesworth/ecowitt-modbus.svg)](LICENSE)

`ecowitt-modbus` is an asynchronous, transport-independent Python library for communicating with **Fine Offset / Ecowitt** weather sensors over Modbus RTU (including RTU-over-TCP, the common way these sensors are bridged onto a network).

The library was developed as the backend for a corresponding Home Assistant integration. As it is kept independent of Home Assistant, it can also be used by other Python applications and projects.

## Supported devices

| Device | Specification | Default address | Comments |
| :----- | :------------ | :-------------- | :------- |
| Fine Offset / Ecowitt WS90 | Modbus RTU V1.0.6 | `0x90` (144) | All-in-one weather sensor array with no moving parts (light, UV, temperature, humidity, wind, rain, pressure) |
| Fine Offset / Ecowitt WN69LP | Modbus RTU V1.0.2 | `0x24` (36) | Wired RS485 7-in-1 sensor array with a mechanical anemometer and tipping-bucket rain gauge |

The two devices share almost no register layout. They are modelled separately and only present a common interface, not common internals.

## Usage

Construct the model you have with a [`modbus_connection.ModbusUnit`](https://github.com/home-assistant-libs/modbus-connection), confirm the right device answered, then poll it:

```python
from ecowitt_modbus import WS90

device = WS90(unit)
await device.async_probe()
await device.async_update()

print(device.sensors.temperature)   # 26.2
print(device.sensors.wind_speed)    # 1.2
```

An application that lets a user pick the model can look the class up by name instead of branching:

```python
from ecowitt_modbus import SUPPORTED_MODELS

device = SUPPORTED_MODELS["WN69LP"](unit)
```

`async_probe()` raises `NotThisDeviceError` when something answers but is not the model asked for. How much it can confirm depends on the device — see [Identifying a device](#identifying-a-device) below.

## Data provided by the library

Every supported model reports light, UV index, temperature, humidity, wind speed, gust speed, wind direction, rainfall, and absolute pressure. Beyond that they differ:

| | WS90 | WN69LP |
| :-- | :--- | :----- |
| Rainfall resolution | 0.1mm, plus a 0.01mm counter | 0.254mm (0.01in tipping bucket) |
| UV index encoding | tenths | whole numbers |
| Battery / supply voltage | archived history only | live registers |
| 30-minute rolling history | yes, 11 parameters at one sample per minute | no |
| Recent-rainfall register | no | yes |
| Firmware version | not reported | reported (specification V1.0.2 and later) |

Both models also expose their RS-485 settings, and accept validated writes to the two settable identity registers (baud rate and device address).

The WS90's history block is 330 registers wide and changes once a minute, so it is polled separately from the live readings:

```python
await device.async_update_history()
print(device.history.battery_voltage)
```

### Identifying a device

The two models differ in how confidently a caller can tell what it is talking to, which matters for any application that needs to recognise a device again later:

- The **WS90** reports a fixed device code and a 32-bit device ID. `async_probe()` is a positive identification, and `device.serial_number` is stable across changes of host, port, and device address.
- The **WN69LP** reports neither. `device.serial_number` is always `None`, and `async_probe()` can only reject a responder whose readings fall outside the physical ranges the specification documents (for example over 100% humidity). That rules out most unrelated devices, but it cannot distinguish a WN69LP from another device whose registers happen to decode plausibly at the same addresses.

## Scope

The library reads live weather readings, RS-485 communication settings, and — on the WS90 — the 30-minute rolling history the sensor archives internally.

It does not implement:

- the WS90's "on-demand measurement" command registers (`0x9C92`-`0x9C9A`), which duplicate the live readings with tighter timing at the cost of a write-then-wait-then-read sequence,
- the WN69LP's automatic reporting mode (register `0x162`), which has the device push readings unprompted rather than answer polls,
- either device's write-only command registers (rainfall reset, software reset),
- the recovery command that reads or sets the baud rate and address when they are unknown, which is a non-Modbus framed exchange.

The library does **not** create or own the Modbus transport. Applications provide a [`modbus_connection.ModbusUnit`](https://github.com/home-assistant-libs/modbus-connection) and may use any backend `modbus-connection` supports (pymodbus, tmodbus, ...).

## Testing and validation

Decode logic (scale, offset, and invalid-value handling) is cross-checked against the manufacturers' own worked examples in the WS90 Modbus RTU V1.0.6 and WN69LP Modbus RTU V1.0.2 specifications. The WS90 model is additionally verified against a live sensor.

Software tests run against an in-memory mock Modbus backend (via `modbus-connection`'s pytest plugin) — no real device or server is needed to run the test suite. The register images those tests use are exported as `ecowitt_modbus.testing` so consuming applications can reuse them.

## Documentation, development and contribution guidelines

Run `script/run_checks.sh` before opening a pull request — it mirrors the CI workflow (formatting, lint, compile, tests, build) in one command. `script/format_code.sh` applies formatting and safe lint fixes only. `script/query.py` is a standalone CLI for querying a real sensor over TCP or serial; run it with `--help` for usage.

Contributions target the `develop` branch; `main` only ever receives fast-forwards from `develop` (enforced in CI).

## Related projects

This library is one of three repositories for Ecowitt Modbus support in Home Assistant:

* [`ha-ecowitt-modbus`](https://github.com/iainchesworth/ha-ecowitt-modbus) — a HACS-installable custom integration, vendoring this library.
* [`ha-core-ws90`](https://github.com/iainchesworth/ha-core-ws90) — a `home-assistant/core` fork adding this as a built-in integration (branch `ecowitt-ws90-integration`).
