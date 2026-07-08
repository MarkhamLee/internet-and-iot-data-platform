# Markham Lee (C) 2023
# productivity-music-stocks-weather-IoT-dashboard
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# A test script that retrieves 5 cat facts from the cat facts API and then
# writes them to PostgreSQL. Just an easy way to test writing to Postgres
# without having to worry about authentication or rate limits.

from datetime import datetime, timedelta
from airflow.decorators import dag, task
from airflow.models import Variable

default_args = {
    "owner": "airflow",
    "start_date": datetime(2023, 11, 21),
    "retries": 1,
}


def send_alerts(context: dict):

    from plugins.slack_utilities import SlackUtilities
    slack_utilities = SlackUtilities()

    webhook_url = Variable.get('slack_hook_alerts')

    slack_utilities.send_slack_webhook(webhook_url, context)


@dag(schedule=timedelta(minutes=30), default_args=default_args, catchup=False,
     on_failure_callback=send_alerts)
def cat_facts_dag():

    @task(retries=1)
    def get_cat_data():

        import requests
        fact_list = []
        count = 0

        while count < 5:
            url = 'https://catfact.ninja/fact'
            headers = {}

            data = requests.get(url=url, headers=headers)
            data = data.json()

            fact = data['fact']

            fact_list.append(fact)

            count += 1

        return fact_list

    @task()
    def parse_data(data: list) -> object:

        import pandas as pd

        # create blank dataframe
        df = pd.DataFrame(columns=['cat_fact'])
        df['cat_fact'] = data

        return df

    @task(retries=2)
    def write_data(data: object):

        # Postgres DB connection data
        POSTGRES_DB = Variable.get('postgres_test_db')
        POSTGRES_HOST = Variable.get('sandbox_server')
        POSTGRES_USER = Variable.get('postgres_user')
        POSTGRES_PORT = Variable.get('postgres_port')
        POSTGRES_SECRET = Variable.get('postgres_secret')
        POSTGRES_TABLE = Variable.get('cat_table')

        # import and instantiate Postgres writing class
        from plugins.postgres_client import PostgresUtilities  # noqa: E402
        postgres_utilities = PostgresUtilities()

        connection_params = {
            "host": POSTGRES_HOST,
            "database": POSTGRES_DB,
            "port": POSTGRES_PORT,
            "user": POSTGRES_USER,
            "password": POSTGRES_SECRET
        }

        # get dataframe columns for managing data quality
        columns = list(data.columns)

        # get connection client
        connection = postgres_utilities.postgres_client(connection_params)

        # prepare payload
        buffer = postgres_utilities.prepare_payload(data, columns)

        # write data
        response = postgres_utilities.write_data(connection, buffer,
                                                 POSTGRES_TABLE)

        # Just to make sure we get the specific error from
        # postgres, otherwise we get the more generic error from Airflow
        if response != 0:
            error_payload = {"error_response": response}
            send_alerts(error_payload)

    # nesting the methods establishes the hiearchy and creates the tasks
    write_data(parse_data(get_cat_data()))


cat_facts_dag()
