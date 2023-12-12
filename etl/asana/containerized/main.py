# Markham Lee (C) 2023
# productivity-music-stocks-weather-IoT-dashboard
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# ETL script for retrieving all the tasks from an Asana project
# CLI: python3 file_name + project ID

import os
import sys
from asana_utilities import AsanaUtilities
import time

# this allows us to import modules from the parent directory
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)


from postgres_client import PostgresUtilities  # noqa: E402

# load utilities class
utilities = AsanaUtilities()


def get_asana_data(asana_client: object, gid: str) -> object:

    return asana_client.tasks.get_tasks_for_project(gid,
                                                    {'completed_since':
                                                     'now'}, opt_pretty=True)


def parse_asana_data(response: object) -> list:

    return utilities.transform_asana_data(response)


# write data to PostgreSQL
def write_data(data: object):

    TABLE = os.environ.get('ASANA_TABLE')

    param_dict = {
        "host": os.environ.get('DB_HOST'),
        "database": os.environ.get('DASHBOARD_DB'),
        "port": int(os.environ.get('PORT')),
        "user": os.environ.get('POSTGRES_USER'),
        "password": os.environ.get('POSTGRES_PASSWORD')

    }

    postgres_utilities = PostgresUtilities()

    # get dataframe columns for managing data quality
    columns = list(data.columns)

    # get connection client
    connection = postgres_utilities.postgres_client(param_dict)

    # prepare payload
    buffer = postgres_utilities.prepare_payload(data, columns)

    # clear table
    response = postgres_utilities.clear_table(connection, TABLE)

    # write data
    response = postgres_utilities.write_data(connection, buffer, TABLE)

    if response != 0:
        print("write_failed")

    else:
        print(f"copy_from_stringio() done, {data} written to database")


def main():

    PROJECT_GID = os.environ.get('GID')
    ASANA_KEY = os.environ.get('ASANA_KEY')
    INTERVAL = int(os.environ['INTERVAL'])

    # get Asana Client
    asana_client = utilities.get_asana_client(ASANA_KEY)

    while True:

        # get project data
        response = get_asana_data(asana_client, PROJECT_GID)

        # parse data
        payload = utilities.transform_asana_data(response)

        # write data
        write_data(payload)

        time.sleep(INTERVAL)


if __name__ == '__main__':
    main()
