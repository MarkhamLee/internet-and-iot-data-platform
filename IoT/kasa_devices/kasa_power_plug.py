# Markham Lee (C) 2023
# Productivity, Weather, Personal, et al dashboard:
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# Python script for receiving energy data from a TP Link
# Kasa TP25P4 smart plug. Note: this data could just as easily be written
# directly to InfluxDB via its REST API, using MQTT because I may
# (at some point) want to send instructions back to the device, communications,
# monitor if a device is connected, etc.

import os
import asyncio
import sys
import json
from kasa import SmartPlug

# this allows us to import modules, classes, scripts et al from higher
# level directories
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from utilities.iot_utilities import DeviceUtilities  # noqa: E402


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
    device_ip = str(args[3])

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

        asyncio.run(get_plug_data(client, topic, device_ip, interval))

    finally:
        client.loop_stop()


if __name__ == "__main__":
    main()
