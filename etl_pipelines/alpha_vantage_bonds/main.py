# Markham Lee (C) 2023
# productivity-music-stocks-weather-IoT-dashboard
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# This pipeline retrieves the daily t-bill rate, valdiates that it's newer
# than the data that's already in the database and if it's newer updates the DB
# with the latest rate.

import os
import sys
import requests
import pandas as pd
from io import StringIO

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from alpha_vantage_library.alpha_utilities import AlphaUtilities  # noqa: E402
from etl_library.logging_util import logger  # noqa: E402
from etl_library.postgres_client import PostgresUtilities  # noqa: E402
from etl_library.general_utilities import EtlUtilities  # noqa: E402


utilities = AlphaUtilities()
postgres_utilities = PostgresUtilities()
etl_utilities = EtlUtilities()

WEBHOOK_URL = os.environ.get('ALERT_WEBHOOK')


def get_tbill_data(url: str) -> dict:

    try:
        response = requests.get(url)
        logger.info('Bond data retrieved successfully')
        return response.json()

    # you can only hit the API 26x a day, so if it fails, just exit and
    # check the error message, rather than retrying and using up the day's
    # attempts
    except Exception as e:
        message = (f'Pipeline failure Alert: Bond data retrieval attempt failed with error: {e}')  # noqa: E501
        logger.info(message)
        etl_utilities.send_slack_webhook(WEBHOOK_URL, message)
        sys.exit()


def parse_tbill_data(data: dict) -> object:

    # this also serves as our data validation step, the below steps won't work
    # if the data format is incorrect, fields are missing, etc.

    try:
        data = utilities.bond_data_parser(data)
        logger.info('Bond data parsed successfully')

    # we exit once the error is logged after encountering any major
    # exception so as to not run afoul of API limits
    except Exception as e:
        message = (f'Pipeline failure alert: data parsing failed due to error: {e}')  # noqa: E501
        logger.debug(message)
        etl_utilities.send_slack_webhook(WEBHOOK_URL, message)

    return data


def check_dates(connection: object, table: str, data: object) -> int:

    cursor = connection.cursor()

    columns = list(data.columns)

    # execute query
    cursor.execute(f"SELECT * FROM {table} ORDER BY date DESC LIMIT 1")

    # query DB
    query_result = cursor.fetchall()

    # convert to dataframe
    df = pd.DataFrame(query_result, columns=columns)

    # convert date column to date-time format
    df['date'] = pd.to_datetime(df['date']).dt.date
    data['date'] = pd.to_datetime(data['date']).dt.date

    # compare

    if data['date'][0] > df['date'][0]:
        return 1
    else:
        return 0


# strict enforcement of what columns are used ensures data quality
# avoids issues where tab delimiting can create erroneous empty columns
# in the data frame
def prepare_payload(payload: object, columns: list) -> object:

    buffer = StringIO()

    # explicit column definitions + tab as the delimiter allow us to ingest
    # text data with punctuation  without having situations where a comma
    # in a sentence is treated as new column or causes a blank column to be
    # created.
    payload.to_csv(buffer, index=False, sep='\t', columns=columns,
                   header=False)
    buffer.seek(0)

    return buffer


# write data to PostgreSQL
def write_data(data: object, connection: object, table: str):

    # get dataframe columns for managing data quality
    columns = list(data.columns)

    # count rows
    row_count = len(data)

    # prepare payload
    buffer = prepare_payload(data, columns)

    # clear table
    # response = postgres_utilities.clear_table(connection, table)

    # write data
    response = postgres_utilities.write_data(connection, buffer, table)

    if response != 0:
        message = (f'write failed with error: {response}')
        logger.debug(message)
        etl_utilities.send_slack_webhook(WEBHOOK_URL, message)

    else:
        logger.debug(f"copy_from_stringio() done, {row_count} rows written to database")  # noqa: E501


def main():

    # Alpha Vantage Key
    ALPHA_KEY = os.environ.get('ALPHA_KEY')

    # Bond Maturity
    MATURITY = os.environ.get('BOND_MATURITY')

    # TABLE
    TABLE = os.environ.get('TBILL_TABLE')

    # Build URL
    url = utilities.build_bond_url(MATURITY, ALPHA_KEY)

    # get bond data
    data = get_tbill_data(url)

    # parse and transform data
    data = pd.json_normalize(parse_tbill_data(data))

    param_dict = {
        "host": os.environ.get('DB_HOST'),
        "database": os.environ.get('DASHBOARD_DB'),
        "port": int(os.environ.get('POSTGRES_PORT')),
        "user": os.environ.get('POSTGRES_USER'),
        "password": os.environ.get('POSTGRES_PASSWORD')

    }

    # get Postgres connection
    connection = postgres_utilities.postgres_client(param_dict)

    # check existing data for duplicates
    if check_dates(connection, TABLE, data) == 1:
        write_data(data, connection, TABLE)

    else:
        logger.info('new bond rates not available, exiting..')
        exit()

    # write data


if __name__ == '__main__':
    main()
