# (C) Markham Lee 2023 - 2024
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# container for loading historical yield curve data from the US Treasury
import os
import sys
import pandas as pd

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

# from etl_library.logging_util import logger  # noqa: E402
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


def check_dates(connection: object, table: str) -> int:

    cursor = connection.cursor()

    # execute query
    cursor.execute(f"SELECT * FROM public.{table} ORDER BY date DESC LIMIT 1")  # noqa: E501

    # get column names
    colnames = [desc[0] for desc in cursor.description]

    # query DB
    query_result = cursor.fetchall()

    # convert to dataframe
    df = pd.DataFrame(query_result, columns=colnames)
    print(df)


def main():

    # get Postgres connection
    connection = postgres_connection()

    # get table
    TABLE = os.environ['RAW_YIELD_CURVE_TABLE']

    # check to see if there is new data before writing to the DB
    # i.e., we don't want to write duplicate rows
    check_dates(connection, TABLE)


if __name__ == '__main__':
    main()
