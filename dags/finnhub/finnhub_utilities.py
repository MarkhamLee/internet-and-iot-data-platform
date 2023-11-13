# (C) Markham Lee
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# Utilities for the Finnhub Finance API. Unnecessary at this point because
# the finnhub python library makes things simple, but splitting out some
# of these items anyway in anticipation of getting a wider variety of
# information from the API in the future


class FinnHubUtilities():

    # placeholder for now
    def __init__(self) -> None:
        pass

    @staticmethod
    def parse_stock_data(data: dict) -> dict:

        payload = {
            "previous_close": data['pc'],
            "last_price": data['l'],
            "change": data['pc']
        }

        return payload
