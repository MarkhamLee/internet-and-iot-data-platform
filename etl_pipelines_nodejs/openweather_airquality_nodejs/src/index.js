"use strict";
// (C) Markham Lee 2023 - 2024
// productivity-music-stocks-weather-IoT-dashboard
// https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
// Node variant of the OpenWeather API ETL - pulls down current weather data
// and writes it to InfluxDB
Object.defineProperty(exports, "__esModule", { value: true });
var main_1 = require("./main");
var openweather_air_library_1 = require("../utils/openweather_air_library");
// baseline endpoint
var endpoint = "air_pollution?";
// create URL for API get request
var airUrl = (0, openweather_air_library_1.createAirqUrl)(endpoint);
// get & write data
(0, main_1.getAirQualityData)(airUrl)
    .then(function (result) {
    // parsed data - i.e., finish the extraction step 
    var parsedData = (0, main_1.parseData)(result);
    // write data to InfluxDB
    (0, main_1.writeData)(parsedData);
});
