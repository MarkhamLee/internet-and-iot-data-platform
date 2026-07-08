# (C) Markham Lee 2023 - 2024
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# Test Script for pulling down data on the availability of
# Raspberry Pi devices. You will need to be mindful of how you set the max age,
# product and related variables so that there is available data from the RSS
# feed. TODO: add direct tests for the data transformations, as opposed to
# implicit ones via the data write (it will fail if data is wrong format),
# add tests for exception handling.

import os
import sys
import main
import unittest
import tracemalloc

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from etl_library.logging_util import logger  # noqa: E402
from etl_library.postgres_client import PostgresUtilities  # noqa: E402


class RaspberryPiLocatorTesting(unittest.TestCase):

    @classmethod
    def setUpClass(self):

        tracemalloc.start()

        self.logger = logger
        self.postgres_utils = PostgresUtilities()

        self.BASE_URL = os.environ['RPI_BASE_URL']
        self.RPI_PRODUCT = os.environ['RPI_PRODUCT']
        self.RPI_COUNTRY = os.environ['RPI_COUNTRY']

        # Load max age env var
        self.MAX_AGE = 120

        # get table for RPI data
        self.TABLE = os.environ.get('RPI5_TABLE')

        self.logger.info("Starting tests...")

    # End to end test, retrieving the data, parsing the pagination
    # object, calculating the age of task and then writing the data
    # to PostgreSQL.
    def test_rpi_end_to_end(self):

        # build URL
        URL = main.build_rss_url(self.BASE_URL,
                                 self.RPI_PRODUCT, self.RPI_COUNTRY)

        self.assertEqual(URL,
                         "https://rpilocator.com/feed/?country=US&cat=PI5",
                         "URL is incorrect")

        self.logger.info('URL creation validated')

        # get data
        data = main.read_rss_data(URL)

        self.assertIsNotNone(data, "Data not available")

        # transform data
        cleaned_data = main.data_transformation(data)

        # calculate alert age
        # update data frame to show age of each entry & filter out newest
        updated_data = main.alert_age(cleaned_data, self.MAX_AGE)

        # send Slack alert
        response = main.send_product_alert(updated_data)
        self.assertEqual(response, 200,
                         "Sending of Slack product alert failed")

        # get Postgres Connection
        connection = main.get_postgres_connection()
        self.assertIsNotNone(connection, "Postgres Connection creation failed")

        # get table for RPI data
        TABLE = os.environ.get('RPI5_TABLE')

        # write data to Postgres
        status, write_response = main.write_data(connection,
                                                 updated_data, TABLE)

        self.assertEqual(status, 0, "Postgres failed to write")
        self.assertEqual(write_response, len(updated_data),
                         "Row counts don't match, data write error")


if __name__ == '__main__':
    unittest.main()
