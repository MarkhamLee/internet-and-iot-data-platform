# (C) Markham Lee 2023 - 2024
# https://github.com/MarkhamLee/finance-productivity-iot-informational-weather-dashboard
# Finance, Productivity, IoT, Informational, Weather, Dashboard
# ETL for ingesting Air Pollution data from the OpenWeather API and writing it
# to InfluxDB.
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


# Get pollution data from the OpenWeather API
def get_air_quality_data():

    # key for OpenWeather API
    WEATHER_KEY = os.environ['OPENWEATHER_KEY']
    ENDPOINT = 'air_pollution?'

    # create URL
    url = utilities.build_url_air(ENDPOINT, WEATHER_KEY)

    # get data
    data = utilities.get_weather_data(url)
    logger.info('Air quality data received')

    # subset the data - note if this is effectively the first validation step
    # e.g., if the subset doesn't exist, the data is wrong
    return data['list'][0]['components']


# validate the data
def validate_air_data(data: object) -> int:

    with open('air_quality.json') as file:
        SCHEMA = json.load(file)

    # validate the data
    return etl_utilities.validate_json(data, SCHEMA)


# pull the desired fields out of the json
def parse_data(data: dict) -> dict:

    return utilities.parse_air_data(data)


# write the data to InfluxDB
def write_data(data: dict):

    MEASUREMENT = os.environ['AIR_QUALITY_MEASUREMENT']

    # Instantiate class with utilities for InfluxDB
    influx = InfluxClient()

    # InfluxDB variables
    INFLUX_KEY = os.environ['INFLUX_KEY']
    ORG = os.environ['INFLUX_ORG']
    URL = os.environ['INFLUX_URL']
    BUCKET = os.environ['BUCKET']

    client = influx.create_influx_client(INFLUX_KEY, ORG, URL)

    # base payload
    payload = {
        "measurement": MEASUREMENT,
        "tags": {
            "OpenWeatherAPI": "Air Quality",
        }
    }

    # Write data
    try:
        influx.write_influx_data(client, payload, data, BUCKET)
        logger.info('Weather data written to InfluxDB')
        return 0

    except Exception as e:
        message = (f'InfluxDB write for open weather air quality failed with error: {e}')  # noqa: E501
        logger.debug(message)
        response = etl_utilities.send_slack_webhook(WEBHOOK_URL, message)
        logger.debug(f'Slack pipeline failure alert sent with code: {response}')  # noqa: E501
        return response


def main():

    # get air quality data
    data = get_air_quality_data()

    # validate data
    if validate_air_data(data) == 0:

        # parse air quality data
        parsed_data = parse_data(data)

        # write data
        write_data(parsed_data)

    else:
        sys.exit()


if __name__ == "__main__":
    main()
