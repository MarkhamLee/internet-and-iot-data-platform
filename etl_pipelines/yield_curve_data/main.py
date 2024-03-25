# (C) Markham Lee 2023 - 2024
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# Pulls down the treasury yield curve data for the last five days from the
# US Treasury.
import os
import sys
import pandas as pd

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from etl_library.logging_util import logger  # noqa: E402
from etl_library.general_utilities import EtlUtilities  # noqa: E402
from etl_library.postgres_client import PostgresUtilities  # noqa: E402

postgres_utilities = PostgresUtilities()
etl_utilities = EtlUtilities()

WEBHOOK_URL = os.environ['ALERT_WEBHOOK']


def postgres_connection():

    param_dict = {
        "host": os.environ['DB_HOST'],
        "database": os.environ['DASHBOARD_DB'],
        "port": int(os.environ['POSTGRES_PORT']),
        "user": os.environ['POSTGRES_USER'],
        "password": os.environ['POSTGRES_PASSWORD']

    }

    # get Postgres connection
    return postgres_utilities.postgres_client(param_dict)


def get_yield_curve_data(url: str) -> object:

    # read data from US Treasury Dept
    try:

        df = pd.read_csv(url)
        return df

    except Exception as e:
        message = (f'Failed to download yield curve CSV with error: {e}')
        etl_utilities.send_slack_webhook(WEBHOOK_URL, message)

        # shutdown ETL process
        sys.exit()

# TODO: add step to validate the data, i.e, make sure all the fields contain
# numbers in the form of x.xx


# write data to PostgreSQL
def write_data(connection: object, data: object,  table: str):

    # write data
    # If the write fails response is the error, else it's the # of rows written
    # to Postgres.
    status, response = postgres_utilities.write_data_raw(connection,
                                                         data, table)

    if status == 1:
        message = (f'Postgres write failed for AlphaVantage T-Bill ETL with error: {response}')  # noqa: E501
        response = etl_utilities.send_slack_webhook(WEBHOOK_URL, message)
        return 1, response

    else:
        logger.info(f"Postgres write successfuly, {response} rows written to database")  # noqa: E501
        return status


def main():

    # load url to download csv from US Treasury
    # YIELD_CURVE_URL = os.environ['YIELD_CURVE_URL']
    YIELD_CURVE_URL = 'https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/all/202403?type=daily_treasury_yield_curve&field_tdr_date_value_month=202403&page&_format=csv'  # noqa: E501

    # get yield curve data
    data = get_yield_curve_data(YIELD_CURVE_URL)

    print(data)

    # get Postgres connection
    connection = postgres_connection()

    TABLE = os.environ['YIELD_CURVE_TABLE']

    # clear table
    postgres_utilities.clear_table(connection, TABLE)

    # write data
    write_data(connection, data, TABLE)


if __name__ == '__main__':
    main()
