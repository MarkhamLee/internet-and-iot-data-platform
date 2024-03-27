# (C) Markham Lee 2023 - 2024
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# container for loading historical yield curve data from the US Treasury
import os
import sys

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from etl_library.logging_util import logger  # noqa: E402
from etl_library.general_utilities import EtlUtilities  # noqa: E402
from etl_library.postgres_client import PostgresUtilities  # noqa: E402
from yield_curve_library.yield_curve_utilities\
    import YieldCurveUtilities  # noqa: E402

postgres_utilities = PostgresUtilities()
etl_utilities = EtlUtilities()
yield_utilities = YieldCurveUtilities()

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
    YIELD_CURVE_URL = os.environ['YIELD_CURVE_URL']

    # get yield curve data
    data = yield_utilities.get_yield_curve_data(YIELD_CURVE_URL)

    # clean up data/remove missing fields, etc.
    cleaned_data = yield_utilities.clean_yield_curve_data(data)

    # get Postgres connection
    connection = postgres_connection()

    TABLE = os.environ['RAW_YIELD_CURVE_TABLE']

    # write data
    write_data(connection, cleaned_data, TABLE)


if __name__ == '__main__':
    main()
