# Markham Lee (C) 2023 - 2024
# productivity-music-stocks-weather-IoT-dashboard
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# ETL bot for monitoring the Raspberry Pi Locator: https://rpilocator.com/
# RSS feed and sending out alerts when selected items are available for
# purchase.

import feedparser
import requests
import os
import sys
import pandas as pd
from datetime import datetime, timezone

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from etl_library.logging_util import logger  # noqa: E402
from etl_library.postgres_client import PostgresUtilities  # noqa: E402
from etl_library.general_utilities import EtlUtilities  # noqa: E402

# Load general utilities
etl_utilities = EtlUtilities()

# instantiate Postgres writing class
postgres_utilities = PostgresUtilities()

PIPELINE_ALERT_WEBHOOK = os.environ['ALERT_WEBHOOK']


def build_rss_url(base: str, product: str, country: str):

    return base + country + '&cat=' + product


# method to read the feed and convert to data frame
def read_rss_data(url: str) -> object:

    # read feed
    rpi_feed = feedparser.parse(url)
    logger.info('Read Raspberry Pi Locator Feed')

    # parse out the entries & convert to data frame
    rpi_feed = pd.DataFrame(rpi_feed.entries)

    # validate that there are entries -helpful for when using
    # pre-filtered URLs
    if len(rpi_feed) > 0:
        # subset the data
        subset = rpi_feed[['title', 'published']]
        logger.info('Retrieved product alert data from RSS feed')
        return subset

    else:
        logger.info('No product alerts available..... exiting')
        no_data_cleanup()


def data_transformation(data: object) -> object:

    # update the column names
    data.rename(columns={'title': 'product_alert'}, inplace=True)

    # need to convert published column to date time format
    data['published'] = pd.to_datetime(data['published'], utc=True)

    return data


# update the data frame to show age of individual entries/product updates
def alert_age(data: object, MAX_AGE: int):

    # set time zone, get current time and set format
    current_time = datetime.now(timezone.utc)

    # add current time to data frame
    data['current time'] = current_time

    # calculate the age of the alert in hours
    data['alert_age'] = round((current_time - data['published']) /
                              pd.Timedelta(hours=1), 2)

    # filter out entries younger than a minimum threshold
    # i.e. older entries are probably already sold out.
    data = data[data['alert_age'] < MAX_AGE]

    # subset the data to just the alerts and the alert's age
    data = data[['product_alert', 'alert_age']]

    if len(data) > 0:
        logger.info(f'{len(data)} fresh product alerts available')
        return data
    else:
        logger.info('no fresh product alerts available... exiting')
        no_data_cleanup()


def get_postgres_connection() -> object:

    param_dict = {
        "host": os.environ.get('DB_HOST'),
        "database": os.environ.get('DASHBOARD_DB'),
        "port": int(os.environ.get('POSTGRES_PORT')),
        "user": os.environ.get('POSTGRES_USER'),
        "password": os.environ.get('POSTGRES_PASSWORD')

    }

    # get connection client
    connection = postgres_utilities.postgres_client(param_dict)

    return connection


# clearing out the table when no fresh alerts are available so that
# the dashboard only shows data for when there are new alerts
def no_data_cleanup():

    # load table name
    TABLE = os.environ.get('RPI5_TABLE')

    # get connection
    postgres_connection = get_postgres_connection()

    # clear table
    postgres_utilities.clear_table(postgres_connection, TABLE)

    sys.exit()


def write_data(connection, payload, table):

    status, response = postgres_utilities.write_data_raw(connection,
                                                         payload, table)

    if status == 1:
        message = (f'Postgres write failed for AlphaVantage T-Bill ETL with error: {response}')  # noqa: E501
        response = etl_utilities.send_slack_webhook(PIPELINE_ALERT_WEBHOOK, message)  # noqa: E501
        return status, response

    else:
        logger.info(f"Postgres write successfull, {response} rows written to database")  # noqa: E501
        return status, response


def send_product_alert(data: object):

    # get webhook link
    PRODUCT_WEBHOOK = os.environ.get('PRODUCT_WEBHOOK')

    # convert to json
    alert_json = data.to_json(orient="values")

    headers = {
        'Content-type': 'application/json'

    }

    # create payload in format Slack Webhook expects
    payload = {
        "text": (f'{alert_json}')

    }

    response = requests.post(PRODUCT_WEBHOOK, headers=headers, json=payload)

    if response.status_code != 200:
        logger.info(f'Slack alert send attempt failed with error code: {response.status_code}')  # noqa: E501

    else:
        logger.info(f'Slack alert sent successfully with status code: {response.status_code}')  # noqa: E501

    return response


def main():

    BASE_URL = os.environ['RPI_BASE_URL']
    RPI_PRODUCT = os.environ['RPI_PRODUCT']
    RPI_COUNTRY = os.environ['RPI_COUNTRY']

    URL = build_rss_url(BASE_URL, RPI_PRODUCT, RPI_COUNTRY)

    # get raw feed data
    data = read_rss_data(URL)

    # clean up/transform data
    cleaned_data = data_transformation(data)

    # Load max age env var
    MAX_AGE = int(os.environ['MAX_AGE'])

    # update data frame to show age of each entry & filter out newest
    updated_data = alert_age(cleaned_data, MAX_AGE)

    # send Slack alert
    response = send_product_alert(updated_data)  # noqa: F841

    # get Postgres connection
    connection = get_postgres_connection()

    # get table for RPI data
    TABLE = os.environ.get('RPI5_TABLE')

    # write data to Postgres
    status, write_response = write_data(connection, updated_data, TABLE)


if __name__ == "__main__":
    main()
