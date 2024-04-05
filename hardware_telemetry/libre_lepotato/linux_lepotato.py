# Markham Lee (C) 2023
# Class with data retrieval and utility methods to support pulling hardware
# data from a Libre LePotato Single Board Computer
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
import psutil


class LibreCpuData():

    def __init__(self):

        # get the # of cores, as we can use that to iterate through and
        # get things like current speed for all CPU cores
        self.core_count = psutil.cpu_count(logical=False)

    # get average clock speed for all cores
    def get_freq(self, all_cpu=False):

        all_freq = psutil.cpu_freq(percpu=all_cpu)[0]
        all_freq = round(all_freq, 1)

        return all_freq, self.core_count

    # CPU load
    def get_cpu_data(self):

        cpu_util = (psutil.cpu_percent(interval=1))
        cpu_util = round(cpu_util, 1)

        return cpu_util

    # get current RAM used
    def get_ram_data(self):

        ram_use = (psutil.virtual_memory()[3]) / 1073741824
        ram_use = round(ram_use, 2)

        return ram_use

    @staticmethod
    def libre_lepotato_temps():

        return psutil.sensors_temperatures()['scpi_sensors'][0].current
