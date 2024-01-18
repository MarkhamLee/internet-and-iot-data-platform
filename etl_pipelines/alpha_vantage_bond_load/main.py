# Markham Lee (C) 2023
# productivity-music-stocks-weather-IoT-dashboard
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# This script retrieves several years from T-Bill data from the Alpha Vantage
# API. This script + container is used to load all the historical data, prior
# to running a separate script that will just get the data from the prior day

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


utilities = AlphaUtilities()


def get_tbill_data(url: str) -> dict:

    try:
        response = requests.get(url)
        logger.info('Bond data retrieved successfully')
        return response.json()

    # you can only hit the API 26x a day, so if it fails, just exit and
    # check the error message, rather than retrying and using up the day's
    # attempts
    except Exception as e:
        logger.info(f'Bond data retrieval attempt failed with error: {e}')
        exit()


def parse_tbill_data(data: dict) -> object:

    # this also serves as our data validation step, the below steps won't work
    # if the data format is incorrect, fields are missing, etc.

    try:

        # split off just the treasury bill data
        subsection = data['data']
        logger.info('Subsection action completed')

        # convert json to pandas data frame and keep the first 1200 rows
        rates = pd.DataFrame(subsection).head(1200)
        logger.info('Successfully converted JSON to pandas dataframe')

        # rename columns
        rates.rename(columns={"value": "rate"}, inplace=True)

        # filter out only the rows with a number for rate
        rates = rates[pd.to_numeric(rates['rate'], errors='coerce').notnull()]
        logger.info('Filtered out rows with valid rates')

        # filter out only the rows with a valid date
        rates = rates[pd.to_datetime(rates['date'], errors='coerce').notnull()]
        logger.info('Filtered out rows with valid dates')
        logger.info('Data cleaning, parsing, et, al complete')

    except Exception as e:
        logger.debug(f'Data parsing failed due to error: {e}')

    return rates


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
def write_data(data: object):

    postgres_utilities = PostgresUtilities()

    TABLE = os.environ.get('TBILL_TABLE')

    param_dict = {
        "host": os.environ.get('DB_HOST'),
        "database": os.environ.get('DASHBOARD_DB'),
        "port": int(os.environ.get('POSTGRES_PORT')),
        "user": os.environ.get('POSTGRES_USER'),
        "password": os.environ.get('POSTGRES_PASSWORD')

    }

    # get dataframe columns for managing data quality
    columns = list(data.columns)

    row_count = len(data)

    # prepare payload
    buffer = prepare_payload(data, columns)

    # get connection client
    connection = postgres_utilities.postgres_client(param_dict)

    # clear table
    response = postgres_utilities.clear_table(connection, TABLE)

    # write data
    response = postgres_utilities.write_data(connection, buffer, TABLE)

    if response != 0:
        logger.info(f'write failed with error {response}')

    else:
        logger.debug(f"copy_from_stringio() done, {row_count} rows written to database")  # noqa: E501


def main():

    # Alpha Vantage Key
    ALPHA_KEY = os.environ.get('ALPHA_KEY')

    # Bond Maturity
    MATURITY = os.environ.get('BOND_MATURITY')

    utilities = AlphaUtilities()

    # Build URL
    url = utilities.build_bond_url(MATURITY, ALPHA_KEY)

    # get bond data

    data = get_tbill_data(url)

    # parse and transform data
    data = parse_tbill_data(data)

    # write data
    write_data(data)


if __name__ == '__main__':
    main()
