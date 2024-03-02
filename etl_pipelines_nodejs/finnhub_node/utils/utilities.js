"use strict";
// (C) Markham Lee 2023 - 2024
// productivity-music-stocks-weather-IoT-dashboard
// https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
// Node variant for the OpenWeather API ETL - pulls down current weather data
// and writes it to InfluxDB
Object.defineProperty(exports, "__esModule", { value: true });
exports.sendSlackAlerts = exports.createInfluxClient = exports.config = void 0;
var influxdb_client_1 = require("@influxdata/influxdb-client");
var axios_1 = require("axios");
var config = {
    bucket: process.env.BUCKET,
    finnhubKey: process.env.FINNHUB_KEY,
    measurement: process.env.WEATHER_MEASUREMENT,
    org: process.env.INFLUX_ORG,
    stock: process.env.STOCK_SYMBOL,
    token: process.env.INFLUX_KEY,
    url: process.env.INFLUX_URL,
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
var sendSlackAlerts = function (message) {
    var payload = JSON.stringify({ "text": message });
    axios_1.default.post(config.webHookUrl, payload)
        .then(function (response) {
        console.log("Slack message sent successfully with code:", response.status);
    })
        .catch(function (error) {
        console.error("Slack message failure with error: ", error.response.statusText);
    });
};
exports.sendSlackAlerts = sendSlackAlerts;
