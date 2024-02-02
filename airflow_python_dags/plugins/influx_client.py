# cliente for connecting to InfluxDB API
# Pass the key, bucket and token and it will return an object
# for use in writing to InfluxDB.

class InfluxClient():

    def __init__(self) -> None:
        pass

    @staticmethod
    def influx_client(token, org, url):

        from influxdb_client import InfluxDBClient # noqa E402
        from influxdb_client.client.write_api import SYNCHRONOUS # noqa E402

        # create client
        write_client = InfluxDBClient(url=url, token=token, org=org)
        write_api = write_client.write_api(write_options=SYNCHRONOUS)

        return write_api

    # Takes an input payload and appends it to a JSON with that payload's
    # InfluxDB table and tag data, and then writes the combined
    # data to InfluxDB
    @staticmethod
    def write_influx_data(client: object, base: dict, data: dict, BUCKET: str):

        # combine the baseline payload with the data to be written to InfluxDB
        base.update({"fields": data})

        # write data to InfluxDB
        client.write(bucket=BUCKET, record=base)
