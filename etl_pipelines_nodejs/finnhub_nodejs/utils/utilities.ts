// (C) Markham Lee 2023 - 2024
// productivity-music-stocks-weather-IoT-dashboard
// https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
// Node variant of the Finnhub Stock Price ETL, pulls down current price data for
// a given stock and then writes it to InfluxDB.
import { config } from '../utils/finnhub_config'


// create OpenWeather URL 
const createFinnhubUrl = (symbol: string) => {

    // load weather related variables 
    const finnhubKey = config.finnhubKey

    // build openweather API URL 
    const baseUrl = "https://finnhub.io/api/v1/quote?symbol="
    const weatherUrl = baseUrl.concat(symbol, '&token=', finnhubKey)
    console.log('Base url created')

    return weatherUrl

}

export { config, createFinnhubUrl }