"use strict";
// (C) Markham Lee 2023 - 2024
// productivity-music-stocks-weather-IoT-dashboard
// https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
// WORK IN PROGRESS
// TODO: turn weather data API call into a function, add await & async
// Use the interface for data checking
// Move build API URL to a separate function 
// Move city and endpoint to environmental variables
Object.defineProperty(exports, "__esModule", { value: true });
var axios_1 = require("axios");
var openweather_library_1 = require("../utils/openweather_library");
// load Bucket (database in InfluxDB parlance) & create InfluxDB client
var bucket = openweather_library_1.config.bucket;
var writeClient = (0, openweather_library_1.createInfluxClient)(bucket);
// load weather related variables 
var weatherKey = openweather_library_1.config.weatherKey;
var city = "&q=seattle";
var endpoint = "weather?";
// build openweather API URL 
var baseUrl = "http://api.openweathermap.org/data/2.5/";
var units = "&units=metric";
var weatherUrl = baseUrl.concat(endpoint, 'appid=', weatherKey, city, units);
console.log('Base url created');
// retrieve weather data 
axios_1.default.get(weatherUrl)
    .then(function (res) {
    var headerDate = res.headers && res.headers.date ? res.headers.date : 'no response date';
    console.log('Weather data retrieved with status code:', res.status);
    // split out parts of the json 
    var data = res.data.main;
    // parse out individual fields 
    var payload = { "barometric_pressure": data.pressure,
        "description": res.data.weather[0].description,
        "feels_like": data.feels_like,
        "high": data.temp_max,
        "humidity": data.humidity,
        "low": data.temp_min,
        "temp": data.temp,
        "time_stamp": res.data.dt,
        "weather": res.data.weather[0].main,
        "wind": res.data.wind.speed };
    console.log("InfluxDB payload ready:", payload);
    (0, openweather_library_1.writeData)(writeClient, payload);
})
    .catch(function (err) {
    var message = "Pipeline failure alert: OpenWeather API current weather node.js variant with error: ";
    console.log(message.concat(err.message));
    //send Slack failure alert
    (0, openweather_library_1.sendSlackAlerts)(message.concat(err.message));
});
