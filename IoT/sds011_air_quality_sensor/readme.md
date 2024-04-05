## Air Qualtiy Data from a Nova PM SDS011 Air Quality Sensor

### What's here?
* The container folder has all the files you would need to create a container that can collect data from a Nova PM SDS011 air quality sensor, and then transmit that data to an MQTT broker. You can get details on how to deploy the Eclipse-Mosquitto MQTT broker on Kubernetes [here](https://github.com/MarkhamLee/kubernetes-k3s-data-platform-IoT/tree/main/deployment_files/application_install_files/mosquitto). However, any MQTT broker will do.
* The container uses environmental variables for storing data like MQTT topics, login secrets, etc, so you'll need to configure those in your environment. 
* The values.yaml file in the k3s folder can be used to deploy the container on a Kubernetes clsuter, again, you'll need to configure your environmental variables in Kubernetes. Namely: opaque secrets for the MQTT login data, and using a config map for things like the topic, broker address, etc. 
    * I configured the USB address and the data retrieval interval directly in the values.yaml file, as I wanted the ability to change those based on preferences or the hardware I was using. 
    * The best practice for USB devices is to setup a persistent mapping directly on your hardware so that you can just refer to Nova PM sensor instead of spelling out /dev/ttyUSB0. However, while that works with the other USB devices I have plugged into my nodes, it does not work with this particular device. So I'm just referring to the current mapping for now. 


#### Troubleshooting USB device to Python connections on Linux

* **Install pyserial DO NOT install the serial library even though the import says "serial"**, you will get an error messaging that "serial does not have the attribute Serial" if this occurs, remove the serial library and then reinstall pyserial
* If you run into issues where the ttyUSB0 can't be found:
    * sudo apt remove brltty
    * Check that /dev/ttyUSB0 exists and what permissions are set on it with 'ls -l /dev/ttyUSB0'. If it's anything like standard serial lines (/dev/ttyS{0..31}) it belongs to the group dialout. Become a member of that group ('sudo usermod -a -G dialout your_username_here'). You might have to log out and back in for that to take effect
* In order to access the USB port within you'll need to configure your Docker container to access USB. I did via portainer and adding a device on host and in the container in the 'runtime' tab in the configure your container screen. In my case, the USB is located at: /dev/ttyUSB0. Another way to do it is to create a Docker_Compose file where you specify the devices address. 
* Keep in mind that ttyUSB0 == the first device plugged into the device's USB port, SO if you already have something plugged into the USB port and then you add the air quality sensor, than that sensor will be located at ttyUSB1, which means you will have update the code accordingly.