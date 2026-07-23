from watch_config_test import load_watch_file

config_file = 'test_config.yml'

config_data = load_watch_file(config_file)
# print(config_data)

enabled_target_count = sum(1 for target in config_data.
                           targets if target.enabled)
print(enabled_target_count)
