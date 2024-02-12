# Markham Lee (C) 2023
# Productivity, Weather, Personal, et al dashboard:
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# Slight remix of utilty script from my hardware monitoring
# repo: https://github.com/MarkhamLee/HardwareMonitoring


import uuid
from paho.mqtt import client as mqtt
from logging_util import logger


class DeviceUtilities():

    # just a placeholder for now
    def __init__(self):

        pass

    # method for parsing the config file with connection data +
    # the secrets file
    @staticmethod
    def getClientID():

        clientID = str(uuid.uuid4())
        logger.info('Client ID generated')

        return clientID

    @staticmethod
    def mqttClient(clientID, username, pwd, host, port):

        def connectionStatus(client, userdata, flags, code):

            if code == 0:
                logger.info('Kasa Plug service Connected to MQTT broker')

            else:
                print(f'connection error: {code} retrying...')
                logger.debug(f'connection error occured, return code: {code}')

        client = mqtt.Client(clientID)
        client.username_pw_set(username=username, password=pwd)
        client.on_connect = connectionStatus

        code = client.connect(host, port)

        # this is so that the client will attempt to reconnect automatically/
        # no need to add reconnect
        # logic.
        client.loop_start()

        return client, code
