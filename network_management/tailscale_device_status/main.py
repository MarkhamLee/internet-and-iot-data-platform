# WORK IN PROGRESS
# (C) Markham Lee 2023-2025
# API, IoT Data Platform
# https://github.com/MarkhamLee/internet-and-iot-data-platform
# Pulling connection status and latency for a tailscale node
import os
import requests
import sys
import pytz
from datetime import datetime
from time import sleep

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)


from network_monitoring_libraries.\
    logging_utils import console_logging  # noqa: E402
from network_monitoring_libraries.\
    general_utils import send_slack_webhook, create_influx_client, write_influx_data  # noqa: E402, E501
from tailscale_library.tailscale_data import TailscaleData  # noqa: E402

tailscale_data_utils = TailscaleData()

logger = console_logging('Tailscale_monitoring_logger')


DEVICE_ID = os.environ['DEVICE_ID']
TAILSCALE_API_KEY = os.environ['TAILSCALE_API_KEY']
TAILSCALE_BASE_URL = 'https://api.tailscale.com/api/v2'
TAILNET_NAME = os.environ['TAILNET_NAME']
DATE_TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
NETWORK_ALERT_WEBHOOK = os.environ['NETWORK_ALERT_WEBHOOK']
NODE_NAME = os.environ['TAILSCALE_NODE_NAME']
LOCAL_CITY = os.environ['LOCALE']
BUCKET = os.environ['INFLUX_NETWORK_MONITORING_BUCKET']
INFLUX_URL = os.environ['INFLUX_URL']
INFLUX_KEY = os.environ['INFLUX_KEY']
INFLUX_ORG = os.environ['INFLUX_ORG']
SLEEP_DURATION = os.environ['SLEEP_DURATION']
MEASUREMENT = os.environ['MEASUREMENT_NAME']
UPTIME_KUMA_WEBHOOK = os.environ['UPTIME_KUMA_HEARTBEAT']


def calculate_online_status(device_data: dict) -> float:

    last = datetime.strptime(device_data['lastSeen'], DATE_TIME_FORMAT)
    now = datetime.strptime(datetime.now(pytz.UTC).strftime("%Y-%m-%dT%H:%M:%SZ"), DATE_TIME_FORMAT)  # noqa: E501

    last_seen_seconds = round(((now - last).total_seconds()), 2)

    return last_seen_seconds


def get_latency(device_data: dict, latency_location: str) -> float:

    local_latency_all_data = device_data['clientConnectivity']['latency'][latency_location]  # noqa: E501
    latency = round(local_latency_all_data['latencyMs'], 2)

    return latency


def write_data(heartbeat, since_last_seen, latency, city):

    # get the client for connecting to InfluxDB
    client = create_influx_client(INFLUX_KEY,
                                  INFLUX_ORG,
                                  INFLUX_URL)

    data = {
        "heartbeat": float(heartbeat),
        "time_since": float(since_last_seen),
        "latency": float(latency),
        "latency_city": city
    }

    # base payload
    payload = {
        "measurement": MEASUREMENT,
        "tags": {
                "Tailscale": "Exit Node Monitoring",
        }
    }

    try:
        # write data to InfluxDB
        write_influx_data(client, payload, data, BUCKET)
        logger.info(f'Tailscale status data for {NODE_NAME} written to InfluxDB')  # noqa: E501

    except Exception as e:
        message = (f'InfluxDB write error for Tailscale Data: {e}')
        logger.debug(message)
        response = send_slack_webhook(NETWORK_ALERT_WEBHOOK, message)
        logger.debug(f'Slack pipeline failure alert sent with code: {response}')  # noqa: E501
        return response
    

def send_uptime_kuma_heartbeat(id):

    # TODO: check response to verify that response
    # is proper, if not trigger alert
    try:
        requests.get(UPTIME_KUMA_WEBHOOK)

    except Exception as e:
        logger.info(f'Publishing of Uptime Kuma alert for {id} failed with error: {e}')  # noqa: E501


def main():

    while True:

        heart_beat = 1

        device_id = DEVICE_ID

        raw_device_data = tailscale_data_utils.\
            get_device_status(device_id, TAILSCALE_API_KEY)
        last_seen = calculate_online_status(raw_device_data)  # in seconds
        latency = get_latency(raw_device_data, LOCAL_CITY)

        logger.info(f'Device was last seen {last_seen} seconds ago')
        logger.info(f'Device latency for {LOCAL_CITY} is {latency}ms')

        if last_seen > 120:

            # this "heart beat" is redundant with uptime kuma integration
            heart_beat = 0  

            # convert to minutes since an offline device's last
            # seen time can stretch into 100s of seconds.
            last_seen = round(last_seen / 60, 2)
            message = (f'Exit node problem: {NODE_NAME} was last seen: {last_seen} ago')  # noqa: E501
            send_slack_webhook(NETWORK_ALERT_WEBHOOK, message)

        if last_seen < 120:
            # send Uptime Kuma heartbeat
            send_uptime_kuma_heartbeat(NODE_NAME)

        logger.info('Recording latency data')

        write_data(heart_beat, last_seen, latency, LOCAL_CITY)
        # TODO add logic for using a shorter sleep duration when the device
        # is offline.

        logger.info(f'Going to sleep for {SLEEP_DURATION} seconds')
        sleep(SLEEP_DURATION)


if __name__ == '__main__':
    main()
