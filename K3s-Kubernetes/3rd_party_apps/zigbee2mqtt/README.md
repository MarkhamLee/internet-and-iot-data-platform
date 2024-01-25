### YAML files for deploying zigbee2mqtt on Kubernetes 

This folder contains the YAML files I used to deploy Zigbee2MQTT on my Kubernetes-K3s cluster. They're largely influenced by what I found [here](https://github.com/Koenkk/zigbee2mqtt/discussions/10899), save a couple of changes:

* I was having issues with values defined in the values.yaml or config map being ignored in favor of the configuration.yaml file baked into the image. To get around this I followed the instructions on the Zigbee2mqtt web site to override those values via environmental varibles. You can still use a config map though, just reference the config values in your environmental variables. 
    * This can be especially problematic if your Zigbee dongle is on USB0 instead of ACM0, no mattter what you put into the configuration.yaml or your values.yaml file, the image will ignore it in favor of the ACM0 address in the image's configuration file. Chances are, if you're having trouble deploying this workload, the device address is the issue. 
    * See below for the format to override the values in configuration.yaml file in the Docker image. I.e. 
    ~~~
    config:
        serial:
            port:
    ~~~
    Becomes:
    ~~~
    ZIGBEE2MQTT_CONFIG_SERIAL_PORT
        value: <path/to/your/USB/device>
    ~~~
* I added environmental variables for secrets
    * You should configure your MQTT secrets in the Kubernetes namespace you're deploying into
* I added a node name for the node that has the USB dongle attached. I.e., you need to explicitly define the node, so the pod for this app doesn't get deployed on a node that the dongle isn't plugged into. 
    * You can get around this limitation by using something like ser2net to allow you to effectively stream your USB device over your network/make it available over tcp. E.g., you could plug your Zigbee dongle into a Raspberry Pi 3B or Zero, use the TCP address as the serial port path and now your Zigbee2MQTT deployment isn't tied to a specifc node. I've never tried it, but the instructions for it are [here](https://www.zigbee2mqtt.io/advanced/remote-adapter/connect_to_a_remote_adapter.html)
    * Similarly there are USB network devices that perform the same function as above only with simpler configuration, you plug the USB device into the network device and now other devices in your network can receive data from it. If you search usb over tcp/ip on Amazon or Newegg, you can find them for for around $50-$70.00. For the record I've never tried it, but it's on my list. 
* I added resource limits so linting doesn't scream at you + just a good practice. 

#### Critical step once you deploy the application

The default for Zigbee2MQTT is to log EVERYTHING, meaning every single time it receives data from any of your devices it will update the log file with the values from that device. Even if you only have a dozen or so devices it won't take long before you use up your container's allocated space for logs (the mount for /data), and then the container will crash. To avoid this: go to settings --> advanced --> Log level and set it to "warn" at minimum, so the service is only logging things you need to troubleshoot or address problems. 

If your container crashes due to this issue you'll get an "out of space" error, and the path to fixing it is just manually increasing the size of persistent volume claim. Once the container crashes it will be too late to fix it in the values.yaml file, because the the container won't be able to spin up and increase the size of the volume claim. 

FTR, I looked for a setting or config for deleting old logs but couldn't find anything, my plan is to keep looking and if I don't find anything either build a fix myself and/or raise it as an issue. 

Other than that, if you follow the setup instructions for making sure you have serial dialout setup and use a USB extension cable, you should be fine.

