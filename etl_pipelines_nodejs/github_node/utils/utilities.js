"use strict";
// (C) Markham Lee 2023 - 2024
// productivity-music-stocks-weather-IoT-dashboard
// https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
// Node variant of the Finnhub Stock Price ETL, pulls down current price data for
// a given stock and then writes it to InfluxDB.
Object.defineProperty(exports, "__esModule", { value: true });
exports.buildUrl = exports.sendSlackAlerts = exports.createInfluxClient = void 0;
var axios_1 = require("axios");
var influxdb_client_1 = require("@influxdata/influxdb-client");
var gh_actions_config_1 = require("../utils/gh_actions_config");
// create InfluxDB client
var createInfluxClient = function (bucket) {
    var url = gh_actions_config_1.config.url;
    var token = gh_actions_config_1.config.token;
    var org = gh_actions_config_1.config.org;
    var client = new influxdb_client_1.InfluxDB({ url: url, token: token });
    console.log('InfluxDB client created');
    return client.getWriteApi(org, bucket, 'ns');
};
exports.createInfluxClient = createInfluxClient;
var sendSlackAlerts = function (message) {
    var payload = JSON.stringify({ "text": message });
    axios_1.default.post(gh_actions_config_1.config.webHookUrl, payload)
        .then(function (response) {
        console.log("Slack message sent successfully with code:", response.status);
    })
        .catch(function (error) {
        console.error("Slack message failure with error: ", error.response.statusText);
    });
};
exports.sendSlackAlerts = sendSlackAlerts;
var buildUrl = function (repo) {
    var baseUrl = 'https://api.github.com/repos/MarkhamLee/';
    var endpoint = 'actions/runs';
    return baseUrl.concat(repo, endpoint);
};
exports.buildUrl = buildUrl;
