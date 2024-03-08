# (C) Markham Lee 2023 - 2024
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# Test script for the OpenWeather API for pulling down current weather
# conditions. Before running this make sure all of your environmental
# variables, connection strings, etc., are setup properly, chances are, those
# will be the source of most of your errors, as opposed to the code itself.
import os
import sys
import unittest
import main
import tracemalloc
tracemalloc.start()

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from etl_library.logging_util import logger  # noqa: E402
from openweather_library.weather_utilities import WeatherUtilities # noqa: 402
from etl_library.general_utilities import EtlUtilities  # noqa: E402


class OpenWeatherCurrentTesting(unittest.TestCase):

    @classmethod
    def setUpClass(self):

        self.utilities = WeatherUtilities()
        self.etl_utilities = EtlUtilities()

        self.logger = logger
        self.logger.info('Testing started...')

    # End to end test, we validate that the API call works and we're
    # able to write successfully to InfluxDB.
    def test_openweather_api(self):

        self.logger.info('Performing end to end tests')

        # get the data
        data = main.get_weather_data()

        # validate the json paylaod
        validation_status = main.validate_data(data)

        # now we check that data parsing works properly
        parsed_data = main.parse_data(data)
        parsed_length = len(parsed_data)

        # Finally, we write the data to the DB
        status = main.write_data(parsed_data)

        self.assertIsNotNone(data, 'API call failed')
        self.assertEqual(validation_status, 0)
        self.assertEqual(parsed_length, 10, "Parsed data is the wrong shape")
        self.assertEqual(status, 0, "InfluxDB write unsuccessful")

    # test sending a bad data payload to InfluxDB that "should" fail type
    # checking. Also testing the triggering of a pipeline failure alert
    # sent via Slack.
    def test_bad_data_write(self):

        data = {
            "weather": 5,
            "temp": "Gojo",
            "feels like": "dancing",
            "low": 6.61
        }

        # Finally, we write the data to the DB
        code, response = main.write_data(data)

        self.assertEqual(code, 1,
                         "Data write was successful, should've failed")
        self.assertEqual(response, 200, "Slack alert was sent unsuccessfully")

    # Test using a bad key for the API request and/or API connection errors,
    # the expected behavior is that any non 200 code http codes/errors will
    # a) be captured and b) trigger a Slack alert. We also validate that the
    # Slack alert was sent properly.
    def test_bad_api_keys(self):

        # build URL
        BAD_KEY = 'kasdkasdfasa'
        ENDPOINT = 'weather?'
        url = self.utilities.build_url_weather(BAD_KEY, ENDPOINT)

        code, response = self.utilities.get_weather_data(url)

        self.assertEqual(code, 1,
                         "API call was successful, it should've failed")
        self.assertEqual(response, 200, "Slack alert was sent unsuccessfully")


if __name__ == '__main__':
    unittest.main()
