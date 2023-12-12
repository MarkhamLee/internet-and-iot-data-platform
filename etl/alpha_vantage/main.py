# Markham Lee (C) 2023
# productivity-music-stocks-weather-IoT-dashboard
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# This script retrieves two year T-Bill data from the Alpha Vantage API
# This script + container is used to load all the historical data, prior to
# running a separate script that will just get the data from the prior day

import os
import requests
import pandas as pd
from alpha_utilities import AlphaUtilities

utilities = AlphaUtilities()


def get_tbill_data(url: str) -> dict:

    response = requests.get(url)

    return response.json()


def parse_tbill_data(data: dict) -> object:

    # split off just the treasury bill data
    subsection = data['data']

    # TODO: add json schema validation

    # convert to json and keep the 1200 most recent entries
    rates = pd.DataFrame(subsection).head(1200)

    # rename columns
    rates.rename(columns={"value": "rate"}, inplace=True)

    return rates


# write data to PostgreSQL
def write_data(data: object):

    TABLE = os.environ.get('2YR_TBILL_TABLE')

    param_dict = {
        "host": os.environ.get('DB_HOST'),
        "database": os.environ.get('DASHBOARD_DB'),
        "port": int(os.environ.get('PORT')),
        "user": os.environ.get('POSTGRES_USER'),
        "password": os.environ.get('POSTGRES_PASSWORD')

    }

    # get dataframe columns for managing data quality
    columns = list(data.columns)

    # get connection client
    connection = utilities.postgres_client(param_dict)

    # prepare payload
    buffer = utilities.prepare_payload(data, columns)

    # clear table
    response = utilities.clear_table(connection, TABLE)

    # write data
    response = utilities.write_data(connection, buffer, TABLE)

    if response != 0:
        print("write_failed")

    else:
        print(f"copy_from_stringio() done, {data} written to database")


def main():

    # Alpha Vantage Key
    ALPHA_KEY = os.environ['KEY']
    # Bond Maturity
    MATURITY = os.environm('BOND_MATURITY')

    utilities = AlphaUtilities()

    # Build URL
    url = utilities.build_bond_url(MATURITY, ALPHA_KEY)

    # get bond data
    data = get_tbill_data(url)

    # parse and transform data
    data = parse_tbill_data(data)

    # write data
    write_data(data)
