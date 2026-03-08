import json
import time
import requests


# -----------------------------------
# FETCH OFFICIAL OREF ALERT
# -----------------------------------
def fetch_homefront_alert():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "Referer": "https://www.oref.org.il/",
        "X-Requested-With": "XMLHttpRequest"
    }
    try:
        url = "https://www.oref.org.il/WarningMessages/alert/alerts.json"
        response = requests.get(url, headers=headers, timeout=5)

        if response.status_code != 200:
            return None

        if not response.content or len(response.content) < 5:
            return None

        # utf-8-sig handles the BOM character automatically
        content = response.content.decode("utf-8-sig").strip()
        return json.loads(content) if content else None

    except Exception as e:
        print(f"Network error: {e}")
        return None


def city_in_alert(alert, city_names):
    if not alert:
        return False

    cities = alert.get("data", [])
    for city_name in city_names:
        if city_name in cities:
            return True
    return False


def alert_has_title(alert, titles):
    if not alert:
        return False
    for title in titles:
        if alert.get("title") == title:
            return True
    return False


def listen_to_oref(cities_to_track, alert_in_city, search_for_titles, last_alert_tracker, time_between_alarms=30):
    alert = fetch_homefront_alert()

    if city_in_alert(alert, cities_to_track) and alert_has_title(alert, search_for_titles):
        current_time = time.time()
        if (current_time - last_alert_tracker[0]) > time_between_alarms:
            alert_in_city[0] = 1

            last_alert_tracker[0] = current_time