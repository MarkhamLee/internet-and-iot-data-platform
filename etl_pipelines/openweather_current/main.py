# Markham Lee (C) 2023 - 2024
# productivity-music-stocks-weather-IoT-dashboard
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# This script retrieves the current weather from the Open Weather API for a
# location provided in the environmental variables: name of city and longitude
# and lattitude coordinates, and then writes that data to InfluxDB.
# If any part of the pipeline fails, an appropriate alert is sent via Slack.
# If the container or pod fails, problems with the node, etc., those issues
# will be detected by Prometheus and Prometheus alert manager will send
# an alert via Slack.

import os
import sys
import json
from jsonschema import validate

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from etl_library.logging_util import logger  # noqa: 402
from etl_library.influx_utilities import InfluxClient  # noqa: E402
from openweather_library.weather_utilities import WeatherUtilities # noqa: 402
from etl_library.general_utilities import EtlUtilities  # noqa: E402

utilities = WeatherUtilities()

# Load general utilities
etl_utilities = EtlUtilities()

# load Slack Webhook URL variable for sending pipeline failure alerts
WEBHOOK_URL = os.environ.get('ALERT_WEBHOOK')


def get_weather_data():

    # key for OpenWeather API
    WEATHER_KEY = os.environ.get('OPENWEATHER_KEY')
    ENDPOINT = 'weather?'

    # create URL
    url = utilities.build_url_weather(WEATHER_KEY, ENDPOINT)

    # get data
    data = utilities.get_weather_data(url)

    # load validation data
    with open('current_weather.json') as file:
        SCHEMA = json.load(file)

    # validate the data
    try:
        validate(instance=data, schema=SCHEMA)

    except Exception as e:
        message = (f'Data validation failed for the pipeline for openweather current, with error: {e}')  # noqa: E501
        logger.debug(message)
        response = etl_utilities.send_slack_webhook(WEBHOOK_URL, message)
        logger.debug(f'Slack pipeline failure alert sent with code: {response}')  # noqa: E501

    return data


def parse_data(data: dict) -> dict:

    return utilities.weather_parser(data)


def write_data(data: dict):

    MEASUREMENT = os.environ['WEATHER_MEASUREMENT']

    influx = InfluxClient()

    # influx DB variables
    INFLUX_KEY = os.environ.get('INFLUX_KEY')
    ORG = os.environ.get('INFLUX_ORG')
    URL = os.environ.get('INFLUX_URL')
    BUCKET = os.environ.get('BUCKET')

    client = influx.create_influx_client(INFLUX_KEY, ORG, URL)

    # base payload
    payload = {
        "measurement": MEASUREMENT,
        "tags": {
            "OpenWeatherAPI": "current_weather",
        }
    }

    try:
        influx.write_influx_data(client, payload, data, BUCKET)
        logger.info('Weather data written to InfluxDB')

    except Exception as e:
        message = (f'InfluxDB write for openweather current failed with error: {e}')  # noqa: E501
        logger.debug(message)
        response = etl_utilities.send_slack_webhook(WEBHOOK_URL, message)
        logger.debug(f'Slack pipeline failure alert sent with code: {response}')  # noqa: E501


def main():

    # get current weather
    data = get_weather_data()

    # parse air quality data
    parsed_data = utilities.weather_parser(data)

    write_data(parsed_data)


if __name__ == "__main__":
    main()
