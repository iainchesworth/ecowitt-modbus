"""Register images for consumers of this library to test against.

Each image below reproduces the worked example in the corresponding
specification, so a consuming application's tests can serve a plausible
device through ``modbus_connection``'s mock backend without inventing raw
register values or duplicating the decode logic under test.
"""

from __future__ import annotations

# Raw holding-register words keyed by their (protocol) address. Reproduces
# Example 2 of Ecowitt's WS90ModbusRTU_V1.0.6 spec verbatim for the live
# block, plus that spec's own worked example for the rain counter register.
WN90LP_LIVE_EXAMPLE: dict[int, int] = {
    0x160: 0x90,  # device_code -> model "WN90LP"
    0x161: 2,  # baud_rate -> BAUD_9600
    0x162: 0x90,  # device_address (factory default)
    0x163: 0x1234,  # device_id MSB
    0x164: 0x5678,  # device_id LSB -> 0x12345678
    0x165: 1767,  # light -> 17670 lux
    0x166: 13,  # uv_index -> 1.3
    0x167: 662,  # temperature -> 26.2 C
    0x168: 60,  # humidity -> 60%
    0x169: 0,  # wind_speed -> 0.0 m/s
    0x16A: 0,  # gust_speed -> 0.0 m/s
    0x16B: 150,  # wind_direction -> 150 deg
    0x16C: 0,  # rainfall -> 0.0 mm
    0x16D: 10010,  # absolute_pressure -> 1001.0 hPa
    0x16E: 18,  # rain_counter -> 0.18 mm
}

#: A WN90LP's factory-default device (slave) address, matching WN90LP_LIVE_EXAMPLE.
WN90LP_UNIT_ID = 0x90

# Reproduces Example 1 of Ecowitt's WN69LP Modbus RTU V1.0.2 spec verbatim
# for the live block (0x180-0x18B), with the configuration block set to the
# defaults that specification documents.
WN69LP_LIVE_EXAMPLE: dict[int, int] = {
    0x160: 0x24,  # device_address (factory default)
    0x161: 2,  # baud_rate -> BAUD_9600
    0x162: 0,  # auto_report_interval -> 0s (reporting disabled, the default)
    0x163: 64,  # sampling_period -> 16.0s (the default)
    0x167: 100,  # firmware_version -> "1.0.0"
    0x180: 0x06E7,  # light -> 17670 lux
    0x181: 0x0001,  # uv_index -> 1
    0x182: 0x0296,  # temperature -> 26.2 C
    0x183: 0x003C,  # humidity -> 60%
    0x184: 0x000C,  # wind_speed -> 1.2 m/s
    0x185: 0x001C,  # gust_speed -> 2.8 m/s
    0x186: 0x0096,  # wind_direction -> 150 deg
    0x187: 0x008B,  # rainfall -> 35.306 mm
    0x188: 0x271F,  # absolute_pressure -> 1001.5 hPa
    0x189: 0x0138,  # battery_voltage -> 3.12 V
    0x18A: 0x0078,  # supply_voltage -> 12.0 V
    0x18B: 0x0005,  # recent_rainfall -> 1.27 mm
}

#: A WN69LP's factory-default device (slave) address, matching
#: WN69LP_LIVE_EXAMPLE and the spec's worked example.
WN69LP_UNIT_ID = 0x24
