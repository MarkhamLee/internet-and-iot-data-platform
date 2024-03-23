// (C) Markham Lee 2023 - 2024
// productivity-music-stocks-weather-IoT-dashboard
// https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
// Node variant of the OpenWeather API ETL - pulls down current weather data
// and writes it to InfluxDB

import { getAirQualityData, parseData, writeData } from "./main";
import { createAirqUrl } from "../utils/openweather_air_library"
import { sendSlackAlerts,  validateJson} from "../../common/etlUtilities";
import { config, AirQualitySchema }
from "../utils/openweather_air_config"

// baseline endpoint
const endpoint = "air_pollution?"

// create URL for API get request
const airUrl = createAirqUrl(endpoint)
  
// get & write data
getAirQualityData(airUrl)
    .then(result => { 

      // parsed data - i.e., finish the extraction step 
      const parsedData = parseData(result)

      //validate the data - if the data is invalid
      const validationStatus = validateJson(parsedData, AirQualitySchema)

      if (validationStatus == 1) {

        const message = "OpenWeather pipeline failure: data validation"

        sendSlackAlerts(message, config.webHookUrl)
        process.exit()
     
          }

    // write data to InfluxDB
    writeData(parsedData)

  });


 