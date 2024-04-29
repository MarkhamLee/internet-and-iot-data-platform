# Markham Lee (C) 2023
# Productivity, Weather, Personal, et al dashboard:
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# Slight remix of script I wrote for monitoring PC case temps:
# https://github.com/MarkhamLee/HardwareMonitoring
# the script gathers data from a DHT22 temperature sensors and a
# a Nova PM SDS011 air quality sensor and then publishes them to a
# MQTT topic.
# Note: the Adafruit library is specific to a Raspberry Pi, using another
# type of SBC may or may not work
import adafruit_dht
import board
import gc
import logging
from time import sleep
from sys import stdout

logger = logging.getLogger('dht22_logger')
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler(stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s - %(message)s')  # noqa: E501
handler.setFormatter(formatter)
logger.addHandler(handler)


def get_temps(total_count: int, sleep_interval: int):

    # The use pulseio parameter is suggested parameter for a Raspberry Pi
    # may not need to use it with other types of SBCs

    # The sensor fails to read about 1/3 of the time but that can be managed
    # via exception handling and the next attempt is nearly always successful.
    # This appears to be an issue of the sensor + the driver, as this rarely
    # happens on a Raspberry Pi Pico Microcontroller (in my experience). Still,
    # given that you you can immediately retry reading the data it doesn't
    # really cause any issues as far as the sensor providing steady/consistent
    # data.

    temp_device = adafruit_dht.DHT22(board.D4, use_pulseio=False)
    logger.info('Connected to DHT22')

    loop_count = 0

    while loop_count < total_count:

        # get temperature and humidity data
        # with the current library, the device fails to read about 1/3
        # of the time, so you will get "Device runtime errors" - this
        # is as expected.
        try:
            temp = temp_device.temperature
            humidity = temp_device.humidity

        except RuntimeError as error:  # noqa: F841
            logger.debug(f'Device runtime error {error}')
            continue

        except Exception as error:
            logger.debug(f'Device read error {error}')
            continue

        if temp is not None:

            payload = {
                    "t": temp,
                    "h": humidity
                }

            loop_count += 1

            logger.info(f'Data received: {payload}')

            del temp, humidity, payload
            gc.collect()
            sleep(sleep_interval)


def main():

    get_temps(10, 2)


if __name__ == '__main__':
    main()
