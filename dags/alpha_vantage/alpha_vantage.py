from datetime import datetime, timedelta
from airflow.decorators import dag, task
from airflow.models import Variable

# key for OpenWeather API
WEATHER_KEY = Variable.get('open_weather')

# influx DB variables
API_KEY = Variable.get('influx_key_air')
ORG = Variable.get('influx_org')
URL = Variable.get('influx_url')
BUCKET = Variable.get('weather_bucket')

default_args = {
    "owner": "airflow",
    "start_date": datetime(2023, 11, 3),
    "retries": 1,
}

API_KEY = Variable.get('alpha_vantage_key')


from alpha_vantage.alpha_utilities import AlphaUtilities  # noqa: E402
utilities = AlphaUtilities()


@dag(schedule=timedelta(minutes=20), default_args=default_args, catchup=False)
def alpha_vantage_dag():

    @task(retries=1)
    def get_stock_data():

        # create URL
        url = utilities.build_url('SPY', WEATHER_KEY)

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
        client = influx.influx_client(API_KEY, ORG, URL)

        # create object for writing to Influx
        point = (
            Point("stocks")
            .field("price", data['price'])
        )

        client.write(bucket=BUCKET, org=ORG, record=point)

    # nesting the methods establishes the hiearchy and creates the tasks
    write_data(parse_data(get_stock_data()))
