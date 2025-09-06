// (C) Markham Lee 2023 - 2025
// internet-and-iot-data-platform
// https://github.com/MarkhamLee/internet-and-iot-data-platform
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

const openWeatherData = async () => {

    const weatherData = await getWeatherData(weatherUrl)

    //parse data - finish extraction
    const parsedData = await parseData(weatherData)

    //validate the data - shutdown if the data is invalid
    const validationStatus = validateJson(parsedData, openWeatherSchema)
    
    if (validationStatus == 1) {
    
        const message = "OpenWeather pipeline failure: data validation"
        sendSlackAlerts(message, config.webHookUrl)
        process.exit()
    }
    
    //write data to InfluxDB
    writeData(parsedData)

}

openWeatherData()