from __future__ import annotations

import sys
from watch_config_test import load_watch_file
from ai_agents.agent_library.logging_util import console_logging

logger = console_logging('test1')

# from common.logging_utils import configure_logger

# logger = configure_logger("test_logger")

sys.exit(1)


config_file = 'test_config.yml'

config_data = load_watch_file(config_file)
# print(config_data)

enabled_target_count = sum(1 for target in config_data.
                           targets if target.enabled)
print(enabled_target_count)
