# Productivity, Home IoT, Music, Stocks & Weather Dashboard

The primary purrpose of this project is to see if I can improve my productivity by putting information I usually get from my phone, forget to monitor, etc., into one place for easy access. I.e. if I can just glance at a browswer tab (or two) or my iPad to get everything I need, it should reduce the amount of time I spend on my phone. Think: you  look at your phone to check the weather and wind up watching IG reels. Additionally, I want to gather aggregate data from IoT and smart devices into one place, so I can check room temps, monitor air quality inside my home and see how much power is used by the various devices I use for all my tinkering and nerd projects. A second but just as important objective is getting more hands on experience with Airflow, Home Automation & IoT devices, I'm a firm believer of the best way to learn a technology is to build something you'd actually use. 

## Architecture - Tech Stack

![Architecture](/images/dashboard_architectureMKI.png)  


* **Airflow:** data ingestion + orchestration from external APIs E.g., OpenWeather API, Spotify. 
* **InfluxDB:** for time series data, **PostgreSQL** for everything else 
* **Grafana:** to display data
* **Eclipse-Mosquito:** for the MQTT broker that will receive messages from IoT/Smart Devices 
* **Docker:** to run nearly everything, save a few things I might deploy directly on a device as a Linux service. Used **Portainer** to manage, configure and deploy containers from images stored in my private Docker Repo. 
* **Node-Red:** to manage the incoming MQTT messages, data transformation of MQTT messages and then writing the data to InfluxDB 
* The **Zigbee2MQTT library** plus a **Sonoff Zigbee USB Dongle** to receive data from Zigbee enabled IoT devices and then send it off as MQTT messages. This allows me to use a wide variety of smart home devices and/or IoT sensors without having to purchase extra hubs or other smart home devices just to use the sensors. Instead, I can instead connect directly to each device and run custom code/solutions to ingest the data. 
* Where possible using code libraries like **Python-Kasa for TP Link Kasa devices** to connect to IoT and Smart Devices directly.
* **GPIO and USB** based sensors and smart devices connected to Raspberry Pis single board computers and/or similar devices like Orange Pi or Libre Computer devices. 
* **Hardware:** currently running on an *Intel NUC like* Beelink Mini S12, will probably move it to my homelab K3s cluster (Beelink SER 5 Pros Ryzen 5 5560s) in the next week or two, but for now, everything works fine where it is. A Raspberry Pi 4B runs the Zigbee2MQTT container and the Zigbee USB hub, I'm also using Raspberry Pis for the Nova PM SDS011 air quality sensors, but may move those to lower cost Le Libre or Orange Pi devices. Once the single board computing situation is more defined, I plan to set them all up to boot via PXE. 
* **IoT/Smart Devices:** 
    * **Aqara and Sonoff** temperature sensors that connect via the Zigbee protocol
    * **TP Link Kasa Smart Plugs** transmitting power, voltage and amp consumption data over Wi-Fi via the [Python-Kasa library](https://python-kasa.readthedocs.io/en/latest/index.html) 
    * **Nova PM SDS011** IoT Air Quality sensors hooked into Libre Computer Le Potato, Orange Pi 3Bs Raspberry Pi 4Bs until I find an air quality device I both like AND uses the Zigbee protocol, and/or is built by a manufacturer that provides an API for interacting with their devices. 
* **Operating Systems:** Ubuntu 22.04 distros for nearly everything, save [Armbian](https://www.armbian.com/) Open Source Community distros for the Libre and Orange Pi 3B machines. The Armbian devices are "experiments" to a degree, in terms of seeing how much use I can get out of Raspberry Pi alternatives despite the operating system/software support not being as good. Due to using Docker on all those devices, I haven't run into problems as of yet, aside from GPIO support lagging a bit. 


### Targeted Sources
* **External/Public API sources:** 
    * Asana (where I keep my to do lists) -- *shockingly, the former project manager uses PM software for day to day task management*
    * Air Quality & Weather via the OpenWeather API [DONE]
    * Finance: tracking the S&P 500, T-Bills and maybe 1-2 other stocks [MOSTLY DONE] - need to find another finance API that allow me to track more items and get more frequent updates. 
    * Discord - I join servers and then rarely pay attention and often miss announcements related to DIY/Makers, Podcasts I enjoy, Video Game Mods and other hobbies. 
    * eBay? I need to explore the API more but the plan is to track auctions and automate searches for items I'm interested in. 
    * Spotify - alerts for podcast updates 
    * I use Roon Music Server to manage my music catalog and listen to services like Tidal and Qubuz, tentative plan is to explore their API and potentially see if I can add "now playing" or even controls to Grafana and/or maybe create a separate web page that I bring Grafana into. 
* **Iot/Smart Devices:**
    * The [Zigbee2MQTT library](https://www.zigbee2mqtt.io/guide/getting-started/) to receive data from Zigbee enabled devices for room temperature and humidity [DONE]
    * Trackinig the Power consumption of my gaming rig, clusters and the devices I used for all my tinkering via TP Link Kasa smart plugs [DONE]
    * Air Quality (PM2.5 and PM10) via Nova PM SDS011 sensors in concert with Raspbery Pis [DONE]

The repo contains the the code for the Airflow Dags (written in TaskFlow API format), custom plugins for connecting to things like InfluxDB and the code for ingesting data from the IoT devices. It also has the extended but not quite custom Docker image I used for Airflow (*so it has all of my Python dependencies*). Plan is to continuously add data sources and then update the repo accordingly. 

### Key References: 
* [Airflow best practices:](https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html) I made extensive use of this documentation to not only re-write my original DAGs into the Taskflow API format, but to make sure I was following as many best practices as possible. I also used their documentation to structure my Docker container. 