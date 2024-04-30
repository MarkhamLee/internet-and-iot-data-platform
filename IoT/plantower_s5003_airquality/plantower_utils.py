# Markham Lee (C) 2023 - 2024
# Finance, Productivity, IoT Dashboard
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# Utility script for pulling data from a PMS5003 air quality sensor
# Influenced by R. Smith's script for the same sensor:
# https://github.com/rsmith-nl/ft232-pms5003/tree/main
import os
import serial
import struct
import sys

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from iot_libraries.logging_util import logger  # noqa: E402
from iot_libraries.communications_utilities\
    import IoTCommunications  # noqa: E402

comms = IoTCommunications()


class PlantowerS5003Utils():

    def __init__(self):

        self.logger = logger

        self.load_variables()
        self.connect_to_sensor()

    def load_variables(self):

        self.com_utilities = IoTCommunications()

        # define sensor access/write codes
        # based on R. F. Smith's deep dive into the Plantower Manual
        # https://github.com/rsmith-nl/ft232-pms5003/blob/main/dust-monitor.py
        self.PASSIVE_READ = b"\x42\x4d\xe2\x00\x00\x01\x71"
        self.PASSIVE_MODE = b"\x42\x4d\xe1\x00\x00\x01\x70"
        self.ACTIVE_MODE = b"\x42\x4d\xe1\x00\x01\x01\x71"
        self.SLEEP = b"\x42\x4d\xe4\x00\x00\x01\x73"
        self.WAKEUP = b"\x42\x4d\xe4\x00\x01\x01\x74"

        self.logger.info('Key variables/write instructions loaded')

    def connect_to_sensor(self):

        USB = os.environ['USB_ADDRESS']

        try:
            self.plantower_s5003 = serial.Serial(USB,
                                                 baudrate=9600,
                                                 stopbits=1,
                                                 parity="N",
                                                 timeout=2)
            # TODO: update this so that the mdodes can be passed as parameters
            self.plantower_s5003.write(self.PASSIVE_MODE)

        except Exception as e:
            self.logger.debug(f"Failed to connect to Plantower S5003 {e}... ")  # noqa: E501

    def get_air_data(self, interval: int):

        self.plantower_s5003.flushInput()

        # query device for data
        self.plantower_s5003.write(self.PASSIVE_READ)

        return self.plantower_s5003.read(32)

    @staticmethod
    def parse_plantower_data(data: object):

        air_data = struct.unpack(">HHHHHHHHHHHHHHHH", data)

        pm1 = float(air_data[2])
        pm25 = float(air_data[3])
        pm10 = float(air_data[4])

        return pm1, pm25, pm10
