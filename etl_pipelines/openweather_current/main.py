import os
import sys
import json
from jsonschema import validate

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from etl_library.logging_util import logger  # noqa: 402
from etl_library.influx_utilities import InfluxClient  # noqa: E402
from openweather_library.weather_utilities import WeatherUtilities # noqa: 402

utilities = WeatherUtilities()


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
        logger.debug(f'data validation failed, with error: {e}')

    return data


def parse_data(data: dict) -> dict:

    return utilities.weather_parser(data)


def write_data(data: dict):

    # Airflow will parse these files every 30s (default) so we move these
    # imports into the functions so that airflow isn't constantly wasting
    # cycles importing libraries.

    influx = InfluxClient()

    # influx DB variables
    INFLUX_KEY = os.environ.get('INFLUX_KEY')
    ORG = os.environ.get('INFLUX_ORG')
    URL = os.environ.get('INFLUX_URL')
    BUCKET = os.environ.get('BUCKET')

    client = influx.create_influx_client(INFLUX_KEY, ORG, URL)

    # base payload
    payload = {
        "measurement": "weather",
        "tags": {
            "OpenWeatherAPI": "current_weather",
        }
    }

    try:
        influx.write_influx_data(client, payload, data, BUCKET)
        logger.info('Weather data written to InfluxDB')

    except Exception as e:
        logger.debug(f'InfluxDB write failed with error: {e}')


def main():

    # get current weather
    data = get_weather_data()

    # parse air quality data
    parsed_data = utilities.weather_parser(data)

    write_data(parsed_data)


if __name__ == "__main__":
    main()
