## All Updates

### 2024
* 04/25/224: updates from the last 5+ weeks 
    * Updates to Kubernetes deployment manifests for IoT devices, added Argo CD configurations for managing CICD for IoT device scripts/containers. Python scripts + container for SGP30 CO2 sensor (4/17)
    * Refactoring/re-writes for all Node.js ETL pipelines: main pipeline code + updated unit tests (4/16)
    * C++ file for provisioning ESP32s with Wi-Fi and MQTT creds (4/11)
    * IoT architecture diagram and documentation (4/10)
    * Added C++ code for retrieving data from a DHT22 temperature sensor connected to an ESP32 and transmitting the data via MQTT (4/9)
    * Added three new ETLs that work in concert to retrieve T-Bill data for use in plotting the daily yield curve. i.e., ETL containers + Airflow DAGs for loading historical data, retrieving data for the current day and data transformations load a reporting/golden table for the yield curve plot.  (4/3)
    * Re-wrote all Dockerfiles to use multi-stage builds, resulting in smaller and more secure Docker images. ETL work flow diagram and documentation (4/2)
    * Added python scripts + container for BME280 temperature sensor (3/31)
* 03/14/24: Pi, obviously... mostly quality control and code monitoring updates
    * Automated unit tests via Jest for Node.js and Unittest for Python
    * Fixed the GitHub actions files for the Node.js ETLs as they weren't always firing properly 
    * Added dependabot DAGs for monitoring the repo for the Kubernetes cluster this project runs on.
* 02/28/24: adding Node.js (JavaScript & TypeScript) based ETL containers, created an ETL that monitors the GitHub dependabot alerts for this repo and sends me a Slack message when security issues are detected.
* 02/15/24: a couple of updates related to CI/CD and shifting ETL workloads to run on the more power efficient arm64 nodes (Orange Pi 5+ and Raspberry Pi 4B) that are now running on the Kubernetes cluster as worker nodes. 
    * Building out automated CI/CD pipeline(s) using GitHub actions to automatically build Docker images and then upload them to Docker Hub, where they can be picked up by Kubernetes the next time an ETL pipeline runs. The process is triggered whenever new code for a particular image is pushed to GitHub. All images are built as multi-container images so they can be run on both the amd64/x86 and arm64 nodes. All ETL containers have been added to the CI/CD pipeline, hardware, IoT and other images are roughly 1/2 complete. 
    * Added a preference to the Airflow DAGs for the arm64 nodes to take advantage of those devices lower power consumption.
    * Updated documentation on building multi-architecture images, CI/CD and future plans.
* 02/02/24: moved all Airflow DAGs to Kubernetes Pod Operator (DAG for Config that runs Docker container), finished Argo Workflow manifest files for all current ETLs. 
* 1/28/24: adding Slack alerts for IoT device failures, manifests for deploying ETL pipelines on Argo Workflow
* 1/22/24: added Slack pipeline failure alerts directly into ETL containers so alerts are agnostic of the tool used to run them, updated architecture diagra
* 1/15/24: shifting all ETL to be ***Docker First*** to simplify local testing, enable deployment with practically any container orchestration soluition and leverage libraries of common files for connecting to DBs, logging, common API files, etc. Meaning:
    * I can test everything locally without having to deploy to Airflow or any other tool
    * If I make a change to a script for writing to InfluxDB, logging or similar, all the ETL pipelines will be able to use that file once their image is updated. 
* 1/11/24: added a bot that regularly pulls down data from [Raspberry Pi Locator](https://rpilocator.com/) via RSS, checks the age of the updates for Raspberry Pi 5s and if they're younger than 12 hours, sends me an alert via Slack. 
* 01/10/24: updating logging within the custom code containers for better integration with K8s logging AKA OpenTelemetry, Loki, et, al. I.e., cleaning up tech debt. 

### 2023

* 12/27/23: Updated the Readme with the latest architecture and technical details
* 12/26/23: moved all single board computers (e.g., Raspberry Pis) to the cluster as dedicated agent nodes for receiving data from USB based climate sensors and the Zigbee Hub. Added instructions + the values.yaml files for deploying Zigbee2MQTT on Kubernetes. 
* 12/18/23: added container/microservice (flask API wrapper around Slack client) for sending alert messages via Slack, so I don't have to include the Slack SDK, client, etc., in the individual services that send Slack alerts.