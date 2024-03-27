# (C) Markham Lee 2023 - 2024
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# Pulls down
import os
import sys
import pandas as pd
from io import StringIO

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


# TODO: move this to a util file all the ETLs can use
def query_postgres(connection: object, query: str, table: str):

    cursor = connection.cursor()

    cursor.execute(query)

    query_result = cursor.fetchall()

    cursor.close()

    # convert to dataframe
    df = pd.DataFrame(query_result)

    # extract the values in the df into a list
    values = df.iloc[0].tolist()

    # remove the date from the list
    values.pop(0)

    return values


# transpose the data so that it's in the right format for
# plotting the yield curve.
def re_org_data(data: object) -> object:

    # transpose data
    df_transpose = data.set_index('Date').transpose()
    df_transpose.reset_index(inplace=True)

    # fix column names
    df_transpose.rename(columns={'index': 'bond_term',
                                 'Date': 'index'}, inplace=True)

    logger.info('Data transformations complete')

    print(df_transpose)

    return df_transpose


def build_dataframe(data: object) -> object:

    columns = ['TTM', 'YTM']

    yield_df = pd.DataFrame(columns=columns)

    ttm = ['1mo', "2mo", "3mo", "4mo", "6mo", "1yr",
           "2yr", "3yr", "5yr", "7yr", "10yr", "20yr", "30yr"]

    # add time to maturity data - standard always the same
    yield_df.loc[:, 'TTM'] = ttm
    yield_df.loc[:, 'YTM'] = data

    logger.info('yield curve data frame ready')

    return yield_df


def prepare_payload(payload: object) -> object:

    # get dataframe columns for managing data quality
    columns = list(payload.columns)
    print(columns)

    buffer = StringIO()

    # explicit column definitions + tab as the delimiter allow us to ingest
    # text data with punctuation  without having situations where a comma
    # in a sentence is treated as new column or causes a blank column to be
    # created.
    payload.to_csv(buffer, index=False, sep='\t', columns=columns,
                   header=True)
    buffer.seek(0)

    return buffer


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

    # get Postgres connection
    connection = postgres_connection()

    TABLE = os.environ['RAW_YIELD_CURVE_TABLE']

    # get data
    with open('db_files/todays_curve.sql', 'r') as q:
        query = q.read()

    data = query_postgres(connection, query, TABLE)
    cleaned_data = build_dataframe(data)

    WRITE_TABLE = "yield_curve_plot"

    # write data
    write_data(connection, cleaned_data, WRITE_TABLE)


if __name__ == '__main__':
    main()
