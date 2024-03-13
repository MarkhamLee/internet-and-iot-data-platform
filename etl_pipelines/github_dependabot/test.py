# (C) Markham Lee 2023 - 2024
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# Test script for the pulling data from the GitHub Dependabot Alerts for
# this repo

import os
import sys
import unittest
import main

import tracemalloc
tracemalloc.start()

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)


class GitHubDependabotTesting(unittest.TestCase):

    @classmethod
    def setUpClass(self):

        # load Slack Webhook URL variable for sending pipeline failure alerts
        self.WEBHOOK_URL = os.environ['ALERT_WEBHOOK']

        # load Slack Webhook URL for sending dependabot security alerts
        self.DEPENDABOT_WEBHOOK_URL = os.environ['SECURITY_SLACK_WEBHOOK']

        # load repo name env vars
        self.REPO_NAME = os.environ['REPO_NAME']

        # load GitHub Token
        self.GITHUB_TOKEN = os.environ['GITHUB_TOKEN']

        self.ENDPOINT = os.environ['ALERTS_ENDPOINT']

    # End to end test
    def test_dependabot_alerts(self):

        # build URL
        full_url = main.build_url(self.ENDPOINT)

        # get GitHub dependabot data
        data = main.get_github_data(self.GITHUB_TOKEN, full_url)

        # count alerts & get alert status code
        alert_count = main.count_alerts(data)

        # Finally, we write the data to the DB
        response = main.write_data(alert_count)

        self.assertIsNotNone(data, 'Data retrieval failed')
        self.assertIsNotNone(alert_count,
                             "Alert counting and data parsing failed")
        self.assertEqual(response, 0, "InfluxDB write unsuccessful")

    # Check the response of the API call if the wrong key is passed
    # expected response is a 200 code from a successful Slack alert being
    # sent. I.e. you already know the bad key won't work, so what you want to
    # happen is the successful triggering of the Slack message.
    def test_github_api_fail(self):

        # build URL
        full_url = main.build_url(self.ENDPOINT)

        # get GitHub dependabot data
        data = main.get_github_data('fake-key', full_url)

        self.assertEqual(data, 200, 'Bad API Key')

    def test_db_write_exception_handlingl(self):

        # purposely send bad data that will fail InfluxDB's
        # type checking.

        bad_data = "cheese"

        # Finally, we write the data to the DB
        code, response = main.write_data(bad_data)

        self.assertEqual(response, 200,
                         "InfluxDB write successful, should've failed")


if __name__ == '__main__':
    unittest.main()