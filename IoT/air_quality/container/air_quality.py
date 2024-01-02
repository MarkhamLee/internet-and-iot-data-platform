# !/usr/bin/env python
# Markham Lee (C) 2023
# Python script for receiving Air Quality data from
# a Nova PM SDS011 air quality sensor
# Productivity/Personal Dashboard:
# https://github.com/MarkhamLee/personal_dashboard

import serial
import uuid
from paho.mqtt import client as mqtt
import logging
import os

# setup logging for static methods
logging.basicConfig(filename='hardwareData.log', level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(name)s %(threadName)s\
                        : %(message)s')


class AirQuality:

    def __init__(self):

        # create variables
        self.defineVariables()

    def defineVariables(self):

        USB = os.environ['USB_ADDRESS']

        self.serialConnection = serial.Serial(USB)

        self.pm2Bytes = 2
        self.pm10Bytes = 4
        self.deviceID = 6

    def getAirQuality(self):

        message = self.serialConnection.read(10)

        # outputs have to be scaled by 0.1 to properly capture the
        # sensor's precision as it returns integers that are actually
        # decimals I.e. 15 is really 1.5

        pm2 = round((self.parse_value(message, self.pm2Bytes) * 0.1), 4)
        pm10 = round((self.parse_value(message, self.pm10Bytes) * 0.1), 4)

        return pm2, pm10

    def parse_value(self, message, start_byte, num_bytes=2,
                    byte_order='little', scale=None):

        """Returns a number from a sequence of bytes."""
        value = message[start_byte: start_byte + num_bytes]
        value = int.from_bytes(value, byteorder=byte_order)
        value = value * scale if scale else value

        return value

    @staticmethod
    def getClientID():

        clientID = str(uuid.uuid4())

        return clientID

    @staticmethod
    def mqttClient(clientID, username, pwd, host, port):

        def connectionStatus(client, userdata, flags, code):

            if code == 0:
                print('connected')

            else:
                print(f'connection error: {code} retrying...')
                logging.DEBUG(f'connection error occured, return code: {code}')

        client = mqtt.Client(clientID)
        client.username_pw_set(username=username, password=pwd)
        client.on_connect = connectionStatus

        code = client.connect(host, port)

        # this is so that the client will attempt to reconnect automatically/
        # no need to add reconnect
        # logic.
        client.loop_start()

        return client, code
