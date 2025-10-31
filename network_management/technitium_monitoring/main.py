# Markham Lee (C) 2023 - 2025
# Internet & IoT Data Platform
# https://github.com/MarkhamLee/internet-and-iot-data-platform
# Script for pulling the dashboard data from Technitium and
# sending alerts when issues like failed requests or server
# errors occur.
import os
import requests
import sys
from time import sleep

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)


from network_monitoring_libraries.\
    logging_utils import console_logging  # noqa: E402
from network_monitoring_libraries.\
    general_utils import send_slack_webhook, create_influx_client, write_influx_data  # noqa: E402, E501

logger = console_logging('technitium_monitoring')


BUCKET = os.environ['INFLUX_NETWORK_MONITORING_BUCKET']
DASHBOARD_TIME_HORIZON = os.environ['DASHBOARD_TIME_HORIZON']
DNS_ID = os.environ['DNS_ID']
INFLUX_URL = os.environ['INFLUX_URL']
INFLUX_KEY = os.environ['INFLUX_KEY']
INFLUX_ORG = os.environ['INFLUX_ORG']
SLEEP_DURATION = os.environ['SLEEP_DURATION']
TABLE = os.environ['DNS_MEASUREMENT_BUCKET']
TAG_KEY = os.environ['TAG_KEY']
TAG_VALUE = os.environ['TAG_VALUE']
TECHNITIUM_SERVER_IP = os.environ['TECHNITIUM_SERVER_IP']
TOKEN = os.environ['TECHNITIUM_TOKEN']
TIME_HORIZON = os.environ['DASHBOARD_TIME_HORIZON']
TIME_TYPE = os.environ['TIME_TYPE']
DNS_ALERT_WEBHOOK = os.environ['DNS_ALERT_WEBHOOK']

influx_client = create_influx_client(TOKEN, INFLUX_ORG, INFLUX_URL)


logger.info('Creating base payload for writing to InfluxDB')
base_payload = {
    "measurement": TABLE,
    "tags": {
            TAG_KEY: TAG_VALUE,
    }
}


def build_dashboard_data_url():

    url = (f'http://{TECHNITIUM_SERVER_IP}:5380/api/dashboard/stats/get?token={TOKEN}&type={TIME_HORIZON}&utc={TIME_TYPE}')  # noqa: E501

    return url


def get_data(url: str):

    response = requests.post(url=url)
    status = response.json()['status']

    return response, status


def extract_alert_data(data: dict):

    # split out the key items we need to determine if we need alert over
    server_failures = data['totalServerFailure']
    refused_queries = data['totalRefused']
    total_queries = data['totalQueries']

    failure_ratio = round((server_failures / total_queries), 2)
    refusal_ratio = round((refused_queries / total_queries), 2)

    if failure_ratio > 5:
        message = (f'Failure ratio for {DNS_ID} is currently {failure_ratio}, check DNS server and general network status immediately')  # noqa: E501
        send_slack_webhook(DNS_ALERT_WEBHOOK, message)

    return failure_ratio, refusal_ratio


def main():

    # build url
    dashboard_url = build_dashboard_data_url()

    while True:

        logger.info('Getting Technitium data')
        data, status = get_data(dashboard_url)
        extract_alert_data(data)
        sleep(30)


if __name__ == '__main__':
    main()
