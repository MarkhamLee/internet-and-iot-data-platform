// (C) Markham Lee 2023 - 2024
// finance-productivity-IoT-weather-dashboard
// https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
// Common methods for Node.js ETL pipelines

import axios from 'axios';
import Ajv from "ajv";
import { InfluxDB } from '@influxdata/influxdb-client';

// create InfluxDB client
const createInfluxClient = (bucket: string, url: string,
    token: string, org: string) => {


    const client = new InfluxDB({url, token})
    console.log('InfluxDB client created')

    return client.getWriteApi(org, bucket, 'ns')

}

// send Slack Alerts
const sendSlackAlerts = async (message: string, webHookUrl: string) => {

    const payload = JSON.stringify({"text": message})
    
    try {
        const response = await axios.post(webHookUrl, payload)
        return response.status

    } catch (error: any) {
        console.error("Slack message failure with error: ", error.statusText)
        return error.statusText
    }

}


// validate json data
const validateJson = (data: object, schema: object) => {

    const ajv = new Ajv()

    const validData = ajv.validate(schema, data)

    if (validData) {

        console.log("DB payload validation successful");
        return 0

      } else {
        
        const message = "Pipeline failure data validation exiting... "
        console.error("Data validation error: ", ajv.errors);

        return 1
   
      }
}

export {createInfluxClient, sendSlackAlerts, validateJson}