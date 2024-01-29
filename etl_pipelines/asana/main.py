# Markham Lee (C) 2023
# productivity-music-stocks-weather-IoT-dashboard
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# ETL script for retrieving all the tasks from an Asana project
# pass the environmental variable with the project GID to retrieve
# data from the right project.

import os
import sys
from io import StringIO
from asana_utilities import AsanaUtilities

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from etl_library.postgres_client import PostgresUtilities  # noqa: E402
from etl_library.logging_util import logger  # noqa: E402
from etl_library.general_utilities import EtlUtilities  # noqa: E402

# Load Asana utilities class
utilities = AsanaUtilities()

# Load general utilities
etl_utilities = EtlUtilities()

# load Slack Webhook URL variable for sending pipeline failure alerts
WEBHOOK_URL = os.environ.get('ALERT_WEBHOOK')


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
        message = (f'Pipeline failure: Asana data read unsuccessful with error: {e}')  # noqa: E501
        logger.debug(message)
        response = etl_utilities.send_slack_webhook(WEBHOOK_URL, message)
        logger.debug(f'Slack pipeline failure alert sent with code: {response}')  # noqa: E501


# extracting data from the returned object + data validation
def parse_asana_data(response: object) -> list:

    return utilities.transform_asana_data(response)


@staticmethod
def prepare_payload(payload: object, columns: list) -> object:

    buffer = StringIO()

    # explicit column definitions + tab as the delimiter allow us to ingest
    # text data with punctuation  without having situations where a comma
    # in a sentence is treated as new column or causes a blank column to be
    # created.
    payload.to_csv(buffer, index_label='id', sep='\t', columns=columns,
                   header=False)
    buffer.seek(0)

    logger.info('CSV buffer created successfully')

    return buffer


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

    # prepare payload
    buffer = prepare_payload(data, columns)

    # get connection client
    connection = postgres_utilities.postgres_client(param_dict)

    # clear table
    response = postgres_utilities.clear_table(connection, TABLE)

    # write data
    response = postgres_utilities.write_data(connection, buffer, TABLE)

    if response != 0:
        message = 'Pipeline Failure: PostgreSQL DB write failed'
        logger.info(message)
        response = etl_utilities.send_slack_webhook(message)
        logger.debug(f'Slack pipeline alert sent with code: {response}')

    else:
        logger.debug(f'copy from stringio buffer complete, {rows} rows written to DB')  # noqa: E501


def main():

    PROJECT_GID = os.environ.get('GID')
    ASANA_KEY = os.environ.get('ASANA_KEY')

    # get Asana client
    asana_client = utilities.get_asana_client(ASANA_KEY)

    # get project data
    response = get_asana_data(asana_client, PROJECT_GID)

    # parse data
    payload, total_rows = utilities.transform_asana_data(response)

    # write data
    write_data(payload, total_rows)


if __name__ == '__main__':
    main()
