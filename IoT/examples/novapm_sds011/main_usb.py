# !/usr/bin/env python
# Markham Lee (C) 2023 - 2024
# Finance, Productivity, IoT Dashboard
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# Python script for pulling data from a Nova PM SDS011 air quality sensor
# connected by USB, and then pushing the data to console.
import serial
import logging
from time import sleep
from sys import stdout

logger = logging.getLogger('asana_etl')
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler(stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s - %(message)s')  # noqa: E501
handler.setFormatter(formatter)
logger.addHandler(handler)


def get_variables():

    pm2Bytes = 2
    pm10Bytes = 4
    # self.deviceID = 6

    return pm2Bytes, pm10Bytes


def connect_to_device():

    USB = '/dev/ttyUSB0'

    try:
        serial_con = serial.Serial(USB)
        logger.info(f'Connected to NovaPM SDS011 at: {USB}')
        return serial_con

    except Exception as e:
        logger.debug(f"Connection to device failed with error: {e}")


def get_air_quality(serial_con, pm2_bytes, pm10_bytes):

    try:

        logger.info('start reading data')

        message = serial_con.read(10)

        # outputs have to be scaled by 0.1 to properly capture the
        # sensor's precision as it returns integers that are actually
        # decimals I.e. 15 is really 1.5

        pm2 = round((parse_value(message, pm2_bytes) * 0.1), 4)
        pm10 = round((parse_value(message, pm10_bytes) * 0.1), 4)

        payload = {
            "pm2.5": pm2,
            "pm10": pm10
        }

        return payload

    except Exception as e:
        logger.debug(f'Failed to retrieve data with error: {e}')


def parse_value(message, start_byte, num_bytes=2,
                byte_order='little', scale=None):

    """Returns a number from a sequence of bytes."""
    value = message[start_byte: start_byte + num_bytes]
    value = int.from_bytes(value, byteorder=byte_order)
    value = value * scale if scale else value

    return value


def main():

    # get variables
    pm2_bytes, pm10_bytes = get_variables()

    # connect to device
    serial_con = connect_to_device()

    count = 0

    # get air quality data
    while count < 10:

        data = get_air_quality(serial_con, pm2_bytes, pm10_bytes)
        logger.info(f'Air quality data received: {data}')
        count += 1
        sleep(2)

    logger.info("Testing Complete")


if __name__ == '__main__':
    main()
