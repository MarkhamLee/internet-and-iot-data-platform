# Markham Lee (C) 2023
# productivity-music-stocks-weather-IoT-dashboard
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# This script retrieves the next day forecast from the Openweather API

from datetime import datetime, timedelta
from airflow.decorators import dag, task
from airflow.models import Variable

default_args = {
    "owner": "airflow",
    "start_date": datetime(2023, 10, 30),
    "retries": 1,
}


def send_alerts(context: dict):

    from plugins.slack_utilities import SlackUtilities
    slack_utilities = SlackUtilities()

    webhook_url = Variable.get('slack_hook_alerts')

    slack_utilities.send_slack_webhook(webhook_url, context)


@dag(schedule=timedelta(minutes=15), default_args=default_args, catchup=False,
     on_failure_callback=send_alerts)
def openweather_air_quality_dag():

    from open_weather.weather_utilities import WeatherUtilities  # noqa: E402
    utilities = WeatherUtilities()

    # key for OpenWeather API
    WEATHER_KEY = Variable.get('open_weather')

    @task(retries=1)
    def get_air_quality_data():

        ENDPOINT = 'air_pollution?'

        SCHEMA = Variable.get(key='openweather_air_quality_schema',
                              deserialize_json=True)

        # create URL
        url = utilities.build_url_air(ENDPOINT, WEATHER_KEY)

        # get data
        data = utilities.get_weather_data(url)

        # validate data - we do this here so that if this fails
        # we automatically repeat getting the data
        from jsonschema import validate

        # subset the data - note if this is effectively the first validation
        # e.g., if the subset doesn't exist, the data is wrong
        data = data['list'][0]['components']

        # validate the subset
        validate(instance=data, schema=SCHEMA)

        return data

    @task(task_id='parse_air_quality_data', multiple_outputs=True)
    def parse_data(data: dict) -> dict:

        return utilities.parse_air_data(data)

    @task(retries=1)
    def write_data(data: dict):

        # Airflow will parse these files every 30s (default) so we move these
        # imports into the functions so that airflow isn't constantly wasting
        # cycles importing libraries.

        # influx DB variables
        INFLUX_KEY = Variable.get('influx_db_key')
        ORG = Variable.get('influx_org')
        URL = Variable.get('influx_url')
        BUCKET = Variable.get('dashboard_bucket')

        from plugins.influx_client import InfluxClient  # noqa: E402
        influx = InfluxClient()

        client = influx.influx_client(INFLUX_KEY, ORG, URL)

        # base payload
        payload = {
            "measurement": "airq",
            "tags": {
                "OpenWeatherAPI": "Air Quality",
            }
        }

        # update the payload with the air quality data
        payload.update({"fields": data})

        # write data to InfluxDB
        client.write(bucket=BUCKET, record=payload)

    # nesting the methods establishes the hiearchy and creates the tasks
    write_data(parse_data(get_air_quality_data()))


openweather_air_quality_dag()
