import mss
import numpy as np
import keyboard


set_vibe = 'ctrl+p'
reset_vibe = 'ctrl+q'


def setup_vibe_hotkeys(vibe_container, reset_container):
    """
    Sets up background listeners for set_vibe and reset_vibe
    """
    # Trigger Screen Vibe
    keyboard.add_hotkey(set_vibe, lambda: vibe_container.__setitem__(0, True))

    # Trigger Reset
    keyboard.add_hotkey(reset_vibe, lambda: reset_container.__setitem__(0, True))

    print(f"Hotkeys active: [{set_vibe}] for Vibe, [{reset_vibe}] for Reset.")


def get_screen_vibe_color():
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        # We only grab a small portion or resize, but even simpler:
        # slicing the numpy array with a step [::10, ::10] takes every 10th pixel.
        sct_img = sct.grab(monitor)
        img_array = np.array(sct_img)

        # Optimization: Use every 20th pixel. 20x20 = 400x fewer calculations.
        # Format is [height, width, channels]
        sampled_data = img_array[::20, ::20, :3]

        avg_bgr = np.mean(sampled_data, axis=(0, 1))
        return int(avg_bgr[2]), int(avg_bgr[1]), int(avg_bgr[0])


def smooth_color(target_rgb, current_rgb, factor=0.1):
    """
    Moves current_rgb closer to target_rgb by a small percentage (factor).
    factor 1.0 = instant snap, factor 0.01 = very slow transition.
    """
    r = current_rgb[0] + (target_rgb[0] - current_rgb[0]) * factor
    g = current_rgb[1] + (target_rgb[1] - current_rgb[1]) * factor
    b = current_rgb[2] + (target_rgb[2] - current_rgb[2]) * factor
    return int(r), int(g), int(b)