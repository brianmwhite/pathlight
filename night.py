import time
from datetime import datetime
from datetime import timezone

from astral import LocationInfo
from astral.sun import sun
from astral.sun import night

def main():   
    home_location = LocationInfo('home', 'US', 'US/Eastern', 36.083660, -80.442180)
    
    print((
        f"Information for {home_location.name}/{home_location.region}\n"
        f"Timezone: {home_location.timezone}\n"
        f"Latitude: {home_location.latitude:.02f}; Longitude: {home_location.longitude:.02f}\n"
    ))
    sun_location_data = sun(home_location.observer)
    print((
        f'Dawn:    {sun_location_data["dawn"]}\n'
        f'Sunrise: {sun_location_data["sunrise"]}\n'
        f'Noon:    {sun_location_data["noon"]}\n'
        f'Sunset:  {sun_location_data["sunset"]}\n'
        f'Dusk:    {sun_location_data["dusk"]}\n'
    ))

    print("Now")
    print(datetime.now(tz=timezone.utc))

    print("Night")
    print(night(home_location.observer, tzinfo=timezone.utc))

if __name__ == "__main__":
    main()