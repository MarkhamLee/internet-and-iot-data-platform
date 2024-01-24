# Markham Lee (C) 2023
# productivity-music-stocks-weather-IoT-dashboard
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# Utility script for retrieving data from Asana

import asana
import os
import sys
import pandas as pd

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from etl_library.logging_util import logger  # noqa: E402
from etl_library.general_utilities import EtlUtilities  # noqa: E402

etl_utilities = EtlUtilities()
WEBHOOK_URL = os.environ.get('ALERT_WEBHOOK')


class AsanaUtilities():

    def __init__(self):

        pass

    @staticmethod
    def get_asana_client(key: str) -> object:

        try:
            client = asana.Client.access_token(key)
            logger.info('Asana client created')
            return client

        except Exception as e:
            message = (f'Pipeline failure: Asana client creation failed with error: {e}')  # noqa: E501
            logger.debug(message)
            response = etl_utilities.send_slack_webhook(WEBHOOK_URL, message)
            logger.debug(f'Slack alert sent with code: {response}')

    @staticmethod
    def transform_asana_data(data: object) -> object:

        try:

            # this serves as a data validation step - the parsing will fail if
            # the pagination object isn't in the expected format, have the
            # right fields, etc.

            # comes back as pagination object, breakdown into a
            # list of dictionaries
            parsed_data = [x for x in data]

            # parse out task names
            task_names = [x.get('name') for x in parsed_data]

            # parse out task gids
            gids = [x.get('gid') for x in parsed_data]

            logger.info('data parsing/extraction successful')

            # create blank data frame
            df = pd.DataFrame(columns=['taskName', 'gid'])

            # write task names & gids to data frame
            df['gid'] = gids
            df['taskName'] = task_names

            total_rows = len(df)

            logger.info('Asana data parsed/extracted successfully')

            return df, total_rows

        except Exception as e:
            message = (f'Pipeline failure: Asana data extraction failed with error: {e}')  # noqa: E501
            logger.info(message)
            response = etl_utilities.send_slack_webhook(WEBHOOK_URL, message)
            logger.info(f'Slack alert published successfully with code: {response}')  # noqa: E501
