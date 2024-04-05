// (C) Markham Lee 2023 - 2024
// productivity-music-stocks-weather-IoT-dashboard
// https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
// Node variant of the Finnhub Stock Price ETL, pulls down current price data for
// a given stock and then writes it to InfluxDB.

import axios from 'axios';
import Ajv from "ajv";
import {InfluxDB} from '@influxdata/influxdb-client';
import { config, FinnhubSchema } from '../utils/finnhub_config'


// create InfluxDB client
const createInfluxClient = (bucket: string) => {

    const url = config.url
    const token = config.token
    const org = config.org

    const client = new InfluxDB({url, token})
    console.log('InfluxDB client created')

    return client.getWriteApi(org, bucket, 'ns')

}

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
    
        const validData = ajv.validate(FinnhubSchema, data)
    
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

export {config, createInfluxClient, sendSlackAlerts, validateJson}