import os
import sys
from finnhub_utilities import FinnHubUtilities

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from etl_library.influx_utilities import InfluxClient  # noqa: E402
from etl_library.logging_util import logger  # noqa: E402
from etl_library.general_utilities import EtlUtilities  # noqa: E402

# instantiate utilities class
finn_util = FinnHubUtilities()

# Load general utilities
etl_utilities = EtlUtilities()

# load Slack Webhook URL variable for sending pipeline failure alerts
WEBHOOK_URL = os.environ.get('ALERT_WEBHOOK')


def get_prices(symbol: str):

    try:
        data = finn_util.get_stock_data(symbol)
        logger.info('stock data retrieved')
        return data

    except Exception as e:
        message = (f'Finnhub stock price data retrieval error: {e}')
        logger.debug(message)
        response = etl_utilities.send_slack_webhook(WEBHOOK_URL, message)
        logger.debug(f'Slack pipeline failure alert sent with code: {response}')  # noqa: E501


def parse_data(data: dict) -> dict:

    return finn_util.parse_stock_data(data)


def write_data(data: dict):

    influx = InfluxClient()

    MEASUREMENT = os.environ['FINNHUB_MEASUREMENT_SPY']

    # Influx DB variables
    INFLUX_KEY = os.environ['INFLUX_KEY']
    ORG = os.environ['INFLUX_ORG']
    URL = os.environ['INFLUX_URL']
    BUCKET = os.environ['BUCKET']

    # get the client for connecting to InfluxDB
    client = influx.create_influx_client(INFLUX_KEY, ORG, URL)

    # base payload
    payload = {
        "measurement": MEASUREMENT,
        "tags": {
                "finnhub_API": "stock_prices",
        }
    }

    try:
        # write data to InfluxDB
        influx.write_influx_data(client, payload, data, BUCKET)
        logger.info('stock data successfuly written to InfluxDB')

    except Exception as e:
        message = (f'InfluxDB write error for Finnhub API data: {e}')
        logger.debug(message)
        response = etl_utilities.send_slack_webhook(WEBHOOK_URL, message)
        logger.debug(f'Slack pipeline failure alert sent with code: {response}')  # noqa: E501


def main():

    STOCK_SYMBOL = os.environ['STOCK_SYMBOL']

    try:
        stock_data = get_prices(STOCK_SYMBOL)
        logger.info('Stock price data retrieved successfully')

    except Exception as e:
        message = (f'Finnhub stock price pipeline failure: {e}')
        logger.debug(message)
        response = etl_utilities.send_slack_webhook(WEBHOOK_URL, message)
        logger.debug(f'Slack pipeline failure alert sent with code: {response}')  # noqa: E501

    # parse data into a json payload
    stock_payload = parse_data(stock_data)

    # write data to InfluxDB
    write_data(stock_payload)


if __name__ == '__main__':
    main()
