# Markham Lee (C) 2023
# productivity-music-stocks-weather-IoT-dashboard
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# ETL script for retrieving all the tasks from an Asana project
# CLI: python3 file_name + project ID

import os
import sys
from asana_utilities import AsanaUtilities
from postgres_client import PostgresUtilities

# load utilities class
utilities = AsanaUtilities()


def get_asana_data(asana_client: object, gid: str) -> object:

    return asana_client.tasks.get_tasks_for_project(gid,
                                                    {'completed_since':
                                                     'now'}, opt_pretty=True)


def parse_asana_data(response: object) -> list:

    return utilities.transform_asana_data(response)


# just prints out data for now to verify everything is working
def write_data(payload: object, TABLE: str):

    TABLE = 'simple_asana'

    param_dict = {
        "host": os.environ.get('SANDBOX_SERVER'),
        "database": os.environ.get('DASHBOARD_DB'),
        "port": int(os.environ.get('PORT')),
        "user": os.environ.get('POSTGRES_USER'),
        "password": os.environ.get('POSTGRES_PASSWORD')

    }

    data_utilities = PostgresUtilities()
    response = data_utilities.write_df_postgres_clear(payload, TABLE,
                                                      param_dict)

    if response != 0:
        print("write_failed")

    else:
        print(f"copy_from_stringio() done, {payload} written to database")


def main():

    # parse command line arguments
    args = sys.argv[1:]

    TABLE = 'simple_asana'

    PROJECT_GID = (args[0])
    ASANA_KEY = os.environ.get('ASANA_KEY')

    # get Asana Client
    asana_client = utilities.get_asana_client(ASANA_KEY)

    # get project data
    response = get_asana_data(asana_client, PROJECT_GID)

    # parse data
    payload = utilities.transform_asana_data(response)

    # write data
    write_data(payload, TABLE)


if __name__ == '__main__':
    main()
