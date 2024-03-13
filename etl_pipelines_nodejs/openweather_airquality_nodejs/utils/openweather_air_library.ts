// (C) Markham Lee 2023 - 2024
// productivity-music-stocks-weather-IoT-dashboard
// https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
// Node variant of the OpenWeather API ETL - pulls down current weather data
// and writes it to InfluxDB

import axios from 'axios';
import Ajv from "ajv";
import { InfluxDB } from '@influxdata/influxdb-client';
import { config, AirQualitySchema } from '../utils/openweather_air_config'


// create InfluxDB client
const createInfluxClient = (bucket: string) => {

    const url = config.url
    const token = config.token
    const org = config.org

    const client = new InfluxDB({url, token})
    console.log('InfluxDB client created')

    return client.getWriteApi(org, bucket, 'ns')

    }

// create OpenWeather URL 
const createAirqUrl = (endpoint: string) => {

    // load weather related variables 
    const weatherKey = config.weatherKey
    const lat = config.lat
    const long = config.long

    // build openweather API URL 
    const baseUrl = "http://api.openweathermap.org/data/2.5/"
    const units = "&units=metric"
    const airUrl = baseUrl.concat(endpoint,'appid=',weatherKey,'&lat=',lat,'&lon=',long)

    return airUrl

}

// send Slack alerts via a web hook specific to a channel for
// data pipeline errors.
const sendSlackAlerts = async (message: string) => {

    const payload = JSON.stringify({"text": message})
    
    try {
        const response = await axios.post(config.webHookUrl, payload)
        console.log("Slack message sent successfully with code:", response.status);
        return response.status

    } catch (error: any) {
        console.error("Slack message failure with error: ", error.statusText)
        return 1
    }

}

const validateJson = (data: any) => {

    const ajv = new Ajv()

    const validData = ajv.validate(AirQualitySchema, data)

    if (validData) {

        console.log("Data validation successful");
        return 0

      } else {
        
        const message = "Pipeline failure data validation - OpenWeather Air Quality (nodejs variant), exiting... "
        console.error("Data validation error: ", ajv.errors);
        sendSlackAlerts(message)

        return 1  

      }

}

export {config, createInfluxClient, sendSlackAlerts, createAirqUrl, validateJson}