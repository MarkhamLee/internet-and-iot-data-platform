# Markham Lee 2023 - 2026
# Internet & IoT Data Platform
# https://github.com/MarkhamLee/internet-and-iot-data-platform
# Python script for receiving energy data from a TP Link Kasa TP254
# smart plug and writing the data to InfluxDB
import asyncio
import os
# import requests
import sys
from kasa.iot import IotPlug

import platform_utils.data_utils as data_utils
import platform_utils.alert_utils as alert_utils
from platform_utils.platform_logger import configure_logger


logger = configure_logger('Kasa_smart_plug_monitoring')


# Load environmental variables
BUCKET = os.environ['BUCKET']
DEVICE_ALERT_WEBHOOK = os.environ['DEVICE_ALERT_WEBHOOK']
DEVICE_ID = os.environ['DEVICE_ID']
DEVICE_IP = os.environ['DEVICE_IP']
SLEEP_INTERVAL = int(os.environ['INTERVAL'])
ORG = os.environ['ORG']
TABLE = os.environ['SMART_PLUG_TABLE']
TAG_KEY = os.environ['TAG_KEY']
TAG_VALUE = os.environ['TAG_VALUE']
TOKEN = os.environ['TOKEN']
URL = os.environ['URL']

logger.info('Preparing base InfluxDB payload')

# base payload
BASE_PAYLOAD = {
    "measurement": TABLE,
    "tags": {
                TAG_KEY: TAG_VALUE,
        }
    }

# get client
INFLUX_CLIENT = data_utils.influx_client(TOKEN, ORG, URL)


async def get_plug_data(dev):

    while True:

        # poll device for update
        try:
            await dev.update()

            # write data to InfluxDB
            write_data(dev)

        except Exception as e:
            logger.exception('Kasa Smart Plug connection error: %s on device %s',  # noqa: E501
                             e,
                             DEVICE_ID)  # noqa: E501

        # wait 30 seconds
        await asyncio.sleep(SLEEP_INTERVAL)  # Sleep some time between updates


def write_data(device_data_object):

    # parse payload
    payload = {
        "power_usage": device_data_object.emeter_realtime.power,
        "voltage": device_data_object.emeter_realtime.voltage,
        "current": device_data_object.emeter_realtime.current,
        "device_id": device_data_object.device_id
        }

    try:
        # write data to InfluxDB
        data_utils.write_influx_data(INFLUX_CLIENT,
                                     BASE_PAYLOAD,
                                     payload,
                                     BUCKET)

    except Exception as e:
        logger.exception('InfluxDB write failed with error: %s',
                         e)


def main():

    # connect to device
    logger.info(f'Connecting to device: {DEVICE_ID}')

    try:
        device = IotPlug(DEVICE_IP)
        logger.info('Connected to Kasa Smart Plug, device ID: %s, starting monitoring....',  # noqa: E501
                    DEVICE_ID)  # noqa: E501

    except Exception as e:
        message = (f'Failed to connect to device ID: {DEVICE_ID} at {DEVICE_IP} with error: {e}')  # noqa: E501
        logger.exception(message)
        alert_utils.send_slack_webhook_basic(DEVICE_ALERT_WEBHOOK,
                                             message)
        sys.exit(1)

    # start device monitoring
    asyncio.run(get_plug_data(device))


if __name__ == "__main__":
    main()
