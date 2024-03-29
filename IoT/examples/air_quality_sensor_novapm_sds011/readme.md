### Troubleshooting

#### If you're having trouble connecting to the USB device (Linux instructions)

* See the troubleshooting steps [here](https://github.com/MarkhamLee/finance-productivity-iot-informational-weather-dashboard/blob/main/IoT/air_quality/readme.md), you can also try:
* Run "lsusb" to see what's connected, you should see a CH340 or UART type device connected
* Unplug all USB devices, plug in the Nova PM device first, then plug in all the rest and try again. You may just need to move the address in the code from USB0 to USB1, USB2, etc., unplugging all and then plugging in the sensor first ensures that it's "USB0" as indicated in the code.
