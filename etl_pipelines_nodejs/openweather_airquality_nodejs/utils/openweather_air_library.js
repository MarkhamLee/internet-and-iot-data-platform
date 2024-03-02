"use strict";
// (C) Markham Lee 2023 - 2024
// productivity-music-stocks-weather-IoT-dashboard
// https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
// Node variant for the OpenWeather API ETL - pulls down current weather data
// and writes it to InfluxDB
Object.defineProperty(exports, "__esModule", { value: true });
exports.createAirqUrl = exports.sendSlackAlerts = exports.createInfluxClient = exports.config = void 0;
var influxdb_client_1 = require("@influxdata/influxdb-client");
var axios_1 = require("axios");
var config = {
    bucket: process.env.BUCKET,
    city: process.env.CITY,
    lat: process.env.LAT,
    long: process.env.LONG,
    measurement: process.env.AIR_QUALITY_MEASUREMENT,
    org: process.env.INFLUX_ORG,
    token: process.env.INFLUX_KEY,
    url: process.env.INFLUX_URL,
    weatherKey: process.env.OPENWEATHER_KEY,
    webHookUrl: process.env.ALERT_WEBHOOK,
};
exports.config = config;
// create InfluxDB client
var createInfluxClient = function (bucket) {
    var url = config.url;
    var token = config.token;
    var org = config.org;
    var client = new influxdb_client_1.InfluxDB({ url: url, token: token });
    console.log('InfluxDB client created');
    return client.getWriteApi(org, bucket, 'ns');
};
exports.createInfluxClient = createInfluxClient;
// create OpenWeather URL 
var createAirqUrl = function (endpoint) {
    // load weather related variables 
    var weatherKey = config.weatherKey;
    var lat = config.lat;
    var long = config.long;
    // build openweather API URL 
    var baseUrl = "http://api.openweathermap.org/data/2.5/";
    var units = "&units=metric";
    var airUrl = baseUrl.concat(endpoint, 'appid=', weatherKey, '&lat=', lat, '&lon=', long);
    console.log('Base url created', airUrl);
    return airUrl;
};
exports.createAirqUrl = createAirqUrl;
var sendSlackAlerts = function (message) {
    var payload = JSON.stringify({ "text": message });
    axios_1.default.post(config.webHookUrl, payload)
        .then(function (response) {
        console.log("Slack message sent successfully with code:", response.status);
    })
        .catch(function (error) {
        console.error("Slack message failure with error: ", error.statusText);
    });
};
exports.sendSlackAlerts = sendSlackAlerts;
