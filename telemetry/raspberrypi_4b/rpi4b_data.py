# Markham Lee (C) 2023
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# methods for retrieving data from a Raspberry Pis CPU, GPU sensors, et al,
# plus utility scripts for MQTT: MQTT client and generating unique client
# IDs

import psutil
import uuid
import logging
from paho.mqtt import client as mqtt


class Rpi4bData():

    def __init__(self):

        # get the # of cores, as we can use that to iterate through and
        # get things like current speed for all CPU cores
        self.coreCount = psutil.cpu_count(logical=False)

    # get average clock speed for all cores
    def getFreq(self, all_cpu=False):

        allFreq = psutil.cpu_freq(percpu=all_cpu)[0]
        allFreq = round(allFreq, 1)

        return allFreq, self.coreCount

    # CPU load/utilization
    def getCPUData(self):

        cpuUtil = (psutil.cpu_percent(interval=1))
        cpuUtil = round(cpuUtil, 1)

        return cpuUtil

    # get current RAM used
    def getRamData(self):

        ramUse = (psutil.virtual_memory()[3]) / 1073741824
        ramUse = round(ramUse, 2)

        return ramUse

    # get CPU temp for Raspberry Pi 4B
    @staticmethod
    def get_rpi4b_temps():

        rpi_cpu_temp = psutil.sensors_temperatures()['cpu_thermal'][0].current

        return rpi_cpu_temp

    @staticmethod
    def getClientID():

        clientID = str(uuid.uuid4())

        return clientID

    @staticmethod
    def mqttClient(clientID: str, username: str, pwd: str,
                   host: str, port: int):

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
