# (C) Markham Lee 2023 - 2024
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# Unit test script for the Alpha Vantage T-Bill ETL.
# Note: the only functions that will be run as tests are those whose function
# names have "test_" at the beginning.

import os
import sys
import unittest
import main
import tracemalloc

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from alpha_vantage_library.alpha_utilities import AlphaUtilities  # noqa: E402
from etl_library.postgres_client import PostgresUtilities  # noqa: E402
from etl_library.logging_util import logger  # noqa: E402
from etl_library.general_utilities import EtlUtilities  # noqa: E402


class AlphaVantageBondTesting(unittest.TestCase):

    @classmethod
    def setUpClass(self):

        tracemalloc.start()

        self.utilities = AlphaUtilities()
        self.etl_utilities = EtlUtilities()
        self.postgres_utilities = PostgresUtilities()

        # Alpha Vantage Key
        self.ALPHA_KEY = os.environ.get('ALPHA_KEY')

        # Bond Maturity
        self.MATURITY = os.environ.get('BOND_MATURITY')

        # TABLE
        self.TABLE = os.environ.get('TBILL_TABLE')

        # count for rows of data we will keep
        self.COUNT = int(os.environ['COUNT'])

        logger.info('Key variables loaded')

    # End to end multi-stage test, we validate that the API call works
    # and we're able to write successfully to PostgreSQL.
    def test_alphavantage_api_good(self):

        # build Alpha Vantage URL
        url = self.utilities.build_bond_url(self.MATURITY, self.ALPHA_KEY)

        # get T-Bill Data
        data = main.get_tbill_data(url)

        # now we check that data parsing & validation works properly and only
        # returns the requested number of rows as defined by the self.COUNT
        # variable
        parsed_data = main.parse_tbill_data(data)

        # get the Postgres Connection
        connection = main.postgres_connection()

        # clear the DB table
        clear_status = self.postgres_utilities.clear_table(connection,
                                                           self.TABLE)

        # parse and validate the data - should only return six rows of data
        response = main.write_data(connection, parsed_data, self.TABLE)

        self.assertEqual(len(parsed_data),
                         self.COUNT, "Parsed data is the wrong length")
        self.assertIsNotNone(connection, "Postgres connection creation failed")
        self.assertEqual(clear_status, 0, "Failed to clear Postgres table")
        self.assertEqual(response, 0, "Postgres DB write failed")

    # Testing exception handling on the API call, expected is that the call
    # fails, the error is caught AND a Slack Alert is generated
    # Bad API calls w/o a key or other key parameters are returning several
    # decades of data for 2-yr t-bills instead of failing. Turning this
    # test off until Alpha Vantage issue fixes the issue.
    def bad_api_calls(self):

        bad_url = self.utilities.build_bond_url(self.MATURITY, 'fakekey')

        # get T-Bill Data
        code, slack_response = main.get_tbill_data(bad_url)

        self.assertEqual(code, 1,
                         "API call was successful, it should've failed")
        self.assertEqual(slack_response, 200,
                         "Slack alert was sent unsuccessfully")

    # Testing the data parsing function's exception handling, as due to missing
    # fields the parsing will definitely fail, so we just need to verify that a
    # Slack alert will be sent if the data is incorrect/missing fields.
    def test_data_parsing(self):

        count = 5
        test_json = {

            "title": "dogman",
            "rate": 5.45,
            "data": "march 3"

        }

        status, slack_response = self.utilities.\
            bond_data_parser_entries(test_json, count)

        self.assertEqual(status, 1,
                         "Data parsing was successful, it should've failed")
        self.assertEqual(slack_response, 200,
                         "Slack alert was sent unsuccessfully")

    # Testing the data write function's exception handling. We use valid data
    # and a valid connection but use a table name that doessn't exist.
    def test_write_data(self):

        # build Alpha Vantage URL
        url = self.utilities.build_bond_url(self.MATURITY, self.ALPHA_KEY)

        # get T-Bill Data
        data = main.get_tbill_data(url)

        # now we check that data parsing & validation works properly and only
        # returns the requested number of rows as defined by the self.COUNT
        # variable
        parsed_data = main.parse_tbill_data(data)

        # get the Postgres Connection
        connection = main.postgres_connection()

        status, slack_response = main.write_data(connection,
                                                 parsed_data, "cheese")

        self.assertEqual(status, 1,
                         "DB write was successful, it should've failed")
        self.assertEqual(slack_response, 200,
                         "Slack alert was sent unsuccessfully")


if __name__ == '__main__':
    unittest.main()
