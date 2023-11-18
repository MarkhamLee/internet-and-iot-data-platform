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

# Alpha Vantage Key
ALPHA_KEY = Variable.get('alpha_vantage_key')

# influx DB variables
INFLUX_KEY = Variable.get('dashboard_influx_key')
ORG = Variable.get('influx_org')
URL = Variable.get('influx_url')
BUCKET = Variable.get('dashboard_bucket')


from alpha_vantage.alpha_utilities import AlphaUtilities  # noqa: E402
utilities = AlphaUtilities()


def send_alerts(context: dict):

    from plugins.slack_utilities import SlackUtilities
    slack_utilities = SlackUtilities()

    webhook_url = Variable.get('slack_hook_alerts')

    slack_utilities.send_slack_webhook(webhook_url, context)


@dag(schedule=timedelta(hours=2), default_args=default_args, catchup=False,
     on_failure_callback=send_alerts)
def alphavantage_tbill10_price_dag():

    @task(retries=1)
    def get_treasury_data():

        # create URL
        url = utilities.build_bond_url('10year', ALPHA_KEY)

        # get data
        return utilities.get_stock_data(url)

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

        from influxdb_client import Point  # noqa: E402

        # get the client for connecting to InfluxDB
        client = influx.influx_client(INFLUX_KEY, ORG, URL)

        # create object for writing to Influx
        point = (
            Point("10yr-T-Bill")
            .tag("Alpha_Vantage", "bond_data")
            .field("rate", data['rate'])
            .field("date", data['date'])
        )

        client.write(bucket=BUCKET, org=ORG, record=point)

    # nesting the methods establishes the hiearchy and creates the tasks
    write_data(parse_data(get_treasury_data()))


alphavantage_tbill10_price_dag()
