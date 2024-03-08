# (C) Markham Lee 2023 - 2024
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# Unit tests for the general ETL libraries, currently a work in progress
import os
import sys
import json
import unittest
import tracemalloc
tracemalloc.start()

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from etl_library.logging_util import logger  # noqa: E402
from openweather_library.weather_utilities import WeatherUtilities # noqa: 402
from etl_library.general_utilities import EtlUtilities  # noqa: E402


class LibraryTesting(unittest.TestCase):

    @classmethod
    def setUpClass(self):

        self.utilities = WeatherUtilities()
        self.etl_utilities = EtlUtilities()

        self.logger = logger
        self.logger.info('Testing started...')

    # Testing data validation, this should throw an error if an improper
    # data json payload is provided.
    def test_data_validation(self):

        # define "bad" data payload
        bad_data = {
            "weather": 5,
            "temp": "Gojo",
            "feels like": "dancing",
            "low": 6.61
        }

        # load data schema
        with open('current_weather.json') as file:
            SCHEMA = json.load(file)

        # test data validation
        code, response = self.etl_utilities.validate_json(bad_data, SCHEMA)

        self.assertEqual(code, 1,
                         "Data validation was unsuccessful")
        self.assertEqual(response, 200, "Slack alert was sent unsuccessfully")


if __name__ == '__main__':
    unittest.main()
