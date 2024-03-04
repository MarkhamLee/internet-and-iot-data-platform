"use strict";
// (C) Markham Lee 2023 - 2024
// productivity-music-stocks-weather-IoT-dashboard
// https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
// Node variant for the OpenWeather API ETL - pulls down data for current weather
// conditions and writes it to InfluxDB
// Config file that contains interfaces, json schemas, env variables, etc.
Object.defineProperty(exports, "__esModule", { value: true });
exports.config = void 0;
exports.config = {
    bucket: process.env.BUCKET,
    city: process.env.CITY,
    measurement: process.env.WEATHER_MEASUREMENT,
    org: process.env.INFLUX_ORG,
    token: process.env.INFLUX_KEY,
    url: process.env.INFLUX_URL,
    weatherKey: process.env.OPENWEATHER_KEY,
    webHookUrl: process.env.ALERT_WEBHOOK,
};
