// (C) Markham Lee 2023 - 2024
// productivity-music-stocks-weather-IoT-dashboard
// https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
// Node variant of the OpenWeather API ETL - pulls down current weather data
// and writes it to InfluxDB

import axios from 'axios'
import { Point } from '@influxdata/influxdb-client';
import { config, AirResponse, AirQualitySchema, ErrorMessage }
from "../utils/openweather_air_config"
import {createInfluxClient, sendSlackAlerts, validateJson}
from "../../common/etlUtilities"


// Get OpenWeather data 
const getAirQualityData = async (airUrl: string): Promise<AirResponse[] | ErrorMessage> => {

    try {
    
        const { data } = await axios.get<AirResponse[]>(airUrl)
        return data

    } catch (error: any){

        const message = "OpenWeather API Pipeline Current Weather (Nodejs variant) failure, API connection error: "
        console.error(message, error.message)
        const slackResponse = sendSlackAlerts(message, config.webHookUrl)

        return {
            message: error.message,
            status: slackResponse
        } 
    }
}

// parse out the desired fields
// TODO: update to calculate AQI - may need all the fields for that 
const parseData = (data: any) => {

    // split out the part of the json that contains the bulk of the data points
    const airData = data['list'][0]['components']

    // validate the data, script(s) will exit if data is invalid
    const status = validateJson(airData, AirQualitySchema)

    if (status == 1) {

        return process.exit()
        
    }
    
    // parse out individual fields 
   const payload = {"carbon_monoxide": airData.co,
                     "pm_2": airData.pm2_5,
                     "pm_10": airData.pm10 }

    console.log('DB payload ready:', payload)

    return payload

}

//method to write data to InfluxDB
// the InfluxDB node.js library doesn't have a clean way of just
// pushing json data to the DB. So, the write methods will have to 
// live in the primary ETL code for now. 
const writeData = (payload: any) => {   

    try {

        const writeClient = createInfluxClient(config.bucket, config.url,
            config.token, config.org)
    
        const point = new Point(config.measurement)
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
              console.log('InfluxDB Client flushed/cleared.')
          }, 1000)

        return 0

    } catch (error: any) {

        const message = "OpenWeather API, Air Pollution Pipeline (Nodejs variant) failure - InfluxDB write error: "
        const fullMessage = (message.concat(JSON.stringify((error.body))));
        console.error(fullMessage);

        //send pipeline failure alert via Slack
        sendSlackAlerts(fullMessage, config.webHookUrl);

    }
  
  }

  export { getAirQualityData, parseData, writeData }