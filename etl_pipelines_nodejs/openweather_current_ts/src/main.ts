// (C) Markham Lee 2023 - 2024
// productivity-music-stocks-weather-IoT-dashboard
// https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
// Node variant for the OpenWeather API ETL - pulls down data for current weather
// conditions and writes it to InfluxDB

import axios from 'axios';
import { Point } from '@influxdata/influxdb-client';
import {config, CurrentWeather, parsedData}
from "../utils/openweather_config";
import {createInfluxClient, sendSlackAlerts}
from "../../common/etlUtilities";


// Get OpenWeather data 
const getWeatherData = async (weatherUrl: string): Promise<CurrentWeather> => {

    try {
    
        const { data } = await axios.get<CurrentWeather>(weatherUrl)
        console.log("OpenWeather API call successful", data)
        return data

    } catch (error: any){

        const message = "OpenWeather API Pipeline Current Weather (Nodejs variant) failure, API connection error: "
        console.error(message, error.message)
        sendSlackAlerts(message, config.webHookUrl)
            .then(result => {
                return result
            })
        throw(error.message)
    }
}

// parse out the desired fields
// TODO: update to calculate AQI - may need all the fields for that 
// TODO: figure out how to write json directly to InfluxDB, doesn't
// seem to be possible with the Node.js library for InfluxDB, need to
// investigate further.
const parseData = (data: CurrentWeather) => {

    try {

        // split out the part of the json that contains the data we need
      const weather_data = data.main;
        
      // parse out individual fields 
        const payload =  {"barometric_pressure": weather_data.pressure,
        "description": data.weather[0].description,
        "feels_like": weather_data.feels_like,
        "high": weather_data.temp_max,
        "humidity": weather_data.humidity,
        "low": weather_data.temp_min,
        "temp": weather_data.temp,
        "time_stamp": data.dt,
        "weather": data.weather[0].main,
        "wind": data.wind.speed }

        console.log("Data parsed successfully: ", payload)
        return payload

    } catch (error: any) {

        const message = "OpenWeather pipeline failure: data parsing failed"
        console.error(message)
        
        //send pipeline failure alert via Slack
        sendSlackAlerts(message, config.webHookUrl)
            .then(slackResponse => {
                    
                return slackResponse
        })

        throw(error)
        
    }
}

//method to write data to InfluxDB
// the InfluxDB node.js library doesn't have a clean way of just
// pushing json data to the DB. So, the write methods will have to 
// live in the primary ETL code for now. 
const writeData = (payload: parsedData) => {  

    try {

        const writeClient = createInfluxClient(config.bucket, config.url,
            config.token, config.org)

        const point = new Point(config.measurement)
                .tag("OpenWeatherAPI", "current_weather")
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
        writeClient.writePoint(point)
        writeClient.close().then(() => {
            console.log('Weather data successfully written to InfluxDB')
          })
        
        return 0

    } catch (error: any) {

        const message = "OpenWeather API Pipeline Current Weather (Nodejs variant) failure, InfluxDB write error: "
        const fullMessage = (message.concat(JSON.stringify(error.body)));
        console.error(fullMessage);

        //send pipeline failure alert via Slack
        sendSlackAlerts(fullMessage, config.webHookUrl)
            .then(slackResponse => {
                return slackResponse
            })
        }
}

export { getWeatherData, parseData, writeData }
