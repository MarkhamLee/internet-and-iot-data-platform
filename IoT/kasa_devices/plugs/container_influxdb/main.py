# Markham Lee (C) 2023
# Productivity, Weather, Personal, et al dashboard:
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# Python script for receiving energy data from a TP Link
# Kasa TP25P4 smart plug. Note: this data could just as easily be written
# directly to InfluxDB via its REST API, using MQTT because I may
# (at some point) want to send instructions back to the device,
# monitor if a device is connected, etc.

import asyncio
import os
import gc
from kasa import SmartPlug
from influx_client import InfluxClient
from logging_util import logger

influxdb_write = InfluxClient()


async def get_plug_data(client: object, device_ip: str,
                        interval: int, bucket: str, table: str):

    try:
        dev = SmartPlug(device_ip)
        logger.info(f'Connected to Kasa smart plug at: {device_ip}')

    except Exception as e:
        logger.debug(f'device connection unsuccessful with error: {e}')

    # base payload
    base_payload = {
        "measurement": table,
        "tags": {
                "k3s_prod": "hardware_telemetry",
        }
    }

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
        del payload, result, status
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
