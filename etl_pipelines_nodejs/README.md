## Node.js ETL Pipelines

For practice/experience building out Node.JS versions of most if not all of the ETLs I built in Python. Given my approach of deploying all ETLs in Docker containers, it just made sense to build them in multiple languages to get experience with building deploying ETL containers on tools like Airflow and Argo Workflow in languages other than Python. To get more details on the overall approach, you can read more in the [Readme](https://github.com/MarkhamLee/finance-productivity-iot-informational-weather-dashboard/tree/main/etl_pipelines) in the folder containing the Python based ETLs. 

Regardless of the language being used, certain core tenants always apply:

* All ETLs are built using Docker containers
* Leverage shared libraries as much as possible, meaning scritps for things like validating json, writing to Postgres or InfluxDB, etc., can be shared among multiple ETls 
* Docker builds are automated via GitHub Actions, and all containers are built for both amd64 and arm64 architectures
* Automated testing via unit testing libraries like jest (Node.js) and Unit Test (Python)
* Alerts are sent via Slack if any problems occur 
* Strict type checking and data validation of API response payloads, prior to the data being written to InfluxDB or PostgreSQL. In some cases the data is checked after the API response, and again once it has been parsed/transformed. 