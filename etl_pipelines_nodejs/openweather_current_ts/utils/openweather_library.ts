// (C) Markham Lee 2023 - 2024
// productivity-music-stocks-weather-IoT-dashboard
// https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
// Node variant for the OpenWeather API ETL - pulls down data for current weather
// conditions and writes it to InfluxDB

import axios from 'axios';
import { InfluxDB } from '@influxdata/influxdb-client';
import { config } from "./openweather_config"



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
const createOpenWeatherUrl = (endpoint: string) => {

    // load weather related variables 
    const weatherKey = config.weatherKey
    const city = config.city

    // build openweather API URL 
    const baseUrl = "http://api.openweathermap.org/data/2.5/"
    const units = "&units=metric"
    const weatherUrl = baseUrl.concat(endpoint,'appid=',weatherKey,'&q=',city,units)
    console.log('Base url created')

    return weatherUrl

}

const sendSlackAlerts = (message: string) => {

    const payload = JSON.stringify({"text": message})
        
        axios.post(config.webHookUrl, payload)
            .then(function (response) {
                console.log("Slack message sent successfully with code:", response.status);
        })
        
        .catch(function (error) {
            console.error("Slack message failure with error: ", error.statusText);
        });
        
}

export {config, createInfluxClient, sendSlackAlerts, createOpenWeatherUrl}