// (C) Markham Lee 2023 - 2024
// productivity-music-stocks-weather-IoT-dashboard
// https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
// Retrieving Air Quality data from the OpenWeather API and writing it to InfluxDB.

import axios from 'axios'
import { Point } from '@influxdata/influxdb-client';
import {config, createAirqUrl, createInfluxClient,
        sendSlackAlerts} from "../utils/openweather_air_library"

// Get OpenWeather data 
const getAirQualityData = async (airUrl: string) => {
    
    try {

      const data = await axios.get(airUrl)
      
      // split out the part of the json that contains the bulk of the data points
      const air_data = data.data['list'][0]['components']
        
      // parse out individual fields 
        const payload = {"carbon_monoxide": air_data.co,
        "pm_2": air_data.pm2_5,
        "pm_10": air_data.pm10 }

        console.log("InfluxDB payload ready:", payload)
        const response = writeData(payload)
        
    } catch (error: any) {
        const message = "Pipeline failure alert - OpenWeather API Air Pollution - node.js variant with error: "
        const full_message = (message.concat(JSON.stringify((error))));
        console.error(full_message);

        //send pipeline failure alert via Slack
        sendSlackAlerts(full_message);

    }
}

//method to write data to InfluxDB
// the InfluxDB node.js library doesn't have a clean way of just
// pushing json data to the DB. So, the write methods will have to 
// live in the primary ETL code for now. 
const writeData = (payload: any) => {   

    console.log(payload)

    const bucket = config.bucket
    const writeClient = createInfluxClient(config.bucket)

    let point = new Point(config.measurement)
            .tag("OpenWeatherAPI", "Air Quality")
            .floatField('carbon_monoxide', payload.carbon_monoxide) 
            .floatField('pm_2', payload.pm_2)
            .floatField('pm_10', payload.pm_10)
            
    // write data to InfluxDB
    void setTimeout(() => {

        writeClient.writePoint(point);
        console.log("Weather data successfully written to InfluxDB")
        }, 1000)

    // flush client
    void setTimeout(() => {

          // flush InfluxDB client
          writeClient.flush()
      }, 1000)
  
  }

const endpoint = "air_pollution?"

// create URL for API get request
const airUrl = createAirqUrl(endpoint)
  
// get & write data
getAirQualityData(airUrl)