### Troubleshooting the Nova PM SDS011 Air Quality Sensor

* **Install pyserial DO NOT install the serial library even though the import says "serial"**, you will get an error messaging that "serial does not have the attribute Serial" if this occurs, remove the serial library and then reinstall pyserial
* If you run into issues where the ttyUSB0 can't be found:
    * sudo apt remove brltty
    * Check that /dev/ttyUSB0 exists and what permissions are set on it with 'ls -l /dev/ttyUSB0'. If it's anything like standard serial lines (/dev/ttyS{0..31}) it belongs to the group dialout. Become a member of that group ('sudo usermod -a -G dialout your_username_here'). You might have to log out and back in for that to take effect
* In order to access the USB port within you'll need to configure your Docker container to access USB. I did via portainer and adding a device on host and in the container in the 'runtime' tab in the configure your container screen. In my case, the USB is located at: /dev/ttyUSB0. Another way to do it is to create a Docker_Compose file where you specify the devices address. 
* Keep in mind that ttyUSB0 == the first device plugged into the device's USB port, SO if you already have something plugged into the USB port and then you add the air quality sensor, than that sensor will be located at ttyUSB1, which means you will have update the code accordingly.