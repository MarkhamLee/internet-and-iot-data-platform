# !/usr/bin/env python
# Markham Lee (C) 2023 - 2024
# Finance, Productivity, IoT Dashboard
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# Python script for pulling data from a PMS5003 air quality sensor
# connected by USB, and then pushing the data to console.
# Alt version with different approach to the calculations, docs are vague
# need to do more research into making sure I'm getting the right numbers.
import serial
import logging
from time import sleep
from sys import stdout

logger = logging.getLogger('Plantower S5003')
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler(stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s - %(message)s')  # noqa: E501
handler.setFormatter(formatter)
logger.addHandler(handler)

# define write
# based on R. F. Smith's deep dive into the Plantower Manual
# https://github.com/rsmith-nl/ft232-pms5003/blob/main/dust-monitor.py
PASSIVE_READ = b"\x42\x4d\xe2\x00\x00\x01\x71"
PASSIVE_MODE = b"\x42\x4d\xe1\x00\x00\x01\x70"
ACTIVE_MODE = b"\x42\x4d\xe1\x00\x01\x01\x71"
SLEEP = b"\x42\x4d\xe4\x00\x00\x01\x73"
WAKEUP = b"\x42\x4d\xe4\x00\x01\x01\x74"


USB = '/dev/ttyUSB0'
ser = serial.Serial(USB, baudrate=9600, stopbits=1, parity="N",  timeout=2)
# ser.write([66, 77, 225, 0, 0, 1, 112])  # puts device in passive mode
ser.write(PASSIVE_MODE)  # puts device in passive mode


def get_air_data(interval: int):

    while True:

        ser.flushInput()
        ser.write(PASSIVE_READ)

        try:
            s = ser.read(32)

            if len(s) != 32:
                continue

            if not s.startswith(b"BM"):
                continue

            pm1_hb_std = s[4]
            pm1_lb_std = s[5]
            pm1_std = float(pm1_hb_std * 256 + pm1_lb_std)
            logger.info(f'PM1 levels are {pm1_std}')

            pm25_hb_std = s[6]
            pm25_lb_std = s[7]
            pm25_std = float(pm25_hb_std * 256 + pm25_lb_std)

            logger.info(f'PM2.5 levels are: {pm25_std}')

            pm10_hb_std = s[8]
            pm10_lb_std = s[9]
            pm10_std = float(pm10_hb_std * 256 + pm10_lb_std)
            logger.info(f'PM10 levels are: {pm10_std}')

        except Exception as e:
            logger.info(f'Read error: {e}')

        sleep(interval)


def main():

    interval = 5

    # start monitoring loop
    get_air_data(interval)


if __name__ == '__main__':
    main()
