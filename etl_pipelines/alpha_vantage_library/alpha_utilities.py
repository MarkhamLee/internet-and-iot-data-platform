# Markham Lee (C) 2023
# productivity-music-stocks-weather-IoT-dashboard
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# Utility scripts for retrieving data from the Alpha Advantage finance API


class AlphaUtilities():

    def __init__(self):

        # create constants
        self.base_tbill_url = 'https://www.alphavantage.co/query?function=TREASURY_YIELD&interval=daily'  # noqa: E501
        self.bond_base = '&maturity='
        self.api_key_base = '&apikey='

    def build_bond_url(self, maturity: str, key: str) -> str:

        full_param = self.bond_base + maturity

        full_url = f'{self.base_tbill_url}{full_param}{self.api_key_base}{key}'

        return full_url

    @staticmethod
    def bond_data_parser(response: dict) -> dict:

        rate = float(response['data'][0]['value'])
        date = response['data'][0]['date']

        payload = {
            'rate': rate,
            'date': date
        }

        return payload
