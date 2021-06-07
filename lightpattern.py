from enum import Enum
import random
from datetime import time
from itertools import cycle
# from abc import ABC, abstractmethod


class pattern_types(Enum):
    NO_PATTERN = 1
    SOLID_PATTERN = 2
    RANDOM_BLINK = 3
    COLOR_CYCLE = 4


class light_state:
    current_color = (0, 0, 0, 0)
    next_updated_time = 0
    cycle_position = 0
    cycle_of_colors = []


def convert_hex_to_tuple(hex_string):
    return tuple(bytes.fromhex(hex_string))


def get_random_color_from_set(color_set):
    hex_color = random.choice(color_set)
    return convert_hex_to_tuple(hex_color)


class lightpattern:
    def __init__(self, number_of_lights):
        default_color = (0, 0, 0, 255)

        self.light_count = number_of_lights

        self.color_set = [default_color]
        self.pattern = pattern_types.NO_PATTERN

        self.is_blinky = False
        self.blink_delay_seconds_min = 1
        self.blink_delay_seconds_max = 5

        self.lights = list[light_state]
        for x in range(number_of_lights):
            self.lights.append(light_state())

    def set_pattern(self, pattern: pattern_types):
        self.pattern = pattern

    def set_colors(self, colors_set):
        self.color_set = colors_set

    def set_blinky_on(self, blink_delay_seconds_min, blink_delay_seconds_max):
        self.is_blinky = True
        self.blink_delay_seconds_min = blink_delay_seconds_min
        self.blink_delay_seconds_max = blink_delay_seconds_max

    def set_blinky_off(self):
        self.is_blinky = False

    def start(self):
        if self.pattern == pattern_types.NO_PATTERN:
            print("no pattern, remote controlled")
        elif self.pattern == pattern_types.SOLID_PATTERN:
            print("start solid pattern")
            color_cycle_loop = cycle(self.color_set)
            for light in self.lights:
                light.current_color = convert_hex_to_tuple(
                    next(color_cycle_loop))
        elif self.pattern == pattern_types.COLOR_CYCLE:
            print("start color cycle")
            color_position_cycle_loop = cycle(range(0, len(self.color_set)))
            for light in self.lights:
                light.cycle_position = next(color_position_cycle_loop)
                light.current_color = self.color_set[light.cycle_position]
        elif self.pattern == pattern_types.RANDOM_BLINK:
            print("start random blink")
            self.next_cycle()

    def next_cycle(self):
        change_lights = False
        if self.is_blinky:
            for light in self.lights:
                now = time.monotonic()
                if now >= light.next_updated_time:
                    change_lights = True
                    if self.pattern == pattern_types.RANDOM_BLINK:
                        light.current_color = get_random_color_from_set(
                            self.color_set)
                        light.next_updated_time = now + \
                            random.uniform(
                                self.blink_delay_seconds_min, self.blink_delay_seconds_max)
                    elif self.pattern == pattern_types.COLOR_CYCLE:
                        light.cycle_position += 1
                        if (light.cycle_position > len(self.color_set)):
                            light.cycle_position = 0
                        light.current_color = self.color_set[light.cycle_position]
                        light.next_updated_time = now + \
                            random.uniform(
                                self.blink_delay_seconds_min, self.blink_delay_seconds_max)
        return change_lights
