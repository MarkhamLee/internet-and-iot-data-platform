# !/usr/bin/env python
# Markham 2023 - 2025
# Internet & IoT Data Platform:
# https://github.com/MarkhamLee/internet-and-iot-data-platform
# Python script for receiving Air Quality data from a Nova PM SDS011 air
# quality sensor and sending it to InfluxDB via Node-RED and MQTT.
import serial
import os
import requests
import sys
from time import sleep

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from iot_libraries.logging_util import logger  # noqa: E402
from iot_libraries.communications_utilities\
    import IoTCommunications  # noqa: E402

DEVICE_ALERT_WEBHOOK = os.environ['DEVICE_ALERT_WEBHOOK']
UPTIME_KUMA_WEBHOOK = os.environ['UPTIME_KUMA_HEARTBEAT']

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
        self.com_utilities = IoTCommunications()

    # connect to sensor, send Slack alert if there is an issue
    def connect_to_sensor(self):

        # TODO: re-write as a regular script, no real need for this
        # to be a class.
        USB = os.environ['USB_ADDRESS']

        try:
            self.serial_connection = serial.Serial(USB)
            logger.info(f'connected to Nova PM SDS011 Air Quality sensor at: {USB}')  # noqa: E501
            self.usb_error_count = 0

        except Exception as e:
            message = (f'USB device connection failure on node: {self.NODE_DEVICE_ID}, with device: {USB} with error message: {e}, going to sleep...')  # noqa: E501
            logger.debug(message)
            self.com_utilities.send_slack_webhook(DEVICE_ALERT_WEBHOOK,
                                                  message)
            
            # just exit the container, as fixing the issue will likely require
            # manual intervention.
            logger.debug('Air Quality sensor not available, exiting container')
            sys.exit()

    # get air quality data, use bit shifting to isolate data
    def get_air_quality(self):

        try:

            message = self.serial_connection.read(10)

            # outputs have to be scaled by 0.1 to properly capture the
            # sensor's precision as it returns integers that are actually
            # decimals I.e. 15 is really 1.5

            pm2 = round((self.parse_value(message, self.pm2_bytes) * 0.1), 4)
            pm10 = round((self.parse_value(message, self.pm10_bytes) * 0.1), 4)

            # flush buffer - should help avoid issues where we get
            # anomolous readings
            self.serial_connection.reset_input_buffer()

            # send heartbeat to uptime Kuma
            self.com_utilities.send_uptime_kuma_heartbeat(self.NODE_DEVICE_ID,
                                                          UPTIME_KUMA_WEBHOOK)

            return pm2, pm10

        except Exception as e:
            message = (f'Failed to read from Nova PM SDS011 device: {self.NODE_DEVICE_ID}, with error: {e}, going to sleep....')  # noqa: E501
            logger.debug(message)
            self.com_utilities.send_slack_webhook(DEVICE_ALERT_WEBHOOK,
                                                  message)
            return 1

    # utility function that uses bit shifting to parse out
    # air quality data.
    def parse_value(self, message, start_byte, num_bytes=2,
                    byte_order='little', scale=None):

        """Returns a number from a sequence of bytes."""
        value = message[start_byte: start_byte + num_bytes]
        value = int.from_bytes(value, byteorder=byte_order)
        value = value * scale if scale else value

        return value