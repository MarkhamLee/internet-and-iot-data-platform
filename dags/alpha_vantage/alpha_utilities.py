
class AlphaUtilities():

    def __init__(self):

        # create constants
        self.base_url = 'https://www.alphavantage.co/query?function=GLOBAL_QUOTE'  # noqa: E501
        self.quote_base = '&symbol='
        self.api_key_base = '&apikey='

    def build_url(self, stock: str, key: str) -> str:

        full_symbol = f'{self.quote_base}{stock}'

        full_url = f'{self.base_url}{full_symbol}{self.api_key_base}{key}'

        return full_url

    @staticmethod
    def get_stock_data(url: str) -> dict:

        import requests  # noqa: E402

        # get weather data
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
