"use strict";
// (C) Markham Lee 2023 - 2024
// productivity-music-stocks-weather-IoT-dashboard
// https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
// Node variant for the OpenWeather API ETL - pulls down data for current weather
// conditions and writes it to InfluxDB
Object.defineProperty(exports, "__esModule", { value: true });
exports.validateJson = exports.createOpenWeatherUrl = exports.sendSlackAlerts = exports.createInfluxClient = exports.config = void 0;
var axios_1 = require("axios");
var ajv_1 = require("ajv");
var influxdb_client_1 = require("@influxdata/influxdb-client");
var openweather_config_1 = require("./openweather_config");
Object.defineProperty(exports, "config", { enumerable: true, get: function () { return openweather_config_1.config; } });
// create InfluxDB client
var createInfluxClient = function (bucket) {
    var url = openweather_config_1.config.url;
    var token = openweather_config_1.config.token;
    var org = openweather_config_1.config.org;
    var client = new influxdb_client_1.InfluxDB({ url: url, token: token });
    console.log('InfluxDB client created');
    return client.getWriteApi(org, bucket, 'ns');
};
exports.createInfluxClient = createInfluxClient;
// create OpenWeather URL 
var createOpenWeatherUrl = function (endpoint) {
    // load weather related variables 
    var weatherKey = openweather_config_1.config.weatherKey;
    var city = openweather_config_1.config.city;
    // build openweather API URL 
    var baseUrl = "http://api.openweathermap.org/data/2.5/";
    var units = "&units=metric";
    var weatherUrl = baseUrl.concat(endpoint, 'appid=', weatherKey, '&q=', city, units);
    console.log('Base url created');
    return weatherUrl;
};
exports.createOpenWeatherUrl = createOpenWeatherUrl;
var sendSlackAlerts = function (message) {
    var status_message;
    var payload = JSON.stringify({ "text": message });
    axios_1.default.post(openweather_config_1.config.webHookUrl, payload)
        .then(function (response) {
        console.log("Slack message sent successfully with code:", response.status);
    })
        .catch(function (error) {
        console.error("Slack message failure with error: ", error.statusText);
    });
};
exports.sendSlackAlerts = sendSlackAlerts;
var validateJson = function (data) {
    var ajv = new ajv_1.default();
    var validData = ajv.validate(openweather_config_1.openWeatherSchema, data);
    if (validData) {
        console.log("DB payload validation successful");
        return 0;
    }
    else {
        var message = "Pipeline failure data validation - OpenWeather Air Quality (nodejs variant), exiting... ";
        console.error("Data validation error: ", ajv.errors);
        sendSlackAlerts(message);
        return 1;
    }
};
exports.validateJson = validateJson;
