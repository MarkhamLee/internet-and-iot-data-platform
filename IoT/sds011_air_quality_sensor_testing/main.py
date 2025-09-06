# Simple script to quickly test and troubleshoot a SDS011 Air Quality sensor
import serial
from time import sleep


pm2_bytes = 2
pm10_bytes = 4
device_id = 6

USB = '/dev/ttyUSB0'

serial_connection = serial.Serial(USB)


def parse_value(message, start_byte, num_bytes=2,
                byte_order='little', scale=None):

    """Returns a number from a sequence of bytes."""
    value = message[start_byte: start_byte + num_bytes]
    value = int.from_bytes(value, byteorder=byte_order)
    value = value * scale if scale else value

    # flush buffer - should help avoid issues where we get
    # anomolous readings
    serial_connection.reset_input_buffer()

    return value


def main():

    rounds = 0

    while rounds < 10:

        data = serial_connection.read(10)

        pm2 = round((parse_value(data, pm2_bytes) * 0.1), 4)
        pm10 = round((parse_value(data, pm10_bytes) * 0.1), 4)

        print(f'The PM2.5 value is: {pm2} and the PM10 value is: {pm10}')
        rounds += 1
        print(f'Completed data read round: {rounds}')

        sleep(5)


if __name__ == '__main__':
    main()
