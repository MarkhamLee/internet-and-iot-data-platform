"use strict";
// (C) Markham Lee 2023 - 2024
// productivity-music-stocks-weather-IoT-dashboard
// https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
// Node variant for the OpenWeather API ETL - pulls down current weather data
// and writes it to InfluxDB
Object.defineProperty(exports, "__esModule", { value: true });
exports.sendSlackAlerts = exports.writeData = exports.createInfluxClient = exports.getWeatherData = exports.config = void 0;
var influxdb_client_1 = require("@influxdata/influxdb-client");
var axios_1 = require("axios");
var config = {
    bucket: process.env.BUCKET,
    weatherKey: process.env.OPENWEATHER_KEY,
    token: process.env.INFLUX_KEY,
    url: process.env.INFLUX_URL,
    org: process.env.INFLUX_ORG,
    webHookUrl: process.env.ALERT_WEBHOOK,
    measurement: process.env.MEASUREMENT
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
// Get OpenWeather data 
var getWeatherData = function (weatherUrl) {
    axios_1.default.get(weatherUrl)
        .then(function (response) {
        console.log(response.data);
    })
        .catch(function (err) {
        console.error(err);
    });
};
exports.getWeatherData = getWeatherData;
//method to write data to InfluxDB
var writeData = function (writeClient, payload) {
    var point = new influxdb_client_1.Point(config.measurement)
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
exports.writeData = writeData;
var sendSlackAlerts = function (message) {
    var payload = JSON.stringify({ "text": message });
    axios_1.default.post(config.webHookUrl, payload)
        .then(function (response) {
        console.log("Slack message sent successfully with code:", response.status);
    })
        .catch(function (error) {
        console.log("Slack message failure with error: ", error.response.statusText);
    });
};
exports.sendSlackAlerts = sendSlackAlerts;
