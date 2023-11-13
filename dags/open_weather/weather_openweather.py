from datetime import datetime, timedelta
from airflow.decorators import dag, task
from airflow.models import Variable


default_args = {
    "owner": "airflow",
    "start_date": datetime(2023, 11, 4),
    "retries": 1,
}


from open_weather.weather_utilities import WeatherUtilities  # noqa: E402
utilities = WeatherUtilities()

# key for OpenWeather API
WEATHER_KEY = Variable.get('open_weather')

# influx DB variables
INFLUX_KEY = Variable.get('dashboard_influx_key')
ORG = Variable.get('influx_org')
URL = Variable.get('influx_url')
BUCKET = Variable.get('dashboard_bucket')


@dag(schedule=timedelta(minutes=5), default_args=default_args, catchup=False)
def openweather_current_weather_dag():

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

    @task(retries=1)
    def write_data(data: dict):

        from plugins.influx_client import InfluxClient  # noqa: E402
        influx = InfluxClient()

        from influxdb_client import Point  # noqa: E402

        # get the client for connecting to InfluxDB
        client = influx.influx_client(INFLUX_KEY, ORG, URL)

        # not the most elegant solution, will change later to
        # write json directly
        point = (
            Point("weather_current")
            .tag("OpenWeatherAPI", "current_weather")
            .field("temp", data['temp'])
            .field("feels_like", data['feels_like'])
            .field("weather", data['weather'])
            .field("description", data['weather_desc'])
            .field("low", data['temp_low'])
            .field("high", data['temp_high'])
            .field("barometric_pressure", data['pressure'])
            .field("humidity", data['humidity'])
            .field("wind", data['wind_speed'])
            .field("time_stamp", data['timestamp'])
        )

        client.write(bucket=BUCKET, org=ORG, record=point)

    # nesting the methods establishes the hiearchy and creates the tasks
    write_data(parse_weather_data(get_weather()))


openweather_current_weather_dag()
