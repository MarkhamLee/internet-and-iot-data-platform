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
var influxdb_client_1 = require("@influxdata/influxdb-client");
var openweather_library_1 = require("../utils/openweather_library");
// Get OpenWeather data 
var getWeatherData = function (weatherUrl) {
    // retrieve weather data 
    axios_1.default.get(weatherUrl)
        .then(function (res) {
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
        writeData(payload);
    })
        .catch(function (err) {
        var message = "Pipeline failure alert: OpenWeather API current weather node.js variant with error: ";
        console.error(message.concat(err.message));
        //send Slack failure alert
        (0, openweather_library_1.sendSlackAlerts)(message.concat(err.message));
    });
};
//method to write data to InfluxDB
// the InfluxDB node.js library doesn't have a clean way of just
// pushing json data to the DB. So, the write methods will have to 
// live in the primary ETL code for now. 
var writeData = function (payload) {
    var bucket = openweather_library_1.config.bucket;
    var writeClient = (0, openweather_library_1.createInfluxClient)(bucket);
    var point = new influxdb_client_1.Point(openweather_library_1.config.measurement)
        .tag("OpenWeatherAPI", "current_weather")
        .floatField('temp', payload.temp)
        .floatField('wind', payload.wind)
        .floatField('barometric_pressure', payload.barometric_pressure)
        .floatField('humidity', payload.humidity)
        .floatField('low', payload.low)
        .floatField('high', payload.high)
        .floatField('feels_like', payload.feels_like)
        .intField('time_stamp', payload.time_stamp)
        .stringField('description', payload.description)
        .stringField('weather', payload.weather);
    // write data to InfluxDB
    void setTimeout(function () {
        writeClient.writePoint(point);
        console.log("Weather data successfully written to InfluxDB");
    }, 1000);
    // flush client
    void setTimeout(function () {
        // flush InfluxDB client
        writeClient.flush();
    }, 1000);
};
var endpoint = "weather?";
// create URL for API get request
var weatherUrl = (0, openweather_library_1.createOpenWeatherUrl)(endpoint);
// get & write data
getWeatherData(weatherUrl);
