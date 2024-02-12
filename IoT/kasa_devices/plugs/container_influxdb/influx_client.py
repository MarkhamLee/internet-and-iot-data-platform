# cliente for connecting to InfluxDB API
# Pass the key, bucket and token and it will return an object
# for use in writing to InfluxDB.
# note: when using this client, don't convert the payload that's appended
# to the base to json. A standard data = {"key": "value"} Python dict
# is fine.

import logging
from influxdb_client import InfluxDBClient # noqa E402
from influxdb_client.client.write_api import SYNCHRONOUS # noqa E402
from sys import stdout

# set up/configure logging with stdout so it can be picked up by K8s
logger = logging.getLogger('rockchip_telemetry_logger')
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler(stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s - %(message)s')  # noqa: E501
handler.setFormatter(formatter)
logger.addHandler(handler)


class InfluxClient():

    def __init__(self) -> None:
        pass

    @staticmethod
    def influx_client(token, org, url):

        try:
            # create client
            write_client = InfluxDBClient(url=url, token=token, org=org)
            write_api = write_client.write_api(write_options=SYNCHRONOUS)
            logger.info('InfluxDB Client created successfully')

            return write_api

        except Exception as e:
            logger.info(f'InfluxDB client creation failed with error: {e}')

    # Takes an input payload and appends it to a JSON with that payload's
    # InfluxDB table and tag data, and then writes the combined
    # data to InfluxDB
    @staticmethod
    def write_influx_data(client: object, base: dict, data: dict, BUCKET: str):

        # combine the baseline payload with the data to be written to InfluxDB
        base.update({"fields": data})

        try:
            # write data to InfluxDB
            client.write(bucket=BUCKET, record=base)

        except Exception as e:
            logger.debug(f'failed to write to InfluxDB with error: {e}')
