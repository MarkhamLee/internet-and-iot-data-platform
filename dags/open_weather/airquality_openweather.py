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
    "start_date": datetime(2023, 10, 30),
    "retries": 1,
}

from open_weather.weather_utilities import WeatherUtilities # noqa: 402
utilities = WeatherUtilities()


@dag(schedule=timedelta(minutes=15), default_args=default_args, catchup=False)
def open_weather_air_dag():

    @task(retries=1)
    def get_air_quality_data():

        ENDPOINT = 'air_pollution?'

        # create URL
        url = utilities.build_url_air(ENDPOINT, WEATHER_KEY)

        return utilities.get_weather_data(url)

    @task(task_id='parse_air_quality_data', multiple_outputs=True)
    def parse_data(data: dict) -> dict:

        return utilities.parse_air_data(data)

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
            Point("air_quality")
            .field("carbon_monoxide", data['co'])
            .field("PM 2.5", data['pm2'])
            .field("pm 10", data['pm10'])
        )

        client.write(bucket=BUCKET, org=ORG, record=point)

    # nesting the methods establishes the hiearchy and creates the tasks
    write_data(parse_data(get_air_quality_data()))


open_weather_air_dag()
