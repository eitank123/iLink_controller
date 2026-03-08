ADDRESS = "AD:D2:0A:5F:5A:A4"


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


async def write_to_client(packet, characteristic, client):
    await client.write_gatt_char(characteristic, packet)
