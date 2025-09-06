# Markham Lee (C) 2023 - 2024
# Productivity, Weather, Personal, et al dashboard:
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# General communication utilities for IoT devices
import os
import uuid
import requests
from paho.mqtt import client as mqtt
from iot_libraries.logging_util import logger


class IoTCommunications():

    def __init__(self):

        pass

    @staticmethod
    def getClientID():

        clientID = str(uuid.uuid4())

        return clientID

    @staticmethod
    def mqttClient(clientID, username, pwd, host, port):

        def connectionStatus(client, userdata, flags,
                             reasonCode,
                             properties=None):

            if reasonCode == 0 or getattr(reasonCode,
                                          'value',
                                          reasonCode) == 0:
                logger.info('connected to MQTT broker')

            else:

                reason_string = str(reasonCode)
                logger.debug(f'connection error occured, return code: {reason_string}, retrying...')  # noqa: E501

        # TODO: while this is good enought to "work", need to look into
        # the updated API library, etc., and re-work the reconnection logic.
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, clientID)
        client.username_pw_set(username=username, password=pwd)
        client.on_connect = connectionStatus

        client.connect(host, port)

        # this is so that the client will attempt to reconnect automatically/
        # no need to add reconnect
        # logic.
        client.loop_start()

        return client

    # method for sending slack alerts
    @staticmethod
    def send_slack_alert(message: str, device_failure_channel, alert_endpoint):
        
        payload = {
            "text": message,
            "slack_channel": device_failure_channel
        }

        headers = {'Content-type': 'application/json'}

        response = requests.post(alert_endpoint, json=payload, headers=headers)
        logger.info(f'Device failure alert sent with code: {response.text}')

    @staticmethod
    def send_slack_webhook(url: str, message: str):

        headers = {
            'Content-type': 'application/json'

        }

        payload = {
            "text": message
        }

        try:

            response = requests.post(url, headers=headers, json=payload)
            logger.info(f'Slack pipeline failure alert published succesfully with code: {response.status_code}')  # noqa: E501

        except Exception as e:
            logger.debug(f'Publishing of Slack alert failed with error: {e}')

        code = response.status_code

        if code == 200:
            logger.info('Publishing of alert to Slack webhook was successful')

        else:
            logger.debug(f'Publishing of alert to Slack webhook failed, with error code {code}')  # noqa: E501

        return response.status_code
