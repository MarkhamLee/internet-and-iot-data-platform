## Future Plans

A more detailed synopsis of future items I plan to add to this project. 

### General 
* Finish building out CI/CD pipelines for ETL containers [DONE]
* Extend the capabilities of Github actions for CI/CD for continuously running containers using either Argo CD or custom code, i.e., containers that run sensors, monitor energy consumption, etc., so that those deployments automatically refresh when those images are updated [In Progress - Testing]

### CI/CD - DevOps 
* Build a DevOps platform tracking the current number of GitHub Actions builds, security alerts, etc. [PENDING]

### ETL
* Make ETL containers more atomic, namely: one container to pull data, another for writing to a DB, etc. 
* Add an S3 compatible object store, either by just connecting to AWS S3, Google object storage or deploying a tool like MinIO. I will likely build the capability to connect all three just for the practice. 
* Uses the object stores as an intermediate landing zone in instances when a database is unavailable, or there is a write or parse error. InfluxDB and Postgres are very strict on data types and formatting as are my data validation processes, so it's quite possible that upstream changes would cause those writes to fail, having a safety valve will make it easier to catch those data changes. 
* Re-write several of the ETL pipelines using Node.js [DONE]
* Re-write all ETL pipelines in Scala as a learning exercise [IN PROGRESS]
* Experiment with streaming data sources 
* Build a dashboard that just shows the status of all data ingestion activities whether it's an ETL or IoT related, I can monitor logs via Loki-Grafana, but I want to build something with summary stats. 


### IoT
* Currently testing running sensors climate and soil sensors off of ESP32 and Raspberry Pi Pico devices, will probably move all sensors to those devices and have them stream data to the cluster. 
* If I do the above, the plan is to re-write nearly all the sensor code in C++ for efficiency reasons. 
* Experiment with streaming data from GPIO and USB devices connected to Raspberry Pi or similar single board computers (SBCs) devices directly to the cluster. This would allow the code/containers that run the logic to process that data to run on any node in the cluster as opposed to just the one the sensor is connected to, while also enabling me to use lower powered SBCs that could also run some additional conditional logic, manage other processes, etc., in a way that the microprocessors aren't able to. 