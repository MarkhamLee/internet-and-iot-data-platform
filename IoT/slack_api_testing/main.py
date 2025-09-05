import os
import sys

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from iot_libraries.communications_utilities\
    import IoTCommunications  # noqa: E402

utilities = IoTCommunications()

webhook = ''  # noqa: E501

message = "test"


utilities.send_slack_webhook(webhook, message)
