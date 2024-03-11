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
WEBHOOK_URL = os.environ['ALERT_WEBHOOK']


class AsanaUtilities():

    def __init__(self):

        pass

    @staticmethod
    def get_asana_client(key: str) -> object:

        try:

            configuration = asana.Configuration()
            configuration.access_token = key
            client = asana.ApiClient(configuration)
            api_instance = asana.TasksApi(client)

            logger.info('Asana client created')
            return api_instance

        except Exception as e:
            message = (f'Pipeline failure: Asana client creation failed with error: {e}')  # noqa: E501
            logger.debug(message)
            response = etl_utilities.send_slack_webhook(WEBHOOK_URL, message)
            logger.debug(f'Slack alert sent with code: {response}')

    # data validation & parsing - the Asana pagination object takes a few more
    # steps than usual compared to most public APIs.
    @staticmethod
    def transform_asana_data(data: object) -> object:

        try:

            # Asana data comes back as pagination object, the list
            # comprehension breaks it down into a list of dictionaries
            # that we can treat as a json and convert it to a panda
            # data frame in one go

            df = pd.json_normalize([x for x in data])

            # drop the 'gid' field and re-order the columns
            df = df[['name', 'created_at', 'modified_at']]

            total_rows = len(df)

            logger.info('Asana data parsed successfully')

            return df, total_rows

        except Exception as e:
            message = (f'Pipeline failure: Asana data extraction failed with error, likely data corruption: {e}')  # noqa: E501
            logger.debug(message)
            response = etl_utilities.send_slack_webhook(WEBHOOK_URL, message)
            logger.info(f'Slack alert published successfully with code: {response}')  # noqa: E501
