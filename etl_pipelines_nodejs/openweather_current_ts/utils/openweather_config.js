"use strict";
// (C) Markham Lee 2023 - 2024
// productivity-music-stocks-weather-IoT-dashboard
// https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
// Node variant for the OpenWeather API ETL - pulls down data for current weather
// conditions and writes it to InfluxDB
// Config file that contains interfaces, json schemas, env variables, etc.
Object.defineProperty(exports, "__esModule", { value: true });
exports.openWeatherSchema = exports.config = void 0;
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
exports.openWeatherSchema = {
    "type": "object",
    "properties": {
        "coord": {
            "type": "object",
            "properties": {
                "barometric_pressure": { "type": "number" },
                "description": { "type": "string" },
                "feels_like": { "type": "string" },
                "high": { "type": "number" },
                "humidity": { "type": "number" },
                "low": { "type": "number" },
                "temp": { "type": "number" },
                "time_stamp": { "type": "number" },
                "weather": { "type": "string" },
                "wind": { "type": "string" },
            },
            "required": ["description", "feels_like", "high", "humidity",
                "low", "temp", "time_stamp", "weather", "wind"],
        }
    }
};
