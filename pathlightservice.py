import time
from datetime import datetime
from datetime import timezone
import random

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

PIXELS_PER_RING = 12

def default():
    pixels.fill((0, 0, 0, 255))
    pixels.show()
    time.sleep(60)

def xmas_alternating():
    RED = (255, 0, 0, 0)
    GREEN = (0, 255, 0, 0)

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

def xmas_random():
    RED = (255, 0, 0, 0)
    GREEN = (0, 255, 0, 0)
    color_options = (RED, GREEN)

    pixels[0:11] = [random.choice(color_options)] * PIXELS_PER_RING
    pixels[12:23] = [random.choice(color_options)] * PIXELS_PER_RING
    pixels[24:35] = [random.choice(color_options)] * PIXELS_PER_RING
    pixels[36:47] = [random.choice(color_options)] * PIXELS_PER_RING
    pixels[48:59] = [random.choice(color_options)] * PIXELS_PER_RING
    pixels[60:71] = [random.choice(color_options)] * PIXELS_PER_RING
    pixels[72:83] = [random.choice(color_options)] * PIXELS_PER_RING

    pixels.show()
    time.sleep(random.uniform(0,2))

def newyears_random():
    blue = (0, 0, 255)
    cyan = (0, 255, 255)
    azure = (0, 128, 255)
    midnight = (25, 25, 112)
    royal_blue = (45, 90, 255)
    medium_blue = (0,0,155)

    color_options = (blue, cyan, azure, midnight, royal_blue, medium_blue)

    pixels[0:11] = [random.choice(color_options)] * PIXELS_PER_RING
    pixels[12:23] = [random.choice(color_options)] * PIXELS_PER_RING
    pixels[24:35] = [random.choice(color_options)] * PIXELS_PER_RING
    pixels[36:47] = [random.choice(color_options)] * PIXELS_PER_RING
    pixels[48:59] = [random.choice(color_options)] * PIXELS_PER_RING
    pixels[60:71] = [random.choice(color_options)] * PIXELS_PER_RING
    pixels[72:83] = [random.choice(color_options)] * PIXELS_PER_RING

    pixels.show()
    time.sleep(random.uniform(0,2))

def lights_on():
    newyears_random()

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
    print(sun_location_data["dawn"])

    while True:
        now = datetime.now(tz=timezone.utc)
        sun_location_data = sun(home_location.observer, date=now, tzinfo=timezone.utc)

        is_daylight = (now > sun_location_data["dawn"] and now < sun_location_data["sunset"])

        if is_daylight:
            lights_off()
        else:
            lights_on()

if __name__ == "__main__":
    main()