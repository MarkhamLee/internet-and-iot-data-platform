// (C) Markham Lee 2023 - 2025
// internet-and-iot-data-platform
// https://github.com/MarkhamLee/internet-and-iot-data-platform
// Node variant of the OpenWeather API ETL - pulls down current weather data
// and writes it to InfluxDB

import { getAirQualityData, parseData, writeData } from "./main";
import { createAirqUrl } from "../utils/openweather_air_library"
import { sendSlackAlerts,  validateJson} from "../../common/etlUtilities";
import { config, AirQualitySchema } from "../utils/openweather_air_config"

// baseline endpoint
const endpoint = "air_pollution?"

// create URL for API get request
const airUrl = createAirqUrl(endpoint)

const openWeatherAirData = async () => {

  const airPollutionData = await getAirQualityData(airUrl)

  // parsed data - i.e., finish the extraction step 
  const parsedData = await parseData(airPollutionData)

  //validate the data, exit if invalid data detected
  const validationStatus = validateJson(parsedData, AirQualitySchema)
  
  if (validationStatus == 1) {
  
    const message = "OpenWeather pipeline failure: data validation"
    sendSlackAlerts(message, config.webHookUrl)
    process.exit()   
  }
  
  // write data to InfluxDB
  writeData(parsedData)

}

openWeatherAirData()