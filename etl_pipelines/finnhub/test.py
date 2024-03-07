# (C) Markham Lee 2023 - 2024
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# Test script for the Finnhub Stock Price ETL

import os
# import json
import unittest
import main
from finnhub_utilities import FinnHubUtilities
import tracemalloc
tracemalloc.start()


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
    def test_finnhub_api_good(self):

        data = main.get_prices(self.STOCK_SYMBOL)

        # get length of json object - the get prices method already
        # validates the json format, so this a double check, still,
        # if that step failed, then so would this one.
        value_count = len(data)

        # now we check that data parsing works properly
        parsed_data = main.parse_data(data)
        parsed_length = len(parsed_data)

        # Finally, we write the data to the DB. We only get a resonse
        # back if the write fails and a Slack alert is triggered.
        response = main.write_data(parsed_data)

        self.assertEqual(value_count, 8, 'json data is the wrong shape')
        self.assertEqual(parsed_length, 4, "Parsed data is the wrong shape")
        self.assertEqual(response, None, "InfluxDB write unsuccessful")

    # validate proper response if an invalid symbol is sent via the main.py
    # price method
    def test_finnhub_api_bad_symbol(self):

        data = main.get_prices('cheese')

        value = data['d']  # comes back as 'None' if the symbol is wrong
        print(value)

        self.assertEqual(value, None,
                         'Incorrect  response to invalid stock symbol')

    # Check the response of the API call if the wrong key is passed
    # expected response is a 200 code from a successful Slack alert being
    # sent. I.e. you already know the bad key won't work, so what you want to
    # happen is the successful triggering of the Slack message.
    def test_finnhub_api_bad_key(self):

        data = main.get_prices(self.STOCK_SYMBOL, 'bad-key')

        self.assertEqual(data, 200, 'Bad API Key')

    # strict type casting and checking is used to ensure that all the numbers
    # are floats. Here we send bad data composed of integers and strings to
    # see if it a) fails as expected b) triggers a Slack alert.
    # We check via sending bad data to InfluxDB as opposed to checking types
    # within the json as InfluxDB has strct type checking, so what matters is
    # if Influx perceives the data type as wrong. E.g., you need to cast fields
    # to floats, in case data comes back as "2" instead of 2.0
    def test_db_write_bad_data(self):

        data = {

            "previous_close": 'Thursday',
            "open": float(544.33),
            "last_price": int(5),
            "change": float(0.33)
        }

        response = main.write_data(data)

        self.assertEqual(response, 200, 'DB type check failed,\
                         wrong data type written to DB!')


if __name__ == '__main__':
    unittest.main()
