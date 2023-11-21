# Markham Lee (C) 2023
# productivity-music-stocks-weather-IoT-dashboard
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# utilities for writing data to PostgreSQL


class PostgresUtilities():

    def __init__(self) -> None:
        pass

    # this is here to support other writing methods or approaches
    # for now, using the write_df method below this one

    @staticmethod
    def postgres_client(params: dict) -> object:

        import psycopg2  # noqa: E402

        # connect to DB

        try:
            conn = psycopg2.connect(**params)

        except (Exception, psycopg2.DatabaseError) as error:
            return error

        return conn

    # for instances where we're adding a dataframe to data in an existing
    # database
    @staticmethod
    def write_df_postgres(payload: object, TABLE: str, params: dict):

        import psycopg2  # noqa: E402
        from io import StringIO  # noqa: E402

        # create DB connection
        try:
            connection = psycopg2.connect(**params)

        except (Exception, psycopg2.DatabaseError) as error:
            return error

        buffer = StringIO()
        payload.to_csv(buffer, index_label='id', header=False)
        buffer.seek(0)
        print(buffer)

        cursor = connection.cursor()

        try:
            cursor.copy_from(buffer, TABLE, sep=",")
            connection.commit()
            cursor.close()
            return 0

        except (Exception, psycopg2.DatabaseError) as error:
            connection.rollback()
            cursor.close()
            return error

    # for when we only want the most recent data in a database, think
    # a list of tasks or items, alerts, current "new things", etc.
    @staticmethod
    def write_df_postgres_clear(payload: object, TABLE: str, params: dict):

        import psycopg2  # noqa: E402
        from io import StringIO  # noqa: E402

        # create DB connection
        try:
            connection = psycopg2.connect(**params)

        except (Exception, psycopg2.DatabaseError) as error:
            return error

        buffer = StringIO()
        payload.to_csv(buffer, index_label='id', header=False)
        buffer.seek(0)
        print(buffer)

        cursor = connection.cursor()

        # clear out table - for things like lists or alerts where we only
        # want the newest data
        delete_string = (f'DELETE FROM {TABLE}')
        cursor.execute(delete_string)
        connection.commit()

        # write new or replacement data
        try:
            cursor.copy_from(buffer, TABLE, sep=",")
            connection.commit()
            cursor.close()
            return 0

        except (Exception, psycopg2.DatabaseError) as error:
            connection.rollback()
            cursor.close()
            return error
