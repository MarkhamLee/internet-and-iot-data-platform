from datetime import datetime, timedelta
from airflow.decorators import dag, task
from airflow.models import Variable

default_args = {
    "owner": "airflow",
    "start_date": datetime(2023, 11, 5),
    "retries": 1,
}

# Alpha Vantage Key
ALPHA_KEY = Variable.get('alpha_vantage_key')

# influx DB variables
INFLUX_KEY = Variable.get('dashboard_influx_key')
ORG = Variable.get('influx_org')
URL = Variable.get('influx_url')
BUCKET = Variable.get('dashboard_bucket')


from alpha_vantage.alpha_utilities import AlphaUtilities  # noqa: E402
utilities = AlphaUtilities()


@dag(schedule=timedelta(hours=4), default_args=default_args, catchup=False)
def alphavantage_stock_price_dag():

    @task(retries=1)
    def get_stock_data():

        # create URL
        url = utilities.build_url('SPY', ALPHA_KEY)

        # get data
        return utilities.get_stock_data(url)

    @task()
    def parse_data(data: dict) -> dict:

        return utilities.stock_data_parser(data)

    @task(retries=2)
    def write_data(data: dict):

        # Airflow will parse these files every 30s (default) so we move these
        # imports into the functions so that airflow isn't constantly wasting
        # cycles importing libraries.

        from plugins.influx_client import WeatherClients  # noqa: E402
        influx = WeatherClients()

        from influxdb_client import Point  # noqa: E402

        # get the client for connecting to InfluxDB
        client = influx.influx_client(INFLUX_KEY, ORG, URL)

        # create object for writing to Influx
        point = (
            Point("stock_prices")
            .tag("Alpha_Vantage", "current_data")
            .field("price", data['price'])
            .field("change", data['change'])
            .field("open", data['open'])
            .field("change_per", data['change_per'])
        )

        client.write(bucket=BUCKET, org=ORG, record=point)

    # nesting the methods establishes the hiearchy and creates the tasks
    write_data(parse_data(get_stock_data()))


alphavantage_stock_price_dag()
