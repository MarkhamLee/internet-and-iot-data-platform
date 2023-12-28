# Productivity, Home IoT, Music, Stocks & Weather Dashboard

![Dashboard Thumbnail](/images/dashboard_screenshot3.png)  
*Snapshot of some of the tracked data* 

This project has the following objectives: 
1) Get more experience with Airflow by building a data aggregation platform that's inclusive of API sources, IoT devices and potentially even some RSS feeds and web scraping. 
2) Aggregate useful data that I would normally get from my phone or various online sources into one place so as to reduce distractions, and/or so I don't miss out on things I often forget to check or keep with. This includes but is not limited to: Asana tasks, financial data, fitness/health data, weather, etc. The basic idea is that instead of looking up something on my phone and then getting distracted by LinkedIn or reels, I can glance at a screen or browswer tab and not interrupt my daily workflow. 
3) Expand my skills with respect to automation, edge and IoT technologies, as home automation and smart devices are a significant part of this project.  
4) Get more hands-on experience building and deploying micro-services to Kubernetes clusters. 

*TL/DR: I over-enginered a data aggregation platform for professional development, improved productivity and to not have limitations on what data I can display, how it's managed, et al that you often encounter when using something off the shelf, even if it's customizable.*

The repo contains the the code for the Airflow Dags (written in TaskFlow API format), custom Airflow plugins for connecting to things like InfluxDB and the custom code for managing and ingesting data It also has the extended but not quite custom Docker image I used for Airflow (*so it has all of my Python dependencies*). Plan is to continuously add data sources/features in the coming months. 

### Recent Updates 
* 12/27: Updated the Readme with the latest architecture and technical details
* 12/26: moved all single board computers (e.g., Raspberry Pis) to the cluster as dedicated agent nodes for receiving data from USB based climate sensors and the Zigbee Hub. Added instructions + the values.yaml files for deploying Zigbee2MQTT on Kubernetes. 
* 12/18: added container/microservice (flask API wrapper around Slack client) for sending alert messages via Slack, so I don't have to include the Slack SDK, client, etc., in the individual services that send Slack alerts. 

## Architecture - Tech Stack

![Architecture](/images/dashboard_architecture_MKIV.png)  
*The TL/DR: is that data from external APIs comes in via Airflow, data from internal sensors and/or smart devices comes in via Zigbee and/or custom code (deployed on Docker containers) to an MQTT broker that is managed/orchestrated via Node-Red. If things go wrong, I get alerts via Slack.*

All logos and trademarks are property of their respective owners and their use in the diagram represents an acceptable use based on my understanding of their guidelines. **If that is not the case, please let me now and I'll update the diagram ASAP.** 

* **K3s Distribution of Kubernetes:** all third party applications and custom code are deployed on Kubernetes-K3s via Docker containers. A couple of additional details:
   * USB devices like air quality sensors and the Zigbee hub are deployed on small board computers (Raspberry Pis, Orange Pis and the like) that serve as "specialty nodes", in that they're part of the K3s cluster but are only used for receiving data from those devices and not for running general workloads. 
   * The initial architecture had USB sensors and Zigbee2MQTT running on computers that weren't part of the cluster, this was mostly done because the dependence on a singular piece of hardware precluded HA or redundancy. I recently moved all of those devices and services to the cluster, because once the USB devices are plugged in adding or moving services around is very quick and easy.  
   * Moving forward I'll test custom code or new to me 3rd party apps on devices that aren't part of the cluster, but can connect to it via MQTT or an api endpoint prior to deploying that service within the cluster. Kubernetes often presents some additional complexities, so it makes sense to get all the service specific wrinkles ironed out before deploying something on Kubernetes 
   * You can get more details on my K3s cluster in the separate repo I created for it [here](https://github.com/MarkhamLee/kubernetes-k3s-data-platform-IoT).
* **Airflow:** data ingestion + orchestration from external APIs E.g.,  Asana, Finnhub, OpenWeather API. etc.   
* **InfluxDB:** for storing time series data, **PostgreSQL** for everything else 
* **Grafana:** to display data/dashboards 
* **Eclipse-Mosquito:** for the MQTT broker that will receive messages from IoT/Smart Devices 
* **Docker:** all the big building blocks (e.g. Airflow, InfluxDB, etc.) are deployed via Docker containers in addition to the custom code I wrote for things like monitoring air quality, managing smart devices and doing one time loads of data, e.g. historical bond price data.
* **Portainer:** used to manage all docker containers not deployed to K3s, meaning: the validation/beta enivronment, plus new services being tested on Raspberry Pis or similar devices. 
* **Rancher:** used to manage the K3s cluster, as far as installing things, updates, managing resources like Longhorn (for shared storage), etc. AWS S3 is also used to back-up both longhorn and Rancher. 
* **Node-Red:** to manage the incoming MQTT messages, data transformation of MQTT messages and then writing the data to InfluxDB 
* **Slack:** is used for alerting and monitoring, in particular alerts when any part of a pipeline or scheduled task fails in Airflow, and general alerting and monitoring for IoT/Smart Device related items. E.g., a data write to InfluxDB fails for Weather data or an air quality sensor or smart plug isn't responding. 
* The **Zigbee2MQTT library** plus a **Sonoff Zigbee USB Dongle** to receive data from Zigbee enabled IoT devices and then send it off as MQTT messages. This makes a lot of smart devices "plug-n-play" as I don't need special apps or hardware to receive data from those devices. 
* Where possible using code libraries like [Python-Kasa for TP Link Kasa devices](https://github.com/python-kasa/python-kasa) to connect to IoT and Smart Devices directly.
* **GPIO and USB** based sensors and smart devices connected to Raspberry Pis single board computers and/or similar devices like Orange Pi or Libre Computer devices. 
* **Hardware Details:** 
    * An *Intel NUC like* **Beelink Mini S12** running the primary stack for testing/validation 
    * **k3s cluster** control/server nodes are running on **Beelink SER 5 Pros (Ryzen 5 5560U CPUs)**, using single board computers (Raspberry Pis and Orange Pis) as agent nodes that are only used for collecting data from USB devices and sensors. 
    * Future plan: add agent nodes that are used for generalized workloads. Will probably use Orange Pi 5+ devices due to their desktop level performance and NPU(6 TOPS), while taking up very little space and power consumption being on par with a tablet.  
    * Single Board Computers(SBCs) details:
        * Primarily using the 8GB version of the Raspberry Pi 4Bs as the *"dedicated for USB sensor"* agent nodes. These devices all have a "no-schedule" taint on them, so K3s doesn't schedule general workloads on them. 
        * Experimenting with an Orange Pi 3B as well because even though it's about 1/2 as fast as a Raspberry Pi 4B per most benchmarks, it's costs about 1/2 as much, while having 8 GB of RAM, an NVME slot and a small NPU that could be useful for ML workloads. Also, while testing it with some computer vision models the inferencing speed was only about 10% slower than the RPI and that's without using the NPU. 
        * I also use the Raspberry Pis, the Orange Pi 3B and a **Libre LePotato** to test new apps and sensors before adding them to the main solution. 
        * Plan is to move all the SBCs boot off the network/PXE boot 
    * I do nearly all my dev work for this project on an **12th Gen Intel NUC**, I use my Orange Pi 3B and 5+ for building and testing the containers that will be deployed to the ARM devices/Single Board Computers.  
* **IoT/Smart Devices:** 
    * **Aqara and Sonoff** temperature sensors that connect via the Zigbee protocol
    * **Nova PM SDS011** IoT Air Quality sensors hooked into Libre Computer Le Potato, Orange Pi 3Bs Raspberry Pi 4Bs until I find an air quality device I both like AND uses the Zigbee protocol, and/or is built by a manufacturer that provides an API for interacting with their devices. 
    * **SONOFF Zigbee 3.0 USB Dongle Plus Gateway:** coupled with the Zigbee2MQTT library, this gives me the ability to receive data from any Zigbee enabled device without having to purchase hubs from each manufacturer to go along with their device. Note: Zigbee2MQTT isn't explicitly required, you could always write your own code for this purpose. 
    * **TP Link Kasa Smart Plugs** transmitting power, voltage and amp consumption data over Wi-Fi via the [Python-Kasa library](https://python-kasa.readthedocs.io/en/latest/index.html) 
    * Experimenting with a variety of small sensors that connect via GPIO for air quality, CO2 detection, temp and the like. Given all the wires involved, I prefer dedicated devices like the Sonoff sensors, but these may still prove useful for certain use cases. 

* **Operating Systems:** Ubuntu 22.04 distros for nearly everything, save [Armbian](https://www.armbian.com/) open source community distro for the Orange Pi 3B. Armbian is an "experiment" in terms of seeing how much use I can get out of Raspberry Pi alternatives despite the operating system/software support not being as good. Due to using Docker on all those devices, I haven't run into problems as of yet, aside from GPIO support lagging a bit. 


### Targeted Sources
* **External/Public API sources:** 
    * Asana (where I keep my to do lists) -- *shockingly, the former project manager uses project management software for day to day task management* [DONE]
    * Air Quality & Weather via the OpenWeather API [DONE]
    * Finance: tracking the S&P 500, T-Bills and maybe 1-2 other stocks [DONE]
        * Using Alpha Advantage for Treasuries and Finnhub for ETFs and Stocks
    * Tracking hydration - still looking for a good way to do this that isn't 1/2 a hack or require me to build an app that is always connected/synching as opposed to being able to just connect periodically. 
    * Discord - I join servers and then rarely pay attention and often miss announcements related to DIY/Makers, Podcasts I enjoy, Video Game Mods and other hobbies. 
    * eBay? I need to explore the API more but the plan is to track auctions and automate searches for items I'm interested in. 
    * Spotify - alerts for podcast updates 
    * I use Roon Music Server to manage my music catalog and listen to services like Tidal and Qubuz, tentative plan is to explore their API and potentially see if I can add "now playing" or even controls to Grafana and/or maybe create a separate web page that I bring Grafana into. 
* **Iot/Smart Devices:**
    * The [Zigbee2MQTT library](https://www.zigbee2mqtt.io/guide/getting-started/) to receive data from Zigbee enabled devices for room temperature and humidity [DONE]
    * Tracking the Power consumption of my gaming rig, clusters and the devices I used for all my tinkering via TP Link Kasa smart plugs [DONE]
    * Air Quality (PM2.5 and PM10) via Nova PM SDS011 sensors in concert with Raspbery Pis or similar devices [DONE]
    * Currently researching/looking for stand-alone air quality sensors with Zigee or Z-wave capability

### Key References: 
* [Airflow best practices:](https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html) I made extensive use of this documentation to not only re-write my original DAGs into the Taskflow API format, but to make sure I was following as many best practices as possible. I also used their documentation to structure my Airflow Docker container. 