"use strict";
// (C) Markham Lee 2023 - 2024
// productivity-music-stocks-weather-IoT-dashboard
// https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
// Node variant for the OpenWeather API ETL - pulls down air pollution data from
// the OpenWeather API writes it to InfluxDB
// Config file that contains interfaces, json schemas, env variables, etc.
Object.defineProperty(exports, "__esModule", { value: true });
exports.airQualitySchema = exports.config = void 0;
// this combined with the above allow us to retriev all the environmental
// variables and make them available to any script that imports this file. 
exports.config = {
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
// this is the schema that we use to validate that the data
// received from the API is correct.
exports.airQualitySchema = {
    "type": "object",
    "properties": {
        "co": { "type": "number" },
        "no": { "type": "number" },
        "no2": { "type": "number" },
        "o3": { "type": "number" },
        "so2": { "type": "number" },
        "pm2_5": { "type": "number" },
        "pm10": { "type": "number" },
        "nnh3": { "type": "number" },
    },
    "required": ["co", "pm2_5", "pm10"],
};
