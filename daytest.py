import time
from datetime import datetime, timezone, timedelta

from astral import LocationInfo
from astral.sun import sun
from astral.sun import night

def main():  
    home_location = LocationInfo('home', 'US', 'US/Eastern', 36.083660, -80.442180)
    now = datetime.now(tz=timezone.utc)    
    print((f'Now:    {now}'))
    sun_location_data = sun(home_location.observer, tzinfo=timezone.utc)
    print((f'Sunset:    {sun_location_data["sunset"]}'))
    print((f'Sunrise:    {sun_location_data["sunrise"]}'))
    testTime = now

    while True:
        testTime = testTime + timedelta(minutes=60)
        sun_location_data = sun(home_location.observer, date=testTime, tzinfo=timezone.utc)

        sunrise = sun_location_data["sunrise"]
        sunset = sun_location_data["sunset"]

        is_daylight = (testTime > sunrise and testTime < sunset)
        print((f'Test Time:    {testTime} = {is_daylight}'))
        time.sleep(1)

if __name__ == "__main__":
    main()