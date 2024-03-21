# (C) Markham Lee 2023 - 2024
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# Test Script for the Asana ETL container

import os
import sys
import main
import unittest
import tracemalloc
from asana_utilities import AsanaUtilities

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from etl_library.logging_util import logger  # noqa: E402
from etl_library.postgres_client import PostgresUtilities  # noqa: E402


class AsanaTasksEtlTesting(unittest.TestCase):

    @classmethod
    def setUpClass(self):

        tracemalloc.start()

        self.logger = logger
        self.asana_utils = AsanaUtilities()
        self.postgres_utils = PostgresUtilities()

        self.logger.info("Starting tests...")

    # End to end test, retrieving the data, parsing the pagination
    # object, calculating the age of task and then writing the data
    # to PostgreSQL.
    def asana_end_to_end(self):

        # Get project ID
        PROJECT_GID = os.environ['GID']

        # Get Asana client
        asana_client = main.get_asana_client(os.environ['ASANA_KEY'])

        # get the raw data
        raw_data = main.get_asana_data(asana_client, PROJECT_GID)

        # now we pull the data out of the pagination object from the
        # above and turn it into a data frame.
        parsed_data, total_rows =\
            self.asana_utils.transform_asana_data(raw_data)

        # get a count of the columns
        column_count = len(parsed_data.columns)

        # Add fields to the data frame for age of tasks and time
        # since last update, then we validate that two columns
        # were added to the dataframe
        payload = main.calculate_task_age(parsed_data)
        new_column_count = len(payload.columns)

        # get Postgres connection
        TABLE, param_dict = main.get_db_vars()
        connection = main.get_postgres_client(TABLE, param_dict)

        # clear the table
        clear_response = self.postgres_utils.clear_table(connection, TABLE)

        # Finally, we write the data to the DB. We only get a resonse
        # back if the write fails and a Slack alert is triggered.
        write_response, rows = main.write_data(connection, payload, TABLE)

        self.assertIsNotNone(raw_data, 'API Connection was unsuccessful')
        self.assertIsNotNone(parsed_data, "Data frame wasn't created")
        self.assertEqual(new_column_count, (column_count + 2),
                         "Data frame wasn't created")
        self.assertIsNotNone(connection, "Postgres client wasn't created")
        self.assertEqual(clear_response, 0, "Failed to clear Postgres Table")
        self.assertEqual(write_response, 0, "Postgres write unsuccessful")

    # Not the best test as the Asana library doesn't catch the error
    # of a successful API but bad GID. The test will validate that the
    # Slack alert gets sent when parsing the paginagion object fails as
    # a result the API containing a bad GID.
    def bad_project_gid(self):

        BAD_GID = "2345546463415"

        # get project data, even with the bad GID the request will succeed
        # and all the error data will be in the pagination object
        data = main.get_asana_data(BAD_GID)

        # attempt to pull out the data from the pagination object,
        # this should fail
        slack_response = self.asana_utils.transform_asana_data(data)

        self.assertEquals(slack_response, 200,
                          "Failed to send Slack message")

    # test exception handling for the data write by intentionally using
    # a table that will throw an error, and checking to see if the Slack
    # alert was sent properly
    def data_write_exceptions(self):

        # get project ID
        PROJECT_GID = os.environ['GID']

        # get the raw data
        raw_data = main.get_asana_data(PROJECT_GID)

        # now we pull the data out of the pagination object from the
        # above and turn it into a data frame.
        parsed_data, total_rows =\
            self.asana_utils.transform_asana_data(raw_data)

        # Add fields to the data frame for age of tasks and time
        # since last update, then we validate that two columns
        # were added to the dataframe
        payload = main.calculate_task_age(parsed_data)

        # get Postgres connection
        TABLE, param_dict = main.get_db_vars()
        connection = main.get_postgres_client(TABLE, param_dict)

        # get project data, should fail due to the bad GID and generate a
        # a pipeline failure alert delivered by Slack.
        status, slack_response = main.write_data(connection, payload,
                                                 "bad_table")

        self.assertEqual(status, 1,
                         "Postgres write was successful, should've failed")
        self.assertEqual(slack_response, 200,
                         "Failed to send Slack message")


if __name__ == '__main__':
    unittest.main()
