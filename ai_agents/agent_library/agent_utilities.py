# (C) Markham Lee 2023-2026
# Internet & IoT Data Platform
# https://github.com/MarkhamLee/internet-and-iot-data-platform

import requests
from agent_library.logging_util import console_logging

logger = console_logging('agent_utilities_logs')


def send_slack_webhook_basic(url: str, message: str):

    headers = {
        'Content-type': 'application/json'

    }

    payload = {
        "text": message
    }

    response = requests.post(url, headers=headers, json=payload)

    code = response.status_code

    if code != 200:
        logger.warning("Publishing of alert to Slack webhook failed with response code: %s",  # noqa: E501
                       code)  # noqa: E501
    else:
        logger.info('Publishing of alert to Slack webhook suceeded with code: %s',  # noqa E501
                    code)  # noqa: E501

    return code


def send_slack_webhook_block(webhook_url: str, payload: dict) -> int:
    headers = {
        "Content-Type": "application/json; charset=utf-8",
    }

    try:
        response = requests.post(
            webhook_url,
            headers=headers,
            json=payload,
            timeout=(5, 20),
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        status_code = getattr(exc.response, "status_code", 0)
        logger.warning("Publishing of alert to Slack webhook failed with response code:  %s with error: %s",  # noqa: E501
                       status_code,
                       exc)
        return status_code

    logger.info("Publishing of alert to Slack webhook succeeded with code: %s",
                response.status_code)
    return response.status_code


def write_instrumentation(
    conn,
    table: str,
    payload: dict,
) -> None:
    columns = ", ".join(payload.keys())
    placeholders = ", ".join(f"%({k})s" for k in payload.keys())
    sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"  # noqa: E501

    try:
        with conn.cursor() as cur:
            cur.execute(sql, payload)
        logger.info("Wrote instrumentation row to table=%s", table)

    except Exception as exc:
        logger.warning(
            "Writing of instrumentation data to table=%s failed with error: %s",  # noqa: E501
            table,
            exc,
        )
