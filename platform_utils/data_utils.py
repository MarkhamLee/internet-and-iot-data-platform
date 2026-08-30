# Markham Lee (C) 2023 - 2026
# https://github.com/MarkhamLee/internet-and-iot-data-platform
# Utils for connecting/writing to persistent data stores
from __future__ import annotations

from influxdb_client import InfluxDBClient # noqa E402
from influxdb_client.client.write_api import SYNCHRONOUS
from platform_utils.platform_logger import configure_logger

logger = configure_logger('data_utilities')


def influx_client(token, org, url):

    try:
        # create client
        write_client = InfluxDBClient(url=url, token=token, org=org)
        write_api = write_client.write_api(write_options=SYNCHRONOUS)
        logger.info('InfluxDB Client created successfully')
        return write_api

    except Exception as e:
        logger.exception('InfluxDB client creation failed with error: %s',
                         e)
        raise


def write_influx_data(client: object, base: dict, data: dict, bucket: str):

    # create the payload by combining the baseline data with the
    # new data to be written to the DB.
    payload = {**base, "fields": data}

    try:
        # write data to InfluxDB
        client.write(bucket=bucket, record=payload)
        logger.info('InfluxDB write successful')

    except Exception as e:
        logger.exception('InfluxDB write failed with error: %s',
                         e)
