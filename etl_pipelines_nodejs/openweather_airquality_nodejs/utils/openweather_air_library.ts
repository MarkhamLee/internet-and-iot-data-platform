// (C) Markham Lee 2023 - 2024
// productivity-music-stocks-weather-IoT-dashboard
// https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
// Node variant of the OpenWeather API ETL - pulls down current weather data
// and writes it to InfluxDB

import { config } from '../utils/openweather_air_config'

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

    return airUrl

}

export { createAirqUrl }