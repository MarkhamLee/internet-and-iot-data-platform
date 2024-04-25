# Markham Lee (C) 2024
# kubernetes-k3s-data-and-IoT-platform
# https://github.com/MarkhamLee/kubernetes-k3s-data-and-IoT-Platform
# Quick test to make sure you can connect to the UPS device, this will also
# give you a good view into what fields are available, in case you need
# to make any modifications to the monitoring code.
import os
from pprint import pp
import subprocess as sp

UPS_IP = os.environ['UPS_IP']
UPS_ID = os.environ['UPS_ID']
CMD = "upsc " + UPS_ID + "@" + UPS_IP

data = sp.check_output(CMD, shell=True)
data = data.decode("utf-8").strip().split("\n")

# parse data into a list of lists, each pair of values will be in its own list
initial_list = [i.split(':') for i in data]

# convert the list into python dictionary
test_dict = dict(initial_list)

pp(test_dict)
