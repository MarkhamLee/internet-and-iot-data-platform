# (C) Markham Lee 2023-2026
# Internet & IoT Data Platform
# https://github.com/MarkhamLee/internet-and-iot-data-platform
# General utlities to support agentic workflows
import requests
from agent_library.logging_util import console_logging

logger = console_logging('agent_utilities_logs')


def send_slack_webhook_basic(url: str, message: str) -> int:
    headers = {
        "Content-Type": "application/json; charset=utf-8",
    }

    payload = {"text": message}

    try:
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=(5, 20),
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        status_code = getattr(exc.response, "status_code", 0)
        logger.warning(
            "Publishing of alert to Slack webhook failed with response code: %s with error: %s",  # noqa: E501
            status_code,
            exc,
        )
        return status_code

    # verify successful message send as the Slack API will return 200
    # when the message doesn't go through but the webhook is invalid
    # or stale
    return evaluate_slack_response(response)


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
        logger.warning(
            "Publishing of alert to Slack webhook failed with response code: %s with error: %s",  # noqa: E501
            status_code,
            exc,
        )
        return status_code

    # verify successful message send as the Slack API will return 200
    # when the message doesn't go through but the webhook is invalid
    # or stale
    return evaluate_slack_response(response)


# Slack's API returns 200 for a successful webhook connection,
# even if the message send fail, this "intercept" ensures that a
# 200 code is only returned for a successfully sent message.
def evaluate_slack_response(response) -> int:
    response_message = response.text.strip()

    if response_message != "ok":
        logger.warning(
            "Slack webhook problem, status=%s response=%r",
            response.status_code,
            response_message,
        )
        return 400

    logger.info(
        "Slack message sent successfully with response code %s and response message %r",  # noqa: E501
        response.status_code,
        response_message,
    )

    return 200


# method for writing log/monitoring data to Postgres
# note: typically used earlier in an agent's development, as the
# agent evolves, it typically gets a dedicated Postgres client
# just for instrumentation data.
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


# quick method for validating Slack webhooks
def validate_webhook(webhook_url: str) -> bool:
    """Returns True if webhook is healthy."""
    try:
        r = requests.post(webhook_url,
                          json={"text": "_health check_"},
                          timeout=(5, 10))
        return r.text.strip() == "ok"
    except requests.RequestException:
        return False
