import os
import sys

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from cicd_common.logging_utils import console_logging  # noqa: E402
from portainer_common.container_control import container_update  # noqa: E402

logger = console_logging('portainer_automation_logger')

API_KEY = os.environ['TN_PORTAINER_API_KEY']
PORTAINER_URL = ''
PORT = ""
ENDPOINT_ID = ''
CONTAINER_ID = ''  # noqa: E501


def main():

    container_update(API_KEY,
                     PORTAINER_URL,
                     PORT,
                     ENDPOINT_ID,
                     CONTAINER_ID,
                     "test_node",
                     "test_app",
                     "restart")


if __name__ == '__main__':
    main()
