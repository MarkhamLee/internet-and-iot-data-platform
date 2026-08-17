from __future__ import annotations

from watch_config_test import load_watch_file
from platform_utils.platform_logger import configure_logger

logger = configure_logger('test1')

logger.info('loading test config')


config_file = 'test_config.yml'

config_data = load_watch_file(config_file)
logger.info('The test config is %s',
            config_data)

enabled_target_count = sum(1 for target in config_data.
                           targets if target.enabled)
logger.info('There are %s total targets',
            enabled_target_count)
