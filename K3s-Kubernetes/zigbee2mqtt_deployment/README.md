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
    * Note: you should configure your MQTT secrets in the Kubernetes space you're deploying 
* I added a node name for the node that has the USB dongle attached. 
* I added resource limits so linting doesn't scream at you + just a good practice. 

Other than that, if you follow the setup instructions for making sure you have serial dialout setup and use a USB extension cable, you should be fine.

