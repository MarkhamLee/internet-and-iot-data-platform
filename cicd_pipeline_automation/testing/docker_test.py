# (C) Markham Lee 2023-2025
# API, IoT Data Platform
# https://github.com/MarkhamLee/internet-and-iot-data-platform
# Script to test the Docker info script and API calls.
import os
import sys

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from cicd_common.logging_utils import console_logging  # noqa: E402
from docker_common.docker_information import get_docker_image_age  # noqa: E402

logger = console_logging('Docker_age_test_script')


DOCKER_PAT = os.environ['DOCKER_API_PAT']
DOCKERHUB_BASE_URL = 'https://hub.docker.com'
DOCKER_LOGIN_ENDPOINT = '/v2/users/login'
NAMESPACE = os.environ['DOCKER_NAMESPACE']
REPO_BASE_ENDPOINT = (f'/v2/namespaces/{NAMESPACE}/repositories/')
NAMESPACES_ENDPOINT = (f'/v2/namespaces/{NAMESPACE}/repositories')
USERNAME = os.environ['DOCKER_USERNAME']

repository = 'airquality'
tag = 'latest'

NAMESPACES_URL = (f'{DOCKERHUB_BASE_URL}{NAMESPACES_ENDPOINT}')


def main():

    image_age = get_docker_image_age(USERNAME,
                                     DOCKER_PAT,
                                     NAMESPACE,
                                     repository,
                                     tag)

    logger.info(f'The Docker image age is: {image_age} hours')


if __name__ == '__main__':
    main()
