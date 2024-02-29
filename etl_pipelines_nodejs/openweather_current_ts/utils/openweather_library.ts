// (C) Markham Lee 2023 - 2024
// productivity-music-stocks-weather-IoT-dashboard
// https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
// Node variant for the OpenWeather API ETL - pulls down current weather data
// and writes it to InfluxDB

import {InfluxDB, Point} from '@influxdata/influxdb-client';
import axios from 'axios';


// interface for weather data
export interface CurrentWeather {
    main: string,
    description: string,
    temp: number,
    feels_like: number,
    temp_min: number,
    temp_max: number,
    pressure: number,
    humidity: number,
    speed: number
  }

interface VarConfig {
    bucket: string;
    weatherKey: string;
    token: string;
    url: string;
    org: string 
    webHookUrl: string;
    measurement: string;
  }

const config: VarConfig = {
    
    bucket: process.env.BUCKET as string,
    weatherKey: process.env.OPENWEATHER_KEY as string,
    token: process.env.INFLUX_KEY as string,
    url: process.env.INFLUX_URL as string,
    org: process.env.INFLUX_ORG as string,
    webHookUrl: process.env.ALERT_WEBHOOK as string,
    measurement: process.env.MEASUREMENT as string


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


// Get OpenWeather data 
const getWeatherData = (weatherUrl: string) => {

    axios.get(weatherUrl)
    .then(response => {

        console.log(response.data)

    })
    .catch(err => {
        
        console.error(err);
    })
}

//method to write data to InfluxDB
const writeData = (writeClient: any, payload: any) => {   
    
        let point = new Point(config.measurement)
                .tag("OpenWeatherAPI", "current_weather",)
                .floatField('temp', payload.temp) 
                .floatField('wind', payload.wind)
                .floatField('barometric_pressure', payload.barometric_pressure)
                .floatField('humidity', payload.humidity)
                .floatField('low', payload.low)
                .floatField('high', payload.high)
                .floatField('feels_like', payload.feels_like)
                .intField('time_stamp', payload.time_stamp)
                .stringField('description', payload.description)
                .stringField('weather', payload.weather)
                
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

const sendSlackAlerts = (message: string) => {

    const payload = JSON.stringify({"text": message})
        
        axios.post(config.webHookUrl, payload)
            .then(function (response) {
                console.log("Slack message sent successfully with code:", response.status);
        })
        
        .catch(function (error) {
            console.log("Slack message failure with error: ", error.response.statusText);
        });
        
    }

export {config, getWeatherData, createInfluxClient, writeData, sendSlackAlerts}