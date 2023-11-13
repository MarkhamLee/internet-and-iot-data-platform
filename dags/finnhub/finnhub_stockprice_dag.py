from datetime import datetime, timedelta
from airflow.decorators import dag, task
from airflow.models import Variable

default_args = {
    "owner": "airflow",
    "start_date": datetime(2023, 11, 5),
    "retries": 1,
}

# get Finnhub API key
FINNHUB_KEY = Variable.get('finnhub_key')

# Influx DB variables
INFLUX_KEY = Variable.get('dashboard_influx_key')
ORG = Variable.get('influx_org')
URL = Variable.get('influx_url')
BUCKET = Variable.get('dashboard_bucket')


@dag(schedule=timedelta(minutes=15), default_args=default_args, catchup=False)
def finnhub_stockprice_dag():

    @task(retries=0)
    def get_prices():

        import finnhub  # noqa: E402

        # create client
        client = finnhub.Client(FINNHUB_KEY)

        # get data
        return client.quote('SPY')

    @task(multiple_outputs=True)
    def parse_data(data: dict) -> dict:

        from finnhub.finnhub_utilities import FinnHubUtilities  # noqa: E402
        utilities = FinnHubUtilities()

        return utilities.parse_stock_data(data)

    @task(retries=2)
    def write_data(data: dict):

        from plugins.influx_client import InfluxClient  # noqa: E402
        influx = InfluxClient()

        from influxdb_client import Point  # noqa: E402

        # get the client for connecting to InfluxDB
        client = influx.influx_client(INFLUX_KEY, ORG, URL)

        point = (
            Point("finnhub_quotes")
            .tag("stock_prices")
            .field("previous_close", data['previous_close'])
            .field("last_price", data['last_price'])
            .field("change", data['pc'])
        )

        client.write(bucket=BUCKET, org=ORG, record=point)

    write_data(parse_data(get_prices()))


finnhub_stockprice_dag()
