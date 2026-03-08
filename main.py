import time

from bleak import BleakClient
import asyncio
import threading
from screen_vibe_color import setup_vibe_hotkeys, get_screen_vibe_color, smooth_color
from light_commands import *
from oref_connection import *

CHARACTERISTIC = "0000a040-0000-1000-8000-00805f9b34fb"

alert_in_city = [0]
cities_to_track = ["רעננה"]
search_for_titles = ["בדקות הקרובות צפויות להתקבל התרעות באזורך"]
shared_var = ["default"]

# Shared triggers
vibe_mode_active = [False]
reset_trigger = [False]
current_color = [255, 255, 255] # Tracks the actual light state for smoothing

neutral_white_level = 1

time_between_alarms = 2.5 * 60  # 2.5 minutes
last_alert_tracker = [time.time() - time_between_alarms]


async def set_white_temp(level, client):
    packet = build_white_temp_packet(level)
    await write_to_client(packet, CHARACTERISTIC, client)


async def set_rgb(r, g, b, client):
    packet = build_rgb_packet(r, g, b)
    await write_to_client(packet, CHARACTERISTIC, client)


async def blink_colors(client, color1=(255, 0, 0), color2=(0, 0, 255), duration=15, delay=1):
    """
    Switch between two colors for a given duration.

    :param client: BleakClient already connected
    :param color1: tuple (r, g, b) first color
    :param color2: tuple (r, g, b) second color
    :param duration: total duration in seconds
    :param delay: seconds to wait between color switches
    """
    elapsed = 0
    while elapsed < duration:
        # switch to first color
        await set_rgb(*color1, client)
        await asyncio.sleep(delay)
        elapsed += delay

        # switch to second color
        await set_rgb(*color2, client)
        await asyncio.sleep(delay)
        elapsed += delay


def blocking_input_task(container):
    while True:
        container[0] = input("Update variable: \n")
        if container[0] == "exit":
            break


async def process_input(inp, client):
    try:
        if inp[0] == 'w':
            level = max(0, min(int(inp[-1]), 5))
            await set_white_temp(level, client)
        elif inp == "blink":
            await blink_colors(client)
        else:
            r, g, b = map(int, inp.split())
            await set_rgb(r, g, b, client)
        shared_var[0] = "default"
    except:
        print("Invalid input")


async def process_alerts(client):
    if alert_in_city[0] == 1:
        alert_in_city[0] = 0
        await blink_colors(client)


def oref_handler(sample_oref_time):
    if (time.time() - sample_oref_time) > 2:
        # Run the blocking network call in a separate thread automatically
        listen_to_oref(cities_to_track, alert_in_city, search_for_titles, last_alert_tracker, time_between_alarms)
        return time.time()
    print(sample_oref_time)
    return sample_oref_time


def start_input_thread():
    input_thread = threading.Thread(target=blocking_input_task, args=(shared_var,), daemon=True)
    input_thread.start()


async def handle_hotkeys(client):
    # --- Continuous Vibe Logic ---
    if vibe_mode_active[0]:
        # 1. Get the "goal" color (Fast)
        t1 = time.time()
        target_rgb = get_screen_vibe_color()
        print(time.time() - t1)
        # 2. Calculate the "next step" color (Smooth)
        # Using a factor of 0.2 makes it feel responsive but soft
        current_color[0], current_color[1], current_color[2] = smooth_color(
            target_rgb,
            (current_color[0], current_color[1], current_color[2]),
            factor=0.2
        )

        # 3. Update Light
        await set_rgb(*current_color, client)

    # --- Reset Trigger (Ctrl+R) ---
    if reset_trigger[0]:
        vibe_mode_active[0] = False
        reset_trigger[0] = False
        print("Resetting lights to neutral...")
        await set_white_temp(neutral_white_level, client)  # Resets to mid-level white


async def main():
    sample_oref_time = time.time()

    # Initialize both hotkeys
    setup_vibe_hotkeys(vibe_mode_active, reset_trigger)

    async with BleakClient(ADDRESS) as client:
        start_input_thread()
        try:
            while True:
                sample_oref_time = oref_handler(sample_oref_time)
                await process_alerts(client)

                await handle_hotkeys(client)

                inp = shared_var[0]
                if inp == 'exit':
                    raise Exception("Exiting")
                if inp != "default":
                    await process_input(inp, client)
                await asyncio.sleep(0.03)

        except Exception as e:
            print(f"Error: {e}")
            print("Exiting")


if __name__ == "__main__":
    asyncio.run(main())
