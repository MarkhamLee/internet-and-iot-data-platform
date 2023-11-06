

class WeatherUtilities():

    def __init__(self):

        # create constants
        self.units = '&units=imperial'
        self.city = 'seattle'
        self.lat = 47.6
        self.long = -122.3321
        self.base_url = 'http://api.openweathermap.org/data/2.5/'

    @staticmethod
    def parse_air_data(data: dict) -> dict:

        qual_data = data['list'][0]['components']

        payload = {
            "co": qual_data['co'],
            "pm2": qual_data['pm2_5'],
            "pm10": qual_data['pm10']
        }

        return payload

    def build_url_air(self, endpoint: str, key: str) -> str:

        url = f'{self.base_url}{endpoint}appid={key}&lat={self.lat}&lon={self.long}'  # noqa: E501

        return url

    def build_url_weather(self, key: str, endpoint: str) -> str:

        url = self.base_url + endpoint + 'appid=' + key + "&q=" +\
            self.city + self.units

        return url

    @staticmethod
    def weather_parser(response: dict) -> dict:

        payload = {
            "weather": response['weather'][0]['main'],
            "weather_desc": response['weather'][0]['description'],
            "temp": float(response['main']['temp']),
            "feels_like": float(response['main']['feels_like']),
            "temp_low": float(response['main']['temp_min']),
            "temp_high": float(response['main']['temp_max']),
            "pressure": float(response['main']['pressure']),
            "humidity": float(response['main']['humidity']),
            "wind_speed": float(response['wind']['speed']),
            "timestamp": response['dt']
        }

        return payload

    @staticmethod
    def get_weather_data(url: str) -> dict:

        import requests  # noqa: E402

        # get weather data
        response = requests.get(url)
        response = response.json()

        return response
