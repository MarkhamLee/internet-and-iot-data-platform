## Future Plans

A more detailed synopsis of future items I plan to add to this project. 

### General 


### ETL
* Make ETL containers more atomic, namely: one container to pull data, another for writing to a DB, etc. Also, integrate S3 compatible data stores as an intermediate landing zone in instances when a databae is unavailable, followed by having a separate job "fix" things by ingesting data from S3 and the writing it to the appropriate DB
* Re-write all ETL pipelines in Scala as a learning exercise 
* Experiment with streaming data sources 


### IoT
* Currently testing running sensors climate and soil sensors off of ESP32 and Raspberry Pi Pico devices, will probably move all sensors to those devices and have them stream data to the cluster. 
* If I do the above, the plan is to re-write nearly all the sensor code in C++ for efficiency reasons. 