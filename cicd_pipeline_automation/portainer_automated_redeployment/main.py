# API, IoT Data Platform, (C) Markham Lee 2023 - 2025
# https://github.com/MarkhamLee/internet-and-iot-data-platform
# Automates the redeployment of Docker containers in response to
# the Docker image being updated.
import os
import sys


parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from cicd_common.logging_utils import console_logging  # noqa: E402
from cicd_common.general_utils import send_slack_webhook  # noqa: E402
from docker_common.docker_information import get_docker_image_age  # noqa: E402


DOCKER_PAT = os.environ['DOCKER_API_PAT']
DOCKERHUB_BASE_URL = 'https://hub.docker.com'
DOCKER_LOGIN_ENDPOINT = '/v2/users/login'
IMAGE_AGE_THRESHOLD = int(os.environ['AGE_THRESHOLD'])
NAMESPACE = os.environ['DOCKER_NAMESPACE']
REPO_BASE_ENDPOINT = (f'/v2/namespaces/{NAMESPACE}/repositories/')
NAMESPACES_ENDPOINT = (f'/v2/namespaces/{NAMESPACE}/repositories')
USERNAME = os.environ['DOCKER_USERNAME']
# ARCH = os.environ['IMAGE_ARCH_CODE']
# REPOSITORY = os.environ['DOCKER_REPO']
# TAG = os.environ['DOCKER_IMAGE_TAG']

IMAGE_AGE_THRESHOLD = 1
TAG = 'latest'
REPOSITORY = 'airquality'
ARCH_CODE = '0'

logger = console_logging('automated_portainer_redeployments')

CICD_SLACK_WEBHOOK = os.environ['CICD_ALERT_SLACK_WEBHOOK']


def main():

    image_age = get_docker_image_age(USERNAME,
                                     DOCKER_PAT,
                                     NAMESPACE,
                                     REPOSITORY,
                                     TAG,
                                     ARCH_CODE)

    if image_age > IMAGE_AGE_THRESHOLD:
        logger.info(f'New stable image available that is {image_age} hours old')  # noqa: E501


if __name__ == '__main__':
    main()
