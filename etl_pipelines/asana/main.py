# Markham Lee (C) 2023
# productivity-music-stocks-weather-IoT-dashboard
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# ETL script for retrieving all the tasks from an Asana project
# pass the environmental variable with the project GID to retrieve
# data from the right project.

import os
import sys
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


def get_asana_data() -> object:

    # get project ID
    PROJECT_GID = os.environ.get('GID')

    # get Asana client
    asana_client = utilities.get_asana_client(os.environ.get('ASANA_KEY'))

    # retrieve data from Asana API
    try:
        data = asana_client.tasks.get_tasks_for_project(PROJECT_GID,
                                                        {'completed_since':
                                                         'now', "opt_fields": "name, modified_at, created_at"},  # noqa: E501
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


def get_asana_vars() -> dict:

    TABLE = os.environ.get('ASANA_TABLE')

    param_dict = {
        "host": os.environ.get('DB_HOST'),
        "database": os.environ.get('DASHBOARD_DB'),
        "port": int(os.environ.get('PORT')),
        "user": os.environ.get('POSTGRES_USER'),
        "password": os.environ.get('POSTGRES_PASSWORD')

    }

    return TABLE, param_dict


def main():

    # get project data
    response = get_asana_data()

    # parse data
    payload, total_rows = utilities.transform_asana_data(response)

    # calculate age of tasks
    payload = utilities.calculate_task_age(payload)

    # get asana variables
    TABLE, param_dict = get_asana_vars()

    postgres_utilities = PostgresUtilities()

    # get connection client
    connection = postgres_utilities.postgres_client(param_dict)

    # clear table
    response = postgres_utilities.clear_table(connection, TABLE)

    # write data
    response = postgres_utilities.write_data_raw(connection, payload, TABLE)


if __name__ == '__main__':
    main()
