# Markham Lee (C) 2023
# productivity-music-stocks-weather-IoT-dashboard
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# This script retrieves the current weather from the Openweather API

from datetime import datetime, timedelta
from airflow.decorators import dag, task
from airflow.models import Variable


default_args = {
    "owner": "airflow",
    "start_date": datetime(2023, 11, 4),
    "retries": 1,
}


def send_alerts(context: dict):

    from plugins.slack_utilities import SlackUtilities
    slack_utilities = SlackUtilities()

    webhook_url = Variable.get('slack_hook_alerts')

    slack_utilities.send_slack_webhook(webhook_url, context)


@dag(schedule=timedelta(minutes=5), default_args=default_args, catchup=False,
     on_failure_callback=send_alerts)
def openweather_current_weather_dag():

    from open_weather.weather_utilities import WeatherUtilities  # noqa: E402
    utilities = WeatherUtilities()

    @task()
    def get_weather():

        # key for OpenWeather API
        WEATHER_KEY = Variable.get('open_weather')
        ENDPOINT = 'weather?'

        # create URL
        url = utilities.build_url_weather(WEATHER_KEY, ENDPOINT)

        # get data from API
        data = utilities.get_weather_data(url)

        # validate data - we do this here so that if this fails
        # we automatically repeat getting the data
        from jsonschema import validate  # noqa: E402
        SCHEMA = Variable.get(key='openweather_current_weather_schema',
                              deserialize_json=True)

        validate(instance=data, schema=SCHEMA)

        return data

    @task(multiple_outputs=True, retries=0)
    def parse_weather_data(data: dict) -> dict:

        return utilities.weather_parser(data)

    @task(retries=1)
    def write_data(data: dict):

        from plugins.influx_client import InfluxClient  # noqa: E402
        influx = InfluxClient()

        # from influxdb_client import Point  # noqa: E402

        # influx DB variables
        INFLUX_KEY = Variable.get('dashboard_influx_key')
        ORG = Variable.get('influx_org')
        URL = Variable.get('influx_url')
        BUCKET = Variable.get('dashboard_bucket')

        # get the client for connecting to InfluxDB
        client = influx.influx_client(INFLUX_KEY, ORG, URL)

        payload = {
            "measurement": "weather_current",
            "tags": {
                "OpenWeatherAPI": "current weather",
            }
        }

        # append the base payload with the weather data
        payload.update({"fields": data})

        # write data to InfluxDB
        client.write(bucket=BUCKET, record=payload)

    # nesting the methods establishes the hiearchy and creates the tasks
    write_data(parse_weather_data(get_weather()))


openweather_current_weather_dag()
