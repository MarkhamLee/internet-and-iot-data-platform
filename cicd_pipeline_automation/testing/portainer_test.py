import os
import sys

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from cicd_common.logging_utils import console_logging  # noqa: E402
from portainer_common.\
    portainer_container_management import container_update  # noqa: E402

logger = console_logging('portainer_automation_logger')

API_KEY = os.environ['TN_PORTAINER_API_KEY']
PORTAINER_URL = 'https://truenas.local.markhamslab.com'
PORT = "31015"
ENDPOINT_ID = '3'
CONTAINER_ID = '6390a36cd4270fa0e779e95f6860f20c06be9479f01c85ea77d4289ee00c49b8'  # noqa: E501


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
