import time

ADDRESS = "AD:D2:0A:5F:5A:A4"

alert_in_city = [0]
cities_to_track = ['רעננה']
search_for_titles = ["בדקות הקרובות צפויות להתקבל התרעות באזורך", "חדירת כלי טיס עוין"]
shared_var = ["default"]

# Shared triggers
vibe_mode_active = [False]
reset_trigger = [False]
current_color = [255, 255, 255] # Tracks the actual light state for smoothing

neutral_white_level = 1

time_between_alarms = 2.5 * 60  # 2.5 minutes
last_alert_tracker = [time.time() - time_between_alarms]