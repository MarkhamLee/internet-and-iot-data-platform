# Productivity, Home IoT, Music, Stocks & Weather Dashboard

![Dashboard Thumbnail](/images/dashboard_snapshot11-15.png)  
*Snapshot of some of the tracked data* 

This project has two primary objectives: 
1) Get more experience with Airflow by building a data aggregation platform that's inclusive of API sources, IoT devices and potentially even some RSS feeds and web scraping. 
2) Aggregate useful data into one place that I would normally get from my phone or various online sources into one place so as to reduce distractions, and/or so I don't miss out on data I often forget to check or keep with. This includes but is not limited to: inancial data, fitness/health data, weather, to-do lists from Asana, etc. The basic idea is that instead of looking up something on my phone and then getting distracted by LinkedIn or reels, I can glance at a screen or browswer tab and not interrupt my daily workflow. 

A secondary objective is to start experimenting with home automation via gathering data from various IoT sensors, smart devices, DIY air quality monitoring stations, that I was using for other projects or just playing around with into one place. 

*TL/DR: I over-enginered a data aggregation platform for professional development, improved productivity and to not have limitations on what data I can display, how it's managed, et al that you often encounter when using something off the shelf, even if it's customizable.*


## Architecture - Tech Stack

![Architecture](/images/dashboard_architecture_MKII.png)  
*The TL/DR: is that data from external APIs comes in via Airflow, data from internal sensors and/or smart devices comes in via Zigbee and/or custom code (deployed on Docker containers) to an MQTT broker that is managed/orchestrated via Node-Red. If things go wrong, I get alerts via Slack.* 

All logos and trademarks are property of their respective owners and the use in the diagram represents an acceptable based on my understanding of their guidelines. **If that is not the case, please let me now and I'll update the diagram ASAP.** 

* **Airflow:** data ingestion + orchestration from external APIs E.g., OpenWeather API, Spotify. 
* **InfluxDB:** for time series data, **PostgreSQL** for everything else 
* **Grafana:** to display data
* **Eclipse-Mosquito:** for the MQTT broker that will receive messages from IoT/Smart Devices 
* **Docker:** all the big building blocks (e.g. Airflow, InfluxDB, etc.) are deployed via Docker containers and I deployed all the custom code for things like monitoring air quality, managing smart devices and the like via Docker containers as well. 
* **Portainer:** I manage all the containers on all of the devices via Portainer, but as I move things to my k3s cluster I might use Rancher instead for k3s, but keep using Portainer for managing the containers on my Raspberry Pis that I use for things like monitoring air quality.  
* **Node-Red:** to manage the incoming MQTT messages, data transformation of MQTT messages and then writing the data to InfluxDB 
* **Slack:** is used for alerting and monitoring, in particular alerts when any part of a pipeline or scheduled task fails in Airflow, and general alerting and monitoring for IoT/Smart Device related items. E.g., a data write to InfluxDB fails for Weather data or an air quality sensor or smart plug isn't responding. 
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
    * Finance: tracking the S&P 500, T-Bills and maybe 1-2 other stocks [DONE] - switched to Finnhub from Alpha Advantage as I can make several requests per second vs 26/day for Alpha Advantage
    * Tracking hydration - still looking for a good way to do this 
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
* [Airflow best practices:](https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html) I made extensive use of this documentation to not only re-write my original DAGs into the Taskflow API format, but to make sure I was following as many best practices as possible. I also used their documentation to structure my Airflow Docker container. 