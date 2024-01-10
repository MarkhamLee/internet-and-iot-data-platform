# Markham Lee (C) 2023
# Productivity, Weather, Personal, et al dashboard:
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# Slight remix of utilty script from my hardware monitoring
# repo: https://github.com/MarkhamLee/HardwareMonitoring


import uuid
import logging
from paho.mqtt import client as mqtt


class DeviceUtilities():

    # just a placeholder for now
    def __init__(self):

        pass

    # method for parsing the config file with connection data +
    # the secrets file
    @staticmethod
    def getClientID():

        clientID = str(uuid.uuid4())
        logging.info('Client ID generated')

        return clientID

    @staticmethod
    def mqttClient(clientID, username, pwd, host, port):

        def connectionStatus(client, userdata, flags, code):

            if code == 0:
                logging.info('Kasa Plug service Connected to MQTT broker')

            else:
                print(f'connection error: {code} retrying...')
                logging.debug(f'connection error occured, return code: {code}')

        client = mqtt.Client(clientID)
        client.username_pw_set(username=username, password=pwd)
        client.on_connect = connectionStatus

        code = client.connect(host, port)

        # this is so that the client will attempt to reconnect automatically/
        # no need to add reconnect
        # logic.
        client.loop_start()

        return client, code
