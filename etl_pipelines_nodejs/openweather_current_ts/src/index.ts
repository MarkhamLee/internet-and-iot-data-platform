// (C) Markham Lee 2023 - 2024
// productivity-music-stocks-weather-IoT-dashboard
// https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
// WORK IN PROGRESS
// TODO: turn weather data API call into a function, add await & async
// Use the interface for data checking
// Move build API URL to a separate function 
// Move city and endpoint to environmental variables

import axios from 'axios'
import { Point } from '@influxdata/influxdb-client';
import {config, createOpenWeatherUrl, createInfluxClient,
        sendSlackAlerts} from "../utils/openweather_library"


// Get OpenWeather data 
const getWeatherData = (weatherUrl: string) => {

  // retrieve weather data 
  axios.get(weatherUrl)
  .then(res => {
  console.log('Weather data retrieved with status code:', res.status)

  // split out parts of the json 
  const data = res.data.main;
  
  // parse out individual fields 
      const payload = {"barometric_pressure": data.pressure,
      "description": res.data.weather[0].description,
      "feels_like": data.feels_like,
      "high": data.temp_max,
      "humidity": data.humidity,
      "low": data.temp_min,
      "temp": data.temp,
      "time_stamp": res.data.dt,
      "weather": res.data.weather[0].main,
      "wind": res.data.wind.speed }

      console.log("InfluxDB payload ready:", payload)
      writeData(payload)


  })
  .catch(err => {
      const message = "Pipeline failure alert: OpenWeather API current weather node.js variant with error: "
      console.error(message.concat(err.message));

      //send Slack failure alert
      sendSlackAlerts(message.concat(err.message))
      });
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

