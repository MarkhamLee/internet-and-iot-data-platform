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
