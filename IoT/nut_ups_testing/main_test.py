# quick script for testing working with NUT and UPS
# devicess. Allows you to just quickly query the device,
# see the available data/fields, diagnose network issues, etc.
import subprocess as sp


UPS_ID = ''
UPS_IP = ''


# build UPS bash query string
def build_ups_query() -> str:

    CMD = "upsc " + UPS_ID + "@" + UPS_IP

    return CMD


def get_ups_data(cmd):

    return sp.check_output(cmd, shell=True)


# parse string from bash ups query into a python dictionary
def parse_data(data: str) -> dict:

    data = data.decode("utf-8").strip().split("\n")

    # parse data into a list of lists, each pair of values becomes
    # its own list.
    initial_list = [i.split(':') for i in data]

    # convert lists into a dictionary
    ups_dict = dict(initial_list)

    return ups_dict


def main():

    CMD = build_ups_query()

    data = get_ups_data(CMD)

    parsed_data = parse_data(data)

    # print data
    print(parsed_data)


if __name__ == '__main__':
    main()
