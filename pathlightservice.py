import configparser
import pickle
import random
import signal
import time
from datetime import date
from itertools import cycle

import board
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
PIXEL_DATA_PIN = board.pin(config_settings.getint('PIXEL_DATA_PIN'))
PIXELS_PER_UNIT = config_settings.getint('PIXELS_PER_LIGHT')
NUMBER_OF_LIGHTS = config_settings.getint('NUMBER_OF_LIGHTS')
NUMBER_OF_TOTAL_LINKED_PIXELS = PIXELS_PER_UNIT * NUMBER_OF_LIGHTS


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
        TARGET_COLOR_AS_HEX = str(message.payload.decode("utf-8"))
        set_light_color(TARGET_COLOR_AS_HEX)


def set_light_color(target_color_as_hex):
    global DEVICE_STATE
    DEVICE_STATE['light_color'] = target_color_as_hex
    client.publish(MQTT_GETRGBW_PATH, target_color_as_hex)
    print(f"color={target_color_as_hex}")

    if DEVICE_STATE['light_is_on'] is True:
        pixels.fill(tuple(bytes.fromhex(DEVICE_STATE['light_color'])))
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


def convert_hex_to_tuple(hex_string):
    return tuple(bytes.fromhex(hex_string))


def get_random_color_from_set(color_set):
    hex_color = random.choice(color_set)
    return convert_hex_to_tuple(hex_color)


def send_colors_to_neopixels(lights):
    if not lights:
        pixels.fill(NEOPIXEL_OFF_COLOR)
    elif len(lights) == 1:
        pixels.fill(lights[0])
    else:
        FIRST_PIXEL_IN_LIGHT = 0
        LAST_PIXEL_IN_LIGHT = PIXELS_PER_UNIT

        for x in range(NUMBER_OF_LIGHTS):
            pixels[FIRST_PIXEL_IN_LIGHT:PIXELS_PER_UNIT] = [lights[x]] * PIXELS_PER_UNIT
            FIRST_PIXEL_IN_LIGHT += PIXELS_PER_UNIT
            LAST_PIXEL_IN_LIGHT += PIXELS_PER_UNIT

    pixels.show()


def get_light_colors():
    color_pattern = get_pattern_by_date(date.today())
    lights = []

    if color_pattern and color_pattern[0] == "SOLID":
        color_cycle_loop = cycle(color_pattern[1])
        for _ in range(NUMBER_OF_LIGHTS):
            lights.append(convert_hex_to_tuple(next(color_cycle_loop)))
    else:
        color = convert_hex_to_tuple(DEVICE_STATE['light_color'])
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

    pattern_delay = 0

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
