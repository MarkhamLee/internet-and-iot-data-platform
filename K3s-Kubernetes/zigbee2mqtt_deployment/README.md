### YAML files for deploying zigbee2mqtt on Kubernetes 

This folder contains the YAML files I used to deploy Zigbee2MQTT on my Kubernetes-K3s cluster. They're largely influenced by what I found [here](https://github.com/Koenkk/zigbee2mqtt/discussions/10899), save a couple of changes:
* I didn't use a config map, I conveyed that data via environmental variables instead as I found the docker image for Zigbee2MQTT ignores the configmap in favor of a configuration.yaml file baked into the image. 
    * This can be especially problematic if your Zigbee dongle is on USB0 instead of ACM0, no mattter what you put into the configuration.yaml file, the image will ignore it in favor of the ACM0 address in the image's configuration file. Chances are, if you're having trouble deploying this workload, the device address is the issue. 

Proper config for my device (Sonoff Zigbee 3.0 USB Dongle that registers on USB0, you can also reference it by the full name of the device. 

```
- name: ZIGBEE2MQTT_CONFIG_SERIAL_PORT
              value: /dev/ttyUSB0
```

* I added environmental variables for secrets
    * Note: you should configure your MQTT secrets in the Kubernetes space you're deploying 
* I added a node name for the node that has the USB dongle attached. 
* I added resource limits so linting doesn't scream at you + just a good practice. 

Other than that, if you follow the setup instructions for making sure you have serial dialout setup and use a USB extension cable, you should be fine.

