from bleak import BleakClient
import threading
from screen_vibe_color import *
from oref_connection import *
from main_headers import *


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
    await set_white_temp(1, client)


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
        elif inp == "flash":
            await flash_effect(client)
        else:
            r, g, b = map(int, inp.split())
            await set_rgb(r, g, b, client)
        shared_var[0] = "default"
    except:
        print("Invalid input")
        shared_var[0] = "default"


async def process_alerts(client):
    if alert_in_city[0] == 1:
        alert_in_city[0] = 0
        await blink_colors(client)


def oref_handler(sample_oref_time):
    if (time.time() - sample_oref_time) > 2:
        # Run the blocking network call in a separate thread automatically
        listen_to_oref(cities_to_track, alert_in_city, search_for_titles, last_alert_tracker, time_between_alarms)
        return time.time()
    return sample_oref_time


def start_input_thread():
    input_thread = threading.Thread(target=blocking_input_task, args=(shared_var,), daemon=True)
    input_thread.start()


async def check_for_flash(client, hsv):
    if hsv[-1] > BRIGHTNESS_THRESHOLD:
        await flash_effect(client)


async def handle_hotkeys(client):
    set = False
    # --- Continuous Vibe Logic ---
    if vibe_mode_active[0]:
        t1 = time.time()
        target_rgb, hsv = await get_rgb_hsv(client)
        # await check_for_flash(client, hsv)
        # print(time.time() - t1)
        current_color[0], current_color[1], current_color[2] = smooth_color(
            target_rgb,
            (current_color[0], current_color[1], current_color[2]),
            factor=0.8
        )

        # 3. Update Light
        await set_rgb(*current_color, client)
        set = True

    # --- Reset Trigger (Ctrl+R) ---
    if reset_trigger[0]:
        vibe_mode_active[0] = False
        reset_trigger[0] = False
        print("Resetting lights to neutral...")
        await set_white_temp(neutral_white_level, client)  # Resets to mid-level white
    return set


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

                if not await handle_hotkeys(client):
                    await asyncio.sleep(0.3)

                inp = shared_var[0]
                if inp == 'exit':
                    raise Exception("Exiting")
                if inp != "default":
                    await process_input(inp, client)
                """
                NO NEED FOR SLEEP
                FRAME PROCESSING TAKES ~40MS
                """
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
