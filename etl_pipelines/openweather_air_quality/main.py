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


def get_air_quality_data():

    # key for OpenWeather API
    WEATHER_KEY = os.environ.get('OPENWEATHER_KEY')

    ENDPOINT = 'air_pollution?'

    with open('air_quality.json') as file:
        SCHEMA = json.load(file)

    # create URL
    url = utilities.build_url_air(ENDPOINT, WEATHER_KEY)

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
        logger.debug(f'data validation failed, with error: {e}')

    return data


def parse_data(data: dict) -> dict:

    return utilities.parse_air_data(data)


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
        "measurement": "airq",
        "tags": {
            "OpenWeatherAPI": "Air Quality",
        }
    }

    try:
        influx.write_influx_data(client, payload, data, BUCKET)
        logger.info('Weather data written to InfluxDB')

    except Exception as e:
        logger.debug(f'InfluxDB write failed with error: {e}')


def main():

    # get air quality data
    data = get_air_quality_data()

    # parse air quality data
    parsed_data = parse_data(data)

    write_data(parsed_data)


if __name__ == "__main__":
    main()
