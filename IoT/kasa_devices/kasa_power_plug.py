# Markham Lee (C) 2023
# Python script for receiving Air Quality data from
# a Nova PM SDS011 air quality sensor
# Productivity/Personal Dashboard:
# https://github.com/MarkhamLee/personal_dashboard
# Note: this data could just as easily be written directly to InfluxDB
# via its REST API, using MQTT because I may (at some point) setup two way
# communications, monitor if a a device is connected, etc.

import asyncio
import sys
import json
import logging
from kasa import SmartPlug
from utilities.iot_utilities import DeviceUtilities


# setup logging for static methods
logging.basicConfig(filename='hardwareData.log', level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(name)s %(threadName)s\
                        : %(message)s')


async def get_plug_data(client, topic, device_ip, interval=30):

    # TODO: add exception handling
    dev = SmartPlug(device_ip)

    while True:

        # poll device for update
        await dev.update()

        # split out data

        payload = {
            "power_usage": dev.emeter_realtime.power,
            "voltage": dev.emeter_realtime.voltage,
            "current": dev.emeter_realtime.current,
            "device_id": dev.device_id
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

        # wait 30 seconds
        await asyncio.sleep(interval)  # Sleep some time between updates


def main():

    # instantiate utilities class
    deviceUtilities = DeviceUtilities()

    # parse command line arguments
    args = sys.argv[1:]

    configFile = args[0]
    secrets = args[1]
    interval = int(args[2])
    device_ip = int(args[3])

    # load variables from config files
    # TODO: move secrets and most of the config to environmental variables
    broker, port, topic, user, pwd = deviceUtilities.loadConfigs(configFile,
                                                                 secrets)

    # get unique client ID
    clientID = deviceUtilities.getClientID()

    # get mqtt client
    client, code = deviceUtilities.mqttClient(clientID, user, pwd, broker,
                                              port)

    # starrt device monitoring
    try:

        get_plug_data(client, topic, device_ip, interval)

    finally:
        client.loop_stop()


if __name__ == "__main__":
    asyncio.run(main())
