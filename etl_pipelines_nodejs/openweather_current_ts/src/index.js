"use strict";
// (C) Markham Lee 2023 - 2024
// productivity-music-stocks-weather-IoT-dashboard
// https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
// Node variant for the OpenWeather API ETL - pulls down data for current weather
// conditions and writes it to InfluxDB
// TODO: add json schema validation via the Ajv library
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __generator = (this && this.__generator) || function (thisArg, body) {
    var _ = { label: 0, sent: function() { if (t[0] & 1) throw t[1]; return t[1]; }, trys: [], ops: [] }, f, y, t, g;
    return g = { next: verb(0), "throw": verb(1), "return": verb(2) }, typeof Symbol === "function" && (g[Symbol.iterator] = function() { return this; }), g;
    function verb(n) { return function (v) { return step([n, v]); }; }
    function step(op) {
        if (f) throw new TypeError("Generator is already executing.");
        while (g && (g = 0, op[0] && (_ = 0)), _) try {
            if (f = 1, y && (t = op[0] & 2 ? y["return"] : op[0] ? y["throw"] || ((t = y["return"]) && t.call(y), 0) : y.next) && !(t = t.call(y, op[1])).done) return t;
            if (y = 0, t) op = [op[0] & 2, t.value];
            switch (op[0]) {
                case 0: case 1: t = op; break;
                case 4: _.label++; return { value: op[1], done: false };
                case 5: _.label++; y = op[1]; op = [0]; continue;
                case 7: op = _.ops.pop(); _.trys.pop(); continue;
                default:
                    if (!(t = _.trys, t = t.length > 0 && t[t.length - 1]) && (op[0] === 6 || op[0] === 2)) { _ = 0; continue; }
                    if (op[0] === 3 && (!t || (op[1] > t[0] && op[1] < t[3]))) { _.label = op[1]; break; }
                    if (op[0] === 6 && _.label < t[1]) { _.label = t[1]; t = op; break; }
                    if (t && _.label < t[2]) { _.label = t[2]; _.ops.push(op); break; }
                    if (t[2]) _.ops.pop();
                    _.trys.pop(); continue;
            }
            op = body.call(thisArg, _);
        } catch (e) { op = [6, e]; y = 0; } finally { f = t = 0; }
        if (op[0] & 5) throw op[1]; return { value: op[0] ? op[1] : void 0, done: true };
    }
};
Object.defineProperty(exports, "__esModule", { value: true });
var axios_1 = require("axios");
var influxdb_client_1 = require("@influxdata/influxdb-client");
var openweather_config_1 = require("../utils/openweather_config");
var openweather_library_1 = require("../utils/openweather_library");
// Get OpenWeather data 
var getWeatherData = function (weatherUrl) { return __awaiter(void 0, void 0, void 0, function () {
    var data, error_1, message, full_message;
    return __generator(this, function (_a) {
        switch (_a.label) {
            case 0:
                _a.trys.push([0, 2, , 3]);
                return [4 /*yield*/, axios_1.default.get(weatherUrl)];
            case 1:
                data = (_a.sent()).data;
                return [2 /*return*/, data];
            case 2:
                error_1 = _a.sent();
                message = "OpenWeather API Pipeline Current Weather (Nodejs variant) failure, API connection error: ";
                full_message = message.concat(error_1.message);
                console.error(full_message);
                (0, openweather_library_1.sendSlackAlerts)(full_message);
                return [2 /*return*/, {
                        message: error_1.message,
                        status: error_1.response.status
                    }];
            case 3: return [2 /*return*/];
        }
    });
}); };
// parse out the desired fields
// TODO: update to calculate AQI - may need all the fields for that 
var parseData = function (data) {
    console.log("incoming data", data);
    // split out the part of the json that contains the bulk of the data points
    var weather_data = data.main;
    // parse out individual fields 
    var payload = { "barometric_pressure": weather_data.pressure,
        "description": data.weather[0].description,
        "feels_like": weather_data.feels_like,
        "high": weather_data.temp_max,
        "humidity": weather_data.humidity,
        "low": weather_data.temp_min,
        "temp": weather_data.temp,
        "time_stamp": data.dt,
        "weather": data.weather[0].main,
        "wind": data.wind.speed };
    // Validate the payload before writing to InfluxDB.
    (0, openweather_library_1.validateJson)(payload);
    console.log('DB payload ready: ', payload);
    return payload;
};
//method to write data to InfluxDB
// the InfluxDB node.js library doesn't have a clean way of just
// pushing json data to the DB. So, the write methods will have to 
// live in the primary ETL code for now. 
var writeData = function (payload) {
    try {
        var writeClient_1 = (0, openweather_library_1.createInfluxClient)(openweather_config_1.config.bucket);
        var point_1 = new influxdb_client_1.Point(openweather_config_1.config.measurement)
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
            writeClient_1.writePoint(point_1);
            console.log("Weather data successfully written to InfluxDB");
        }, 1000);
        // flush client
        void setTimeout(function () {
            // flush InfluxDB client
            writeClient_1.flush();
        }, 1000);
    }
    catch (error) {
        var message = "OpenWeather API Pipeline Current Weather (Nodejs variant) failure, InfluxDB write error: ";
        var full_message = (message.concat(JSON.stringify((error.body))));
        console.error(full_message);
        //send pipeline failure alert via Slack
        (0, openweather_library_1.sendSlackAlerts)(full_message);
    }
};
//baseline endpoint
var endpoint = "weather?";
// create URL for API get request
var weatherUrl = (0, openweather_library_1.createOpenWeatherUrl)(endpoint);
// get & write data
getWeatherData(weatherUrl)
    .then(function (result) {
    //parse data - finish extraction
    var parsedData = parseData(result);
    //write data to InfluxDB
    writeData(parsedData);
});
