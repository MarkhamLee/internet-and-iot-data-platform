# Markham Lee (C) 2023
# productivity-music-stocks-weather-IoT-dashboard
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# This script retrieves the list of tasks from an Asana Project, an then write
# them to PostgreSQL. The script will empty the table before writing the tasks,
# as goal is just to have the latest list of open tasks.

from datetime import datetime, timedelta
from airflow.decorators import dag, task
from airflow.models import Variable

default_args = {
    "owner": "airflow",
    "start_date": datetime(2023, 11, 21),
    "retries": 1,
}

# Asana Key
ASANA_KEY = Variable.get('asana_key')

# Postgres DB connection data
POSTGRES_DB = Variable.get('postgres_db')
POSTGRES_HOST = Variable.get('sandbox_server')
POSTGRES_USER = Variable.get('postgres_user')
POSTGRES_PORT = Variable.get('postgres_port')
POSTGRES_SECRET = Variable.get('postgres_secret')
POSTGRES_TABLE = Variable.get('asana_table_simple')
PROJECT_GID = Variable.get('asana_project_gid_priorities')

from asana_data.asana_utilities import AsanaUtilities  # noqa: E402
asana_utilities = AsanaUtilities()


def send_alerts(context: dict):

    from plugins.slack_utilities import SlackUtilities
    slack_utilities = SlackUtilities()

    webhook_url = Variable.get('slack_hook_alerts')

    slack_utilities.send_slack_webhook(webhook_url, context)


@dag(schedule=timedelta(hours=4), default_args=default_args, catchup=False,
     on_failure_callback=send_alerts)
def asana_project_tasks_dag():

    @task(retries=1)
    def get_project_data():

        # get Asana Client
        asana_client = asana_utilities.get_asana_client(ASANA_KEY)

        # get Asana data
        # pushing the API call + initial data parsing to an external script
        # enables us to get around the XCom error that is caused by Asana's
        # returning the data as a pagination object that can't be parsed into
        # JSON.
        data = asana_utilities.get_asana_data(asana_client, PROJECT_GID)

        return data

    @task()
    def parse_data(data: dict) -> object:

        # creating a data frame that can be written to PostgreSQL

        return asana_utilities.transform_asana_data(data)

    @task(retries=2)
    def write_data(data: object):

        # import and instantiate Postgres writing class
        from plugins.postgres_client import PostgresUtilities  # noqa: E402
        postgres = PostgresUtilities()

        connection_params = {
            "host": POSTGRES_HOST,
            "database": POSTGRES_DB,
            "port": POSTGRES_PORT,
            "user": POSTGRES_USER,
            "password": POSTGRES_SECRET
        }

        response = postgres.write_df_postgres_clear(data, POSTGRES_TABLE,
                                                    connection_params)

        # probably redundant, just to make sure we get the specific error from
        # postgres as opposed to a more general Python error
        if response != 0:
            error_payload = {"error_response": response}
            send_alerts(error_payload)

    # nesting the methods establishes the hiearchy and creates the tasks
    write_data(parse_data(get_project_data()))


asana_project_tasks_dag()
