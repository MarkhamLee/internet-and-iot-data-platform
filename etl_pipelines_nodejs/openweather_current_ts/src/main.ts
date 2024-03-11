// (C) Markham Lee 2023 - 2024
// productivity-music-stocks-weather-IoT-dashboard
// https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
// Node variant for the OpenWeather API ETL - pulls down data for current weather
// conditions and writes it to InfluxDB

import axios from 'axios';
import { Point } from '@influxdata/influxdb-client';
import {config, WeatherResponse, ErrorMessage} from "../utils/openweather_config";
import { createInfluxClient, sendSlackAlerts, validateJson, }
from "../utils/openweather_library";


// Get OpenWeather data 
const getWeatherData = async (weatherUrl: string): Promise<WeatherResponse[] | ErrorMessage> => {

    try {
    
        const { data } = await axios.get<WeatherResponse[]>(weatherUrl)
        return data

    } catch (error: any){

        const message = "OpenWeather API Pipeline Current Weather (Nodejs variant) failure, API connection error: "
        const full_message = message.concat(error.message)
        sendSlackAlerts(full_message)
        console.error(full_message)

        return {
            message: error.message,
            status: error.response.status,
        }
    } 
}

// parse out the desired fields
// TODO: update to calculate AQI - may need all the fields for that 
// TODO: figure out how to write json directly to InfluxDB, doesn't
// seem to be possible with the Node.js library for InfluxDB, need to
// investigate further.
const parseData = (data: any) => {

      // split out the part of the json that contains the bulk of the data points
      const weather_data = data.main;
        
      // parse out individual fields 
        const payload = {"barometric_pressure": weather_data.pressure,
        "description": data.weather[0].description,
        "feels_like": weather_data.feels_like,
        "high": weather_data.temp_max,
        "humidity": weather_data.humidity,
        "low": weather_data.temp_min,
        "temp": weather_data.temp,
        "time_stamp": data.dt,
        "weather": data.weather[0].main,
        "wind": data.wind.speed }

    // Validate the payload before writing to InfluxDB.
    const status = validateJson(payload) 

    if (status == 1) {

        return process.exit()
        
    }

    console.log('DB payload ready: ', payload)

    return payload

}

//method to write data to InfluxDB
// the InfluxDB node.js library doesn't have a clean way of just
// pushing json data to the DB. So, the write methods will have to 
// live in the primary ETL code for now. 
const writeData = (payload: any) => {  

    try {

        const writeClient = createInfluxClient(config.bucket)

        let point = new Point(config.measurement)
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

    } catch (error: any) {

        const message = "OpenWeather API Pipeline Current Weather (Nodejs variant) failure, InfluxDB write error: "
        const full_message = (message.concat(JSON.stringify((error.body))));
        console.error(full_message);

        //send pipeline failure alert via Slack
        sendSlackAlerts(full_message);

    }

}

export {getWeatherData, parseData, writeData}
