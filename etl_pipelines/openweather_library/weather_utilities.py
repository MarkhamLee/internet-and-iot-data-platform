import sys
import os
import requests

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from etl_library.logging_util import logger  # noqa: E402
from etl_library.general_utilities import EtlUtilities  # noqa: E402


class WeatherUtilities():

    def __init__(self):

        self.get_variables()

    def get_variables(self):

        self.etl_utilities = EtlUtilities()
        self.units = '&units=metric'
        self.base_url = 'http://api.openweathermap.org/data/2.5/'

        # load environmental variables
        self.city = os.environ['CITY']
        self.lat = float(os.environ['LAT'])
        self.long = float(os.environ['LONG'])

    @staticmethod
    def parse_air_data(data: dict) -> dict:

        # influx DB is very strict about types, e.g. won't allow integers and
        # floats in the same field. Casting to float to avoid this.
        payload = {
            "carbon_monoxide": float(data['co']),
            "pm_2": float(data['pm2_5']),
            "pm_10": float(data['pm10'])
        }

        return payload

    def build_url_air(self, endpoint: str, key: str) -> str:

        url = f'{self.base_url}{endpoint}appid={key}&lat={self.lat}&lon={self.long}'  # noqa: E501

        return url

    def build_url_weather(self, key: str, endpoint: str) -> str:

        url = self.base_url + endpoint + 'appid=' + key + "&q=" + self.city + self.units  # noqa: E501

        return url

    @staticmethod
    def weather_parser(response: dict) -> dict:

        payload = {
            "weather": response['weather'][0]['main'],
            "description": response['weather'][0]['description'],
            "temp": float(response['main']['temp']),
            "feels_like": float(response['main']['feels_like']),
            "low": float(response['main']['temp_min']),
            "high": float(response['main']['temp_max']),
            "barometric_pressure": float(response['main']['pressure']),
            "humidity": float(response['main']['humidity']),
            "wind": float(response['wind']['speed']),
            "time_stamp": int(response['dt'])
        }

        return payload

    def get_weather_data(self, url: str) -> dict:

        try:
            # get weather data
            response = requests.get(url)
            response = response.json()
            logger.info('weather data retrieved')
            return response

        except Exception as e:
            WEBHOOK_URL = os.environ['ALERT_WEBHOOK']
            message = (f'weather data retrieval failed with error: {e}')
            logger.debug(message)
            self.etl_utilities.send_slack_webhook(WEBHOOK_URL, message)
            return e
