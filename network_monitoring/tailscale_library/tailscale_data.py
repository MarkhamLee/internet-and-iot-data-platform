# (C) Markham Lee 2023-2025
# API, IoT Data Platform
# https://github.com/MarkhamLee/internet-and-iot-data-platform
# Functions for pulling data from the Tailscale API
import requests


TAILSCALE_BASE_URL = 'https://api.tailscale.com/api/v2'
DATE_TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


class TailscaleData():

    def __init_(self):

        pass

    def build_auth_headers(self, tailscale_api_key: str) -> dict:

        auth_string = (f'Bearer {tailscale_api_key}')

        auth_headers = {
            "Content-Type": "application/json",
            "Authorization": auth_string
        }

        return auth_headers

    def build_tailscale_device_url(self, device_id) -> str:

        return (f'{TAILSCALE_BASE_URL}/device/{device_id}?fields=all')

    def build_tailscale_status_url(self, tailnet_name) -> str:

        url = (f'{TAILSCALE_BASE_URL}/tailnet/{tailnet_name}/devices')

        return url

    def get_device_status(self, device_id, api_key) -> dict:

        auth_headers = self.build_auth_headers(api_key)

        # get API URL for device status
        url = self.build_tailscale_device_url(device_id)

        response = requests.get(url,
                                headers=auth_headers)

        return response.json()

    # get status of all devices
    def get_tailnet_status(self, auth_headers) -> dict:

        # get API URL for tailnet status
        url = self.build_tailscale_status_url()

        response = requests.get(url,
                                headers=auth_headers)

        return response.json()
