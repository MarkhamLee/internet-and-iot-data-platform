# Markham Lee (C) 2023 - 2024
# Productivity, Weather, Personal, et al dashboard:
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# General communication utilities for IoT devices
# import os
import uuid
import requests
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


def send_slack_alert(message: str, device_failure_channel, alert_endpoint):

    payload = {
        "text": message,
        "slack_channel": device_failure_channel
    }

    headers = {'Content-type': 'application/json'}

    response = requests.post(alert_endpoint, json=payload, headers=headers)
    logger.info('Device failure alert sent with code %s',
                response.text)


def send_slack_webhook(url: str, message: str):

    headers = {'Content-type': 'application/json'}

    payload = {"text": message}

    try:

        response = requests.post(url, headers=headers, json=payload)
        logger.info('Slack pipeline failure alert published succesfully with code: %s',  # noqa: E501
                    response.status_code)

    except Exception as e:

        logger.warning('Publishing of Slack alert failed with error: %s',
                       e)

    code = response.status_code

    if code == 200:
        logger.info('Publishing of alert to Slack webhook was successful')

    else:
        logger.warning('Publishing of alert to Slack webhook failed, with error code: %s',  # noqa: E501
                       code)

    return response.status_code
