import asyncio
from bleak import BleakClient

ADDRESS = "AD:D2:0A:5F:5A:A4"


async def main():
    async with BleakClient(ADDRESS) as client:

        print("Connected:", client.is_connected)

        services = await client.get_services()

        for service in services:
            print("\nSERVICE:", service.uuid)

            for char in service.characteristics:
                print(
                    "  CHAR:",
                    char.uuid,
                    "| properties:",
                    char.properties
                )

asyncio.run(main())