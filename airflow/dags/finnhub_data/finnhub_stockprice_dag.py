# Markham Lee (C) 2023
# productivity-music-stocks-weather-IoT-dashboard
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# This script retrieves stock price information from the Finnhub API

from datetime import datetime, timedelta
from airflow.decorators import dag, task
from airflow.models import Variable

default_args = {
    "owner": "airflow",
    "start_date": datetime(2023, 11, 17),
    "retries": 0,
}


def send_alerts(context: dict):

    from slack_utilities import SlackUtilities
    slack_utilities = SlackUtilities()

    webhook_url = Variable.get('slack_hook_alerts')

    slack_utilities.send_slack_webhook(webhook_url, context)


@dag(schedule=timedelta(minutes=2), default_args=default_args, catchup=False,
     on_failure_callback=send_alerts)
def finnhub_stockprice_dag():

    from finnhub_data.finnhub_utilities import FinnHubUtilities
    finn_util = FinnHubUtilities()

    # get Finnhub API key
    FINNHUB_KEY = Variable.get('finnhub_key')

    @task(retries=0)
    def get_prices():

        import finnhub  # noqa: E402
        from jsonschema import validate

        # import data schema for validation
        SCHEMA = Variable.get(key='finnhub_schema',
                              deserialize_json=True)

        # create client
        client = finnhub.Client(FINNHUB_KEY)

        # get data
        data = client.quote('SPY')

        # validate data
        validate(instance=data, schema=SCHEMA)

        return data

    @task(multiple_outputs=True)
    def parse_data(data: dict) -> dict:

        return finn_util.parse_stock_data(data)

    @task(retries=1)
    def write_data(data: dict):

        from influx_client import InfluxClient  # noqa: E402
        influx = InfluxClient()

        # Influx DB variables
        INFLUX_KEY = Variable.get('dashboard_influx_key')
        ORG = Variable.get('influx_org')
        URL = Variable.get('influx_url')
        BUCKET = Variable.get('dashboard_bucket')

        # get the client for connecting to InfluxDB
        client = influx.influx_client(INFLUX_KEY, ORG, URL)

        # base payload
        payload = {
            "measurement": "finnhub_quotes",
            "tags": {
                "finnhub_API": "stock_prices",
            }
        }

        # write data to InfluxDB
        influx.write_influx_data(client, payload, data, BUCKET)

    write_data(parse_data(get_prices()))


finnhub_stockprice_dag()
