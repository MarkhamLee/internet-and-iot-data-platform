# Markham Lee (C) 2023
# productivity-music-stocks-weather-IoT-dashboard
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# utilities for writing data to PostgreSQL

import psycopg2
from etl_library.logging_util import logger  # noqa: E402


class PostgresUtilities():

    def __init__(self) -> None:
        pass

    @staticmethod
    def postgres_client(params: dict) -> object:

        # connect to DB

        try:
            conn = psycopg2.connect(**params)
            logger.info('Connection to Postgres Successful')

        except (Exception, psycopg2.DatabaseError) as error:
            logger.debug(f'Postgres connection failed with error: {error}')
            return error

        return conn

    @staticmethod
    def clear_table(connection: object, table: str):

        try:
            # clear out table - for things like lists or alerts where we only
            # want the newest data
            delete_string = (f'DELETE FROM {table}')
            cursor = connection.cursor()

            cursor.execute(delete_string)
            connection.commit()
            logger.info('Postgres Table cleared succesfully')
            return 0

        except (Exception, psycopg2.DatabaseError) as error:
            logger.debug(f'Table clearing operation failed with error: {error}')  # noqa: E501
            return error

    @staticmethod
    def write_data(connection: object, buffer: object, table: str):

        cursor = connection.cursor()

        try:
            cursor.copy_from(buffer, table, sep="\t")
            connection.commit()
            cursor.close()
            logger.info("Data successfully written to Postgres")
            return 0

        except (Exception, psycopg2.DatabaseError) as error:
            connection.rollback()
            cursor.close()
            logger.debug(f'PostgresDB write failed with error: {error}')
            return error
