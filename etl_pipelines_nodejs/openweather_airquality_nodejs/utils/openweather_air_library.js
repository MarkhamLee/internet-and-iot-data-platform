"use strict";
// (C) Markham Lee 2023 - 2024
// productivity-music-stocks-weather-IoT-dashboard
// https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
// Node variant of the OpenWeather API ETL - pulls down current weather data
// and writes it to InfluxDB
Object.defineProperty(exports, "__esModule", { value: true });
exports.validateJson = exports.createAirqUrl = exports.sendSlackAlerts = exports.createInfluxClient = exports.config = void 0;
var axios_1 = require("axios");
var ajv_1 = require("ajv");
var influxdb_client_1 = require("@influxdata/influxdb-client");
var openweather_air_config_1 = require("../utils/openweather_air_config");
Object.defineProperty(exports, "config", { enumerable: true, get: function () { return openweather_air_config_1.config; } });
// create InfluxDB client
var createInfluxClient = function (bucket) {
    var url = openweather_air_config_1.config.url;
    var token = openweather_air_config_1.config.token;
    var org = openweather_air_config_1.config.org;
    var client = new influxdb_client_1.InfluxDB({ url: url, token: token });
    console.log('InfluxDB client created');
    return client.getWriteApi(org, bucket, 'ns');
};
exports.createInfluxClient = createInfluxClient;
// create OpenWeather URL 
var createAirqUrl = function (endpoint) {
    // load weather related variables 
    var weatherKey = openweather_air_config_1.config.weatherKey;
    var lat = openweather_air_config_1.config.lat;
    var long = openweather_air_config_1.config.long;
    // build openweather API URL 
    var baseUrl = "http://api.openweathermap.org/data/2.5/";
    var units = "&units=metric";
    var airUrl = baseUrl.concat(endpoint, 'appid=', weatherKey, '&lat=', lat, '&lon=', long);
    return airUrl;
};
exports.createAirqUrl = createAirqUrl;
// send Slack alerts via a web hook specific to a channel for
// data pipeline errors.
var sendSlackAlerts = function (message) {
    var payload = JSON.stringify({ "text": message });
    axios_1.default.post(openweather_air_config_1.config.webHookUrl, payload)
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
    var validData = ajv.validate(openweather_air_config_1.airQualitySchema, data);
    if (validData) {
        console.log("Data validation successful");
    }
    else {
        var message = "Pipeline failure data validation - OpenWeather Air Quality (nodejs variant), exiting... ";
        console.error("Data validation error: ", ajv.errors);
        // exit the script so we don't attempt a DB write that won't work or
        // would write bad data to our db.
        return process.exit();
    }
};
exports.validateJson = validateJson;
