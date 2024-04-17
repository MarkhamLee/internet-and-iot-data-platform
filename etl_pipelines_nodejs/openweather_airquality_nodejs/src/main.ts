// (C) Markham Lee 2023 - 2024
// productivity-music-stocks-weather-IoT-dashboard
// https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
// Node variant of the OpenWeather API ETL - pulls down Air Pollution Data and
// writes it to InfluxDB.

import axios from 'axios'
import { Point } from '@influxdata/influxdb-client';
import { config, AirQualityMetrics, AirQualitySubset, airPointData }
from "../utils/openweather_air_config"
import {createInfluxClient, sendSlackAlerts }
from "../../common/etlUtilities"


// Get OpenWeather data 
const getAirQualityData = async (airUrl: string): Promise<AirQualitySubset> => {

    try {
        
        const { data } = await axios.get<AirQualityMetrics>(airUrl)

        // split out the part of the json that contains the bulk of the data points
        const airData = data['list'][0]['components']

        console.log("OpenWeather Air Pollution API call successful", airData)

        return airData

    } catch (error: any){

        const message = "OpenWeather API Pipeline Air Pollution (Nodejs variant) failure, API connection error: "
        const fullMessage = message.concat(error)
        console.error(fullMessage)

        //send pipeline failure alert via Slack
        const result = await sendSlackAlerts(message, config.webHookUrl)
        console.error("Slack alert sent with code:", result)
        return result

    }
}

// parse out the desired fields
// TODO: update to calculate AQI - may need all the fields for that 
const parseData = async (data: AirQualitySubset) => {

    try {

        // parse out individual fields 
        const payload = {"co": data['co'],
        "pm2_5": data['pm2_5'],
        "pm10": data['pm10']}

        console.log('DB payload ready:', payload)
        return payload


    } catch (error: any) {

        const message = "OpenWeather air pollution pipeline error: parsing failed"
        const fullMessage  = message.concat(error)
        console.error(fullMessage)

        //send pipeline failure alert via Slack
        const result = await sendSlackAlerts(fullMessage, config.webHookUrl)
        console.error("Slack alert sent for Open Weather Air Pollution:", result)
        return result

    }
}

//method to write data to InfluxDB
// the InfluxDB node.js library doesn't have a clean way of just
// pushing json data to the DB. So, the write methods will have to 
// live in the primary ETL code for now. 
const writeData = async (payload: airPointData) => {   

    try {

        const writeClient = createInfluxClient(config.bucket, config.url,
            config.token, config.org)
    
        const point = new Point(config.measurement)
                .tag("OpenWeatherAPI", "Air Quality")
                .floatField('carbon_monoxide', payload.co) 
                .floatField('pm_2', payload.pm2_5)
                .floatField('pm_10', payload.pm10)
                

        writeClient.writePoint(point)
        writeClient.close().then(() => {
            console.log('Weather data successfully written to InfluxDB')
          })
        return 0

    } catch (error: any) {

        const message = "OpenWeather API, Air Pollution Pipeline (Nodejs variant) failure - InfluxDB write error: "
        const fullMessage = message.concat(error)
        console.error(fullMessage)

        //send pipeline failure alert via Slack
        const result = await sendSlackAlerts(message, config.webHookUrl)
        console.error("Slack alert sent with code:", result)
        return result
   
    }
  
  }

  export { getAirQualityData, parseData, writeData }