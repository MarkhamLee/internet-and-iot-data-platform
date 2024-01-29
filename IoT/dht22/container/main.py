# Markham Lee 2023
# Efficient, automated greenhouse
# https://github.com/MarkhamLee/automated-resource_efficient-greenhouse
# the script gathers data from a DHT22 temperature sensor and then
# publishes that data to a MQTT topic.

import adafruit_dht  
import board  
import json
import time
import gc
import os
import logging
import uuid
import requests
from sys import stdout
from paho.mqtt import client as mqtt

# setup logging
logger = logging.getLogger('telemetry_logger')
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler(stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s - %(message)s')  # noqa: E501
handler.setFormatter(formatter)
logger.addHandler(handler)


def getTemps(client: object, topic: str, interval: int, error_topic: str):

    # The use pulseio parameter is suggested parameter for a Raspberry Pi
    # may not need to use it with other types of SBCs

    # The sensor fails to read about 1/3 of the time but that can be managed
    # via exception handling and the next attempt is nearly always successful.
    # This appears to be an issue of the sensor + the driver, as this rarely
    # happens on a Raspberry Pi Pico Microcontroller (in my experience). Still,
    # given that you you can immediately retry reading the data it doesn't
    # really cause any issues as far as the sensor providing steady/consistent
    # data.

    temp_device = adafruit_dht.DHT22(board.D4, use_pulseio=False)
    logger.info('Connected to DHT22')

    while True:

        # get temperature and humidity data
        try:
            temp = temp_device.temperature
            humidity = temp_device.humidity

        except RuntimeError as error:  # noqa: F841
            # logging.debug(f'Device runtime error {error}')
            continue

        except Exception as error:
            logging.debug(f'Device read error {error}')
            continue

        if temp is not None:

            payload = {
                    "t": temp,
                    "h": humidity
                }

            payload = json.dumps(payload)
            send_message(client, payload, topic)
            del temp, humidity, payload
            gc.collect()

        time.sleep(interval)


def error_payload(count: int) -> dict:
    error_payload = {"current_count": count}

    return json.dumps(error_payload)


def send_slack_alert(message: str, device_failure_channel):

    ALERT_ENDPOINT = os.environ['ALERT_ENDPOINT']
    payload = {
        "text": message,
        "slack_channel": device_failure_channel
    }

    headers = {'Content-type': 'application/json'}

    response = requests.post(ALERT_ENDPOINT, json=payload, headers=headers)
    logger.info(f'Device failure alert sent with code: {response.text}')


def send_message(client: object, payload: dict, topic: str):

    try:
        result = client.publish(topic, payload)
        status = result[0]

    except Exception as error:
        logger.debug(f'MQTT connection error: {error}\
                            with status: {status}')

    # given that this is a RAM constrained device,
    # let's delete everything and do some garbage collection

    del payload, result, status
    gc.collect()


def mqttClient(clientID: str, username: str, pwd: str,
               host: str, port: int):

    def connectionStatus(client, userdata, flags, code):

        if code == 0:
            logger.info('connected to MQTT broker')

        else:
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


def getClientID():

    clientID = str(uuid.uuid4())

    return clientID


def main():

    # load environmental variables
    TOPIC = os.environ['TOPIC']
    ERROR_TOPIC = os.environ['ERROR_TOPIC']
    INTERVAL = int(os.environ['INTERVAL'])
    MQTT_BROKER = os.environ['MQTT_BROKER']
    MQTT_USER = os.environ['MQTT_USER']
    MQTT_SECRET = os.environ['MQTT_SECRET']
    MQTT_PORT = int(os.environ['MQTT_PORT'])

    # get unique client ID
    clientID = getClientID()

    # get mqtt client
    client, code = mqttClient(clientID, MQTT_USER,
                              MQTT_SECRET, MQTT_BROKER,
                              MQTT_PORT)

    # start data monitoring
    try:
        getTemps(client, TOPIC, INTERVAL, ERROR_TOPIC)

    finally:
        client.loop_stop()


if __name__ == '__main__':
    main()
