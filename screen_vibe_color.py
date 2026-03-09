import mss
import numpy as np
import keyboard
import colorsys
from light_commands import *
import asyncio


set_vibe = 'ctrl+p'
reset_vibe = 'ctrl+q'

# ===== vibe tuning =====
BRIGHTNESS_THRESHOLD = 0.4
SATURATION_BOOST = 1.5
DARK_BASE = 0.2
FLASH_DELTA_THRESHOLD = 0.4
dim_factor = 0.25


class screen:
    def __init__(self):
        self.avg_bgr = None
        self.HSV = None
        self.set_avg_bgr()
        h, s, v = self.calc_HSV()
        self.set_HSV(h, s, v)

    def set_avg_bgr(self):
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            sct_img = sct.grab(monitor)
            img_array = np.array(sct_img)

            # Sample fewer pixels for speed
            sampled_data = img_array[::20, ::20, :3]

            # Average BGR
            avg_bgr = np.mean(sampled_data, axis=(0, 1))
        self.avg_bgr = avg_bgr

    def calc_HSV(self):
        # Convert to RGB
        r = self.avg_bgr[2] / 255.0
        g = self.avg_bgr[1] / 255.0
        b = self.avg_bgr[0] / 255.0

        # RGB -> HSV
        h, s, v = colorsys.rgb_to_hsv(r, g, b)
        return h, s, v

    def set_HSV(self, h, s, v):
        self.HSV = h, s, v

    def get_rgb(self):
        bgr = self.avg_bgr
        return bgr[2], bgr[1], bgr[0]

    def get_hsv(self):
        return self.HSV

    def __str__(self):
        bgr_s = str(self.avg_bgr)
        hsv_s = str(self.HSV)
        return "BGR: " + bgr_s + "HSV: " + hsv_s


screen_state = screen()


async def flash_effect(client):
    await set_rgb(255, 0, 0, client)  # red warning
    await asyncio.sleep(0.2)

    # explosion
    await set_white_temp(1, client)
    await asyncio.sleep(1.5)
    await set_brightness_value(128, client)
    await asyncio.sleep(0.3)
    await set_brightness_value(64, client)
    await asyncio.sleep(0.3)
    await set_brightness_value(10, client)


def setup_vibe_hotkeys(vibe_container, reset_container):
    """
    Sets up background listeners for set_vibe and reset_vibe
    """
    keyboard.add_hotkey(set_vibe, lambda: vibe_container.__setitem__(0, True))
    keyboard.add_hotkey(reset_vibe, lambda: reset_container.__setitem__(0, True))

    print(f"Hotkeys active: [{set_vibe}] for Vibe, [{reset_vibe}] for Reset.")


async def check_for_flash(v, previous_v, client):
    delta_v = v - previous_v
    print(delta_v, v, previous_v)
    shown_v = v
    # ----- vibe logic -----
    # Bright scene boost (explosions / flashes)
    if delta_v > FLASH_DELTA_THRESHOLD:
        await flash_effect(client)

    # Dark cinematic baseline
    else:
        show_v = v * dim_factor  # dim everything by half
        shown_v = max(v, DARK_BASE)
    return shown_v


async def get_screen_vibe_color(client):
    screen_state.set_avg_bgr()
    h, s, v = screen_state.calc_HSV()
    previous_v = screen_state.get_hsv()[-1]
    shown_v = await check_for_flash(v, previous_v, client)
    # HSV -> RGB
    r, g, b = colorsys.hsv_to_rgb(h, s, shown_v)
    print(v, previous_v)
    screen_state.set_HSV(h, s, v)
    return int(r * 255), int(g * 255), int(b * 255), h, s, v


def smooth_color(target_rgb, current_rgb, factor=1):
    """
    Moves current_rgb closer to target_rgb by a small percentage (factor).
    factor 1.0 = instant snap, factor 0.01 = very slow transition.
    """
    r = current_rgb[0] + (target_rgb[0] - current_rgb[0]) * factor
    g = current_rgb[1] + (target_rgb[1] - current_rgb[1]) * factor
    b = current_rgb[2] + (target_rgb[2] - current_rgb[2]) * factor
    return int(r), int(g), int(b)


async def get_rgb_hsv(client):
    RGB_HSV = await get_screen_vibe_color(client)
    target_rgb = RGB_HSV[0:3]
    hsv = RGB_HSV[3:]
    return target_rgb, hsv
