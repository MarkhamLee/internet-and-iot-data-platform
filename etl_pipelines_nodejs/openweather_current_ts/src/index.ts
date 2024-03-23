// (C) Markham Lee 2023 - 2024
// productivity-music-stocks-weather-IoT-dashboard
// https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
// Node variant for the OpenWeather API ETL - pulls down data for current weather
// conditions and writes it to InfluxDB

import { createOpenWeatherUrl } from "../utils/openweather_library";
import { getWeatherData, parseData, writeData } from "../src/main"
import { sendSlackAlerts,  validateJson} from "../../common/etlUtilities";
import { config, openWeatherSchema } from "../utils/openweather_config";

//baseline endpoint
const endpoint = "weather?"

// create URL for API get request
const weatherUrl = createOpenWeatherUrl(endpoint)

// get & write data
getWeatherData(weatherUrl)
    .then(result => { //unpack value from Axios API call 

        //parse data - finish extraction
        const parsedData = parseData(result)

        //validate the data - shutdown if the data is invalid
        const validationStatus = validateJson(parsedData, openWeatherSchema)

        if (validationStatus == 1) {

            const message = "OpenWeather pipeline failure: data validation"

            sendSlackAlerts(message, config.webHookUrl)
            process.exit()
        }

        //write data to InfluxDB
        writeData(parsedData)

    })
