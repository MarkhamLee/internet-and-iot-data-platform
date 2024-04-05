# Markham Lee (C) 2023
# Class with data retrieval and utility methods to support pulling hardware
# data from an Orange Pi 3B
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
import psutil


class OrangePi3BData():

    def __init__(self):

        # get the # of cores, as we can use that to iterate through and
        # get things like current speed for all CPU cores
        self.coreCount = psutil.cpu_count(logical=False)

    # get average clock speed for all cores
    def get_freq(self, all_cpu=False):

        allFreq = psutil.cpu_freq(percpu=all_cpu)[0]
        allFreq = round(allFreq, 1)

        return allFreq, self.coreCount

    # CPU load/utilization
    def get_cpu_data(self):

        cpuUtil = (psutil.cpu_percent(interval=1))
        cpuUtil = round(cpuUtil, 1)

        return cpuUtil

    # get current RAM used
    def get_ram_data(self):

        ramUse = (psutil.virtual_memory()[3]) / 1073741824
        ramUse = round(ramUse, 2)

        return ramUse

    # Orange Pi 3B Temps, however, should work on any device
    # # running a Rockchip 3566
    @staticmethod
    def rockchip_3566_temps():

        return psutil.sensors_temperatures()['cpu_thermal'][0].current, \
            psutil.sensors_temperatures()['gpu_thermal'][0].current
