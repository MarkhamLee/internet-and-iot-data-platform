# Markham Lee (C) 2023 - 2024
# Finance, Productivity, IoT Dashboard
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# Python script for pulling data from a PMS5003 air quality sensor
# connected by USB, and then pushing the data to console.
# Influenced by R. Smith's script for the same sensor:
# https://github.com/rsmith-nl/ft232-pms5003/tree/main
import serial
import logging
import os
import struct
from time import sleep
from sys import stdout

logger = logging.getLogger('asana_etl')
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler(stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s - %(message)s')  # noqa: E501
handler.setFormatter(formatter)
logger.addHandler(handler)

# define sensor access/write codes
# based on R. F. Smith's deep dive into the Plantower Manual
# https://github.com/rsmith-nl/ft232-pms5003/blob/main/dust-monitor.py
PASSIVE_READ = b"\x42\x4d\xe2\x00\x00\x01\x71"
PASSIVE_MODE = b"\x42\x4d\xe1\x00\x00\x01\x70"
ACTIVE_MODE = b"\x42\x4d\xe1\x00\x01\x01\x71"
SLEEP = b"\x42\x4d\xe4\x00\x00\x01\x73"
WAKEUP = b"\x42\x4d\xe4\x00\x01\x01\x74"


USB = '/dev/ttyUSB0'
ser = serial.Serial(USB, baudrate=9600, stopbits=1, parity="N",  timeout=2)
ser.write(PASSIVE_MODE)  # puts device in passive mode
# ser.write(ACTIVE_MODE)


def get_air_data(interval: int):

    while True:

        ser.flushInput()
        ser.write(PASSIVE_READ)  # query device for data

        try:
            air_data = ser.read(32)

            if len(air_data) != 32:
                continue

            if not air_data.startswith(b"BM"):
                continue

            numbers = struct.unpack(">HHHHHHHHHHHHHHHH", air_data)

            pm1 = float(numbers[2])
            pm25 = float(numbers[3])
            pm10 = float(numbers[4])

            logger.info(f'PM1 levels are {pm1}')
            logger.info(f'PM2.5 levels are: {pm25}')
            logger.info(f'PM10 levels are: {pm10}')

            sleep(interval)

        except Exception as e:
            logger.info(f'Read error: {e}')
            sleep(interval)


def main():

    interval = int(os.environ['PLANTOWER_INTERVAL'])

    # start monitoring loop
    get_air_data(interval)


if __name__ == '__main__':
    main()
