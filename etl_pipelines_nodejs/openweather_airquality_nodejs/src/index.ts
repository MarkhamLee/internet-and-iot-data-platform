// (C) Markham Lee 2023 - 2024
// productivity-music-stocks-weather-IoT-dashboard
// https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
// Node variant of the OpenWeather API ETL - pulls down current weather data
// and writes it to InfluxDB

import { getAirQualityData, parseData, writeData } from "./main";
import { createAirqUrl } from "../utils/openweather_air_library"


// baseline endpoint
const endpoint = "air_pollution?"

// create URL for API get request
const airUrl = createAirqUrl(endpoint)
  
// get & write data
getAirQualityData(airUrl)
    .then(result => { 

    // parsed data - i.e., finish the extraction step 
    const parsedData = parseData(result)

    // write data to InfluxDB
    writeData(parsedData)

  });

 