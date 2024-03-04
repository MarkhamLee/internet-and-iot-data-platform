// (C) Markham Lee 2023 - 2024
// productivity-music-stocks-weather-IoT-dashboard
// https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
// Retrieving Air Quality data from the OpenWeather API and writing it to InfluxDB.

import axios from 'axios'
import { Point } from '@influxdata/influxdb-client';
import {config, createAirqUrl, createInfluxClient,
        sendSlackAlerts, AirResponse, ErrorMessage} from "../utils/openweather_air_library"


// Get OpenWeather data 
const getAirQualityData = async (airUrl: string): Promise<AirResponse[] | ErrorMessage> => {

    try {
    
        const { data } = await axios.get<AirResponse[]>(airUrl)
        return data

    } catch (error: any) {

        const message = "Pipeline failure on nodejs version of OpenWeather Air Quality Pipeline: "
        const full_message = message.concat(error)
        console.error(full_message)
        sendSlackAlerts(full_message)
        
        return {
            message: error.message,
            status: error.response.status
        }
        
    }

}


const parseData = (data: any) => {

    // split out the part of the json that contains the bulk of the data points
    const airData = data['list'][0]['components']

    const { co } = airData
    const { pm2_5} = airData
    const { pm10 } = airData
        
    // parse out individual fields 
   const payload = {"carbon_monoxide": co,
                     "pm_2": pm2_5,
                     "pm_10": pm10 }

    console.log('DB payload ready: ', payload)

    return payload

}


//method to write data to InfluxDB
// the InfluxDB node.js library doesn't have a clean way of just
// pushing json data to the DB. So, the write methods will have to 
// live in the primary ETL code for now. 
const writeData = (payload: any) => {   

    try {

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

    } catch (error: any) {

        const message = "Pipeline failure alert - InfluxDB write error: "
        const full_message = (message.concat(JSON.stringify((error.body))));
        console.error(full_message);

        //send pipeline failure alert via Slack
        sendSlackAlerts(full_message);

    }
  
  }

// baseline endpoint
const endpoint = "air_pollution?"

// create URL for API get request
const airUrl = createAirqUrl(endpoint)
  
// get & write data
getAirQualityData(airUrl)
  .then(result => { 

    // parsed data - i.e., finish teh extraction step 
    const parsedData = parseData(result)

    // write data to InfluxDB
    writeData(parsedData)

  });
