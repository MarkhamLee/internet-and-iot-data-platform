# Markham Lee 2023 - 2024
# Finance, Productivity, IoT, & Weather dashboard
# https://github.com/MarkhamLee/finance-productivity-iot-informational-weather-dashboard
# Python script for receiving energy data from a TP Link Kasa TP254
# smart plug and writing the data to InfluxDB
import asyncio
import os
import requests
import sys
from kasa.iot import IotPlug


parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from iot_libraries.logging_util import logger  # noqa: E402
from iot_libraries.influx_client import InfluxClient  # noqa: E402
from iot_libraries.communications_utilities\
    import IoTCommunications  # noqa: E402

com_utilities = IoTCommunications

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
UPTIME_KUMA_WEBHOOK = os.environ['UPTIME_KUMA_WEBHOOK']

influxdb_write = InfluxClient()

logger.info('Preparing base InfluxDB payload')

# base payload
BASE_PAYLOAD = {
    "measurement": TABLE,
    "tags": {
                TAG_KEY: TAG_VALUE,
        }
    }

# get client
INFLUX_CLIENT = influxdb_write.influx_client(TOKEN, ORG, URL)


async def get_plug_data(dev):

    while True:

        # poll device for update
        try:
            await dev.update()

            # send out heartbeat
            send_uptime_kuma_heartbeat()

            # write data to InfluxDB
            write_data(dev)

        except Exception as e:
            logger.debug(f'Kasa Smart Plug connection error: {e} on device {DEVICE_ID}')  # noqa: E501

        # wait 30 seconds
        await asyncio.sleep(SLEEP_INTERVAL)  # Sleep some time between updates


def send_uptime_kuma_heartbeat():

    # TODO: check response to verify that response
    # is proper, if not trigger alert
    try:
        requests.get(UPTIME_KUMA_WEBHOOK)

    except Exception as e:
        logger.info(f'Publishing of Uptime Kuma alert for {DEVICE_ID} failed with error: {e}')  # noqa: E501


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
        influxdb_write.write_influx_data(INFLUX_CLIENT,
                                         BASE_PAYLOAD,
                                         payload,
                                         BUCKET)

    except Exception as e:

        message = (f'InfluxDB write failed with error: {e}')
        logger.debug(message)


def main():

    # connect to device
    logger.info(f'Connecting to device: {DEVICE_ID}')

    # TODO: write better reconnection logic
    try:
        device = IotPlug(DEVICE_IP)
        logger.info(f'Connected to Kasa Smart Plug, device ID: {DEVICE_ID}, starting monitoring....')  # noqa: E501

    except Exception as e:
        message = (f'Failed to connect to device ID: {DEVICE_ID} at {DEVICE_IP} with error: {e}')  # noqa: E501
        logger.info(message)
        com_utilities.send_slack_webhook(DEVICE_ALERT_WEBHOOK,
                                         message)
        sys.exit()

    # start device monitoring
    asyncio.run(get_plug_data(device))


if __name__ == "__main__":
    main()
