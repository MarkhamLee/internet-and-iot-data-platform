import serial
import logging
# from time import sleep
from sys import stdout

logger = logging.getLogger('asana_etl')
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler(stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s - %(message)s')  # noqa: E501
handler.setFormatter(formatter)
logger.addHandler(handler)

# WIP

def connect_to_device():

    pass


def read_co2_data(serial_con: object, bytes=2):

    pass


def main():

    pass


if __name__ == '__main__':
    main()
