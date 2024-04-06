// (C) Markham Lee 2023 - 2024
// productivity-music-stocks-weather-IoT-dashboard
// https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
// Node.js - TypeScript version of the Finnhub ETL: pulling down daily stock price data 
// and writing it to InfluxDB.

import { getFinnhubData, parseData, writeData} from './main';
import { config, FinnhubSchema } from '../utils/finnhub_config'
import { sendSlackAlerts,  validateJson} from "../../common/etlUtilities";
import { createFinnhubUrl } from "../utils/utilities"


// create Finnhub URL
const finnhubUrl = createFinnhubUrl(config.stock);

// get & write data
getFinnhubData(finnhubUrl)
    .then(result => {

        //validate the data - shutdown if the data is invalid
        const validationStatus = validateJson(result, FinnhubSchema)

        if (validationStatus == 1) {

            const message = "OpenWeather pipeline failure: data validation"

            sendSlackAlerts(message, config.webHookUrl)
            process.exit()
        }
        
        // parse data - finish extraction
        const parsedData = parseData(result)

        // write data 
        const writeResponse = writeData(parsedData)

    })