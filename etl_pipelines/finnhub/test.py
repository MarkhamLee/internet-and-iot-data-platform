# (C) Markham Lee 2023 - 2024
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# Test script for the Finnhub Stock Price ETL

import os
import sys
import unittest
import main

import tracemalloc
tracemalloc.start()

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from finnhub_libraries.finnhub_utilities import FinnHubUtilities  # noqa: E402


class FinnhubTesting(unittest.TestCase):

    @classmethod
    def setUpClass(self):

        self.STOCK_SYMBOL = os.environ['STOCK_SYMBOL']
        self.utilities = FinnHubUtilities()

    # End to end test, we validate that the API call works and we're
    # able to write successfully to InfluxDB. The ETL pipeline already
    # has data format validation and type checking/casting built in,
    # i.e. it won't work with the wrong data type, BUT,
    # we double check json shape to be doubly sure.
    def test_finnhub_api_(self):

        data = main.get_prices(self.STOCK_SYMBOL)

        # validate the returned payload
        validation_status = main.validate_json_payload(data)

        # now we check that data parsing works properly
        parsed_data = main.parse_data(data)
        parsed_length = len(parsed_data)

        # Finally, we write the data to the DB. We only get a resonse
        # back if the write fails and a Slack alert is triggered.
        response = main.write_data(parsed_data)

        self.assertEqual(validation_status, 0,
                         'json data is missing fields and/or has errors')
        self.assertEqual(parsed_length, 4, "Parsed data is the wrong shape")
        self.assertEqual(response, None, "InfluxDB write unsuccessful")

    # Check the response of the API call if the wrong key is passed
    # expected response is a 200 code from a successful Slack alert being
    # sent. I.e. you already know the bad key won't work, so what you want to
    # happen is the successful triggering of the Slack message.
    def test_finnhub_api_bad_key(self):

        data = main.get_prices(self.STOCK_SYMBOL, 'bad-key')

        self.assertEqual(data, 200, 'Bad API Key')

    # Validate the json schema by purposely sending a bad data payload
    # to be compared against the data schema for this ETL.
    def test_db_write_bad_data(self):

        data = {

            "previous_close": 'Thursday',
            "open": "Lateralus",
            "last_price": int(5),
            "change": float(0.33)
        }

        status, slack_response = main.validate_json_payload(data)

        self.assertEqual(status, 1,
                         "Data validation suceeded, it should've failed")
        self.assertEqual(slack_response, 200, "Slack alert failed to send")


if __name__ == '__main__':
    unittest.main()
