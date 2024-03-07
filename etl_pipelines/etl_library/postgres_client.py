# Markham Lee (C) 2023
# productivity-music-stocks-weather-IoT-dashboard
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# utilities for writing data to PostgreSQL

import psycopg2
from io import StringIO
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
            return 1

    # strict enforcement of what columns are used ensures data quality
    # avoids issues where tab delimiting can create erroneous empty columns
    # in the data frame
    @staticmethod
    def prepare_payload(payload: object) -> object:

        # get dataframe columns for managing data quality
        columns = list(payload.columns)

        buffer = StringIO()

        # explicit column definitions + tab as the delimiter allow us to ingest
        # text data with punctuation  without having situations where a comma
        # in a sentence is treated as new column or causes a blank column to be
        # created.
        payload.to_csv(buffer, index=False, sep='\t', columns=columns,
                       header=False)
        buffer.seek(0)

        return buffer

    # this method is for instances where the buffer has already been prepared
    # and the data is ready to be written to PostgreSQL
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

    # sending over a data frame or csv - still need to create a buffer object
    @staticmethod
    def write_data_raw(connection: object, data: object, table: str):

        # count rows
        row_count = len(data)

        # prepare payload
        buffer = PostgresUtilities.prepare_payload(data)

        cursor = connection.cursor()

        try:
            cursor.copy_from(buffer, table, sep="\t")
            connection.commit()
            cursor.close()
            logger.info(f"{row_count} rows successfully written to Postgres")

        except (Exception, psycopg2.DatabaseError) as error:
            connection.rollback()
            cursor.close()
            logger.debug(f'PostgresDB write failed with error: {error}')
