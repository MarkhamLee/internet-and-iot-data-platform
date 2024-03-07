"use strict";
// (C) Markham Lee 2023 - 2024
// productivity-music-stocks-weather-IoT-dashboard
// https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
// Node variant for the OpenWeather API ETL - pulls down data for current weather
// conditions and writes it to InfluxDB
Object.defineProperty(exports, "__esModule", { value: true });
var openweather_library_1 = require("../utils/openweather_library");
var main_1 = require("../src/main");
//baseline endpoint
var endpoint = "weather?";
// create URL for API get request
var weatherUrl = (0, openweather_library_1.createOpenWeatherUrl)(endpoint);
// get & write data
(0, main_1.getWeatherData)(weatherUrl)
    .then(function (result) {
    //parse data - finish extraction
    var parsedData = (0, main_1.parseData)(result);
    //write data to InfluxDB
    (0, main_1.writeData)(parsedData);
});
