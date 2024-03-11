# Markham Lee (C) 2023
# productivity-music-stocks-weather-IoT-dashboard
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# This pipeline retrieves t-bill rates for the last six days and then writes it
# Postgres.
import os
import sys
import requests

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from alpha_vantage_library.alpha_utilities import AlphaUtilities  # noqa: E402
from etl_library.logging_util import logger  # noqa: E402
from etl_library.postgres_client import PostgresUtilities  # noqa: E402
from etl_library.general_utilities import EtlUtilities  # noqa: E402


utilities = AlphaUtilities()
postgres_utilities = PostgresUtilities()
etl_utilities = EtlUtilities()

WEBHOOK_URL = os.environ['ALERT_WEBHOOK']


def load_variables():

    # Alpha Vantage Key
    ALPHA_KEY = os.environ['ALPHA_KEY']

    # Bond Maturity
    MATURITY = os.environ['BOND_MATURITY']

    # TABLE
    TABLE = os.environ['TBILL_TABLE']

    return ALPHA_KEY, MATURITY, TABLE


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


def get_tbill_data(url: str) -> dict:

    # get T-Bill Data
    response = requests.get(url)

    try:
        response.raise_for_status()

    except requests.exceptions.HTTPError as e:
        message = (f'Pipeline failure Alert: Bond data retrieval attempt failed with error: {e}')  # noqa: E501
        logger.debug(message)
        response = etl_utilities.send_slack_webhook(WEBHOOK_URL, message)
        return 1, response

    logger.info('Bond data retrieved successfully')
    return response.json()


def parse_tbill_data(data: dict) -> object:

    # this also serves as our data validation step, the below steps won't work
    # if the data format is incorrect, fields are missing, etc.

    COUNT = int(os.environ['COUNT'])

    return utilities.bond_data_parser_entries(data, COUNT)


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

    # load variables
    ALPHA_KEY, MATURITY, TABLE = load_variables()

    # Build URL
    url = utilities.build_bond_url(MATURITY, ALPHA_KEY)

    # get bond data
    data = get_tbill_data(url)

    # parse and transform data
    parsed_data = parse_tbill_data(data)

    # get Postgres connection
    connection = postgres_connection()

    # clear table
    postgres_utilities.clear_table(connection, TABLE)

    # write data
    write_data(connection, parsed_data, TABLE)


if __name__ == '__main__':
    main()
