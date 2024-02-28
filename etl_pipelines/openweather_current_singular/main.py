# Markham Lee (C) 2023 - 2024
# productivity-music-stocks-weather-IoT-dashboard
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# This script retrieves the current weather from the Open Weather API for a
# location provided in the environmental variables (name of city and longitude
# and lattitude coordinates) and then exports that data to an xcom so that
# another process, container, etc., can pick it up.

import os
import sys
import json
from jsonschema import validate

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from etl_library.logging_util import logger  # noqa: 402
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


def export_data(data: dict):

    try:

        f = open("./airflow/xcom/return.json", "w")
        f.write(f"{data}")
        f.close()
        logger.info(f'data exported to XCOM {data}')

    except Exception as e:
        message = (f'Openweather Current pipeline failure: {e}')
        logger.debug(message)
        response = etl_utilities.send_slack_webhook(WEBHOOK_URL, message)
        logger.debug(f'Slack pipeline failure alert sent with code: {response}')  # noqa: E501


def main():

    # get current weather
    data = get_weather_data()

    # parse air quality data
    utilities.weather_parser(data)


if __name__ == "__main__":
    main()
