# Markham Lee (C) 2023
# Productivity, Weather, Personal, et al dashboard:
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# Slight remix of script I wrote for monitoring PC case temps:
# https://github.com/MarkhamLee/HardwareMonitoring
# the script gathers data from a DHT22 temperature sensors and a
# a Nova PM SDS011 air quality sensor and then publishes them to a
# MQTT topic.
# note: the Adafruit library is specific to a Raspberry Pi, using another
# type of SBC may or may not work

import Adafruit_DHT
import json
import time
import gc
import sys
import logging
from IoT.utilities.mqtt_client import DeviceUtilities
from airquality import AirQuality

# setup logging for static methods
logging.basicConfig(filename='hardwareData.log', level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(name)s %(threadName)s\
                        : %(message)s')


def getTemps(client, topic, quality, interval=30):

    while True:

        # TODO: add exception handling + alerting if a sensor fails

        # get temperature and humidity data
        humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.
                                                        DHT22, 4)

        temperature = round(temperature, 2)
        humidity = round(humidity, 2)

        # get air quality data
        pm2, pm10 = quality.getAirQuality()

        # round off air quality numbers
        pm2 = round(pm2, 2)
        pm10 = round(pm10, 2)

        payload = {
            "temp": temperature,
            "humidity": humidity,
            "pm2": pm2,
            "pm10": pm10
        }

        payload = json.dumps(payload)
        result = client.publish(topic, payload)
        status = result[0]

        if status == 0:
            print(f'Data {payload} was published to: {topic}')

        else:
            print(f'Failed to send {payload} to: {topic}')
            logging.debug(f'data failed to publish to MQTT topic, status code:\
                          {status}')

        # given that this is a RAM constrained device, let's delete
        # everything and do some garbage collection, watching things
        # on htop the RAM usage was creeping upwards...
        del payload, result, status, temperature, humidity, pm2, pm10
        gc.collect()

        time.sleep(interval)


def main():

    # instantiate utilities class
    deviceUtilities = DeviceUtilities()

    # instantiate air quality class
    quality = AirQuality()

    # parse command line arguments
    args = sys.argv[1:]

    configFile = args[0]
    secrets = args[1]
    interval = int(args[2])

    broker, port, topic, user, pwd = deviceUtilities.loadConfigs(configFile,
                                                                 secrets)

    # get unique client ID
    clientID = deviceUtilities.getClientID()

    # get mqtt client
    client, code = deviceUtilities.mqttClient(clientID, user, pwd, broker,
                                              port)

    # start data monitoring
    try:
        getTemps(client, topic, interval, quality)

    finally:
        client.loop_stop()


if __name__ == '__main__':
    main()
