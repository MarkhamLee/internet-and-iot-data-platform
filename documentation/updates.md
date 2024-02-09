## All Updates

### 2024

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