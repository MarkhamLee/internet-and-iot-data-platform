# Markham Lee (C) 2024
# kubernetes-k3s-data-and-IoT-platform
# https://github.com/MarkhamLee/kubernetes-k3s-data-and-IoT-Platform
# Quick test to make sure you can connect to the UPS device, this will also
# give you a good view into what fields are available, in case you need
# to make any modifications to the monitoring code.
# Note: you will need to install the NUT client on your machine first,
# e.g., sudo apt install nut-client
import os
from pprint import pp
import subprocess as sp

# IP of your server running NUT, you can hard code for initial testing
UPS_IP = os.environ['UPS_IP']

# name you gave your UPS during setup, you can hard code for testing
UPS_ID = os.environ['UPS_ID']

# define the command, same one you'd use at the command line
CMD = "upsc " + UPS_ID + "@" + UPS_IP

# run command using subprocess library, clean up output
data = sp.check_output(CMD, shell=True)
data = data.decode("utf-8").strip().split("\n")

# parse data into a list of lists, each pair of values will be in its own list
initial_list = [i.split(':') for i in data]

# convert the list into python dictionary, each list in the list of lists
# becomes a key value pair
test_dict = dict(initial_list)

# print out the dictionary to see the values
pp(test_dict)
