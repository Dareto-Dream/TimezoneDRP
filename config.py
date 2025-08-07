import os
import time
import asyncio
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from pypresence import AioPresence
from dotenv import load_dotenv

load_dotenv(override=True)

def run(stop_event=None):
    from dotenv import load_dotenv
    load_dotenv(override=True)
    asyncio.run(presence_loop(stop_event=stop_event))

async def presence_loop(stop_event=None):
    print("ENV:", {
        "TIMEZONE_NAME": os.getenv("TIMEZONE_NAME"),
        "TIMEZONE_LABEL": os.getenv("TIMEZONE_LABEL"),
        "TIMEZONE_OFFSET": os.getenv("TIMEZONE_OFFSET"),
        "TIMEZONE_CITY": os.getenv("TIMEZONE_CITY"),
        "TIMEZONE_ABBREV": os.getenv("TIMEZONE_ABBREV"),
        "LABEL_MODE": os.getenv("LABEL_MODE"),
    })


    print("[DRP] Starting async DRP...")
    client_id = os.getenv("DISCORD_CLIENT_ID", "1402709604588322836")
    RPC = AioPresence(client_id)

    # Wait for Discord to be ready
    while True:
        try:
            await RPC.connect()
            print("[DRP] Connected.")
            break
        except Exception:
            print("[DRP] Discord not ready, retrying in 3s...")
            await asyncio.sleep(3)

    # Load all relevant config
    tz_name      = os.getenv("TIMEZONE_NAME", "Asia/Tashkent")
    tz_label     = os.getenv("TIMEZONE_LABEL", "UZT (UTC+5)")
    tz_offset    = float(os.getenv("TIMEZONE_OFFSET", "5"))
    tz_city      = os.getenv("TIMEZONE_CITY", "Tashkent")
    tz_abbrev    = os.getenv("TIMEZONE_ABBREV", "UZT")
    image_mode   = os.getenv("IMAGE_MODE", "auto").lower()
    label_mode   = os.getenv("LABEL_MODE", "abbreviation").lower()

    tz = ZoneInfo(tz_name)

    def get_midnight():
        now = datetime.now(tz)
        return int(now.replace(hour=0, minute=0, second=0, microsecond=0).timestamp())
    start_timestamp = get_midnight()

    while True:
        now = datetime.now(tz)
        hour = now.hour
        time_str = now.strftime("%a %I:%M %p")

        # Determine label style
        if label_mode == "city/region":
            state_str = tz_city
        else:
            state_str = tz_label

        # Image mode logic
        if image_mode == "day":
            large_image, large_text = "clock_day", "Daytime"
            small_image, small_text = "clock_night", "Nighttime"
        elif image_mode == "night":
            large_image, large_text = "clock_night", "Nighttime"
            small_image, small_text = "clock_day", "Daytime"
        else:  # auto
            if 6 <= hour < 18:
                large_image, large_text = "clock_day", "Daytime"
                small_image, small_text = "clock_night", "Nighttime"
            else:
                large_image, large_text = "clock_night", "Nighttime"
                small_image, small_text = "clock_day", "Daytime"

        await RPC.update(
            state=state_str,
            details=time_str,
            start=start_timestamp,
            large_image=large_image,
            large_text=large_text,
            small_image=small_image,
            small_text=small_text
        )

        for _ in range(60):
            if stop_event and stop_event.is_set():
                print("[DRP] Stop signal received, exiting presence loop.")
                return
            await asyncio.sleep(1)


# Optional: run directly for dev
if __name__ == "__main__":
    run()