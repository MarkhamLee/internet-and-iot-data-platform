// (C) Markham Lee 2023 - 2024
// productivity-music-stocks-weather-IoT-dashboard
// https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
// Node variant for the OpenWeather API ETL - pulls down data for current weather
// conditions and writes it to InfluxDB
// WORK IN PROGRESS
// TODO: add an interface to the API call

import axios from 'axios'
import { Point } from '@influxdata/influxdb-client';
import {config, createOpenWeatherUrl, createInfluxClient,
        sendSlackAlerts, WeatherResponse, CurrentWeather} from "../utils/openweather_library"


// Get OpenWeather data 
const getWeatherData = async (weatherUrl: string) => {
    
    try {

      const data = await axios.get(weatherUrl)
      
      // split out the part of the json that contains the bulk of the data points
      const weather_data = data.data.main;
        
      // parse out individual fields 
        const payload = {"barometric_pressure": weather_data.pressure,
        "description": data.data.weather[0].description,
        "feels_like": weather_data.feels_like,
        "high": weather_data.temp_max,
        "humidity": weather_data.humidity,
        "low": weather_data.temp_min,
        "temp": weather_data.temp,
        "time_stamp": data.data.dt,
        "weather": data.data.weather[0].main,
        "wind": data.data.wind.speed }

        console.log("InfluxDB payload ready:", payload)
        const response = writeData(payload)

    } catch (error: any) {
        const message = "Pipeline failure alert - OpenWeather API current weather node.js variant with error: "
        const full_message = (message.concat(JSON.stringify((error.response.data))));
        console.error(full_message);

        //send pipeline failure alert via Slack
        sendSlackAlerts(full_message);

    }

}


//method to write data to InfluxDB
// the InfluxDB node.js library doesn't have a clean way of just
// pushing json data to the DB. So, the write methods will have to 
// live in the primary ETL code for now. 
const writeData = (payload: any) => {   

  const bucket = config.bucket
  const writeClient = createInfluxClient(bucket)

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


const endpoint = "weather?"

// create URL for API get request
const weatherUrl = createOpenWeatherUrl(endpoint)
  
// get & write data
getWeatherData(weatherUrl)

