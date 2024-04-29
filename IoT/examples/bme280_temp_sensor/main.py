import smbus2
import bme280
import logging
from time import sleep
from sys import stdout

logger = logging.getLogger('bme280_logging')
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler(stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s - %(message)s')  # noqa: E501
handler.setFormatter(formatter)
logger.addHandler(handler)


def get_sensor_data(total_count: int, sleep_interval: int):

    loop_count = 0

    while loop_count < total_count:

        # define key variables
        port = 1
        address = 0x77
        bus = smbus2.SMBus(port)

        calibration_params = bme280.load_calibration_params(bus, address)

        # read data
        data = bme280.sample(bus, address, calibration_params)

        # build payload
        payload = {
            "device_id": data.id,
            "timestamp": data.timestamp,
            "temperature": data.temperature,
            "barometric_pressure": data.pressure,
            "humidity": data.humidity
        }

        print(payload)
        loop_count += 1

        sleep(sleep_interval)


def main():

    get_sensor_data(10, 2)


if __name__ == '__main__':
    main()
