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
WEBHOOK_URL = os.environ['ALERT_WEBHOOK']


def get_weather_data():

    # key for OpenWeather API
    WEATHER_KEY = os.environ['OPENWEATHER_KEY']
    ENDPOINT = 'weather?'

    # create URL
    url = utilities.build_url_weather(WEATHER_KEY, ENDPOINT)

    return utilities.get_weather_data(url)


def validate_data(data: dict) -> dict:

    # load validation data
    with open('current_weather.json') as file:
        SCHEMA = json.load(file)

    # validate the data
    return etl_utilities.validate_json(data, SCHEMA)


def parse_data(data: dict) -> dict:

    return utilities.weather_parser(data)


def write_data(data: dict):

    MEASUREMENT = os.environ['WEATHER_MEASUREMENT']

    influx = InfluxClient()

    # influx DB variables
    INFLUX_KEY = os.environ['INFLUX_KEY']
    ORG = os.environ['INFLUX_ORG']
    URL = os.environ['INFLUX_URL']
    BUCKET = os.environ['BUCKET']

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
        return 0

    except Exception as e:
        message = (f'InfluxDB write for openweather current failed with error: {e}')  # noqa: E501
        logger.debug(message)
        response = etl_utilities.send_slack_webhook(WEBHOOK_URL, message)
        logger.debug(f'Pipeline failure alert sent via Slack with code: {response}')  # noqa: E501
        return 1, response


def main():

    # get current weather
    data = get_weather_data()

    # parse air quality data
    parsed_data = utilities.weather_parser(data)

    # validate data
    # validating after splitting off the data we need
    # as the data is simpler to work with.
    if validate_data(parsed_data) == 0:

        # write data to InfluxDB
        write_data(parsed_data)

    else:
        sys.exit()


if __name__ == "__main__":
    main()
