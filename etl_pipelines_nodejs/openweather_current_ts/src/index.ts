// (C) Markham Lee 2023 - 2024
// productivity-music-stocks-weather-IoT-dashboard
// https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
// WORK IN PROGRESS
// TODO: turn weather data API call into a function, add await & async
// Use the interface for data checking
// Move build API URL to a separate function 
// Move city and endpoint to environmental variables


import axios from 'axios';
import {config, createOpenWeatherUrl, writeData, 
        sendSlackAlerts, getWeatherData} from "../utils/openweather_library"

const endpoint = "weather?"
const weatherUrl = createOpenWeatherUrl(endpoint)

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
        console.log(message.concat(err.message));

        //send Slack failure alert
        sendSlackAlerts(message.concat(err.message))
        });
