import time

import board
import neopixel

import random


PIXEL_DATA_PIN = board.NEOPIXEL

NUMBER_OF_TOTAL_LINKED_PIXELS = 10

ORDER = neopixel.GRB

pixels = neopixel.NeoPixel(
    PIXEL_DATA_PIN, NUMBER_OF_TOTAL_LINKED_PIXELS, brightness=0.2, auto_write=False, pixel_order=ORDER
)

blue = (0, 0, 255)
cyan = (0, 255, 255)
azure = (0, 128, 255)
midnight = (25, 25, 112)
royal_blue = (45, 90, 255)
medium_blue = (0,0,155)

color_options = (blue, cyan, azure, midnight, royal_blue, medium_blue)

def main():
    while True:
        # pixels.fill((0,0,0))
        # pixels.show()
        # time.sleep(1)

        for color in color_options:
            pixels.fill(random.choice(color_options))
            pixels.show()
            time.sleep(1)            
            pass

if __name__ == "__main__":
    main()