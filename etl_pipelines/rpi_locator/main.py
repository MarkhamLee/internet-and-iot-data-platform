import feedparser
import requests
import os
import sys
import pandas as pd
from io import StringIO  # noqa: E402
from datetime import datetime, timezone

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from etl_library.logging_util import logger  # noqa: E402
from etl_library.postgres_client import PostgresUtilities  # noqa: E402

# instantiate Postgres writing class
utilities = PostgresUtilities()


# method to read the feed and convert to data frame
def read_rss_convert(url: str) -> object:
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
    data['published'] = pd.to_datetime(data['published'])

    return data


# update the data frame to show age of individual entries/product updates
def alert_age(data: object, MIN_AGE: int):

    # set time zone, get current time and set format
    current_time = datetime.now(timezone.utc)
    current_date_time = current_time.strftime("%Y-%m-%d %H:%M:%S")

    # add current time to data frame
    data['current time'] = current_date_time

    # convert the date string to date time format
    data['current time'] = pd.to_datetime(data['current time'])

    # calculate the age of the alert in hours
    data['alert_age'] = (data['current time'] - data['published'])\
        / pd.Timedelta(hours=1)

    # filter out entries younger than a minimum threshold
    # i.e. older entries are probably already sold out.
    data = data[data['alert_age'] < MIN_AGE]

    # subset the data to just the alerts and the alert's age
    data = data[['product_alert', 'alert_age']]

    if len(data) > 0:
        logger.info(f'{len(data)} fresh product alerts available')
    else:
        logger.info('no fresh product alerts available... exiting')
        no_data_cleanup()

    return data


def get_postgres_connection() -> object:

    param_dict = {
        "host": os.environ.get('DB_HOST'),
        "database": os.environ.get('DASHBOARD_DB'),
        "port": int(os.environ.get('POSTGRES_PORT')),
        "user": os.environ.get('POSTGRES_USER'),
        "password": os.environ.get('POSTGRES_PASSWORD')

    }

    # get connection client
    connection = utilities.postgres_client(param_dict)

    return connection


# clearing out the table when no fresh alerts are available so that
# the dashboard only shows data for when there are new alerts
def no_data_cleanup():

    # load table name
    TABLE = os.environ.get('RPI5_TABLE')

    # get connection
    postgres_connection = get_postgres_connection()

    # clear table
    utilities.clear_table(postgres_connection, TABLE)

    exit()


# strict enforcement of what columns are used ensures data quality
# avoids issues where tab delimiting can create erroneous empty columns
# in the data frame
def prepare_payload(payload: object, columns: list) -> object:

    buffer = StringIO()

    # explicit column definitions + tab as the delimiter allow us to ingest
    # text data with punctuation  without having situations where a comma
    # in a sentence is treated as new column or causes a blank column to be
    # created.
    payload.to_csv(buffer, sep='\t', columns=columns, header=False)
    buffer.seek(0)

    return buffer


# write data to PostgreSQL
def write_data(data: object):

    TABLE = os.environ.get('RPI5_TABLE')

    # get dataframe columns for managing data quality
    columns = list(data.columns)

    # count rows
    row_count = len(data)

    # get connection and clear the table
    postgres_connection = get_postgres_connection()

    # clear table
    utilities.clear_table(postgres_connection, TABLE)

    # prepare payload
    buffer = prepare_payload(data, columns)

    # write data
    response = utilities.write_data(postgres_connection, buffer, TABLE)

    if response == 0:
        logger.info(f"PostgreSQL write complete, {row_count} rows written to database")  # noqa: E501


def send_alert(data: object):

    # get webhook link
    WEBHOOK_URL = os.environ.get('WEBHOOK')

    # convert to json
    alert_json = data.to_json(orient="values")

    headers = {
        'Content-type': 'application/json'

    }

    # create payload in format Slack Webhook expects
    payload = {
        "text": (f'{alert_json}')

    }

    response = requests.post(WEBHOOK_URL, headers=headers, json=payload)

    if response.status_code != 200:
        logger.info(f'Slack alert send attempt failed with error code: {response.status_code}')  # noqa: E501

    else:
        logger.info(f'Slack alert sent successfully with status code: {response.status_code}')  # noqa: E501

    return response


def main():

    URL = os.environ.get('LOCATOR_URL')
    MIN_AGE = int(os.environ.get('MIN_AGE'))

    # get raw feed data
    data = read_rss_convert(URL)

    # clean up/transform data
    cleaned_data = data_transformation(data)

    # update data frame to show age of each entry & filter out newest
    updated_data = alert_age(cleaned_data, MIN_AGE)

    # write data to Postgres
    write_data(updated_data)

    # send Slack alert
    response = send_alert(updated_data)  # noqa: F841


if __name__ == "__main__":
    main()
