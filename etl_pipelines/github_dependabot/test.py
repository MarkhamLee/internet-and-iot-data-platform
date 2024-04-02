# (C) Markham Lee 2023 - 2024
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# Test script for the ETL that pulls dependabot security alerts from the GitHub
# API.

import os
import sys
import unittest
import main

import tracemalloc
tracemalloc.start()

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from github_library.github_utilities import GitHubUtilities  # noqa: E402


class GitHubDependabotTesting(unittest.TestCase):

    @classmethod
    def setUpClass(self):

        # load Slack Webhook URL variable for sending pipeline failure alerts
        self.WEBHOOK_URL = os.environ['ALERT_WEBHOOK']

        # load Slack Webhook URL for sending dependabot security alerts
        self.DEPENDABOT_WEBHOOK_URL = os.environ['SECURITY_SLACK_WEBHOOK']

        self.NAME = os.environ['GITHUB_PIPELINE_NAME']

        # load repo name env vars
        self.REPO_NAME = os.environ['REPO_NAME']

        # load GitHub Token
        self.GITHUB_TOKEN = os.environ['GITHUB_TOKEN']

        self.ENDPOINT = os.environ['ALERTS_ENDPOINT']

        self.github_utilities = GitHubUtilities()

    # End to end test
    def test_dependabot_alerts(self):

        # build URL
        full_url = main.build_url(self.ENDPOINT)

        # get GitHub dependabot data
        data = main.get_dependabot_data(full_url, self.GITHUB_TOKEN)

        # count alerts & get alert status code
        alert_count = main.count_alerts(data)

        # load InfluxDB variables for storing data
        MEASUREMENT = os.environ['GITHUB_ALERTS_MEASUREMENT']
        BUCKET = os.environ['DEVOPS_BUCKET']

        # load tag name
        tag_name = "Dependabot Alerts"

        # Finally, we write the data to the DB
        response = self.github_utilities.write_github_data(alert_count,
                                                           MEASUREMENT,
                                                           BUCKET, tag_name)

        self.assertIsNotNone(data, 'Data retrieval failed')
        self.assertIsNotNone(alert_count,
                             "Alert counting and data parsing failed")
        self.assertEqual(response, 0, "InfluxDB write unsuccessful")

    # Check the response of the API call if the wrong key is passed,
    # expected response is a 200 code from a successful Slack alert being
    # sent. I.e. you already know the bad key won't work, so what you want to
    # happen is the successful triggering of the Slack message.
    def test_github_api_fail(self):

        # build URL
        full_url = main.build_url(self.ENDPOINT)

        # get GitHub dependabot data
        data = main.get_dependabot_data(full_url, 'fake-key')

        self.assertEqual(data, 200, 'Bad API Key')

    # Testing exception handling for sending bad data to
    # InfluxDB.
    def test_db_write_exception_handlingl(self):

        # purposely send bad data that will fail InfluxDB's
        # type checking.

        bad_data = "cheese"

        # load InfluxDB variables for storing data
        MEASUREMENT = os.environ['GITHUB_ALERTS_MEASUREMENT']
        BUCKET = os.environ['DEVOPS_BUCKET']

        # load tag name
        tag_name = "Dependabot Alerts"

        # Finally, we write the data to the DB
        response = self.github_utilities.write_github_data(bad_data,
                                                           MEASUREMENT,
                                                           BUCKET, tag_name)

        self.assertEqual(response, 200,
                         "InfluxDB write successful, should've failed")


if __name__ == '__main__':
    unittest.main()
