## Open Weather - Current Weather ETL 

### Folder Contents




#### Data Quality 

* The "current_weather.json" file is used to validate that the payload is correct, if the payload doesn't match the format specified in the validation json an error will be thrown and the pipeline will fail.


#### Implementation 

To run the container you will need to populate the following environmental variables and spin-up a database to store the data. If you want to receive Slack alerts when you have a pipeline failure, you will also need to sign up for [Slack API access](https://api.slack.com/), create a channel to receive alerts and then configuring a webhook to send messages to that channel. 

* INFLUX_KEY: API key for InfluxDB 
* OPENWEATHER_KEY: API key for the Open Weather API
* INFLUX_ORG: org name for your InfluxDB instance 
* INFLUX_URL: ip address or URL for your InfluxDB instance 
* BUCKET: InfluxDB's term for a database 
* MEASUREMENT: InfluxDB's term for a table 
* CITY: the city you're pulling weather data for 
* LAT: lattitude of the city you're pulling weather data for
* LONG: longitude of the city you're pullingweather data for
* ALERT_WEBHOOK: webhook to send pipeline failure alerts to Slack 

Additionally, this ETL container builds using files from the "etl_library" and the "openweather_library" folders that are in this folder's parent/the "etl_pipelines" folder. Please refer to the README in the "etl_pipelines" folder on how to run the 'Docker build' command so that you can properly copy over all the files into your image, otherwise you will get errors related to Docker context and the files it has access to. 
