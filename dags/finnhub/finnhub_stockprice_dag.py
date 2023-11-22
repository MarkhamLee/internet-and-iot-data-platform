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
    "retries": 1,
}


def send_alerts(context: dict):

    from plugins.slack_utilities import SlackUtilities
    slack_utilities = SlackUtilities()

    webhook_url = Variable.get('slack_hook_alerts')

    slack_utilities.send_slack_webhook(webhook_url, context)


@dag(schedule=timedelta(minutes=2), default_args=default_args, catchup=False,
     on_failure_callback=send_alerts)
def finnhub_stockprice_dag():

    # get Finnhub API key
    FINNHUB_KEY = Variable.get('finnhub_key')

    @task(retries=0)
    def get_prices():

        import finnhub  # noqa: E402

        # create client
        client = finnhub.Client(FINNHUB_KEY)

        # get data
        return client.quote('SPY')

    @task(multiple_outputs=True)
    def parse_data(data: dict) -> dict:

        payload = {
            "previous_close": float(data['pc']),
            "open": float(data['o']),
            "last_price": float(data['l']),
            "change": float(data['dp'])
        }

        return payload

    @task(retries=1)
    def write_data(data: dict):

        from plugins.influx_client import InfluxClient  # noqa: E402
        influx = InfluxClient()

        from influxdb_client import Point  # noqa: E402

        # Influx DB variables
        INFLUX_KEY = Variable.get('dashboard_influx_key')
        ORG = Variable.get('influx_org')
        URL = Variable.get('influx_url')
        BUCKET = Variable.get('dashboard_bucket')

        # get the client for connecting to InfluxDB
        client = influx.influx_client(INFLUX_KEY, ORG, URL)

        point = (
            Point("finnhub_quotes")
            .tag("finnhub_API", "stock_prices")
            .field("previous_close", data['previous_close'])
            .field("last_price", data['last_price'])
            .field("change", data['change'])
            .field("open", data['open'])
        )

        client.write(bucket=BUCKET, org=ORG, record=point)

    write_data(parse_data(get_prices()))


finnhub_stockprice_dag()
