# (C) Markham Lee 2023 - 2024
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# Utilities for the Finnhub Finance API. Unnecessary at this point because
# the finnhub python library makes things simple, but splitting out some
# of these items anyway in anticipation of getting a wider variety of
# information from the API in the future

import os
import finnhub


class FinnHubUtilities():

    def __init__(self) -> None:
        pass

    # making the key the default value allows us to pass different keys and/or
    # wrong keys durinig testing.
    @staticmethod
    def get_stock_data(symbol: str,
                       FINNHUB_KEY=os.environ.get('FINNHUB_SECRET')) -> dict:

        # create client
        client = finnhub.Client(FINNHUB_KEY)

        # get data
        data = client.quote(symbol)

        return data

    @staticmethod
    def parse_stock_data(data: dict) -> dict:

        payload = {
            "previous_close": float(data['pc']),
            "open": float(data['o']),
            "last_price": float(data['l']),
            "change": float(data['dp'])
        }

        return payload
