# Productivity, Home IoT, Music, Stocks & Weather Dashboard

![Dashboard Thumbnail](/images/dashboard_screenshot3.png)  
*Snapshot of some of the tracked data* 

This project has the following objectives: 
1) Get more experience with Airflow by building a data aggregation platform that's inclusive of API sources, IoT devices and potentially even some RSS feeds and web scraping. 
2) Aggregate useful data that I would normally get from my phone or various online sources into one place so as to reduce distractions, and/or so I don't miss out on things I often forget to check or keep with. This includes but is not limited to: Asana tasks, financial data, fitness/health data, weather, etc. The basic idea is that instead of looking up something on my phone and then getting distracted by LinkedIn or reels, I can glance at a screen or browswer tab and not interrupt my daily workflow. 

A secondary objective is to start experimenting with home automation via gathering data from various IoT sensors, smart devices, DIY air quality monitoring stations and the like. 

*TL/DR: I over-enginered a data aggregation platform for professional development, improved productivity and to not have limitations on what data I can display, how it's managed, et al that you often encounter when using something off the shelf, even if it's customizable.*

The repo contains the the code for the Airflow Dags (written in TaskFlow API format), custom plugins for connecting to things like InfluxDB and the custom code for ingesting data from IoT devices. It also has the extended but not quite custom Docker image I used for Airflow (*so it has all of my Python dependencies*). Plan is to continuously add data sources/features in the coming months. 


## Architecture - Tech Stack

![Architecture](/images/dashboard_architecture_MKII.png)  
*The TL/DR: is that data from external APIs comes in via Airflow, data from internal sensors and/or smart devices comes in via Zigbee and/or custom code (deployed on Docker containers) to an MQTT broker that is managed/orchestrated via Node-Red. If things go wrong, I get alerts via Slack.*

All logos and trademarks are property of their respective owners and their use in the diagram represents an acceptable use based on my understanding of their guidelines. **If that is not the case, please let me now and I'll update the diagram ASAP.** 

* **K3s Distribution of Kubernetes:** all of the third party applications (save Zigbee2MQTT) are deployed on K3s. All of the custom code is running on K3s as well, with the exception of docker containers running on Raspberry Pis (or similar devices) collecting climate data from either GPIO or USB based sensors. 
    * You can get more details on my K3s cluster in the separate repo I created for it [here](https://github.com/MarkhamLee/kubernetes-k3s-data-platform-IoT).
* **Airflow:** data ingestion + orchestration from external APIs E.g.,  Asana, Finnhub, OpenWeather API. etc.   
* **InfluxDB:** for storing time series data, **PostgreSQL** for everything else 
* **Grafana:** to display data/dashboards 
* **Eclipse-Mosquito:** for the MQTT broker that will receive messages from IoT/Smart Devices 
* **Docker:** all the big building blocks (e.g. Airflow, InfluxDB, etc.) are deployed via Docker containers in addition to the custom code I wrote for things like monitoring air quality, managing smart devices and doing one time loads of data, e.g. historical bond price data.
* **Portainer:** used to manage all docker containers not deployed to K3s, meaning: the validation/beta enivronment, plus services running on Raspberry Pis or similar devices. I could move these devices to K3s, but given they're all running various GPIO and/or USB devices, they don't exactly fit into a distributed/pod paradigm. This will likely change in the near future after I experiment with a code library that can expose a USB device connected to one node to the entire cluster. 
* **Rancher:** used to manage the K3s cluster, as far as installing things, updates, managing resources like Longhorn (for shared storage), etc. AWS S3 is also used to back-up both longhorn and Rancher. 
* **Node-Red:** to manage the incoming MQTT messages, data transformation of MQTT messages and then writing the data to InfluxDB 
* **Slack:** is used for alerting and monitoring, in particular alerts when any part of a pipeline or scheduled task fails in Airflow, and general alerting and monitoring for IoT/Smart Device related items. E.g., a data write to InfluxDB fails for Weather data or an air quality sensor or smart plug isn't responding. 
* The **Zigbee2MQTT library** plus a **Sonoff Zigbee USB Dongle** to receive data from Zigbee enabled IoT devices and then send it off as MQTT messages. This allows me to use a wide variety of smart home devices and/or IoT sensors without having to purchase extra hubs or other smart home devices just to use the sensors. Instead, I can instead connect directly to each device and run custom code/solutions to ingest the data. 
* Where possible using code libraries like **Python-Kasa for TP Link Kasa devices** to connect to IoT and Smart Devices directly.
* **GPIO and USB** based sensors and smart devices connected to Raspberry Pis single board computers and/or similar devices like Orange Pi or Libre Computer devices. 
* **Hardware Details:** 
    * An *Intel NUC like* **Beelink Mini S12** running the primary stack for testing/validation 
    * **k3s cluster** built on **Beelink SER 5 Pros (Ryzen 5 5560U CPUs)** for production
    * Single Board Computers(SBCs)
        * A **Raspberry Pi 4B** runs the **Zigbee2MQTT container**, the Zigbee USB hub and the Nova PM SDS011 air quality sensor in my office. 
        * An **Orange Pi 3B** and a **Libre LePotato** run air quality sensors elsewhere in the house
        * Plan is to move at least the Rasperry Pi and the LePotato to PXE boot as they run off of SD cards, the Orange Pi 3B runs off an eMMC so it's a lower priority for PXE. Also, might just replae the Raspbery Pi 4B and LePotato with Orange Pi 3B (or maybe a 5) since those devices have built in eMMC and NVME slots. I.e. remove the SD card weak point. 
    * I do nearly all my dev work for this project on an **Intel NUC 12th gen**, but I use either the Orange Pi 3B or my Orange Pi 5+ for building and testing the containers that will be deployed to the ARM devices/Single Board Computers.  
* **IoT/Smart Devices:** 
    * **Aqara and Sonoff** temperature sensors that connect via the Zigbee protocol
    * **Nova PM SDS011** IoT Air Quality sensors hooked into Libre Computer Le Potato, Orange Pi 3Bs Raspberry Pi 4Bs until I find an air quality device I both like AND uses the Zigbee protocol, and/or is built by a manufacturer that provides an API for interacting with their devices. 
    * **SONOFF Zigbee 3.0 USB Dongle Plus Gateway:** coupled with the Zigbee2MQTT library, this gives me the ability to receive data from any Zigbee enabled device without having to purchase hubs from each manufacturer to go along with their device. Note: Zigbee2MQTT isn't explicitly required, you could always write your own code for this purpose. 
    * **TP Link Kasa Smart Plugs** transmitting power, voltage and amp consumption data over Wi-Fi via the [Python-Kasa library](https://python-kasa.readthedocs.io/en/latest/index.html) 

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