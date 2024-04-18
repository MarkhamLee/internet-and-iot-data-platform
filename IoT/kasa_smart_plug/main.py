# Markham Lee 2023 - 2024
# Finance, Productivity, IoT, & Weather dashboard
# https://github.com/MarkhamLee/finance-productivity-iot-informational-weather-dashboard
# Python script for receiving energy data from a TP Link Kasa TP254
# smart plug and writing the data to InfluxDB
import asyncio
import gc
import os
import sys
from kasa import SmartPlug


parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from iot_libraries.logging_util import logger  # noqa: E402
from iot_libraries.influx_client import InfluxClient  # noqa: E402

influxdb_write = InfluxClient()


async def get_plug_data(client: object, device_ip: str, interval: int,
                        bucket: str, table: str):

    # base payload
    base_payload = {
        "measurement": table,
        "tags": {
                "homelab monitoring": "energy consumption",
        }
    }

    try:
        dev = SmartPlug(device_ip)
        logger.info(f'Connected to Kasa smart plug at: {device_ip}')

    except Exception as e:
        message = (f'Kasa smart plug connection unsuccessful with error: {e}')
        logger.debug(message)
        # TODO: add Slack Alerts

    logger.info('starting monitoring loop...')

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

        try:

            # write data to InfluxDB
            influxdb_write.write_influx_data(client, base_payload,
                                             payload, bucket)

        except Exception as e:
            message = (f'InfluxDB write failed with error: {e}')
            logger.debug(message)

        # clean up RAM, container metrics show RAM usage creeping up daily
        del payload
        gc.collect()

        # wait 30 seconds
        await asyncio.sleep(interval)  # Sleep some time between updates


def main():

    # Load operating parameters
    INTERVAL = int(os.environ['INTERVAL'])
    DEVICE_IP = os.environ['DEVICE_IP']

    TOKEN = os.environ['TOKEN']
    ORG = os.environ['ORG']
    URL = os.environ['URL']
    BUCKET = os.environ['BUCKET']
    TABLE = os.environ['SMART_PLUG_TABLE']
    INTERVAL = int(os.environ['INTERVAL'])

    # get client
    client = influxdb_write.influx_client(TOKEN, ORG, URL)

    # start device monitoring
    asyncio.run(get_plug_data(client, DEVICE_IP, INTERVAL, BUCKET, TABLE))


if __name__ == "__main__":
    main()
