# (C) Markham Lee 2023-2025
# API, IoT Data Platform
# https://github.com/MarkhamLee/internet-and-iot-data-platform
# Purpose is to automate restarting/updating containers running on
# edge devices (e.g., RPIs), typically running sensor or IoT
# related containers.
import os
import requests
import sys

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from cicd_common.logging_utils import console_logging  # noqa: E402
from cicd_common.general_utils import send_slack_webhook  # noqa: E402

logger = console_logging('Portainer_container_control')

CICD_SLACK_WEBHOOK = os.environ['CICD_ALERT_SLACK_WEBHOOK']


def build_container_api_url(portainer_url: str,
                            port: str,
                            endpoint_id: str,
                            container_id: str,
                            action: str):

    api_url = (f'{portainer_url}:{port}/api/endpoints/{endpoint_id}/docker/containers/{container_id}/{action}')  # noqa: E501

    logger.info('API URL created')

    return api_url


def container_update(api_key: str,
                     portainer_url: str,
                     port: str,
                     endpoint_id: str,
                     container_id: str,
                     node_name: str,
                     app_name: str,
                     action: str):

    # generate API URL
    api_url = build_container_api_url(portainer_url,
                                      port,
                                      endpoint_id,
                                      container_id,
                                      action)

    headers = {
        "X-API-KEY": api_key

    }

    logger.info(f'Sending {action} command to the {app_name} container on {node_name}')  # noqa: E501

    response = requests.post(api_url, headers=headers)

    response_code = response.status_code

    if response_code == 204:
        message = (f'{action} command for {app_name} container on {node_name} was executed successfully')  # noqa: E501

    else:
        message = (f'{action} command for {app_name} container on {node_name} failed')  # noqa: E501

    logger.info(message)
    logger.info('Sending container status update via Slack')
    send_slack_webhook(CICD_SLACK_WEBHOOK, message)
