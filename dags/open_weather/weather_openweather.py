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


from open_weather.weather_utilities import WeatherUtilities  # noqa E402
utilities = WeatherUtilities()


@dag(schedule=timedelta(minutes=5), default_args=default_args, catchup=False)
def open_weather_current_dag():

    @task
    def get_weather():

        ENDPOINT = 'weather?'

        # create URL
        url = utilities.build_url_weather(WEATHER_KEY, ENDPOINT)

        # get data from API
        return utilities.get_weather_data(url)

    @task(multiple_outputs=True)
    def parse_weather_data(data: dict) -> dict:

        return utilities.weather_parser(data)

    @task(retries=2)
    def write_data(data: dict):

        from plugins.influx_client import WeatherClients  # noqa: E402
        influx = WeatherClients()

        from influxdb_client import Point  # noqa: E402

        # get the client for connecting to InfluxDB
        client = influx.influx_client(API_KEY, ORG, URL)

        # not the most elegant solution, will change later to write
        # json directly
        point = (
            Point("current_weather")
            .tag("OpenWeatherAPI", "CurrentWeather")
            .field("Current Temp", data['temp'])
            .field("Feels Like", data['feels_like'])
            .field("Current Weather", data['weather'])
            .field("Weather Description", data['weather_desc'])
            .field("Low", data['temp_low'])
            .field("High", data['temp_high'])
            .field("Barometric Pressure", data['pressure'])
            .field("Humidity", data['humidity'])
            .field("Wind", data['wind_speed'])
            .field("Time Stamp", data['timestamp'])
        )

        client.write(bucket=BUCKET, org=ORG, record=point)

    # nesting the methods establishes the hiearchy and creates the tasks
    write_data(parse_weather_data(get_weather()))


open_weather_current_dag()
