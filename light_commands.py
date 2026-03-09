CHARACTERISTIC = "0000a040-0000-1000-8000-00805f9b34fb"


def calc_crc(data_bytes):
    s = sum(data_bytes)
    return (0xFF - (s & 0xFF)) & 0xFF


def build_rgb_packet(r, g, b):
    r = max(0, min(255, r))
    g = max(0, min(255, g))
    b = max(0, min(255, b))

    packet = bytearray([
        0x55, 0xAA,
        0x03,
        0x08, 0x02,
        r, g, b
    ])

    crc = calc_crc(packet)
    packet.append(crc)

    return packet


def build_white_temp_packet(level):
    # clamp level
    level = max(1, min(5, level))

    packet = bytearray([
        0x55, 0xAA,   # header
        0x01,         # standard/white mode
        0x08, 0x09,   # white temperature command
        level
    ])

    crc = calc_crc(packet)
    packet.append(crc)

    return packet


def build_brightness_packet(value):
    # clamp brightness
    value = max(1, min(255, value))

    packet = bytearray([
        0x55, 0xAA,   # header
        0x01,         # standard/white mode
        0x08, 0x01,   # brightness command
        value
    ])

    crc = calc_crc(packet)
    packet.append(crc)

    return packet


async def set_brightness(value, characteristic, client):
    packet = build_brightness_packet(value)
    await client.write_gatt_char(characteristic, packet)


async def write_to_client(packet, characteristic, client):
    await client.write_gatt_char(characteristic, packet)


async def set_white_temp(level, client):
    packet = build_white_temp_packet(level)
    await write_to_client(packet, CHARACTERISTIC, client)


async def set_rgb(r, g, b, client):
    packet = build_rgb_packet(r, g, b)
    await write_to_client(packet, CHARACTERISTIC, client)


async def set_brightness_value(value, client):
    await set_brightness(value, CHARACTERISTIC, client)
