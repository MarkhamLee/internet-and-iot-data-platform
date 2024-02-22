# Productivity, Home IoT, Music, Stocks & Weather Dashboard

![Dashboard Thumbnail](/images/dashboard_screenshot4.png)  
*Snapshot of some of the tracked data* 

This project has the following objectives: 
1) Get more experience with Airflow by building a data aggregation platform that's inclusive of API sources, IoT devices and potentially even some RSS feeds and web scraping. 
2) Get more hands on experience and/or experiment with other tools that can be used to build ETL pipelines like Argo, OpenFaaS, etc. 
3) Aggregate useful data that I would normally get from my phone or various online sources into one place so as to reduce distractions, and/or so I don't miss out on things I often forget to check or keep with. This includes but is not limited to: Asana tasks, financial data, fitness/health data, weather, etc. The basic idea is that instead of looking up something on my phone and then getting distracted by LinkedIn or reels, I can glance at a screen or browswer tab and not interrupt my daily workflow. 
4) Expand my skills with respect to IoT automation and edge technologies, as those are items that keep coming up at work AND I'm planning on building some automation projects around my home. 
5) Get more hands-on experience building and deploying micro-services to Kubernetes clusters. 

*TL/DR: I over-enginered a data aggregation platform for professional development, improved productivity and to not have limitations on what data I can display, how it's managed, et al that you often encounter when using something off the shelf, even if it's customizable.*

This repo contains the code for the ETL pipelines for various data sources, YAML files for deploying various micro-services on Kubernetes, containers for interacting with/pulling data from remote sensors/IoT devices and a lot more. Plan is to continuously add data sources/features in the coming months. 

### Recent Updates 
* 02/15/24: a couple of updates related to CI/CD and shifting ETL workloads to run on the more power efficient arm64 nodes (Orange Pi 5+ and Raspberry Pi 4B) that are now running on the Kubernetes cluster as worker nodes. 
    * Automated CI/CD pipeline(s) using GitHub actions to automatically build Docker images and then upload them to Docker Hub, where they can be picked up by Kubernetes the next time an ETL pipeline runs. The process is triggered whenever new code for a particular image is pushed to GitHub. All images are built as multi-container images so they can be run on both the amd64/x86 and arm64 nodes. All ETL containers have been added to the CI/CD pipeline, hardware, IoT and other images are roughly 1/2 complete. 
    * Added an arm64 node "preference" to the Airflow DAGs, to take advantage of those device's lower power consumption.
    * Updated documentation on building multi-architecture images, CI/CD and future plans.
* 02/02/24: moved all Airflow DAGs to Kubernetes Pod Operator (DAG for Config that runs Docker container), finished Argo Workflow manifest files for all current ETLs.
* 1/28/24: adding Slack alerts for IoT device failures, manifests for deploying ETL pipelines on Argo Workflow
* 1/22/24: added Slack pipeline failure alerts directly into ETL containers so alerts are agnostic of the tool used to run them, updated architecture diagram
* 1/15/24: shifting all ETL to be ***Docker First*** to simplify local testing, enable deployment with practically any container orchestration soluition and leverage libraries of common files for connecting to DBs, logging, common API files, etc. Meaning:
    * I can test everything locally without having to deploy to Airflow or any other tool
    * If I make a change to a script for writing to InfluxDB, logging or similar, all the ETL pipelines will be able to use that file once their image is updated.  

## Architecture - Tech Stack

![Architecture](/images/new_architecture_mkII.png)  
*The TL/DR: is that data from external APIs comes in via Airflow or Argo, data from internal sensors and/or smart devices comes in via Zigbee and/or custom code (deployed on Docker containers) to an MQTT broker that is managed/orchestrated via Node-Red and infra data comes from a combination of open source libraries, and data feeds from the firewall and UPS device. 
If things go wrong, I get alerts via Slack.*

All logos and trademarks are property of their respective owners and their use in the diagram represents an acceptable use based on my understanding of their guidelines. **If that is not the case, please let me now and I'll update the diagram ASAP.** 

### Tech Stack

* **ETL Tools:** using a variety of ETL/container orchestration tools to gather data from external APIs (Asana, Finnhub, OpenWeather and the like), in addition to general container orchestration: 
    * **Airflow:** for ETL/data ingestion only
    * **Argo Workflows:** ETL, general container orchestration and in addition to event based use cases, as it's capable of more complex logic than Airflow or just deploying containers directly on Kubernetes. 
    * **Kubernetes Cron Jobs:** not as elegant as some of the other options but often the simplest to implement, currently being used to deploy IoT related containers
    * **Open FaaS:** ETL, event-based microservices [Still Evaluating]
* **CI/CD Pipelines:** each Dockerized microservice or workload has an accompanying Githug Actions config file (see .github/workflows), which tells GitHub Actions what folders/files to monitor. Whenever a file that is used to build an image(s) is updated/pushed to this repo, GitHub actions will automatically build multi-architecture Docker images (amd64, arm64) and then upload them to Docker Hub, where they will be picked up by my Kubernetes cluster. What this means in practice is that I update the Python script that all the ETL containers include in their images, updating that file will trigger an update for all the ETL containers that use it, which will be then be used the next time that pipeline runs.
* **InfluxDB:** for storing time series data, **PostgreSQL** for everything else 
* **Grafana:** to display data/dashboards 
* **Grafana-Loki Stack:** for log aggregation, Prometheus for general monitoring
* **Eclipse-Mosquito:** for the MQTT broker that will receive messages from IoT/Smart Devices 
* **Docker:** practically everything is deployed as a containerized workload on Kubernetes or on an orchestration tool that runs on Kubernetes. 
* **Monitoring:** **Grafana-Loki** for aggregating logs from the cluster and from individual containers, workloads and the like. **The Kube Prometheus Stack** to monitor the cluster, detect when a container crashes, a node goes offline, etc. All alerts are sent via **Prometheus Alerts Manager & Slack**. 
* **Portainer:** used to manage all docker containers not deployed to K3s, meaning: the validation/beta enivronment, plus new services being tested on Raspberry Pis or similar devices.
* **Node-RED:** to manage the incoming MQTT messages, data transformation of MQTT messages and then writing the data to InfluxDB 
* **Slack:** is integrated into practically every function: alerts for cluster monitoring, issues with data pipelines, IoT sensors malfunctioning, etc., alerts are generated both when an issue occurs and when it's resolved. Additionally, reminder alerts are generated for things like Raspberry Pi 5s being in stock (detected by the Raspberry Pi locator bot), reminders that the secure certs for my firewall need to be renewed, etc.
* The **Zigbee2MQTT library** plus a **Sonoff Zigbee USB Dongle** to receive data from Zigbee (local wireless mesh network for IoT devices) enabled IoT devices and then send it off as MQTT messages. This makes a lot of smart devices "plug-n-play" as I don't need special apps or hardware to receive data from those devices. 
* Where possible using code libraries like [Python-Kasa for TP Link Kasa devices](https://github.com/python-kasa/python-kasa) to connect to IoT and Smart Devices directly.

#### **K3s Distribution of Kubernetes:** 
* All third party applications and custom code are deployed on Kubernetes-K3s via Docker containers. A couple of additional details:
* High availability configuration via three Server/control plane + general workload nodes arunning on three **Beelink SER 5 Pros (Ryzen 5 5560U CPUs)**. These high performance but power efficient devices can deliver about 70-80% of the performance of an 11th Gen i5, but in an Intel NUC sized chassis and using less than 10% of the power. The server nodes are all equipped with 2TB NVME drives and 64GB of RAM. 
* GPIO and USB based sensors are running on **Raspberry Pi 4B 8GB** devices as "sensor nodes", "node_type=sensor_node:NoSchedule" taints and tolerations are used so that key K8s components for monitoring, storage and logging are scheduled on these nodes but general workloads (e.g. ETL containers, apps like Argo or Node-Red) are excluded.  
* Hardware wise future plans include adding dedicated storage nodes, general purpose worker nodes and nodes equipped with hardware for AI/ML acceleration, E.g., NVIDIA GPUs, RockChip NPUs, etc. 
* I use **letsencrypt.org certificates + traekik** as an ingress controller to secure/encrypt connections to the services running on the cluster. 
* The cluster is managed with **Rancher**, **Longhorn** is used to manage shared storage accross the cluster, and all shared storage + Rancher data is backed up to AWS S3 on an hourly basis. 
* Prometheus is used for monitoring the nodes and the **Grafana-Loki Stack** is used for aggregating/collecting logs. 
* **Operating Systems:** Only **Ubuntu 22.04** distros for the moment 
* You can get more details on my K3s cluster in the separate repo I created for it [here](https://github.com/MarkhamLee/kubernetes-k3s-data-platform-IoT).


## ETL Pipeline Details

I originally, built all ETL pipelines as Airflow DAGs, but that made testing tricky as the file structure that worked for testing on my local Airflow instance didn't always work on my Airflow instance deployed on Kubernetes due to how files were imported from Github. I have since moved everything to "standard" Python scripts running in Docker containers for a couple of reasons:

* By making the pipelines more agnostic, it's much easier to experiment with, test, get experience with other ETL and orchestration tools. 
* No longer need to worry about managing dependencies for Airflow as they're all baked into the container
* I can test locally without having to maintain multiple Airflow instances, or do things like test a standard python ETL script and then test it again as a DAG.  
* The CI/CD pipeline automatically rebuilds the images whenver a relevant file is updated and the pipelines always check for new images before they run, this makes updating the pipelines very smooth and easy: I update a file and everything is taken care of via the automations for CI/CD and ETL.
* By leveraging libraries of common functions/scripts/files (API clients, writing to DBs, logging, etc.), I can not only build new pipelines faster, but updates/improvements to those core files can be used by any of the existing ETL pipelines as soon as their images are updated.

*i.e., all the advantages of using containers...* 

~~At the moment I'm experimenting with running the ETL containers with Airflow, Argo, Kubernetes cron jobs and OpenFaaS, and will eventually settle on 1-2 of those solutions on a go-forward basis.~~

Airflow and Argo Workflows will be the ETL tools of record. While my preference leans slightly towards Airflow, building ETL containers that work with both will help ensure I meet my goals of making things as as "tool agnostic" as possible. I'll also continue to use Kubernetes cron jobs to test containers. 

To compensate for logging and alerting when using the Airflow Kubernetes Pod Operator or Argo Workflows vs traditional DAGs, I've added more logging to the ETL containers and Slack Alerts for failures at any stage of the pipeline. 

#### Current and Future Data Sources
* **External/Public API sources:** 
    * Asana (where I keep my to do lists) -- *shockingly, the former project manager uses project management software for day to day task management* [DONE]
    * Air Quality & Weather via the OpenWeather API [DONE]
    * Finance: tracking the S&P 500, T-Bills and maybe 1-2 other stocks [DONE]
        * Alpha Vantage for treasuries [DONE]
        * Finnhub for stocks [DONE]
    * Raspberry Pi Locator: built a simple bot for consuming the RSS feed and then alerting me via Slack if the stock update is less than 12 hours old [DONE]
    * GitHub: now that I'm using GitHub actions I need to track my usage so I can see any potential costs/if I'm going to go past the allotment of minutes already included in my current subscription. [IN PROCESS]
    * Tracking hydration - still looking for a good way to do this that isn't 1/2 a hack or require me to build an app that is always connected/synching as opposed to being able to just connect periodically. 
    * Discord - I join servers and then rarely pay attention and often miss announcements related to DIY/Makers, Podcasts I enjoy, Video Game Mods and other hobbies. 
    * eBay? I need to explore the API more but the plan is to track auctions and automate searches for items I'm interested in. 


## Automation, Edge and IoT Devices

* **SONOFF Zigbee 3.0 USB Dongle Plus Gateway:** coupled with the [Zigbee2MQTT library](https://www.zigbee2mqtt.io/guide/getting-started/), this gives me the ability to receive data from any Zigbee enabled device without having to purchase hubs from each manufacturer to go along with their device. Note: Zigbee2MQTT isn't explicitly required, you could always write your own code for this purpose
* Zigbee is a mesh network where the battery powered devices only transmit data and the ones powered by mains/AC power also serve as routers. I've deployed Zigbee smart plugs as routers in each room I've deployed Zigbee devices to, as without them the battery powered devices often suffer from unstable connections. 
* **Aqara and Sonoff** temperature sensors that connect via the Zigbee protocol
* **Nova PM SDS011** IoT Air Quality sensors connected to the Raspberry Pi 4Bs *"dedicated sensor nodes"* until I find an air quality device I both like AND uses the Zigbee protocol, and/or is built by a manufacturer that provides an API for interacting with their devices. 
* **TP Link Kasa Smart Plugs** tracking power consumption, voltage and amps data over Wi-Fi via the [Python-Kasa library](https://python-kasa.readthedocs.io/en/latest/index.html) 
* Currently testing SCD40 and MH-Z19B CO2 sensors, when these are fully deployed they will likely be connected to the Raspberry Pis I already have deployed around the house, but I am considering using a microcontroller like a Raspberry Pi Pico or ESP32 device instead. 
* I've also tested DHT22 temperature sensors and found them to be more reliable than the Zigbee based devices I tried in terms of how often they send data, stability, etc., the only knock on them is that deploying Zigbee device is just easier/has fewer moving parts and a good 1/3 of the devices I received were duds. That being said, I am using DHT22s + a Raspberry Pi Pico to monitor the temperatures inside of my gaming PC and send that data to the cluster via MQTT. 
* ~~Currently researching/looking for stand-alone air quality sensors with Zigbee or Z-wave capability~~ I've halted this as the devices I've found aren't especially accurate, so I've shfited gears to looking at DIY options and industrial air quality kits that I can adapt/integrate with this project. 
* Currently testing GPIO based sensors for temperature, air quality and soil moisture 

## Key References: 
* [Airflow best practices:](https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html) I made extensive use of this documentation to not only re-write my original DAGs into the Taskflow API format, but to make sure I was following as many best practices as possible. I also used their documentation to structure my Airflow Docker container. 