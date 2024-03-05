"use strict";
// (C) Markham Lee 2023 - 2024
// productivity-music-stocks-weather-IoT-dashboard
// https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
// Config file for Finnhub ETL
Object.defineProperty(exports, "__esModule", { value: true });
exports.finnhubSchema = exports.config = void 0;
;
// For using the Finnhub interface
exports.config = {
    bucket: process.env.BUCKET,
    finnhubKey: process.env.FINNHUB_SECRET,
    measurement: process.env.FINNHUB_MEASUREMENT_SPY,
    org: process.env.INFLUX_ORG,
    stock: process.env.STOCK_SYMBOL,
    token: process.env.INFLUX_KEY,
    url: process.env.INFLUX_URL,
    webHookUrl: process.env.ALERT_WEBHOOK,
};
// schema for validating the API response from Finnhub
exports.finnhubSchema = {
    "type": "object",
    "properties": {
        "c": { "type": "number" },
        "d": { "type": "number" },
        "dp": { "type": "number" },
        "h": { "type": "number" },
        "l": { "type": "number" },
        "o": { "type": "number" },
        "pc": { "type": "number" },
        "t": { "type": "number" },
    },
    "required": ["pc", "o", "l", "dp"],
};
