## Finance, Productivity, Home IoT, General Info & Weather Dashboard

This project started out with the following goals: 

1) Enhance my productivity by aggregating finance, productivity, weather, and other useful data in a way that would prevent me from getting distracted by looking up that data on my phone. Think: the scenario where you pick up your phone to check the weather and wind up distracted by Instagram.  

2) Gain insights into climate and energy consumption by collecting data from a variety of sensors around my house. 

3) Professional development, by giving me an opportunity to work with technologies I have had limited exposure to and/or technologies I am curious about. 

It has since morphed more into building an extensible, scalable, and easy to manage data platform to support projects that have a significant data collection or management component. The general idea is that whether its through common files for building data logging, IoT sensor or ETL containers, CICD pipelines, etc., the level of effort to add new types of sensors, connect to IoT devices or do anything involving collecting data will be relatively easy as the bulk of the work is already complete. E.g., through the use of templates, pre-built code for MQTT and writing to InfluxDB 80-90% of the code for adding new IoT sensors is already written. This also means that while the items in this repo are items that specifically for the original scope of the project, this same platform is also being used for other projects ranging from custom PC mods to monitoring plants. 

### Recent Updates 
* 04/17/224: updates from the last ~3 weeks 
    * Updates to Kubernetes deployment manifests for IoT devices, added Argo CD configurations for managing CICD for IoT device scripts/containers. Python scripts + container for SGP30 CO2 sensor (4/17)
    * Refactoring/re-writes for all Node.js ETL pipelines: main pipeline code + updated unit tests (4/16)
    * C++ file for provisioning ESP32s with Wi-Fi and MQTT creds (4/11)
    * IoT architecture diagram and documentation (4/10)
    * Added C++ code for retrieving data from a DHT22 temperature sensor connected to an ESP32 and transmitting the data via MQTT (4/9)
    * Added three new ETLs that work in concert to retrieve T-Bill data for use in plotting the daily yield curve. i.e., ETL containers + Airflow DAGs for loading historical data, retrieving data for the current day and data transformations load a reporting/golden table for the yield curve plot.  (4/3)
    * Re-wrote all Dockerfiles to use multi-stage builds, resulting in smaller and more secure Docker images. ETL work flow diagram and documentation (4/2)
    * Added python scripts + container for BME280 temperature sensor (3/31)
* Additional updates are available [here](https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard/blob/main/documentation/updates.md)

![Dashboard Thumbnail](/images/dashboard_screenshot4.png)  
*Snapshot of some of the tracked data* 

This repo contains the code for the ETL pipelines for various data sources, YAML files for deploying various micro-services on Kubernetes, containers for interacting with/pulling data from remote sensors/IoT devices and a lot more. The plan is to continuously add data sources/features in the coming months. You can read a full list of recent updates [here](https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard/blob/main/documentation/updates.md).

## Architecture - Tech Stack
This project has the following primary components: 
* **ETL Pipelines:** data ingestion from external sources (APIs) 
* **IoT:** ingesting and managing a variety of sensor/data collection devices
* **CICD:** automated multi-architecture Docker image builds and comtainer deployments, building and deploying micro-services that used shared/common private libraries.
* **Monitoring & Alerting:** sending out alerts via Slack in response to specific events, pipeline failures, device issues, measurements above a pre-defined threshold, etc.
* **Ops Data:** collecting data from hardware devices, the firewall, UPS, et, al.

![Architecture](/images/new_architecture_mkIIa.png)  
*The TL/DR: data from external sources/APIs comes in via Airflow or Argo Workflows, data from IoT devices from in via device specific libraries, GPIO or USB sensors or the Zigbee2MQTT library. Alerts are generated due to measurements exceeding certain thresholds, data specific conditions (GitHub security alerts, certain products in stock) and when data pipelines or devices malfunction.*
All logos and trademarks are property of their respective owners and their use in the diagram represents an acceptable use based on my understanding of their guidelines. **If that is not the case, please let me now and I'll update the diagram ASAP.** 

### Tech Stack - Detailed Description

* **ETL Tools:** using a variety of ETL/container orchestration tools to gather data from external APIs (Asana, Finnhub, OpenWeather and the like), in addition to general container orchestration:  

    * **Airflow:** container orchestration/scheduling for data ingestion from external sources.  

    * **Argo Workflows:** ETL, general container orchestration and in addition to event based use cases, as it is capable of more complex logic than Airflow or just deploying containers directly on Kubernetes.  

    * **Kubernetes Cron Jobs:** not as elegant as some of the other options but often the simplest to implement, currently being used to deploy IoT related containers 

* **CI/CD Pipelines:** each Dockerized microservice or workload has an accompanying GitHub Actions config file (see .github/workflows), which tells GitHub Actions what folders/files to monitor. Whenever a file that is used to build an image(s) is updated/pushed to a monitored folder for a particular image, GitHub actions will automatically build multi-architecture Docker images (amd64, arm64) and then upload them to Docker Hub, where they will be picked up by my Kubernetes cluster. What this means in practice is that I update a Python script that several ETL containers include in their images (E.g., InfluxDB used by Finnhub, GitHub and Openweather ETLs), updating that file will trigger an update for all the ETL containers that use it, which will be then be used the next time that pipeline runs. 

* **Languages:** up until recently everything (ETL, Monitoring, Ops Microservices, IoT, et al) was written in **Python**. However, all the ETL workloads are built and deployed via Docker containers so I can use the same pipeline code on Airflow (via the K8s Pod Operator), Argo Workflows and other orchestration tools without having to maintain separate code for each; meaning: the ETL workflows can be language agnostic, even when using Python based tools like Airflow. To take full advantage of this *"language agnostic ETLs"* approach, I am currently writing **TypeScript w/ Node.js** versions of most of the ETLs and will write **Scala with Spark** versions soon.   

* **InfluxDB:** for storing time series data, **PostgreSQL** for everything else  

* **Grafana:** to display data/dashboards  

* **Grafana-Loki Stack:** for log aggregation, Prometheus for general monitoring 

* **Eclipse-Mosquito:** for the MQTT broker that will receive messages from IoT/Smart Devices  

* **Docker:**  where possible, all custom code, micro-services, et, al are deployed as containerized workloads.  

* **Monitoring:** **Grafana-Loki** for aggregating logs from the cluster and from individual containers, workloads and the like. **The Kube Prometheus Stack** to monitor the cluster, detect when a container crashes, a node goes offline, etc. All alerts are sent via **Prometheus Alerts Manager & Slack**.  

* **Portainer:** used to manage all docker containers not deployed to K3s, meaning: the validation/beta environment, plus new services being tested on Raspberry Pis or similar devices. 

* **Node-RED:** to manage the incoming MQTT messages, data transformation of MQTT messages and then writing the data to InfluxDB  

* **Slack:** is integrated into every function: alerts for cluster monitoring, issues with data pipelines, IoT sensors malfunctioning, etc., alerts are generated both when an issue occurs and when it is resolved. Additionally, reminder alerts are generated for things like Raspberry Pi 5s being in stock (detected by the Raspberry Pi locator bot), reminders that the secure certs for my firewall need to be renewed, etc. 

* The **Zigbee2MQTT library** plus a **Sonoff Zigbee USB Dongle** to receive data from Zigbee (local wireless mesh network for IoT devices) enabled IoT devices and then send it off as MQTT messages. This makes a lot of smart devices "plug-n-play" as I do not need special apps or hardware to receive data from those devices.  

* Where possible using code libraries like [Python-Kasa for TP Link Kasa devices](https://github.com/python-kasa/python-kasa) to connect to IoT and Smart Devices directly. 

## ETL Pipeline Details

I originally, built all ETL pipelines as Airflow DAGs, but that made testing tricky as the file structure that worked for testing on my local Airflow instance did not always work on my Airflow instance deployed on Kubernetes due to how files were imported from Github. I have since moved everything to "standard" Python scripts running in Docker containers for a couple of reasons: 

* By making the pipelines more agnostic, it is much easier to experiment with, test, and get experience with other ETL and orchestration tools.  

* No longer need to worry about managing dependencies for Airflow as they are all baked into the container 

* I can test locally without having to maintain multiple Airflow instances or do things like test a standard python ETL script and then test it again as a DAG.  

* The CI/CD pipeline automatically rebuilds the images whenever a relevant file is updated and the pipelines always check for new images before they run, this makes updating the pipelines smooth and easy: I update a file, and everything is taken care of via the automations for CI/CD and ETL. 

* By leveraging libraries of common functions/scripts/files (API clients, writing to DBs, logging, etc.), I can not only build new pipelines faster, but updates/improvements to those core files can be used by any of the existing ETL pipelines as soon as their images are updated. 

*i.e., all the advantages of using containers...*  

Airflow and Argo Workflows are my primary ETL tools. While my preference leans slightly towards Airflow, building ETL containers that work with both will help ensure I meet my goals of making things as "tool agnostic" as possible. I will also sometimes use Kubernetes cron jobs to test containers.  

To compensate for logging and alerting when using the Airflow Kubernetes Pod Operator or Argo Workflows vs traditional DAGs, I have added more logging to the ETL containers and Slack Alerts for failures at any stage of the pipeline. 

### Current and Future Data Sources

* Asana (where I keep my to do lists) -- *shockingly, the former project manager uses project management software for day to day task management* [DONE]
* Air Quality & Weather via the OpenWeather API [DONE]
* Finance: tracking the S&P 500, T-Bills and maybe 1-2 other stocks [DONE]
    * Alpha Vantage for treasuries [DONE]
    * Finnhub for stocks [DONE]
    * Currency exchange rates: British Pounds, Canadian Dollar, Euros and Japanese Yen [PENDING]
* Raspberry Pi Locator: built a simple bot for consuming the RSS feed and then alerting me via Slack if the stock update is less than 12 hours old [DONE]
* Tracking the Air Quality, CO2 levels, Humidity and Temperature levels inside various rooms in my house [DONE]
* Tracking the power consumption of my homelab [DONE]
* GitHub: now that I'm using GitHub actions I need to track my usage so I can monitor potential costs/if I'm going to go past the allotment of minutes already included in my current subscription. [DONE]
* GitHub: tracking dependabot security alerts for this and other repos, and sending myself Slack alerts whenever a new security risk is identified. [DONE]
* Tracking soil moisture levels of houseplants [TESTING]
* Tracking hydration - still looking for a good way to do this that isn't janky and/or require me to build a web app that is always connected/synching as opposed to being able to periodically retrieve data. 
* Discord - I join servers and then rarely pay attention and often miss announcements related to DIY/Makers, Podcasts I enjoy, Video Game Mods and other hobbies. 
* eBay? I need to explore the API more but the plan is to track auctions and automate searches for items I'm interested in. 

## **K3s Distribution of Kubernetes:** 

All third-party applications and custom code are deployed on Kubernetes-K3s via Docker containers. A couple of additional details: 

* High availability configuration via three Server/control plane + general workload nodes running on three **Beelink SER 5 Pros (Ryzen 5 5560U CPUs):** these high performance but power efficient devices can deliver about 70-80% of the performance of a desktop 11th Gen i5, but in an Intel NUC sized chassis that consumes about 70-80% less power. The server nodes are all equipped with 2TB NVME drives and 64GB of RAM.  

* **Orange Pi 5+ worker nodes:** this device is on par with most N95/N100 mini computers, but in a smaller and more power efficient footprint, with faster (full Gen3 NVME) storage to boot. 

* GPIO and USB based sensors are running on **Raspberry Pi 4B 8GB** devices primarily as "sensor nodes" that collect data from USB and GPIP based sensors, but given the minimal resources used by these sensors I also have them in the "arm64 worker" pool of nodes that run ETL jobs. However, I do not use them for more general workloads like Mosquitto or Node-RED. 

* Hardware wise future plans include adding dedicated storage nodes, additional general purpose worker nodes and nodes equipped with hardware for AI/ML acceleration, E.g., NVIDIA GPUs, RockChip NPUs, etc.  

* I use **letsencrypt.org certificates + Traefik** as an ingress controller to secure/encrypt connections to the services running on the cluster.  

* The cluster is managed with **Rancher**, **Longhorn** is used to manage shared storage across the cluster, and all shared storage + Rancher data is backed up to an AWS S3 bucket on an hourly basis. However, given the increasing cost I plan to spin up a local object store and/or NAS to back-up my data. 

* Prometheus is used for monitoring the nodes and the **Grafana-Loki Stack** is used for aggregating/collecting logs.  

* **Operating Systems:** Only **Ubuntu 22.04** distros for the moment  

* You can get more details on my K3s cluster in the separate repo I created for it [here](https://github.com/MarkhamLee/kubernetes-k3s-data-platform-IoT). 


## Automation, Edge and IoT Devices

* **SONOFF Zigbee 3.0 USB Dongle Plus Gateway:** coupled with the [Zigbee2MQTT library](https://www.zigbee2mqtt.io/guide/getting-started/), this gives me the ability to receive data from any Zigbee enabled device without having to purchase hubs from each manufacturer to go along with their device. Note: Zigbee2MQTT is not explicitly required, you could always write your own code for this purpose 

* Zigbee is a mesh network where the battery powered devices only transmit data and the ones powered by mains/AC power also serve as routers. I have deployed Zigbee smart plugs as routers in each room I've also deployed Zigbee devices to, as without them the battery powered devices often suffer from unstable connections.  

* **Aquara and Sonoff** temperature sensors that connect via the Zigbee protocol 

* **Nova PM SDS011** IoT Air Quality sensors connected to the Raspberry Pi 4Bs *"dedicated sensor nodes"* until I find an air quality device I both like AND uses the Zigbee protocol, and/or is built by a manufacturer that provides an API for interacting with their devices.  

* **TP Link Kasa Smart Plugs** tracking power consumption, voltage and amps data over Wi-Fi via the [Python-Kasa library](https://python-kasa.readthedocs.io/en/latest/index.html)  

* Currently testing SCD40 and MH-Z19B CO2 sensors, when these are fully deployed, they will likely be connected to the Raspberry Pis I already have deployed around the house, but I am considering using a microcontroller like a Raspberry Pi Pico or ESP32 device instead.  

* I have also tested DHT22 temperature sensors and found them to be more reliable than the Zigbee based devices I tried in terms of how often they send data, stability, etc., however, a good 1/3 of the DHT22 devices I received were duds. That said, the working DHT22s I received have been running 24/7 for several months without issues. 

## Key References: 
* [Airflow best practices:](https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html) I made extensive use of this documentation to not only re-write my original DAGs into the Taskflow API format, but to make sure I was following as many best practices as possible. I also used their documentation to structure my Airflow Docker container. 