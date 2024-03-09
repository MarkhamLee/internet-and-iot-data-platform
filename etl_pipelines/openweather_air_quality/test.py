# (C) Markham Lee 2023 - 2024
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# Test Script for OpenWeather API for Air Pollution Data

import os
import sys
import json
import main
import unittest
import tracemalloc

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from etl_library.logging_util import logger  # noqa: E402
from openweather_library.weather_utilities import WeatherUtilities # noqa: 402
from etl_library.general_utilities import EtlUtilities  # noqa: E402


class OpenWeatherAirPollutionTesting(unittest.TestCase):

    @classmethod
    def setUpClass(self):

        tracemalloc.start()

        self.utilities = WeatherUtilities()
        self.etl_utilities = EtlUtilities()

        self.logger = logger
        self.logger.info('Testing started...')

    # End to end test, we validate that the API call works and
    # that we're able to write successfully to InfluxDB.
    def test_openweather_airquality_api_good(self):

        # get the data from the OpenWeather API
        data = main.get_air_quality_data()
        self.logger.info(data)

        # validate the json paylaod
        validation_status = main.validate_air_data(data)

        # now we check that data parsing works properly
        parsed_data = main.parse_data(data)

        parsed_length = len(parsed_data)

        # Finally, we write the data to the DB. We only get a resonse
        # back if the write fails and a Slack alert is triggered.
        response = main.write_data(parsed_data)

        self.assertIsNotNone(data, 'API Connection unsuccessful')
        self.assertEqual(validation_status, 0)
        self.assertEqual(parsed_length, 3, "Parsed data is the wrong shape")
        self.assertEqual(response, 0, "InfluxDB write unsuccessful")

    # Test using a bad key for the API request and/or API connection errors,
    # the expected behavior is that any non 200 code http codes/errors will
    # a) be captured and b) trigger a Slack alert. We also validate that the
    # Slack alert was sent properly.
    def test_bad_api_keys(self):

        # build URL
        BAD_KEY = 'fus-rah-dah'
        ENDPOINT = 'air_pollution?'
        url = self.utilities.build_url_weather(ENDPOINT, BAD_KEY)

        code, response = self.utilities.  get_weather_data(url)

        self.assertEqual(code, 1,
                         "API call was successful, it should've failed")
        self.assertEqual(response, 200, "Slack alert was sent unsuccessfully")

    # Test json validation for the air quality data payload/validating that
    # the schema has beeen defined properly.
    # This should fail and generate an alert message via Slack
    def test_validate_json_validation(self):

        # bad data
        bad_data = {
            "co": "carbon-monoxide",
            "pm2_5": "1.2",
            "pm10": "Full Metal Alchemist"
        }

        # load data schema
        with open('air_quality.json') as file:
            SCHEMA = json.load(file)

        # validate
        code, response = self.etl_utilities.validate_json(bad_data, SCHEMA)

        self.assertEquals(code, 1,
                          "Data validation successful, should've failed")
        self.assertEquals(response, 200, "Slack alert w")


if __name__ == '__main__':
    unittest.main()
