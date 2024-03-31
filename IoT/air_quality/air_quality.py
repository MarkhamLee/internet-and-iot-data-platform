# !/usr/bin/env python
# Markham 2023 - 2024
# Productivity, Weather, Personal, et al dashboard:
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# Python script for receiving Air Quality data from
# a Nova PM SDS011 air quality sensor and sending it to InfluxDB
# via an MQTT Broker
import serial
import os
import sys
from time import sleep

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from iot_libraries.logging_util import logger  # noqa: E402
from iot_libraries.communications_utilities\
    import IoTCommunications  # noqa: E402

# TODO: elegant way of shutting of sensor/activating sleep mode
# code examples I've found are 5+ years old and don't work with
# current serial library. Solution is probably to use GPIO pins
# and/or C++


class AirQuality:

    def __init__(self):

        # create variables
        self.define_variables()
        self.connect_to_sensor()

    def define_variables(self):

        self.pid = 1
        self.pm2_bytes = 2
        self.pm10_bytes = 4
        self.device_id = 6
        self.read_error_count = 0
        self.usb_error_count = 0
        self.NODE_DEVICE_ID = os.environ['DEVICE_ID']
        self.DEVICE_FAILURE_CHANNEL = os.environ['DEVICE_FAILURE_CHANNEL']

        self.com_utilities = IoTCommunications()

    # connect to sensor, send Slack alert if there is an issue
    def connect_to_sensor(self):

        USB = os.environ['USB_ADDRESS']

        try:
            self.serial_connection = serial.Serial(USB)
            logger.info(f'connected to Nova PM SDS011 Air Quality sensor at: {USB}')  # noqa: E501

        except Exception as e:
            message = (f'USB device connection failure on node: {self.NODE_DEVICE_ID}, with device: {USB} with error message: {e}, going to sleep...')  # noqa: E501
            logger.debug(message)
            self.com_utilities.send_slack_alert(message,
                                                self.DEVICE_FAILURE_CHANNEL)
            # back-off limits/pod restart patterns are hard-coded into K8s,
            # SO... we put the container to sleep for an hour to provide
            # enough time to fix the physical issue w/o being spammed with
            # constant restart and container back-off alerts
            self.usb_error_count += 1
            sleep(3600 * self.usb_error_count)

    # get air quality data, use bit shifting to isolate data
    def get_air_quality(self):

        try:

            message = self.serialConnection.read(10)

            # outputs have to be scaled by 0.1 to properly capture the
            # sensor's precision as it returns integers that are actually
            # decimals I.e. 15 is really 1.5

            pm2 = round((self.parse_value(message, self.pm2Bytes) * 0.1), 4)
            pm10 = round((self.parse_value(message, self.pm10Bytes) * 0.1), 4)

            # flush buffer - should help avoid issues where we get
            # anomolous readings
            self.serial_connection.reset_input_buffer()

            return pm2, pm10

        except Exception as e:
            message = (f'Potential Nova PM SDS011 device error/failure on: {self.NODE_DEVICE_ID}, with error: {e}, going to sleep....')  # noqa: E501
            logger.debug(message)
            self.com_utilities.send_slack_alert(message,
                                                self.DEVICE_FAILURE_CHANNEL)
            # put container to sleep to avoid getting continuous container
            # creation back off alerts
            self.error_count += 1
            sleep(3600 * self.read_error_count)

    # utility function that uses bit shifting to parse out
    # air quality data.
    def parse_value(self, message, start_byte, num_bytes=2,
                    byte_order='little', scale=None):

        """Returns a number from a sequence of bytes."""
        value = message[start_byte: start_byte + num_bytes]
        value = int.from_bytes(value, byteorder=byte_order)
        value = value * scale if scale else value

        return value
