# (C) Markham Lee
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# Utilities for the Finnhub Finance API. Unnecessary at this point because
# the finnhub python library makes things simple, but splitting out some
# of these items anyway in anticipation of getting a wider variety of
# information from the API in the future

from airflow.models import Variable


class FinnHubUtilities():

    def __init__(self) -> None:
        pass

    @staticmethod
    def get_stock_data(symbol: str) -> dict:

        import finnhub  # noqa: E402
        from jsonschema import validate  # noqa: E402

        FINNHUB_KEY = Variable.get('finnhub_key_secret')

        # import data schema for validation
        SCHEMA = Variable.get(key='finnhub_schema',
                              deserialize_json=True)

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
