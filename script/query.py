#!/usr/bin/env python3

"""Query a Fine Offset / Ecowitt sensor over Modbus and print every value.

Connects over Modbus TCP (including RTU-over-TCP, the common way these
sensors are bridged onto a network) or a serial/USB port, reads the whole
device once, and dumps every value to the terminal. Handy for checking a real
sensor without Home Assistant.

The library only needs the connection protocol; this script selects the
tmodbus backend, so install the ``cli`` extra first.
"""

from __future__ import annotations

import argparse
import asyncio
import sys
import time

from modbus_connection import ModbusError
from modbus_connection.cli_helper import (
    CountingUnit,
    add_connection_args,
    connect_from_args,
    print_component,
)

from ecowitt_modbus import SUPPORTED_MODELS, WN90LP, EcowittDevice, NotThisDeviceError

# These sensors only ever speak RTU framing, whether carried over TCP (a
# transparent serial gateway, the common bridge for them) or a direct serial
# port.
_CONNECTIONS = (("tcp", "rtu"), ("tcp", "socket"), ("serial", "rtu"))


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    add_connection_args(parser, connections=_CONNECTIONS)
    parser.add_argument(
        "--model",
        choices=sorted(SUPPORTED_MODELS),
        default=WN90LP.MODEL,
        help=f"sensor model to read (default: {WN90LP.MODEL})",
    )
    parser.add_argument(
        "--unit",
        type=int,
        default=None,
        help="Modbus unit/device address (default: the model's factory default)",
    )
    parser.add_argument(
        "--history",
        action="store_true",
        help="also read the WN90LP's 30 minutes of archived per-minute readings",
    )
    return parser.parse_args(argv)


async def _read(device: EcowittDevice, args: argparse.Namespace) -> None:
    """Read everything the chosen model can report."""
    await device.async_probe()
    if isinstance(device, WN90LP):
        if args.history:
            await device.async_update_history()
    elif args.history:
        print(
            f"--history is a WN90LP feature; {device.MODEL} archives nothing.",
            file=sys.stderr,
        )


async def _run(args: argparse.Namespace) -> int:
    model = SUPPORTED_MODELS[args.model]
    unit_id = model.DEFAULT_UNIT_ID if args.unit is None else args.unit

    try:
        connection = await connect_from_args(args)
    except ModbusError as err:
        print(f"Could not connect: {err}", file=sys.stderr)
        return 1

    counting = CountingUnit(connection.for_unit(unit_id))
    device = model(counting)
    elapsed = 0.0
    try:
        start = time.monotonic()
        await _read(device, args)
        elapsed = time.monotonic() - start
    except NotThisDeviceError as err:
        print(f"That is not a {args.model}: {err}", file=sys.stderr)
        return 1
    except ModbusError as err:
        print(f"Error reading device: {err}", file=sys.stderr)
        return 1
    finally:
        await connection.close()

    print_component(device.info, title="Device")  # type: ignore[attr-defined]
    print()
    print_component(device.sensors, title="Live readings")  # type: ignore[attr-defined]
    if args.history and isinstance(device, WN90LP):
        print()
        print_component(device.history, title="History (last 30 minutes)")
    print(f"\nQueried in {elapsed * 1000:.0f} ms ({counting.reads} Modbus reads)")
    return 0


def main() -> int:
    return asyncio.run(_run(_parse_args()))


if __name__ == "__main__":
    raise SystemExit(main())
