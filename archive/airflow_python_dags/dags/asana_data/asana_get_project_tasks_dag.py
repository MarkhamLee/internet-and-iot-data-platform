# Markham Lee (C) 2023
# productivity-music-stocks-weather-IoT-dashboard
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# This script retrieves ten year T-Bill data from the Alpha Vantage API

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


@dag(schedule=timedelta(hours=1), default_args=default_args, catchup=False,
     on_failure_callback=send_alerts)
def asana_project_tasks_dag():

    from asana_data.asana_utilities import AsanaUtilities  # noqa: E402
    asana_utilities = AsanaUtilities()

    @task(retries=1)
    def get_project_data():

        # Asana Data
        ASANA_KEY = Variable.get('asana_key')
        PROJECT_GID = Variable.get('asana_project_gid_priorities')

        # get Asana Client
        asana_client = asana_utilities.get_asana_client(ASANA_KEY)

        # get Asana data
        # pushing the API call + data parsing to an external script allows
        # us to get around the XCom error that is caused by Asana's returning
        # the data as a pagination object that can't be parsed into JSON.
        data = asana_utilities.get_asana_data(asana_client, PROJECT_GID)

        return data

    @task()
    def parse_data(data: dict) -> object:

        # convert the list of dictionaries from the prior step into a
        # pandas data frame
        return asana_utilities.transform_asana_data(data)

    @task(retries=2)
    def write_data(data: object):

        # import and instantiate Postgres writing class
        from plugins.postgres_client import PostgresUtilities  # noqa: E402
        postgres_utilities = PostgresUtilities()

        # Postgres Table
        POSTGRES_TABLE = Variable.get('asana_table_simple')

        connection_params = {
            "host": Variable.get('postgres_host'),
            "database": Variable.get('postgres_db'),
            "port": Variable.get('postgres_port'),
            "user": Variable.get('postgres_user'),
            "password": Variable.get('postgres_secret')
        }

        # get Postgres client
        client = postgres_utilities.postgres_client(connection_params)

        # get dataframe columns for managing data quality
        columns = list(data.columns)

        # prepare payload
        buffer = postgres_utilities.prepare_payload(data, columns)

        # clear out the table, as we only want the most recent values
        response = postgres_utilities.clear_table(client, POSTGRES_TABLE)

        # write the most recent tasks list to Postgres
        response = postgres_utilities.write_data(client, buffer,
                                                 POSTGRES_TABLE)

        # probably redundant, just to make sure we get the specific error from
        # postgres as opposed to a more general Python error
        if response != 0:
            error_payload = {"error_response": response}
            send_alerts(error_payload)

    # nesting the methods establishes the hiearchy and creates the tasks
    write_data(parse_data(get_project_data()))


asana_project_tasks_dag()
