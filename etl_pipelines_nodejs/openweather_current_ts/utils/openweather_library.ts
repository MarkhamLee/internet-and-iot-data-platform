// (C) Markham Lee 2023 - 2024
// productivity-music-stocks-weather-IoT-dashboard
// https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
// Node variant for the OpenWeather API ETL - pulls down data for current weather
// conditions and writes it to InfluxDB
import { config } from "./openweather_config"

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


export { createOpenWeatherUrl }