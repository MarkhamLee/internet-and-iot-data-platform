# Markham Lee (C) 2023
# productivity-music-stocks-weather-IoT-dashboard
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# Utility scripts for retrieving data from the Alpha Advantage finance API

import psycopg2


class AlphaUtilities():

    def __init__(self):

        # create constants
        self.base_tbill_url = 'https://www.alphavantage.co/query?function=TREASURY_YIELD&interval=daily'  # noqa: E501
        self.bond_base = '&maturity='
        self.api_key_base = '&apikey='

    def build_bond_url(self, maturity: str, key: str) -> str:

        full_param = self.bond_base + maturity

        full_url = f'{self.base_tbill_url}{full_param}{self.api_key_base}{key}'

        return full_url

    @staticmethod
    def bond_data_parser(response: dict) -> dict:

        rate = float(response['data'][0]['value'])
        date = response['data'][0]['date']

        payload = {
            'rate': rate,
            'date': date
        }

        return payload

    @staticmethod
    def postgres_client(params: dict) -> object:

        # connect to DB

        try:
            conn = psycopg2.connect(**params)

        except (Exception, psycopg2.DatabaseError) as error:
            return error

        return conn

    # strict enforcement of what columns are used ensures data quality
    # avoids issues where tab delimiting can create erroneous empty columns
    # in the data frame
    @staticmethod
    def prepare_payload(payload: object, columns: list) -> object:

        from io import StringIO  # noqa: E402

        buffer = StringIO()

        # explicit column definitions + tab as the delimiter allow us to ingest
        # text data with punctuation  without having situations where a comma
        # in a sentence is treated as new column or causes a blank column to be
        # created.
        payload.to_csv(buffer, index_label='id', sep='\t', columns=columns,
                       header=False)
        buffer.seek(0)

        return buffer

    @staticmethod
    def clear_table(connection: object, table: str):

        try:
            # clear out table - for things like lists or alerts where we only
            # want the newest data
            delete_string = (f'DELETE FROM {table}')
            cursor = connection.cursor()

            cursor.execute(delete_string)
            connection.commit()
            return 0

        except (Exception, psycopg2.DatabaseError) as error:
            return error

    @staticmethod
    def write_data(connection: object, buffer: object, table: str):

        cursor = connection.cursor()

        try:
            cursor.copy_from(buffer, table, sep="\t")
            connection.commit()
            cursor.close()
            return 0

        except (Exception, psycopg2.DatabaseError) as error:
            connection.rollback()
            cursor.close()
            return error
