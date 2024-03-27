# (C) Markham Lee 2023 - 2024
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# Utilities/common code for retrieving yield curve data from the US Treasury
import os
import sys
import pandas as pd

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from etl_library.logging_util import logger  # noqa: E402
from etl_library.general_utilities import EtlUtilities  # noqa: E402
etl_utilities = EtlUtilities()

WEBHOOK_URL = os.environ['ALERT_WEBHOOK']


class YieldCurveUtilities():

    # not really needed, but placing it here in anticipation of
    # future changes
    def __init__(self):

        pass

    @staticmethod
    def get_yield_curve_data(url: str) -> object:

        # read data from US Treasury Dept
        try:

            df = pd.read_csv(url)
            logger.info('Yield curve data received')
            return df

        except Exception as e:
            message = (f'Failed to download yield curve CSV with error: {e}')
            etl_utilities.send_slack_webhook(WEBHOOK_URL, message)

            # shutdown ETL process
            sys.exit()

    @staticmethod
    def clean_yield_curve_data(data: object) -> object:

        # drop any rows with missing values. We "could" just ignore in our
        # plots, but then we're not comparing "like vs like" so we'll just not
        # use the days that have incomplete data.
        df = data.dropna()

        return df
