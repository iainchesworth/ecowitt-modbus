#!/usr/bin/env python3

"""Query a Fine Offset / Ecowitt WS90 over Modbus and print every value.

Connects over Modbus TCP (including RTU-over-TCP, the common way this sensor
is bridged onto a network) or a serial/USB port, reads the whole device once,
and dumps every value to the terminal. Handy for checking a real sensor
without Home Assistant.

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

from ecowitt_ws90_modbus import WS90

# The WS90 only ever speaks RTU framing, whether carried over TCP (a
# transparent serial gateway, the common bridge for this sensor) or a direct
# serial port.
_CONNECTIONS = (("tcp", "rtu"), ("tcp", "socket"), ("serial", "rtu"))


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    add_connection_args(parser, connections=_CONNECTIONS)
    parser.add_argument(
        "--unit",
        type=int,
        default=0x90,
        help="Modbus unit/device address (default: 0x90, the WS90 factory default)",
    )
    parser.add_argument(
        "--history",
        action="store_true",
        help="also read the last 30 minutes of archived per-minute readings",
    )
    return parser.parse_args(argv)


async def _run(args: argparse.Namespace) -> int:
    try:
        connection = await connect_from_args(args)
    except ModbusError as err:
        print(f"Could not connect: {err}", file=sys.stderr)
        return 1
    counting = CountingUnit(connection.for_unit(args.unit))
    device = WS90(counting)
    elapsed = 0.0
    try:
        start = time.monotonic()
        await device.async_update()
        if args.history:
            await device.async_update_history()
        elapsed = time.monotonic() - start
    except ModbusError as err:
        print(f"Error reading device: {err}", file=sys.stderr)
        return 1
    finally:
        await connection.close()

    print_component(device.info, title="Device")
    print()
    print_component(device.sensors, title="Live readings")
    if args.history:
        print()
        print_component(device.history, title="History (last 30 minutes)")
    print(f"\nQueried in {elapsed * 1000:.0f} ms ({counting.reads} Modbus reads)")
    return 0


def main() -> int:
    return asyncio.run(_run(_parse_args()))


if __name__ == "__main__":
    raise SystemExit(main())
