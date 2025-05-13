import os
import sys

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from iot_libraries.logging_util import logger  # noqa: E402
from iot_libraries.communications_utilities\
    import IoTCommunications  # noqa: E402

# instantiate hardware monitoring class
monitor_utilities = IoTCommunications()

SLACK_WEBH00K = os.environ['UPS_SLACK_ALERT_WEBHOOK']

message = "test"
logger.info(f'The test message is: {message}')

monitor_utilities.send_slack_webhook(SLACK_WEBH00K, message)
