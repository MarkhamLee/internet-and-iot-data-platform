# Markham Lee (C) 2023
# productivity-music-stocks-weather-IoT-dashboard
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# Utility script for retrieving data from Asana

import asana
import pandas as pd
# import logging
from logging_util import logger


class AsanaUtilities():

    def __init__(self):

        pass

    @staticmethod
    def get_asana_client(key: str) -> object:

        return asana.Client.access_token(key)

    @staticmethod
    def transform_asana_data(data: object) -> object:

        # this serves as a data validation step - the parsing will fail if
        # the pagination object isn't in the expected format, have the right
        # fields, etc.

        try:
            # comes back as pagination object, breakdown into a
            # list of dictionaries
            parsed_data = [x for x in data]

            # parse out task names
            task_names = [x.get('name') for x in parsed_data]

            # parse out task gids
            gids = [x.get('gid') for x in parsed_data]

            logger.info('data parsing/extraction successful')

        except Exception as e:
            logger.debug(f'attempted parsing of data failed, likely data corruption due to error: {e}')  # noqa: E501

        # create blank data frame
        df = pd.DataFrame(columns=['taskName', 'gid'])

        # write task names & gids to data frame
        df['gid'] = gids
        df['taskName'] = task_names

        total_rows = len(df)

        return df, total_rows
