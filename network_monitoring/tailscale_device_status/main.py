# WORK IN PROGRESS
# (C) Markham Lee 2023-2025
# API, IoT Data Platform
# https://github.com/MarkhamLee/internet-and-iot-data-platform
# Pulling connection status and latency for a tailscale node
import os
import sys
import pytz
from datetime import datetime

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)


from network_monitoring_libraries.\
    logging_utils import console_logging  # noqa: E402
from network_monitoring_libraries.\
    general_utils import send_slack_webhook  # noqa: E402
from tailscale_library.tailscale_data import TailscaleData  # noqa: E402

tailscale_data_utils = TailscaleData()

logger = console_logging('Tailscale_monitoring_logger')


TAILSCALE_API_KEY = os.environ['MARKHAMSLAB_TAILSCALE_DEVICE_STATUS_KEY']
TAILSCALE_BASE_URL = 'https://api.tailscale.com/api/v2'
TAILNET_NAME = os.environ['TAILNET_NAME']
DATE_TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
NETWORK_ALERT_WEBHOOK = os.environ['NETWORK_ALERT_WEBHOOK']
NODE_NAME = os.environ['NODE_NAME']
LOCAL_CITY = os.environ['LOCALE']


def calculate_online_status(device_data: dict) -> float:

    last = datetime.strptime(device_data['lastSeen'], DATE_TIME_FORMAT)
    now = datetime.strptime(datetime.now(pytz.UTC).strftime("%Y-%m-%dT%H:%M:%SZ"), DATE_TIME_FORMAT)  # noqa: E501

    last_seen_seconds = round(((now - last).total_seconds()), 2)

    return last_seen_seconds


def get_latency(device_data: dict, latency_location: str) -> float:

    local_latency_all_data = device_data['clientConnectivity']['latency'][latency_location]  # noqa: E501
    latency = round(local_latency_all_data['latencyMs'], 2)

    return latency


def main():

    device_id = NODE_NAME

    raw_device_data = tailscale_data_utils.\
        get_device_status(device_id, TAILSCALE_API_KEY)
    last_seen_seconds = calculate_online_status(raw_device_data)
    latency = get_latency(raw_device_data, LOCAL_CITY)

    logger.info(f'Device was last seen {last_seen_seconds} seconds ago')
    logger.info(f'Device latency for {LOCAL_CITY} is {latency}ms')

    if last_seen_seconds > 120:

        minutes = round(last_seen_seconds / 60, 2)
        message = (f'Exit node problem: {NODE_NAME} was last seen: {minutes} ago')  # noqa: E501
        send_slack_webhook(NETWORK_ALERT_WEBHOOK, message)


if __name__ == '__main__':
    main()
