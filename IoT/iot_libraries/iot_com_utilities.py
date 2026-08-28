# Markham Lee (C) 2023 - 2024
# Productivity, Weather, Personal, et al dashboard:
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# General communication utilities for IoT devices
# import os
import uuid
# import requests
from paho.mqtt import client as mqtt

from platform_utils.platform_logger import configure_logger

logger = configure_logger('iot_com_utilities')


def get_client_id():

    clientID = str(uuid.uuid4())

    return clientID


def mqtt_client(clientID, username, pwd, host, port):

    def connection_status(client,
                          userdata,
                          flags,
                          reasonCode,
                          properties=None):

        if reasonCode == 0 or getattr(reasonCode,
                                      'value',
                                      reasonCode) == 0:
            logger.info('connected to MQTT broker')

        else:

            reason_string = str(reasonCode)
            logger.warning('connection error occured, return code: %s, retrying...',  # noqa: E501
                           reason_string)  # noqa: E501

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, clientID)
    client.username_pw_set(username=username, password=pwd)
    client.on_connect = connection_status

    client.connect(host, port)

    # this is so that the client will attempt to reconnect automatically/
    # no need to add reconnect
    # logic.
    client.loop_start()

    return client
