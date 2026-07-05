# API and IoT Data Platform

This repository is a platform for ingesting data from public APIs, IoT devices, networking devices and other services, to enable dashboards, alerts, and agentic workflows. The ETL (extract-transform-load) jobs, agents, monitoring services, and automation are deployed as Dockerized workloads to a [K3s-based private cloud](https://github.com/MarkhamLee/kubernetes-k3s-cluster-for-data-and-iot-projects).


GitHub Actions builds the containers and pushes/stores them on Docker Hub, and ArgoCD deploys them to K3s.  
Reusable infrastructure in the form of private code libraries for alerting, data I/O, database writes and agentic AI, enable fast creation of new data pipelines, monitoring services and AI agents, as the development effort is nearly entirely focused on building new features rather than rebuilding common patterns for data access, alerting, and observability.

## System Architecture and Data Flow

The diagram below shows how code in this repository interacts with the broader private cloud:
![Dashboard Thumbnail](/images/data_platform_architecture_2026_v1.1.png)  


### Key Capabilities 

* **API and scheduled data ingestion** – Argo Workflows runs ETLs and other task-oriented workloads that collect data from API sources and then writing the data PostgreSQL and InfluxDB.

* **IoT and infrastructure telemetry** – containerized services deployed to K3s collect data from smart plugs, UPS devices, sensors, and network or infrastructure systems for continuous monitoring and alerting. 

* **MQTT-based IoT routing** – MQTT is used as a lightweight ingestion path for devices such as ESP32-based sensors, with Node-RED subscribing to broker topics, normalizing payloads, and routing time-series data into InfluxDB.

* **Agentic workflows** – LLMs ingest data from the ETL workloads to automate tasks such as dependency analysis for security alerts (GitHub dependabot), analyze web site changes and other tasks.

* **Observability and alerting** – key state changes and errors (e.g., UPS power status, temperature, pipeline failures) trigger alerts via Slack. Additionally, all workloads are built so that either Prometheus or Victoria Logs can collect logs and other data, and container level problems will trigger service status alerts via Prometheus Alert Manager running on K3s. 

* **CI/CD and reusable platform components** – GitHub Actions builds container images and then pushes them to DockerHub, where they will be pulled down and used the next time an Agentic or ETL job runs via Argo Workflows. Constantly running containers (E.g., IoT and networking monitoring), are re-deployed via ArgoCD. Shared libraries and common clients (e.g., Postgres, Ollama) make new ETLs, collectors, and agents faster to develop and maintain.


### Agentic AI and Automation

The platform incrementally adds agentic AI capabilities on top of existing ETL and monitoring pipelines. ETLs are responsible for producing LLM-friendly datasets; agents consume those datasets to automate higher-level workflows.

**Current examples include:**

- **GitHub Dependabot Agent** – The GitHub ETL was extended to emit structured dependency data; an agent consumes this feed to research each alert to identify breaking changes and provide more focused refactoring suggestion. 
- **Site Monitoring Agent** - takes web site change detection a step further by being able to leverage an LLM to monitor for certain types of content and to also interpret/evaluate that content. E.g., it can monitor a page for the availabilty of certain collectibles, but also evaluate the condition of same. 
- **Extensible agent runtime** – Agents share standard clients (for example, a Qwen client and clients for MQTT and InfluxDB) so they can reuse existing infrastructure for data access, configuration, and logging.

This design keeps agents thin and focused on decision-making logic while reusing battle-tested ingestion and infrastructure components.

### Platform and Reuse 

New ETLs, IoT monitoring services, and AI agents are built on top of a shared platform layer:
* **Private libraries** provide common features such as Slack notifications, PostgreSQL and InfluxDB access, MQTT publishing/subscribing, and structured logging.
&* **Standardized clients** (for example, a shared Qwen client and MQTT/InfluxDB clients) are injected into workloads so new services can be bootstrapped quickly.
* **Multi-stage Docker builds and shared base images** ensure consistent runtime environments and make it easy to roll out improvements. When a shared library or base image is updated, the CI/CD pipeline rebuilds all dependent containers. Improvements to a shared library (for example, improved retry logic in the InfluxDB client) are then propagated automatically across the platform.

### Observability and alerting: 

* **IoT and environment alerts** – Slack alerts are triggered when thresholds are exceeded or states change. Examples include air-quality drops, unusual climate readings, and device state changes.
* **Power and infrastructure alerts** – UPS devices emit Slack notifications when they switch to battery and when utility power returns, providing early warning for outages in the private cloud. 
* **Application and ETL monitoring** – ETL failures, task-level errors, and other application events are surfaced through centralized logging/metrics and routed to Slack. Alert rules and configurations are defined as code and versioned alongside workloads, so changes to thresholds and alert logic follow the same review and deployment workflows as application changes.

### Testbed for Production Environments

In addition to running production/regularly used workloads, this data platform also serves as both a testbed and reference implementation for real-world systems. E.g., the CI/CD patterns for building Docker containers and network monitoring features, were built and tested/hardened here and then re-used for computer vision inference pipelines. 


### Sample Dashboards

![Dashboard Thumbnail](/images/dashboard_screenshot4.png)  
![UPS Dashboard Thumbnail](/images/ups_monitoring.png)  