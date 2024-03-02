"use strict";
// (C) Markham Lee 2023 - 2024
// productivity-music-stocks-weather-IoT-dashboard
// https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
// Retrieving Air Quality data from the OpenWeather API and writing it to InfluxDB.
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
var openweather_air_library_1 = require("../utils/openweather_air_library");
// Get OpenWeather data 
var getAirQualityData = function (airUrl) { return __awaiter(void 0, void 0, void 0, function () {
    var data, air_data, payload, response, error_1, message, full_message;
    return __generator(this, function (_a) {
        switch (_a.label) {
            case 0:
                _a.trys.push([0, 2, , 3]);
                return [4 /*yield*/, axios_1.default.get(airUrl)
                    // split out the part of the json that contains the bulk of the data points
                ];
            case 1:
                data = _a.sent();
                air_data = data.data['list'][0]['components'];
                payload = { "carbon_monoxide": air_data.co,
                    "pm_2": air_data.pm2_5,
                    "pm_10": air_data.pm10 };
                console.log("InfluxDB payload ready:", payload);
                response = writeData(payload);
                return [3 /*break*/, 3];
            case 2:
                error_1 = _a.sent();
                message = "Pipeline failure alert - OpenWeather API Air Pollution - node.js variant with error: ";
                full_message = (message.concat(JSON.stringify((error_1))));
                console.error(full_message);
                //send pipeline failure alert via Slack
                (0, openweather_air_library_1.sendSlackAlerts)(full_message);
                return [3 /*break*/, 3];
            case 3: return [2 /*return*/];
        }
    });
}); };
//method to write data to InfluxDB
// the InfluxDB node.js library doesn't have a clean way of just
// pushing json data to the DB. So, the write methods will have to 
// live in the primary ETL code for now. 
var writeData = function (payload) {
    console.log(payload);
    var bucket = openweather_air_library_1.config.bucket;
    var writeClient = (0, openweather_air_library_1.createInfluxClient)(openweather_air_library_1.config.bucket);
    var point = new influxdb_client_1.Point(openweather_air_library_1.config.measurement)
        .tag("OpenWeatherAPI", "Air Quality")
        .floatField('carbon_monoxide', payload.carbon_monoxide)
        .floatField('pm_2', payload.pm_2)
        .floatField('pm_10', payload.pm_10);
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
var endpoint = "air_pollution?";
// create URL for API get request
var airUrl = (0, openweather_air_library_1.createAirqUrl)(endpoint);
// get & write data
getAirQualityData(airUrl);