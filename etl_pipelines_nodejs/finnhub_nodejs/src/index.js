"use strict";
// (C) Markham Lee 2023 - 2024
// productivity-music-stocks-weather-IoT-dashboard
// https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
// Node.js - TypeScript version of the Finnhub ETL: pulling down daily stock price data 
// and writing it to InfluxDB.
Object.defineProperty(exports, "__esModule", { value: true });
var main_1 = require("./main");
// run ETL function from main
(0, main_1.getFinanceData)();
