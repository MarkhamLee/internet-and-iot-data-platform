## IoT Overview

This folder contains code for capturing data from a variety of sensors and smart devices, and then either writing that data to InfluxDB or transmitting it via MQTT. Except for code, deployed on microcontrollers (e.g., ESP32 or Raspberry Pi Pico), all the code is containerized and typically orchestrated via Kubernetes. The "iot_libraries" folder contains code for common functions like MQTT, Slack Alerts and writing to InfluxDB, each device folder contains the code specific to that device. Currently, all the devices are of the "data collection" variety, gathering climate data (air quality, humidity, temperature), power consumption information and the like.   

![IoT Architecture](images/IoT_architecture_v1.png)  
*Note #1: while this architecture includes the IoT tech stack's full data collection capabilities, but not all of them are used for this specific project, some (microcontrollers) are used for other projects that aren't technically part of this one but use its tech stack/infrastructure. E.g., [MicroPython code for a Raspberry Pi Pico](https://github.com/MarkhamLee/HardwareMonitoring/tree/main/case_temps_rpi_pico) gathering intake, interior and exhaust temperatures for a PC case* 

*Note #2: while not pictured here, hardware telemetry makes use of the above stack as well. All nodes attached to the Kubernetes cluster have containers running on them gathering hardware temperature data and utilization data. For small or arm64 based nodes that data is sent out via MQTT and for the rest the data is written directly to InfluxDb. In the future the plan is for all devices to send out data via MQTT so that two-way communication is possible/enable better HW management.* 

As one can see in the diagram that are currently five paths or types of IoT Devices currently supported by this platform:

* **USB Based Sensors:** while this could be connected to any device, they are usually connected to Raspberry Pis (or similar) that are part of the Kubernetes cluster. These devices are located throughout the house and are also general worker nodes in addition to gathering data from the device(s) plugged into their USB ports.  

* **APIs & Code Libraries:** these are devices that either have a customer accessible API and/or a code library has been created (often unofficial community creations) that allow users to directly access the device without having to use an associated cloud service. Currently, this just applies to the Kasa Smart Plugs used to monitor the power consumption of the Kubernetes cluster and its associated hardware.  

* **Zigbee2MQTT:** is an [open-source community creation](https://www.zigbee2mqtt.io/) to allow people to interact with Zigbee based devices without the need for a proprietary hub, cloud service, etc. [Zigbee is a low-power mesh network protocol](https://csa-iot.org/all-solutions/zigbee/) used to network embedded or IoT devices without the need for Wi-Fi or a local network; this "path" is currently being used to gather data from temperature and humidity sensors and several smart plugs located through my home. The smart plugs also serve as "Zigbee Routers" that relay signals from nearby battery powered Zigbee devices.  

* **GPIO Sensors - Microcontrollers:** these are either ESP32 or Raspberry Pi Pico devices. I'm effectively flashing the device with custom code that allows it to capture data from a connected sensor and then transmit the data via MQTT. The advantage here is that these devices are small, inexpensive, and are often better suited for capturing sensor data than a Raspberry Pi, given the cost difference ($10-12 vs $75-$80) and Raspberry Pis often being under-utilized for this use case. However, I will probably continue to use at least some Pis for gathering sensor data due to the ease of use of deploying code to them when they are part of a Kubernetes cluster or managed via Portainer.  

* **GPIO Sensors - Raspberry Pis:** like the above, sensors plugged into the GPIO pins of a Raspberry Pi or similar device, typically to gather climate related data. These "nodes" are part of the Kubernetes cluster with the code for each sensor running on Docker containers, and the nodes also run general purpose workloads in addition to collecting data from their connected sensors. 

### CI/CD Details

For sensors supported by containerized custom code, the CICD pipeline has two components as the application code and the deployment configurations are managed in two separate repos. This is in keeping with Kubernetes best practices, keeping things separate makes builds cleaner, protects against build loops and is (for me anyway) simpler to manage.  

* Pushing application code to the Git triggers an automated build process that rebuilds the image for the device.  
* In the repo for deployment manifests, configuration files and infrastructure as code items for the Kubernetes cluster, pushing updates to that repo will trigger a new deployment via Argo CD.  

I am currently triggering deployments manually when I update the application code, because in some cases those changes might require physically interacting with the device.  

Microcontrollers are updated manually until I find/develop an elegant way of doing OTA updates. My ideal solution would still leverage Kubernetes even though the microcontrollers are not part of the cluster, e.g., an “update container” managed via Kubernetes that remotely flashes all the microcontrollers. 


### Future Plans: 
* **Upgrade UPS data collection and management:** I have a Raspberry Pi running the server version of an open-source project for managing UPS devices, Network UPS Tools (NUT). The UPS is plugged into the Pi and NUT allows other machines on the network to pull data from the UPS and to receive shutdown signals if the UPS’ battery runs low during a power outage.  I would like to move the manual parts of the setup to an Ansible playbook and containerize the deployment of the clients that receive signals from the main server. I.e., automate as much of the setup as possible. 

* **Add CO2 sensors:** tested an SPG30 sensor and found the results inconsistent, recently purchased MH-Z19B CO2 sensors that I will probably deploy attached to microcontrollers.  

* **Update Nova PMSDS011 sensor control:** update the control code so they warm-up take a few readings over the course of a few minutes and then for 10-20 minutes. I also want to have the sleep period decreased in instances where bad air quality is detected, i.e., run continuously until air quality improves. 

* **Improved storage for the Raspberry Pis:** all the Raspberry Pis are using shared storage from Kubernetes via Longhorn, which takes quite a bit of stress off their internal storage since all their workloads (aside from system related things) are Kubernetes related and the main I/O is over the network. One of the Raspberry Pis boots from an NVME and the other two boot from mini-SD cards, the plan is to either switch the other two to NVME hats OR set them all up to boot over the network.  

* **Rewrite all sensor code currently in Python in C++:** while this is not explicitly necessary it is a good skills development exercise, and it will allow me to potentially move all the sensor code to microcontrollers, thus making my entire setup more energy efficient and potentially freeing up the Raspberry Pis for other projects. I may also just replace the Python based containers on the Raspberry Pis with ones written in C++. 

* **Develop a good method for OTA updates for the microcontrollers:** the idea here is to develop an elegant solution for testing and pushing updates whenever I update the sensor related code. 

* **Setup MQTT topic(s) and a microservice for microcontroller logging:** the idea is to build something to bridge the gap between the microcontrollers and the [Loki-Grafana](https://github.com/MarkhamLee/kubernetes-k3s-data-and-IoT-platform/blob/main/deployment_files/application_install_files/loki_stack/install_instructions.md) logging service on the Kubernetes that picks up logs from the containerized sensor applications. The idea would be to use Node-RED to pass the logs to the Loki or build a containerized service that picks up the logs from the sensors and then pushes it to stdout so that Loki can pick them up.  
