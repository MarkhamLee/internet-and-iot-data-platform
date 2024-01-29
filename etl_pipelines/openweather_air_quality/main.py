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


def get_air_quality_data():

    # key for OpenWeather API
    WEATHER_KEY = os.environ.get('OPENWEATHER_KEY')

    ENDPOINT = 'air_pollution?'

    with open('air_quality.json') as file:
        SCHEMA = json.load(file)

    # create URL
    url = utilities.build_url_air(ENDPOINT, WEATHER_KEY)
    logger.info('retrieving air quality data....')

    # get data
    data = utilities.get_weather_data(url)
    logger.info('Air quality data received')

    # subset the data - note if this is effectively the first validation step
    # e.g., if the subset doesn't exist, the data is wrong
    data = data['list'][0]['components']

    # validate the subset
    try:
        validate(instance=data, schema=SCHEMA)

    except Exception as e:
        message = (f'data validation failed, with error: {e}')
        logger.debug(message)
        response = etl_utilities.send_slack_webhook(WEBHOOK_URL, message)
        logger.debug(f'Slack pipeline failure alert sent with code: {response}')  # noqa: E501

    return data


def parse_data(data: dict) -> dict:

    return utilities.parse_air_data(data)


def write_data(data: dict):

    MEASUREMENT = os.environ['AIR_QUALITY_MEASUREMENT']

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
            "OpenWeatherAPI": "Air Quality",
        }
    }

    try:
        influx.write_influx_data(client, payload, data, BUCKET)
        logger.info('Weather data written to InfluxDB')

    except Exception as e:
        message = (f'InfluxDB write failed with error: {e}')
        logger.debug(message)
        response = etl_utilities.send_slack_webhook(WEBHOOK_URL, message)
        logger.debug(f'Slack pipeline failure alert sent with code: {response}')  # noqa: E501


def main():

    # get air quality data
    data = get_air_quality_data()

    # parse air quality data
    parsed_data = parse_data(data)

    write_data(parsed_data)


if __name__ == "__main__":
    main()
