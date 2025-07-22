# (C) Markham Lee 2023-2025
# API, IoT Data Platform
# https://github.com/MarkhamLee/internet-and-iot-data-platform
# Pulls data from the Docker HUB API to enable CICD automations
import os
import pytz
import requests
import sys
from datetime import datetime, timezone


DOCKERHUB_BASE_URL = 'https://hub.docker.com'
DATE_TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
FULL_LOGIN_URL = (f'{DOCKERHUB_BASE_URL}/v2/users/login')

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from cicd_common.logging_utils import console_logging  # noqa: E402

logger = console_logging('Docker_information_logging')


def get_auth_headers(identifier: str, secret: str) -> dict:

    auth_payload = {
        "username": identifier,
        "password": secret

    }

    login_response = requests.post(FULL_LOGIN_URL, json=auth_payload)

    jwt_token = login_response.json()['token']

    logger.info('Login token created successfully')

    return {"Authorization": f"JWT {jwt_token}"}


def build_docker_repo_url(namespace, repository, tag) -> str:

    REPO_BASE_ENDPOINT = (f'/v2/namespaces/{namespace}/repositories/')

    return (f'{DOCKERHUB_BASE_URL}{REPO_BASE_ENDPOINT}{repository}/tags/{tag}')


def get_docker_image_data(repo_url: str, auth_headers: dict) -> dict:

    try:

        repo_status = requests.get(repo_url, headers=auth_headers)
        status_code = repo_status.status_code

        if status_code == 200:
            logger.info(f'Dockerhub API call successful with return code: {status_code}')  # noqa: E501
            data = repo_status.json()
            return data

    except Exception as e:
        logger.debug(f'Dockerhub API call failed with error code: {e}')
        sys.exit()


def calculate_image_age(raw_data: dict) -> float:

    logger.info('Calculating image age')

    last_pushed = raw_data['tag_last_pushed']

    # need to strip out the microseconds and then put the timestamp
    # back into the following format: "%Y-%m-%dT%H:%M:%SZ"
    last_pushed = datetime.strptime(last_pushed[:-1], "%Y-%m-%dT%H:%M:%S.%f")
    last_pushed_cleaned = last_pushed.\
        replace(microsecond=0, tzinfo=timezone.utc)
    last_pushed_final = last_pushed_cleaned.isoformat().replace("+00:00", "Z")
    last_pushed_dt_object = datetime.strptime(last_pushed_final,
                                              DATE_TIME_FORMAT)

    now = datetime.\
        strptime(datetime.now(pytz.UTC).
                 strftime("%Y-%m-%dT%H:%M:%SZ"), DATE_TIME_FORMAT)

    time_delta = round(((now - last_pushed_dt_object).
                        total_seconds()) / 3600, 2)

    return time_delta


def get_docker_image_age(identifier: str,
                         secret: str,
                         namespace: str,
                         repository: str,
                         tag: str):

    auth_headers = get_auth_headers(identifier,
                                    secret)

    repo_url = build_docker_repo_url(namespace,
                                     repository,
                                     tag)
    raw_data = get_docker_image_data(repo_url,
                                     auth_headers)

    image_age = calculate_image_age(raw_data)

    return image_age
