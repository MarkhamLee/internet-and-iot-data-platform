## Open Weather - Current Weather ETL 

### Folder Contents
This folder contains an ETL container that will pull current weather data from the Open Weather API and then writes that data to an InfluxDB database. InfluxDB was choosen as regular weather data updates are a natural fit for a time series database like Influx. 

#### The Data
The Open Weather API endpoint for current weather returns the following:

* General weather description, in the form of a a main and detailed discription, think "Clear" and "Clear Sky"
* Temperature: current temp, "feels like", min and max 
* Atmospheric Pressure
* Humidity 
* Visiblity 
* Wind speed and direction 
* Cloud
* timestamp
* Country
* Sunrise time 
* Sunset time
* City Name 
* timezone 

Note: all times are given in Unix epoch format 

#### Data Quality & Testing
* The "current_weather.json" file is used to validate that the payload is correct, if the payload doesn't match the expected format an error will be thrown, the pipeline will fail and a Slack message will be generated to alert me that there is a problem. 
* The test.py file will run a series of unit tests, checking both primary and secondary functionality:
    * The end to end ETL workflow, if any part of the process fails, the entire test fails 
    * Validating that the appropriate error messages and alerts are sent in response to a bad or failed API call
    * Testing the data validation process, i.e, comparing a provided "bad" data payload with the ETL's JSON schema, followed by checking that the appropriate error messages and alerts are generated. 


#### Implementation 

To run the container you will need to populate the following environmental variables and spin-up a database to store the data. If you want to receive Slack alerts when you have a pipeline failure, you will also need to sign up for [Slack API access](https://api.slack.com/), create a channel to receive alerts and then configuring a webhook to send messages to that channel. 

* ALERT_WEBHOOK: webhook to send pipeline failure alerts to Slack 
* BUCKET: InfluxDB's term for a database 
* CITY: the city you're pulling weather data for 
* INFLUX_KEY: API key for InfluxDB 
* INFLUX_ORG: org name for your InfluxDB instance 
* INFLUX_URL: ip address or URL for your InfluxDB instance 
* LAT: lattitude of the city you're pulling weather data for
* LONG: longitude of the city you're pullingweather data for
* OPENWEATHER_KEY: API key for the Open Weather API
* WEATHER_MEASUREMENT: the InfluxDB table, called a "measurement" in InfluxDB parlance

#### Container Details 

* The ETL container builds using files from the "etl_library" and the "openweather_library" folders that are in this folder's parent/the "etl_pipelines" folder. Please refer to the README in the "etl_pipelines" folder on how to run the 'Docker build' command so that you can properly copy over all the files into your image, otherwise you will get errors related to Docker context and the files it has access to. 
* Github actions are used to automate the building of multi-architecture containers that can be used by both the x86 and ARM nodes in the Kubernetes cluster, whenever updates for the relevant folders for this pipeline are pushed the Github the Docker image build process will be triggered and a new container pushed to Dockerhub. The new image will then be used by the ETL pipeline the next time it runs. 
