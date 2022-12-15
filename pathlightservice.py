import configparser
import pickle
import random
import signal
import time
from datetime import date
from itertools import cycle

import neopixel
import paho.mqtt.client as mqtt

import pathlightconfig

# install commands
# sudo pip3 install simple_term_menu
# sudo pip3 install paho-mqtt
# git clone https://github.com/brianmwhite/pathlight.git
# sudo cp pathlight.service /etc/systemd/system/
# sudo systemctl enable pathlight

# ./deploy_local.sh
# ./svcmenu.py

# sudo systemctl start pathlight
# sudo systemctl stop pathlight
# sudo systemctl restart pathlight

# systemctl status pathlight
# journalctl -u pathlight -f

# sudo systemctl disable pathlight
# sudo cp pathlight.service /etc/systemd/system/
# sudo systemctl enable pathlight

# git commands to ignore changes specific file
# git update-index config.ini
# git update-index --skip-worktree config.ini
# git update-index --no-skip-worktree config.ini
# git ls-files -v|grep '^S'

# stop auto time sync:
# sudo systemctl stop systemd-timesyncd
# change date/time:
# sudo date --s="15 DEC 2020 12:49:00"
# start auto time sync:
# sudo systemctl start systemd-timesyncd
# check the date:
# date

config = configparser.ConfigParser()
config.read('/home/pi/pathlight/config.ini')

config_settings = config['SETTINGS']
config_pattern_section = config['PATTERNS']
color_pattern_by_date = pathlightconfig.get_color_pattern_config(config_pattern_section)

MQTT_HOST = config_settings.get('MQTT_HOST')
MQTT_PORT = config_settings.getint('MQTT_PORT')

MQTT_SETON_PATH = config_settings.get("MQTT_SETON_PATH")
MQTT_GETON_PATH = config_settings.get("MQTT_GETON_PATH")

MQTT_SETRGBW_PATH = config_settings.get("MQTT_SETRGBW_PATH")
MQTT_GETRGBW_PATH = config_settings.get("MQTT_GETRGBW_PATH")

MQTT_SETBRIGHTNESS_PATH = config_settings.get("MQTT_SETBRIGHTNESS_PATH")
MQTT_GETBRIGHTNESS_PATH = config_settings.get("MQTT_GETBRIGHTNESS_PATH")

MQTT_GETONLINE_PATH = config_settings.get("MQTT_GETONLINE_PATH")
MQTT_ONLINEVALUE = config_settings.get("MQTT_ONLINEVALUE")
MQTT_OFFLINEVALUE = config_settings.get("MQTT_OFFLINEVALUE")

MQTT_ON_VALUE = config_settings.get("MQTT_ON_VALUE")
MQTT_OFF_VALUE = config_settings.get("MQTT_OFF_VALUE")

PICKLE_FILE_LOCATION = config_settings.get("PICKLE_FILE_LOCATION")

DEFAULT_COLOR = config_settings.get("DEFAULT_COLOR")
DEVICE_STATE = {'light_is_on': False, 'light_color': DEFAULT_COLOR}

STATUS_CHECKIN_DELAY = config_settings.getfloat("STATUS_CHECKIN_DELAY")
last_time_status_check_in = 0.0

# neopixel setup
PIXEL_DATA_PIN = pathlightconfig.lookup_pin(config_settings.getint('PIXEL_DATA_PIN'))

PIXELS_PER_UNIT = config_settings.getint('PIXELS_PER_LIGHT')
print(f"PIXELS_PER_UNIT={PIXELS_PER_UNIT}")

NUMBER_OF_LIGHTS = config_settings.getint('NUMBER_OF_LIGHTS')
print(f"NUMBER_OF_LIGHTS={NUMBER_OF_LIGHTS}")

NUMBER_OF_TOTAL_LINKED_PIXELS = PIXELS_PER_UNIT * NUMBER_OF_LIGHTS
print(f"NUMBER_OF_TOTAL_LINKED_PIXELS={NUMBER_OF_TOTAL_LINKED_PIXELS}")


MAX_NEOPIXEL_BRIGHTNESS = config_settings.getfloat("MAX_NEOPIXEL_BRIGHTNESS")

ORDER = neopixel.GRBW

pixels = neopixel.NeoPixel(
    PIXEL_DATA_PIN,
    NUMBER_OF_TOTAL_LINKED_PIXELS,
    brightness=MAX_NEOPIXEL_BRIGHTNESS,
    auto_write=False,
    pixel_order=ORDER
)

NEOPIXEL_OFF_COLOR = (0, 0, 0, 0)


class exit_monitor_setup:
    exit_now_flag_raised = False

    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        self.exit_now_flag_raised = True


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("MQTT: Connected with result code " + str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("$SYS/#")
    client.subscribe(MQTT_SETON_PATH)
    client.subscribe(MQTT_SETRGBW_PATH)


# The callback for when a DISCONNECT message is received from the server.
def on_disconnect(client, userdata, rc):
    print("MQTT: disconnecting reason " + str(rc))


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, message):
    global last_time_status_check_in

    if message.topic == MQTT_SETON_PATH:
        last_time_status_check_in = time.monotonic()

        if str(message.payload.decode("utf-8")) == MQTT_ON_VALUE:
            turn_on_lights()
            client.publish(MQTT_GETON_PATH, MQTT_ON_VALUE)
        elif str(message.payload.decode("utf-8")) == MQTT_OFF_VALUE:
            turn_off_lights()
            client.publish(MQTT_GETON_PATH, MQTT_OFF_VALUE)
    elif message.topic == MQTT_SETRGBW_PATH:
        target_color_as_rgbw_string = str(message.payload.decode("utf-8"))
        set_light_color(target_color_as_rgbw_string)
    elif message.topic == MQTT_SETBRIGHTNESS_PATH:
        brightness_value_as_string = str(message.payload.decode("utf-8"))
        set_brightness(int(brightness_value_as_string))


def Convert_RGBW_String_To_Tuple(input_string: str):
    return tuple(int(item) if item.isdigit()
                 else item for item in input_string.split(','))


def Convert_Hex_To_RGBW_Tuple(hex_string: str):
    return tuple(bytes.fromhex(hex_string))


# def Convert_RGBW_Tuple_To_String(input_tuple: tuple):
#     return ','.join(str(item) for item in input_tuple)


def Convert_RGB_Tuple_To_Hex(input_tuple: tuple):
    return '%02X%02X%02X%02X' % input_tuple


def Convert_RGBW_String_To_Hex(input_string: str):
    t = Convert_RGBW_String_To_Tuple(input_string)
    return Convert_RGB_Tuple_To_Hex(t)


def set_brightness(brightness_value: int):
    pixels.brightness = (255 / brightness_value)
    pixels.show()
    client.publish(MQTT_GETBRIGHTNESS_PATH, brightness_value)


def set_light_color(target_color_as_rgbw_string):
    global DEVICE_STATE

    target_color_as_hex = Convert_RGBW_String_To_Hex(target_color_as_rgbw_string)
    DEVICE_STATE['light_color'] = target_color_as_hex

    client.publish(MQTT_GETRGBW_PATH, target_color_as_rgbw_string)
    print(f"color={target_color_as_hex}")

    rgbw_tuple = Convert_RGBW_String_To_Tuple(target_color_as_rgbw_string)

    if DEVICE_STATE['light_is_on'] is True:
        pixels.fill(rgbw_tuple)
        pixels.show()


def save_light_state_to_pickle():
    try:
        with open(PICKLE_FILE_LOCATION, 'wb') as datafile:
            pickle.dump(DEVICE_STATE, datafile)
            print(
                f"saved light state={DEVICE_STATE['light_is_on']}")
    except pickle.UnpicklingError as e:
        print(e)
        pass
    except (AttributeError, EOFError, ImportError, IndexError) as e:
        print(e)
        pass
    except Exception as e:
        print(e)
        pass


def turn_off_lights(change_state=True):
    global DEVICE_STATE
    DEVICE_STATE['light_is_on'] = False

    if change_state:
        print("turning lights OFF ....")
        save_light_state_to_pickle()

    send_colors_to_neopixels([NEOPIXEL_OFF_COLOR])


def get_pattern_by_date(date_to_check):
    date_key = date_to_check.strftime("%m/%d")
    return color_pattern_by_date.get(date_key)


def get_random_color_from_set(color_set):
    hex_color = random.choice(color_set)
    return Convert_Hex_To_RGBW_Tuple(hex_color)


def send_colors_to_neopixels(lights):
    if not lights:
        pixels.fill(NEOPIXEL_OFF_COLOR)
    elif len(lights) == 1:
        pixels.fill(lights[0])
    else:
        FIRST_PIXEL_IN_LIGHT = 0
        LAST_PIXEL_IN_LIGHT = PIXELS_PER_UNIT

        for x in range(NUMBER_OF_LIGHTS):
            pixels[FIRST_PIXEL_IN_LIGHT:LAST_PIXEL_IN_LIGHT] = ([lights[x]]
                                                                * PIXELS_PER_UNIT)

            FIRST_PIXEL_IN_LIGHT += PIXELS_PER_UNIT
            LAST_PIXEL_IN_LIGHT += PIXELS_PER_UNIT

    pixels.show()


def get_light_colors():
    color_pattern = get_pattern_by_date(date.today())
    lights = []

    if color_pattern and color_pattern[0] == "SOLID":
        color_cycle_loop = cycle(color_pattern[1])
        for _ in range(NUMBER_OF_LIGHTS):
            lights.append(Convert_Hex_To_RGBW_Tuple(next(color_cycle_loop)))
    else:
        color = Convert_Hex_To_RGBW_Tuple(DEVICE_STATE['light_color'])
        lights = [color]

    return lights


def turn_on_lights():
    global DEVICE_STATE
    DEVICE_STATE['light_is_on'] = True

    light_colors = get_light_colors()

    print("turning lights ON ....")
    print(f"color={DEVICE_STATE['light_color']}")

    save_light_state_to_pickle()
    send_colors_to_neopixels(light_colors)


if __name__ == '__main__':
    exit_monitor = exit_monitor_setup()

    try:
        with open(PICKLE_FILE_LOCATION, 'rb') as datafile:
            DEVICE_STATE = pickle.load(datafile)
            print(f"loaded light state={DEVICE_STATE['light_is_on']}")
    except (FileNotFoundError, pickle.UnpicklingError):
        print("failed to load light state, default=OFF")
        DEVICE_STATE['light_is_on'] = False
        pass

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message

    client.connect(MQTT_HOST, MQTT_PORT, 60)
    client.loop_start()
    # see below, not sure if sleep is needed here, probably not
    time.sleep(0.001)

    print("started light service...")
    last_time_status_check_in = time.monotonic()
    last_time_pattern_update = time.monotonic()

    if DEVICE_STATE['light_is_on']:
        turn_on_lights()
    else:
        turn_off_lights()

    while not exit_monitor.exit_now_flag_raised:
        # added time.sleep 1 ms after seeing 100% CPU usage
        # found this solution https://stackoverflow.com/a/41749754
        time.sleep(0.001)
        current_seconds_count = time.monotonic()

        if current_seconds_count - last_time_status_check_in > STATUS_CHECKIN_DELAY:
            last_time_status_check_in = current_seconds_count

            client.publish(MQTT_GETONLINE_PATH, MQTT_ONLINEVALUE)

    client.loop_stop()
    client.disconnect()
    pixels.deinit()
    print("light service ended")
