// (C) Markham Lee 2023 - 2024
// productivity-music-stocks-weather-IoT-dashboard
// https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
// Node variant of the Finnhub Stock Price ETL, pulls down current price data for
// a given stock and then writes it to InfluxDB.


import axios from 'axios';
import {InfluxDB} from '@influxdata/influxdb-client';
import { config } from '../utils/gh_actions_config'

// create InfluxDB client
const createInfluxClient = (bucket: string) => {

    const url = config.url
    const token = config.token
    const org = config.org

    const client = new InfluxDB({url, token})
    console.log('InfluxDB client created')

    return client.getWriteApi(org, bucket, 'ns')

    }

// send Slack alerts via a webhook for the pipeline failure channel
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

const buildUrl = (repo: string) => {

    const baseUrl = 'https://api.github.com/repos/MarkhamLee/'

    const endpoint = 'actions/runs'

    return baseUrl.concat(repo, endpoint)

}


export {createInfluxClient, sendSlackAlerts, buildUrl}