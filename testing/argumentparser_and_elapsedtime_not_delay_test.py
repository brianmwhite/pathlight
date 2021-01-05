import time
from datetime import datetime
from datetime import timezone
import random

from astral import LocationInfo
from astral.sun import sun
from astral.sun import night

import argparse

parser = argparse.ArgumentParser(description='Control pathway lighting')
arg_override_group = parser.add_mutually_exclusive_group()
arg_override_group.add_argument("--on", dest="override_on", action="store_true", help="Turns the lights on, ignoring any on/off times")
arg_override_group.add_argument("--off", dest="override_off", action="store_true", help="Turns the lights off, ignoring any on/off times")
args = parser.parse_args()

def main():
    last_time_counter_on = time.monotonic()
    last_time_counter_off = time.monotonic()
    on_time_delay = 2.0
    off_time_delay = 5.0
    lights_on = False
    first_run = True

    print("started path light service...")

    home_location = LocationInfo('home', 'US', 'US/Eastern', 36.083660, -80.442180)
    print("now(utc): ", str(datetime.now(tz=timezone.utc)))

    sun_location_data = sun(home_location.observer, tzinfo=timezone.utc)
    print("dawn(utc): ", str(sun_location_data["dawn"]))
    print("sunset(utc): ", str(sun_location_data["sunset"]))


    while True:
        current_seconds_count = time.monotonic()

        if args.override_on:
            if first_run:
                print("...override lights on")
                lights_on = True
                first_run = False
        elif args.override_off:
            if first_run:
                print("...override lights off")
                lights_on = False
                first_run = False
        else:
            now = datetime.now(tz=timezone.utc)
            sun_location_data = sun(home_location.observer, date=now, tzinfo=timezone.utc)

            is_daylight = (now > sun_location_data["dawn"] and now < sun_location_data["sunset"])

            if is_daylight and (first_run or lights_on) and current_seconds_count - last_time_counter_off > off_time_delay:
                lights_on = False
                last_time_counter_off = current_seconds_count
                if first_run:
                    print("is daylight, lights turning off")
                    first_run = False
                else:
                    print("still day")
            elif not is_daylight and (first_run or lights_on) and current_seconds_count - last_time_counter_on > on_time_delay:
                lights_on = True
                last_time_counter_on = current_seconds_count
                if first_run:
                    print("is night, lights turning on")
                    first_run = False
                else:
                    print("still night")




if __name__ == "__main__":
    main()