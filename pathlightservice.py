import time
from datetime import datetime
from datetime import timezone

from astral import LocationInfo
from astral.sun import sun
from astral.sun import night

import board
import neopixel


PIXEL_DATA_PIN = board.D18

NUMBER_OF_TOTAL_LINKED_PIXELS = 84

ORDER = neopixel.GRBW

pixels = neopixel.NeoPixel(
    PIXEL_DATA_PIN, NUMBER_OF_TOTAL_LINKED_PIXELS, brightness=1.0, auto_write=False, pixel_order=ORDER
)

RED = (255, 0, 0, 0)
GREEN = (0, 255, 0, 0)
PIXELS_PER_RING = 12

def lights_on():
    pixels[0:11] = [RED] * PIXELS_PER_RING
    pixels[24:35] = [RED] * PIXELS_PER_RING
    pixels[48:59] = [RED] * PIXELS_PER_RING
    pixels[72:83] = [RED] * PIXELS_PER_RING

    pixels[12:23] = [GREEN] * PIXELS_PER_RING
    pixels[36:47] = [GREEN] * PIXELS_PER_RING
    pixels[60:71] = [GREEN] * PIXELS_PER_RING

    pixels.show()
    time.sleep(1)   

    pixels[0:11] = [GREEN] * PIXELS_PER_RING
    pixels[24:35] = [GREEN] * PIXELS_PER_RING
    pixels[48:59] = [GREEN] * PIXELS_PER_RING
    pixels[72:83] = [GREEN] * PIXELS_PER_RING

    pixels[12:23] = [RED] * PIXELS_PER_RING
    pixels[36:47] = [RED] * PIXELS_PER_RING
    pixels[60:71] = [RED] * PIXELS_PER_RING

    pixels.show()
    time.sleep(1)

def lights_off():
    pixels.fill((0, 0, 0, 0))
    pixels.show()
    time.sleep(60)

def main():
    print("started path light service...")
    lights_off()
    
    home_location = LocationInfo('home', 'US', 'US/Eastern', 36.083660, -80.442180)
    print(datetime.now(tz=timezone.utc))
    sun_location_data = sun(home_location.observer, tzinfo=timezone.utc)
    print(sun_location_data["sunset"])
    print(sun_location_data["sunrise"])

    while True:
        now = datetime.now(tz=timezone.utc)
        sun_location_data = sun(home_location.observer, tzinfo=timezone.utc)

        sunrise = sun_location_data["sunrise"]
        sunset = sun_location_data["sunset"]

        is_daylight = (sunrise < now > sunset)

        if is_daylight:
            lights_off()
        else:
            lights_on()

if __name__ == "__main__":
    main()