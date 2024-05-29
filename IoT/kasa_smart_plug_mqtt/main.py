# Markham Lee 2023 - 2024
# Finance, Productivity, IoT, & Weather dashboard
# https://github.com/MarkhamLee/finance-productivity-iot-informational-weather-dashboard
# Python script for receiving energy data from a TP Link Kasa TP254
# smart plug and transmitting the data via MQTT
import asyncio
import gc
import json
import os
import sys
from kasa import SmartPlug

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from iot_libraries.logging_util import logger  # noqa: E402
from iot_libraries.communications_utilities\
    import IoTCommunications  # noqa: E402

com_utilities = IoTCommunications()


async def get_plug_data(client: object, topic: str,
                        device_ip: str, interval: int):

    error_n = 1
    error_interval = 180  # sleep interval due to connetion errors

    try:
        dev = SmartPlug(device_ip)
        logger.info(f'Connected to Kasa smart plug at: {device_ip}')

    except Exception as e:
        logger.debug(f'device connection unsuccessful with error: {e}')

    while True:

        # poll device for update
        try:
            await dev.update()

        except Exception as e:
            logger.debug(f'connection error: {e}')

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

        if status != 0:
            logger.debug(f'data failed to publish to MQTT topic, status code:\
                          {status}')

        # clean up RAM, container metrics show RAM usage creeping up daily
        del payload, result, status
        gc.collect()

        # wait 30 seconds
        await asyncio.sleep(interval)  # Sleep some time between updates


def main():

    # Load operating parameters
    INTERVAL = int(os.environ['INTERVAL'])
    DEVICE_IP = os.environ['DEVICE_IP']
    TOPIC = os.environ['TOPIC']

    # Load connection variables
    MQTT_BROKER = os.environ['MQTT_BROKER']
    MQTT_USER = os.environ['MQTT_USER']
    MQTT_SECRET = os.environ['MQTT_SECRET']
    MQTT_PORT = int(os.environ['MQTT_PORT'])

    # get unique client ID
    clientID = com_utilities.getClientID()

    # get mqtt client
    client, code = com_utilities.mqttClient(clientID, MQTT_USER,
                                            MQTT_SECRET, MQTT_BROKER,
                                            MQTT_PORT)

    # start device monitoring
    try:
        asyncio.run(get_plug_data(client, TOPIC, DEVICE_IP, INTERVAL))

    finally:
        client.loop_stop()


if __name__ == "__main__":
    main()
