# (C) Markham Lee 2023 - 2024
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# container for loading historical yield curve data from the US Treasury
import os
import sys
import pandas as pd

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


# filters the dataframe down to the first/most recent row
def parse_data(data: object) -> object:

    return data.iloc[:1]


# Ensures we only attempt a database write if we have data that's newer
# than what's already in the raw yield curve data table.
def check_dates(connection: object, table: str, data: object) -> int:

    cursor = connection.cursor()

    # execute query
    cursor.execute(f"SELECT * FROM public.{table} ORDER BY date DESC LIMIT 1")  # noqa: E501

    # query DB
    query_result = cursor.fetchall()

    # get column names
    colnames = [desc[0] for desc in cursor.description]

    # convert to dataframe
    df = pd.DataFrame(query_result, columns=colnames)

    # convert date column to date-time format
    df.loc[:, 'date'] = pd.to_datetime(df['date']).dt.date
    data.loc[:, 'Date'] = pd.to_datetime(data['Date']).dt.date

    # check for new data
    if data['Date'][0] > df['date'][0]:
        logger.info('New yield curve data available')
        return 0
    else:
        logger.info('No new yield curve data available, exiting...')
        sys.exit()


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

    # parse data, we only need the most recent row
    subset_df = parse_data(cleaned_data)

    # get Postgres connection
    connection = postgres_connection()

    # get table
    TABLE = os.environ['RAW_YIELD_CURVE_TABLE']

    # check to see if there is new data before writing to the DB
    # i.e., we don't want to write duplicate rows
    data_status = check_dates(connection, TABLE, subset_df)

    if data_status == 0:
        # write data
        write_data(connection, subset_df, TABLE)


if __name__ == '__main__':
    main()
