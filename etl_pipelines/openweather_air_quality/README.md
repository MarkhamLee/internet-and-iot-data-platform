## Open Weather Air Quality ETL

### Folder Contents 

This folder contains an ETL container for pulling local air quality data from the Open Weather Air Pollution API and writing that data to InfluxDB. I used Influx because weather data + a time series database is a natural fit, and because of its natural synergy with Grafana AKA the dashboard I use to view all of my ETL data. 

#### The Data 

The API returns the concentrations of eight different pollutants expressed in migrograms per cubic meter of air or ug/m^3. However, I'm only using a subset of the datapoints the API returns, namely: CO, PM 2.5 and PM 10. The complete list of fields are:

* CO - Carbon monoxide
* NO - Nitrogen monoxide
* NO2 - Nitrogen dioxide
* O3 - Ozone 
* SO2 - Sulphur dioxide
* NH3 - Ammonia 
* PM2.5 - fine particulate matter concentration 
* PM10 - coarse particulate matter concentration  

You can get more details on the Open Weather Air Pollution API [here](https://openweathermap.org/api/air-pollution)

In the IoT section of this repo you can find the code that supports/pulls data from the air quality sensors I have around my house. I.e., my original reason for connecting to the Air Pollution API and building the internal air quality stations was to track the difference between the air quality outdoors and the air quality indoors during this past summer's forest fires. 

#### Notes on Data Quality 

* The "air_quality.json" file is used to validate that the payload is correct, if the payload doesn't match the format specified in the validation json an error will be thrown and the pipeline will fail. 


#### Implementation 

To run the container you will need to populate the following environmental variables, 

* Influx_KEY: API key for InfluxDB 
* OPENWEATHER_KEY: API key for the Open Weather API
* INFLUX_ORG: org name for your InfluxDB instance 
* INFLUX_URL: ip address or URL for your InfluxDB instance 
* BUCKET: InfluxDB's term for a database 
* MEASUREMENT: InfluxDB's term for a table 
* CITY: the city you're pulling weather data for 
* LAT: lattitude of the city you're pulling weather data for
* LONG: longitude of the city you're pullingweather data for
* ALERT_WEBHOOK: webhook to send pipeline failure alerts to Slack 

You will also need to sign-up for [Slack API access](https://api.slack.com/), create a channel for receiving pipeline failures and then generate a web hook for receiving to send those alerts to. Alternatively, if you're just experimenting, you can just comment out the Slack Alert code.

Additionally, this ETL container builds using files from the "etl_library" and the "openweather_library" folders that are in this folder's parent/the "etl_pipelines" folder. Please refer to the README in the "etl_pipelines" folder on how to run the 'Docker build' command so that you can properly copy over all the files into your image, otherwise you will get errors related to Docker context and the files it has access to. 

