import os
import signal
import time
import random
import paho.mqtt.client as mqtt
import board
import neopixel

# systemd commands
#sudo systemctl start pathlight
#sudo systemctl stop pathlight
#sudo systemctl restart pathlight
#systemctl status pathlight
#journalctl -u pathlight -f

path_light_is_on = False
last_time_status_check_in = 0
status_checkin_delay = 60.0

MQTT_HOST = os.environ["MQTT_HOST"]
MQTT_PORT = int(os.environ["MQTT_PORT"])

MQTT_SETON_PATH = "home/outside/switches/pathlight/setOn"
MQTT_GETON_PATH = "home/outside/switches/pathlight/getOn"

ON_VALUE = "ON"
OFF_VALUE = "OFF"

LIGHT_PATTERN = "DEFAULT"

PIXEL_DATA_PIN = board.D18

NUMBER_OF_TOTAL_LINKED_PIXELS = 84

ORDER = neopixel.GRBW

pixels = neopixel.NeoPixel(
    PIXEL_DATA_PIN, NUMBER_OF_TOTAL_LINKED_PIXELS, brightness=1.0, auto_write=False, pixel_order=ORDER
)

PIXELS_PER_RING = 12


class exit_monitor_setup:
    exit_now_flag_raised = False

    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        self.exit_now_flag_raised = True


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("MQTT: Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("$SYS/#")
    client.subscribe(MQTT_SETON_PATH)


def on_disconnect(client, userdata, rc):
    print("MQTT: disconnecting reason " + str(rc))


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, message):
    global last_time_status_check_in

    if message.topic == MQTT_SETON_PATH:
        last_time_status_check_in = time.monotonic()

        if str(message.payload.decode("utf-8")) == ON_VALUE:
            lights_on(showPrint=True)
            client.publish(MQTT_GETON_PATH, ON_VALUE)
        elif str(message.payload.decode("utf-8")) == OFF_VALUE:
            lights_off(showPrint=True)
            client.publish(MQTT_GETON_PATH, OFF_VALUE)


def lights_on(showPrint = False):
    global path_light_is_on
    path_light_is_on = True
    light_pattern_delay = 60
    if showPrint:
        print("turning lights ON ....")

    if LIGHT_PATTERN == "DEFAULT":
        pixels.fill((0, 0, 0, 255))
        pixels.show()
    elif LIGHT_PATTERN == "XMAS":
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
        light_pattern_delay = random.uniform(0,2)
    elif LIGHT_PATTERN == "NEWYEARS":
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
        light_pattern_delay = random.uniform(0,2)
    elif LIGHT_PATTERN == "VALENTINES":
        red = (255, 0, 0, 0)
        white = (0, 0, 0, 255)
        pink = (255, 192, 203, 0)

        color_options = (red, white, pink)

        pixels[0:11] = [random.choice(color_options)] * PIXELS_PER_RING
        pixels[12:23] = [random.choice(color_options)] * PIXELS_PER_RING
        pixels[24:35] = [random.choice(color_options)] * PIXELS_PER_RING
        pixels[36:47] = [random.choice(color_options)] * PIXELS_PER_RING
        pixels[48:59] = [random.choice(color_options)] * PIXELS_PER_RING
        pixels[60:71] = [random.choice(color_options)] * PIXELS_PER_RING
        pixels[72:83] = [random.choice(color_options)] * PIXELS_PER_RING

        pixels.show()
        light_pattern_delay = random.uniform(0,2)
    return light_pattern_delay


def lights_off(showPrint=False):
    global path_light_is_on
    path_light_is_on = False
    if showPrint:
        print("turning lights OFF ....")

    pixels.fill((0, 0, 0, 0))
    pixels.show()


if __name__ == "__main__":
    exit_monitor = exit_monitor_setup()

    client = mqtt.Client()
	client.on_connect = on_connect
	client.on_disconnect = on_disconnect
	client.on_message = on_message

    client.connect(MQTT_HOST, MQTT_PORT, 60)
    client.loop_start()
    # see below, not sure if sleep is needed here, probably not
    time.sleep(0.001)

    print("started path light service...")
    last_time_status_check_in = time.monotonic()
    last_time_pattern_update = time.monotonic()

    while not exit_monitor.exit_now_flag_raised:
        # added time.sleep 1 ms after seeing 100% CPU usage
        # found this solution https://stackoverflow.com/a/41749754
        time.sleep(0.001)
        current_seconds_count = time.monotonic()
        pattern_delay = 0
        
        if path_light_is_on and (current_seconds_count - last_time_pattern_update > pattern_delay):
            pattern_delay = lights_on()
        
        if current_seconds_count - last_time_status_check_in > status_checkin_delay:
			last_time_status_check_in = current_seconds_count
			if path_light_is_on:
				client.publish(MQTT_GETON_PATH, ON_VALUE)
			else:
				client.publish(MQTT_GETON_PATH, OFF_VALUE)

	client.loop_stop()
	client.disconnect()
	pixels.deinit()
	print("pathlight service ended")