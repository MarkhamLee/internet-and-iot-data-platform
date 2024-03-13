"use strict";
// (C) Markham Lee 2023 - 2024
// productivity-music-stocks-weather-IoT-dashboard
// https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
// Node variant of the OpenWeather API ETL - pulls down current weather data
// and writes it to InfluxDB
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
exports.validateJson = exports.createAirqUrl = exports.sendSlackAlerts = exports.createInfluxClient = exports.config = void 0;
var axios_1 = require("axios");
var ajv_1 = require("ajv");
var influxdb_client_1 = require("@influxdata/influxdb-client");
var openweather_air_config_1 = require("../utils/openweather_air_config");
Object.defineProperty(exports, "config", { enumerable: true, get: function () { return openweather_air_config_1.config; } });
// create InfluxDB client
var createInfluxClient = function (bucket) {
    var url = openweather_air_config_1.config.url;
    var token = openweather_air_config_1.config.token;
    var org = openweather_air_config_1.config.org;
    var client = new influxdb_client_1.InfluxDB({ url: url, token: token });
    console.log('InfluxDB client created');
    return client.getWriteApi(org, bucket, 'ns');
};
exports.createInfluxClient = createInfluxClient;
// create OpenWeather URL 
var createAirqUrl = function (endpoint) {
    // load weather related variables 
    var weatherKey = openweather_air_config_1.config.weatherKey;
    var lat = openweather_air_config_1.config.lat;
    var long = openweather_air_config_1.config.long;
    // build openweather API URL 
    var baseUrl = "http://api.openweathermap.org/data/2.5/";
    var units = "&units=metric";
    var airUrl = baseUrl.concat(endpoint, 'appid=', weatherKey, '&lat=', lat, '&lon=', long);
    return airUrl;
};
exports.createAirqUrl = createAirqUrl;
// send Slack alerts via a web hook specific to a channel for
// data pipeline errors.
var sendSlackAlerts = function (message) { return __awaiter(void 0, void 0, void 0, function () {
    var payload, response, error_1;
    return __generator(this, function (_a) {
        switch (_a.label) {
            case 0:
                payload = JSON.stringify({ "text": message });
                _a.label = 1;
            case 1:
                _a.trys.push([1, 3, , 4]);
                return [4 /*yield*/, axios_1.default.post(openweather_air_config_1.config.webHookUrl, payload)];
            case 2:
                response = _a.sent();
                console.log("Slack message sent successfully with code:", response.status);
                return [2 /*return*/, response.status];
            case 3:
                error_1 = _a.sent();
                console.error("Slack message failure with error: ", error_1.statusText);
                return [2 /*return*/, 1];
            case 4: return [2 /*return*/];
        }
    });
}); };
exports.sendSlackAlerts = sendSlackAlerts;
var validateJson = function (data) {
    var ajv = new ajv_1.default();
    var validData = ajv.validate(openweather_air_config_1.AirQualitySchema, data);
    if (validData) {
        console.log("Data validation successful");
        return 0;
    }
    else {
        var message = "Pipeline failure data validation - OpenWeather Air Quality (nodejs variant), exiting... ";
        console.error("Data validation error: ", ajv.errors);
        sendSlackAlerts(message);
        return 1;
    }
};
exports.validateJson = validateJson;
