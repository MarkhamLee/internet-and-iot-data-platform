
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

        payload = {
            "open": response['Global Quote']['02. open'],
            "price": response['Global Quote']['05. price'],
            "change_per": response['Global Quote']['10. change percent'],
            "change": response['Global Quote']['09. change']
        }

        return payload
