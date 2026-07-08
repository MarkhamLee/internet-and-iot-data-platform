# Markham Lee (C) 2023
# productivity-music-stocks-weather-IoT-dashboard
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# This script retrieves ten year T-Bill data from the Alpha Vantage API

from datetime import datetime, timedelta
from airflow.decorators import dag, task
from airflow.models import Variable

default_args = {
    "owner": "airflow",
    "start_date": datetime(2023, 11, 16),
    "retries": 1,
}


def send_alerts(context: dict):

    from plugins.slack_utilities import SlackUtilities
    slack_utilities = SlackUtilities()

    webhook_url = Variable.get('slack_hook_alerts')

    slack_utilities.send_slack_webhook(webhook_url, context)


@dag(schedule=timedelta(hours=4), default_args=default_args, catchup=False,
     on_failure_callback=send_alerts)
def alphavantage_tbill10_price_dag():

    # Alpha Vantage Key
    ALPHA_KEY = Variable.get('alpha_vantage_key')

    from alpha_vantage.alpha_utilities import AlphaUtilities  # noqa: E402
    utilities = AlphaUtilities()

    @task(retries=1)
    def get_treasury_data():

        # create URL
        url = utilities.build_bond_url('10year', ALPHA_KEY)

        # get data
        return utilities.get_financial_data(url)

    @task()
    def parse_data(data: dict) -> dict:

        return utilities.bond_data_parser(data)

    @task(retries=2)
    def write_data(data: dict):

        # Airflow will parse these files every 30s (default) so we move these
        # imports into the functions so that airflow isn't constantly wasting
        # cycles importing libraries.

        from plugins.influx_client import InfluxClient  # noqa: E402
        influx = InfluxClient()

        # influx DB variables
        INFLUX_KEY = Variable.get('dashboard_influx_key')
        ORG = Variable.get('influx_org')
        URL = Variable.get('influx_url')
        BUCKET = Variable.get('dashboard_bucket')

        # get the client for connecting to InfluxDB
        client = influx.influx_client(INFLUX_KEY, ORG, URL)

        # base payload
        payload = {
            "measurement": "10yr-T-Bill",
            "tags": {
                "Alpha_Advantage": "bond_data",
            }
        }

        # write data to InfluxDB
        influx.write_influx_data(client, payload, data, BUCKET)

    # nesting the methods establishes the hiearchy and creates the tasks
    write_data(parse_data(get_treasury_data()))


alphavantage_tbill10_price_dag()
