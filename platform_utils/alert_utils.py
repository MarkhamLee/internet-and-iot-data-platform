import requests
from platform_utils.platform_logger import configure_logger

logger = configure_logger('alert_utilities_logs')


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
