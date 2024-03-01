"use strict";
// (C) Markham Lee 2023 - 2024
// productivity-music-stocks-weather-IoT-dashboard
// https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
// Node.js - TypeScript version of the Finnhub ETL: pulling down daily stock price data 
// and writing it to InfluxDB.
Object.defineProperty(exports, "__esModule", { value: true });
var influxdb_client_1 = require("@influxdata/influxdb-client");
var finnhub_1 = require("finnhub");
var utilities_1 = require("../utils/utilities");
var api_key = finnhub_1.default.ApiClient.instance.authentications['api_key'];
api_key.apiKey = utilities_1.config.finnhubKey;
var finnhubClient = new finnhub_1.default.DefaultApi();
finnhubClient.quote(utilities_1.config.stock, function (error, data, response) {
    if (error) {
        console.error(error);
    }
    else {
        console.log(data);
        var payload = {
            "previous_close": Number(data['pc']),
            "open": Number(data['o']),
            "last_price": Number(data['l']),
            "change": Number(data['dp'])
        };
        writeData(payload);
    }
});
//method to write data to InfluxDB
// the InfluxDB node.js library doesn't have a clean way of just
// pushing json data to the DB. So, the write methods will have to 
// live in the primary ETL code for now. 
var writeData = function (payload) {
    var bucket = utilities_1.config.bucket;
    var writeClient = (0, utilities_1.createInfluxClient)(bucket);
    var point = new influxdb_client_1.Point(utilities_1.config.measurement)
        .tag("Finnhub-API", "stock_prices")
        .floatField('change', payload.change)
        .floatField('last_price', payload.last_price)
        .floatField('open', payload.open)
        .floatField('previous_close', payload.previous_close);
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
