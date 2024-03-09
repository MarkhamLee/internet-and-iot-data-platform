# (C) Markham Lee 2023 - 2024
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# Unit tests for the general ETL libraries, currently a work in progress
# note: you will need to define the relevant environmental variables before
# you can run these tests.

import os
import sys
import json
import unittest
import tracemalloc
tracemalloc.start()

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from etl_library.logging_util import logger  # noqa: E402
from openweather_library.weather_utilities\
    import WeatherUtilities  # noqa: E402
from etl_library.general_utilities import EtlUtilities  # noqa: E402
from etl_library.postgres_client import PostgresUtilities  # noqa: E402


class LibraryTesting(unittest.TestCase):

    @classmethod
    def setUpClass(self):

        self.utilities = WeatherUtilities()
        self.etl_utilities = EtlUtilities()
        self.postgres_tools = PostgresUtilities()

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

        # load data schema - using one for current weather conditions from the
        # OpenWeather API
        with open('current_weather.json') as file:
            SCHEMA = json.load(file)

        # test data validation
        code, response = self.etl_utilities.validate_json(bad_data, SCHEMA)

        self.assertEqual(code, 1,
                         "Data validation was unsuccessful")
        self.assertEqual(response, 200, "Slack alert was sent unsuccessfully")

    # test connecting to Postgres - it should be able to connect to DB
    # and then clear a given table
    def test_postgres_connection(self):

        # load connection parameters for Postgres
        param_dict = {
            "host": os.environ.get('DB_HOST'),
            "database": os.environ.get('DASHBOARD_DB'),
            "port": int(os.environ.get('POSTGRES_PORT')),
            "user": os.environ.get('POSTGRES_USER'),
            "password": os.environ.get('POSTGRES_PASSWORD')
            }

        # get the Postgres Connection
        connection = self.postgres_tools.postgres_client(param_dict)

        # clear the DB table
        clear_status = self.postgres_utilities.clear_table(connection,
                                                           self.TABLE)

        self.assertIsNotNone(connection, "Postgres connection creation failed")
        self.assertEqual(clear_status, 0, "Failed to clear Postgres table")

        # self.assertEqual(response, 0, "Postgres DB write failed")


if __name__ == '__main__':
    unittest.main()
