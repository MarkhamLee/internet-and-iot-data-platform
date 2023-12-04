# Markham Lee (C) 2023
# productivity-music-stocks-weather-IoT-dashboard
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# Utility script for retrieving data from Asana

import asana
import pandas as pd


class AsanaUtilities():

    def __init__(self):

        pass

    @staticmethod
    def get_asana_client(key: str) -> object:

        client = asana.Client.access_token(key)

        return client

    @staticmethod
    def get_asana_data(client: object, project_gid: str) -> dict:

        # get project data
        data = client.tasks.get_tasks_for_project(project_gid,
                                                  {'completed_since':
                                                      'now'},
                                                  opt_pretty=True)

        # data comes back as pagination object that XCom isn't compatible
        # with, break down into a list of dictionaries
        data = [x for x in data]

        return data

    @staticmethod
    def transform_asana_data(data: object) -> object:

        # parse out task names
        task_names = [x.get('name') for x in data]

        # parse out task gids
        gids = [x.get('gid') for x in data]

        # create blank data frame
        df = pd.DataFrame(columns=['taskName', 'gid'])

        # write task names & gids to data frame
        df['gid'] = gids
        df['taskName'] = task_names

        return df
