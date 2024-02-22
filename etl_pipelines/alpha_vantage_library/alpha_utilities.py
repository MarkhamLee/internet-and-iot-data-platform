# Markham Lee (C) 2023
# productivity-music-stocks-weather-IoT-dashboard
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# Utility scripts for retrieving data from the Alpha Advantage finance API
import os
import sys
import pandas as pd

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from etl_library.logging_util import logger  # noqa: E402
from etl_library.general_utilities import EtlUtilities  # noqa: E402


class AlphaUtilities():

    def __init__(self):

        # create constants
        self.base_tbill_url = 'https://www.alphavantage.co/query?function=TREASURY_YIELD&interval=daily'  # noqa: E501
        self.bond_base = '&maturity='
        self.api_key_base = '&apikey='
        self.utilities = EtlUtilities()

    def build_bond_url(self, maturity: str, key: str) -> str:

        full_param = self.bond_base + maturity

        full_url = f'{self.base_tbill_url}{full_param}{self.api_key_base}{key}'

        return full_url

    @staticmethod
    def bond_data_parser(response: dict) -> dict:

        rate = float(response['data'][0]['value'])
        date = response['data'][0]['date']

        payload = {
            'date': date,
            'rate': rate
        }

        return payload

    # this one will retrieve n number of bond data entries
    def bond_data_parser_entries(self, data: dict, count: int):

        try:

            # split off just the treasury bill data
            subsection = data['data']
            logger.info('Subsection action completed')

            # convert json to pandas data frame and keep the first N rows
            rates = pd.DataFrame(subsection).head(count)
            logger.info('Successfully converted JSON to pandas dataframe')

            # rename columns
            rates.rename(columns={"value": "rate"}, inplace=True)

            # filter out only the rows with a number for rate
            rates = rates[pd.to_numeric(rates['rate'],
                                        errors='coerce').notnull()]
            logger.info('Filtered out rows with valid rates')

            # filter out only the rows with a valid date
            rates = rates[pd.to_datetime(rates['date'],
                                         errors='coerce').notnull()]

            logger.info(f'data parsing complete, returning {len(rates)} rows of data')  # noqa: E501

            return rates

        except Exception as e:
            WEBHOOK_URL = os.environ['ALERT_WEBHOOK']
            message = (f'ETL pipeline failure Alpha Vantage multi-day bond prices: {e}')  # noqa: E501
            logger.debug(message)
            self.utilities.send_slack_webhook(WEBHOOK_URL, message)
