# Markham Lee (C) 2023
# productivity-music-stocks-weather-IoT-dashboard
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# ETL script for retrieving all the tasks from an Asana project
# pass the environmental variable with the project GID to retrieve
# data from the right project.

import os
import sys
import pandas as pd
from datetime import datetime, timezone
from asana.rest import ApiException
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
WEBHOOK_URL = os.environ['ALERT_WEBHOOK']

# instantiate the Postgres class
postgres_utilities = PostgresUtilities()


def get_asana_data(PROJECT_GID: str) -> object:

    # get Asana client
    asana_client = utilities.get_asana_client(os.environ['ASANA_KEY'])

    extra_params = {'completed_since': 'now',
                    "opt_fields": "name, modified_at, created_at"}

    # retrieve data from Asana API
    try:
        data = asana_client.get_tasks_for_project(PROJECT_GID,
                                                  extra_params)
        logger.info('Data successfully retrieved from Asana')
        return data

    except ApiException as e:
        message = (f'Pipeline failure: Asana data read unsuccessful with error: {e}')  # noqa: E501
        logger.debug(message)
        response = etl_utilities.send_slack_webhook(WEBHOOK_URL, message)
        logger.debug(f'Slack pipeline failure alert sent with code: {response}')  # noqa: E501
        return 1, response


# calculate age and days since last update for each task
def calculate_task_age(df: object) -> object:

    # set field names to date-time format
    df[['created_at', 'modified_at']] =\
        df[['created_at', 'modified_at']].apply([pd.to_datetime])

    # Calculate the age of each task

    # set time zone, get current time and set format
    current_time = datetime.now(timezone.utc)

    # calculate the age of the alert in days
    df['task_age(days)'] = round((current_time - df['created_at']) /
                                 pd.Timedelta(days=1), 2)

    # calculate duration since last update in days
    df['task_idle(days)'] = round((current_time - df['modified_at']) /
                                  pd.Timedelta(days=1), 2)

    # adjust/clean-up date time columns
    df['created_at'] = df['created_at'].dt.strftime('%Y/%m/%d %H:%M')
    df['modified_at'] = df['modified_at'].dt.strftime('%Y/%m/%d %H:%M')

    return df


def get_db_vars() -> dict:

    TABLE = os.environ['ASANA_TABLE']

    param_dict = {
        "host": os.environ['DB_HOST'],
        "database": os.environ['DASHBOARD_DB'],
        "port": int(os.environ['POSTGRES_PORT']),
        "user": os.environ['POSTGRES_USER'],
        "password": os.environ['POSTGRES_PASSWORD']

    }

    return TABLE, param_dict


def get_postgres_client(TABLE, param_dict):

    # get database variables, connection parameters
    TABLE, param_dict = get_db_vars()

    return postgres_utilities.postgres_client(param_dict)


def write_data(connection, payload, table):

    status, response = postgres_utilities.write_data_raw(connection,
                                                         payload, table)

    if status == 1:
        message = (f'Postgres write failed for AlphaVantage T-Bill ETL with error: {response}')  # noqa: E501
        response = etl_utilities.send_slack_webhook(WEBHOOK_URL, message)
        return status, response

    else:
        logger.info(f"Postgres write successfull, {response} rows written to database")  # noqa: E501
        return status, response


def main():

    # get project ID
    PROJECT_GID = os.environ['GID']

    # get project data
    response = get_asana_data(PROJECT_GID)

    # parse data
    payload, total_rows = utilities.transform_asana_data(response)

    # calculate age of tasks
    payload = calculate_task_age(payload)

    # get Postgres connection
    TABLE, param_dict = get_db_vars()
    connection = get_postgres_client(TABLE, param_dict)

    # clear table
    response = postgres_utilities.clear_table(connection, TABLE)

    # write data
    response = write_data(connection, payload, TABLE)


if __name__ == '__main__':
    main()
