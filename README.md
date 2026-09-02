# `ecowitt-ws90-modbus` Python library

[![CI](https://github.com/iainchesworth/ecowitt-ws90-modbus/actions/workflows/ci.yml/badge.svg?branch=develop)](https://github.com/iainchesworth/ecowitt-ws90-modbus/actions/workflows/ci.yml)
[![License](https://img.shields.io/github/license/iainchesworth/ecowitt-ws90-modbus.svg)](LICENSE)

<!-- Not yet published to PyPI -- restore these once it is:
[![PyPI](https://img.shields.io/pypi/v/ecowitt-ws90-modbus.svg)](https://pypi.org/project/ecowitt-ws90-modbus/)
[![Python](https://img.shields.io/pypi/pyversions/ecowitt-ws90-modbus.svg)](https://pypi.org/project/ecowitt-ws90-modbus/)
-->


`ecowitt-ws90-modbus` is an asynchronous, transport-independent Python library for communicating with the **Fine Offset / Ecowitt WS90** all-in-one weather sensor array over Modbus RTU (including RTU-over-TCP, the common way this sensor is bridged onto a network).

The library was developed as the backend for a corresponding Home Assistant integration. As it is kept independent of Home Assistant, it can also be used by other Python applications and projects.

## Purpose and scope

`ecowitt-ws90-modbus` reads the WS90's live weather readings, its identity and RS-485 communication settings, and the 30-minute rolling history the sensor archives internally. It does not attempt to reproduce the sensor's "on-demand measurement" command registers (`0x9C92`-`0x9C9A`), which duplicate the live readings with tighter timing at the cost of a write-then-wait-then-read sequence -- not needed for a polling integration.

The library:

* contains the WS90's Modbus register map, including data types, scaling, and invalid-value sentinels,

* provides the identity registers (model, RS-485 baud rate, device address, device ID) alongside the live weather readings,

* exposes the sensor's 30-minute rolling per-minute history, including battery and capacitance voltage, which are not available anywhere in the live register block,

* does **not** create or own the Modbus transport. Applications using the library provide a [`modbus_connection.ModbusUnit`](https://github.com/home-assistant-libs/modbus-connection) and may use any backend supported by `modbus-connection` (pymodbus, tmodbus, ...).

An example script `query.py` in the code of the library shows how to build an application that can query a WS90 over Modbus/TCP (including RTU-over-TCP), or a direct serial connection.

## Supported devices

| Device | Registers | Comments |
| :----- | :-------: | :------- |
| Fine Offset / Ecowitt WS90 | Modbus RTU spec v1.0.6 | All-in-one weather sensor array (light, UV, temperature, humidity, wind, rain, pressure) |

## Data provided by the library

The library provides:

* device identity (model, RS-485 baud rate, device address, device ID),

* live weather readings: light, UV index, temperature, humidity, wind speed, gust speed, wind direction, rainfall, absolute pressure, and a finer-resolution rain counter,

* the last 30 minutes of archived per-minute readings for the same parameters, plus battery and capacitance voltage,

* validated writes for the two writable identity registers (RS-485 baud rate and device address).

## Testing and validation

The library's decode logic (scale, offset, and invalid-value handling) is cross-checked against the manufacturer's own worked examples in the WS90 Modbus RTU v1.0.6 specification, and against a live WS90 sensor.

Software-based tests run against an in-memory mock Modbus backend (via `modbus-connection`'s pytest plugin) -- no real device or server is needed to run the test suite.

## Documentation, development and contribution guidelines

Run `script/run_checks.sh` before opening a pull request -- it mirrors the CI workflow (formatting, lint, compile, tests, build) in one command. `script/format_code.sh` applies formatting and safe lint fixes only. `script/query.py` is a standalone CLI for querying a real WS90 over TCP or serial; run it with `--help` for usage.

Contributions target the `develop` branch; `main` only ever receives fast-forwards from `develop` (enforced in CI).

## Related projects

This library is one of three repositories for WS90 support in Home Assistant:

* [`ha-ecowitt-ws90`](https://github.com/iainchesworth/ha-ecowitt-ws90) -- a HACS-installable custom integration, vendoring this library.
* [`ha-core-ws90`](https://github.com/iainchesworth/ha-core-ws90) -- a `home-assistant/core` fork adding this as a built-in integration (branch `ecowitt-ws90-integration`).
