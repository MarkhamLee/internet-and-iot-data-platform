// (C) Markham Lee 2023 - 2024
// productivity-music-stocks-weather-IoT-dashboard
// https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
// Node variant for the OpenWeather API ETL - pulls down current weather data
// and writes it to InfluxDB

import { InfluxDB } from '@influxdata/influxdb-client';
import axios from 'axios';

// interface for weather data

export interface AirQualityMetrics {
    no: number,
    no2: number,
    temp: number,
    o3: number,
    so2: number,
    pm2_5: number,
    pm10: number,
    nh3: number,
    dt: number,
  }

export interface AirResponse {
    data: AirQualityMetrics,
    status: number
}


interface VarConfig {
    bucket: string;
    city: string;
    lat: string;
    long: string;
    measurement: string;
    org: string 
    token: string;
    url: string;
    weatherKey: string;
    webHookUrl: string;
    
  }

const config: VarConfig = {
    
    bucket: process.env.BUCKET as string,
    city: process.env.CITY as string,
    lat: process.env.LAT as string,
    long: process.env.LONG as string,
    measurement: process.env.AIR_QUALITY_MEASUREMENT as string,
    org: process.env.INFLUX_ORG as string,
    token: process.env.INFLUX_KEY as string,
    url: process.env.INFLUX_URL as string,
    weatherKey: process.env.OPENWEATHER_KEY as string,
    webHookUrl: process.env.ALERT_WEBHOOK as string,
    
  };

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
    console.log('Base url created', airUrl)

    return airUrl

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


export {config, createInfluxClient, sendSlackAlerts, createAirqUrl}