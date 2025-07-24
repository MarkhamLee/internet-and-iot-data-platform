# (C) Markham Lee 2023-2025
# API, IoT Data Platform
# https://github.com/MarkhamLee/internet-and-iot-data-platform
# Functions for pulling data from the Tailscale API
import pytz
import requests
from datetime import datetime


TAILSCALE_BASE_URL = 'https://api.tailscale.com/api/v2'
DATE_TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


class TailscaleData():

    def __init_(self):

        pass

    def build_auth_headers(tailscale_api_key: str) -> dict:

        auth_string = (f'Bearer {tailscale_api_key}')

        auth_headers = {
            "Content-Type": "application/json",
            "Authorization": auth_string
        }

        return auth_headers

    def build_tailscale_device_url(device_id) -> str:

        return (f'{TAILSCALE_BASE_URL}/device/{device_id}?fields=all')

    def build_tailscale_status_url(tailnet_name) -> str:

        url = (f'{TAILSCALE_BASE_URL}/tailnet/{tailnet_name}/devices')

        return url

    def get_device_status(device_id, auth_headers) -> dict:

        # get API URL
        url = TailscaleData.build_tailscale_device_url(device_id)

        response = requests.get(url,
                                headers=auth_headers)

        return response.json()

    # get status of all devices
    def get_tailnet_status(auth_headers) -> dict:

        # get API URL
        url = TailscaleData.build_tailscale_status_url()

        response = requests.get(url,
                                headers=auth_headers)

        return response.json()

    def calculate_online_status(device_status: dict) -> int:

        last = datetime.strptime(device_status['lastSeen'], DATE_TIME_FORMAT)
        now = datetime.strptime(datetime.now(pytz.UTC).strftime("%Y-%m-%dT%H:%M:%SZ"), DATE_TIME_FORMAT)  # noqa: E501

        last_seen_minutes = round(((now - last).
                                  total_seconds()) / 60, 2)

        return last_seen_minutes
