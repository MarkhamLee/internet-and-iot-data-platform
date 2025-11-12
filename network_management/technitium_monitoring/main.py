# Markham Lee (C) 2023 - 2025
# Internet & IoT Data Platform
# https://github.com/MarkhamLee/internet-and-iot-data-platform
# Script for pulling the dashboard data from Technitium and
# sending alerts when issues like failed requests or server
# errors occur.
import json
import os
import requests
import sys
from jsonschema import validate
from time import sleep

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)


from network_monitoring_libraries.\
    logging_utils import console_logging  # noqa: E402
from network_monitoring_libraries.\
    general_utils import send_slack_webhook, create_influx_client, write_data  # noqa: E402, E501

logger = console_logging('technitium_monitoring')


BUCKET = os.environ['INFLUX_BUCKET']
DNS_ALERT_WEBHOOK = os.environ['DNS_ALERT_WEBHOOK']
DNS_ID = os.environ['DNS_ID']
INFLUX_URL = os.environ['INFLUX_URL']
INFLUX_KEY = os.environ['INFLUX_KEY']
INFLUX_ORG = os.environ['INFLUX_ORG']
SLEEP_DURATION = int(os.environ['SLEEP_DURATION'])
TAG_KEY = os.environ['TAG_KEY']
TAG_VALUE = os.environ['TAG_VALUE']
TECHNITIUM_DASHBOARD_MEASUREMENT = os.environ['TECHNITIUM_DASHBOARD_MEASUREMENT']  # noqa: E501
TECHNITIUM_SERVER_IP = os.environ['TECHNITIUM_SERVER_IP']
TECHNITIUM_TOKEN = os.environ['TECHNITIUM_TOKEN']
TIME_HORIZON = os.environ['DASHBOARD_TIME_HORIZON']
UTC_STATUS = os.environ['UTC_STATUS']


influx_client = create_influx_client(INFLUX_KEY, INFLUX_ORG, INFLUX_URL)

logger.info('Creating base payload for writing to InfluxDB')
base_payload = {
    "measurement": TECHNITIUM_DASHBOARD_MEASUREMENT,
    "tags": {
            TAG_KEY: TAG_VALUE,
    }
}

data_message = (f'Technitium status data for {DNS_ID}')


def build_dashboard_data_url():

    url = (f'http://{TECHNITIUM_SERVER_IP}:5380/api/dashboard/stats/get?token={TECHNITIUM_TOKEN}&type={TIME_HORIZON}&utc={UTC_STATUS}')  # noqa: E501
    logger.info(f'API connection URL created for {DNS_ID}')

    return url


def get_data(url: str):

    try:

        response = requests.post(url=url)
        status = response.json()['status']
        response_data = response.json()
        dns_stats = response_data['response']['stats']
        logger.info(dns_stats)
        return dns_stats, status

    except Exception as e:
        message = (f'DNS server connection on: {DNS_ID} failed with error: {e}')  # noqa: E501
        logger.debug(message)
        send_slack_webhook(DNS_ALERT_WEBHOOK, message)
        data = 'no data'

        # ensure we have a connection status even if the connection failed
        status = 'connection failure'
        return data, status


def validate_json_payload(data: dict, schema_file: dict) -> int:

    with open(schema_file) as file:
        schema = json.load(file)

    # validate the data
    try:
        validate(instance=data, schema=schema)
        logger.info('Data validation successful')
        return 0

    except Exception as e:
        message = (f'Data validation failed with error: {e}')  # noqa: E501
        logger.debug(message)
        response = send_slack_webhook(DNS_ALERT_WEBHOOK, message)
        logger.debug(f'Slack pipeline failure alert sent with code: {response}')  # noqa: E501
        return 1


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


def prepare_payload(data: dict, failure_ratio, refusal_ratio):

    # InfluxDB has fairly tight type requirements, e.g., if the
    # first value is a 1 and it implies INT,it will reject subsequent
    # values that are floats.

    payload = {

        "failure_ratio": float(failure_ratio),
        "refusal_ratio": float(refusal_ratio),
        "total_queries": float(data['totalQueries']),
        "total_clients": float(data['totalClients']),
        "total_zones": float(data['zones']),
        "blockedListZones": float(data['blockListZones']),
        "totalBlocked": float(data['totalBlocked'])

    }

    logger.info(f'Technitium DNS payload ready: {payload}')

    return payload


def main():

    # build url
    dashboard_url = build_dashboard_data_url()

    while True:

        logger.info('Getting Technitium data')
        data, status = get_data(dashboard_url)

        if status != 'ok':
            logger.info(f'Connection issue, status is: {status}, going to sleep for {SLEEP_DURATION} seconds')  # noqa: E501
            sleep(SLEEP_DURATION)
            continue

        logger.info('Validating data payload')

        code = validate_json_payload(data, 'data_reference.json')

        if code == 0:
            failure_ratio, refusal_ratio = extract_alert_data(data)
            finished_payload = prepare_payload(data,
                                               failure_ratio,
                                               refusal_ratio)
            logger.info('Writing data to InfluxDB')

            write_data(base_payload,
                       finished_payload,
                       influx_client,
                       BUCKET,
                       data_message,
                       DNS_ALERT_WEBHOOK)
        sleep(SLEEP_DURATION)


if __name__ == '__main__':
    main()
