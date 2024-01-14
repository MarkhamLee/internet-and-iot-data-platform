# Markham Lee (C) 2023
# productivity-music-stocks-weather-IoT-dashboard
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# ETL script for retrieving all the tasks from an Asana project
# pass the environmental variable with the project GID to retrieve
# data from the right project.

import os
from postgres_client import PostgresUtilities
from asana_utilities import AsanaUtilities
from logging_util import logger


# load utilities class
utilities = AsanaUtilities()


def get_asana_data(asana_client: object, gid: str) -> object:

    # retrieve data from Asana API
    try:
        data = asana_client.tasks.get_tasks_for_project(gid,
                                                        {'completed_since':
                                                         'now'},
                                                        opt_pretty=True)
        logger.info('Data successfully retrieved from Asana')
        return data

    except Exception as e:
        logger.debug(f'Asana data read unsuccessful with error: {e}')


def parse_asana_data(response: object) -> list:

    return utilities.transform_asana_data(response)


# write data to PostgreSQL
def write_data(data: object, rows: int):

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
        logger.info('PostgreSQL DB write failed')

    else:
        logger.debug(f'copy from stringio buffer complete, {rows} rows written to DB')  # noqa: E501


def main():

    PROJECT_GID = os.environ.get('GID')
    ASANA_KEY = os.environ.get('ASANA_KEY')

    # get Asana client
    asana_client = utilities.get_asana_client(ASANA_KEY)
    logger.info('Asana client created')

    # get project data
    response = get_asana_data(asana_client, PROJECT_GID)

    # parse data
    payload, total_rows = utilities.transform_asana_data(response)

    # write data
    write_data(payload, total_rows)


if __name__ == '__main__':
    main()
