# (C) Markham Lee
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# Utilities for the Finnhub Finance API. Unnecessary at this point because
# the finnhub python library makes things simple, but splitting out some
# of these items anyway in anticipation of getting a wider variety of
# information from the API in the future

import os
import json
import finnhub
from jsonschema import validate


class FinnHubUtilities():

    def __init__(self) -> None:
        pass

    @staticmethod
    def get_stock_data(symbol: str) -> dict:

        FINNHUB_KEY = os.environ.get('finnhub_key_secret')

        # import data schema for validation
        with open('stock_prices_payload.json') as file:
            SCHEMA = json.load(file)

        # create client
        client = finnhub.Client(FINNHUB_KEY)

        # get data
        data = client.quote(symbol)

        # validate data
        validate(instance=data, schema=SCHEMA)

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
