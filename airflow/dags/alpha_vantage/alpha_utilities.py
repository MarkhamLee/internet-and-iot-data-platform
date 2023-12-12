# Markham Lee (C) 2023
# productivity-music-stocks-weather-IoT-dashboard
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# Utility scripts for retrieving data from the Alpha Advantage finance API

class AlphaUtilities():

    def __init__(self):

        # create constants
        self.base_url = 'https://www.alphavantage.co/query?function=GLOBAL_QUOTE'  # noqa: E501
        self.base_tbill_url = 'https://www.alphavantage.co/query?function=TREASURY_YIELD&interval=daily'  # noqa: E501
        self.quote_base = '&symbol='
        self.bond_base = '&maturity='
        self.api_key_base = '&apikey='

    def build_url(self, stock: str, key: str) -> str:

        full_symbol = f'{self.quote_base}{stock}'

        full_url = f'{self.base_url}{full_symbol}{self.api_key_base}{key}'

        return full_url

    def build_bond_url(self, maturity: str, key: str) -> str:

        full_param = self.bond_base + maturity

        full_url = f'{self.base_tbill_url}{full_param}{self.api_key_base}{key}'

        return full_url

    @staticmethod
    def get_financial_data(url: str) -> dict:

        import requests  # noqa: E402

        # get financial data
        response = requests.get(url)
        response = response.json()

        return response

    @staticmethod
    def stock_data_parser(response: dict) -> dict:

        opening_price = float(response['Global Quote']['02. open'])
        price = float(response['Global Quote']['05. price'])
        change = float(response['Global Quote']['09. change'])
        change_per = round((change/opening_price), 4) * 100

        payload = {
            "open": opening_price,
            "price": price,
            "change_per": change_per,
            "change": change
        }

        return payload

    @staticmethod
    def bond_data_parser(response: dict) -> dict:

        rate = float(response['data'][0]['value'])
        date = response['data'][0]['date']

        payload = {
            'rate': rate,
            'date': date
        }

        return payload
