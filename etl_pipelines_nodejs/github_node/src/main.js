"use strict";
// (C) Markham Lee 2023 - 2024
// productivity-music-stocks-weather-IoT-dashboard
// https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
// Node.js - TypeScript version of the Finnhub ETL: pulling down daily stock price data 
// and writing it to InfluxDB.
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
exports.writeData = exports.parseData = exports.getGitHubActions = void 0;
var influxdb_client_1 = require("@influxdata/influxdb-client");
var octokit_1 = require("octokit");
var utilities_1 = require("../utils/utilities");
var gh_actions_config_1 = require("../utils/gh_actions_config");
// retrieve data from tehe GitHub API using the Octokit library
var getGitHubActions = function (gitUrl) { return __awaiter(void 0, void 0, void 0, function () {
    var octokit, data, error_1, message;
    return __generator(this, function (_a) {
        switch (_a.label) {
            case 0:
                _a.trys.push([0, 2, , 3]);
                octokit = new octokit_1.Octokit({
                    auth: gh_actions_config_1.config.ghToken
                });
                return [4 /*yield*/, octokit.request(gitUrl, { owner: 'MarkhamLee',
                        repo: 'finance-productivity-iot-informational-weather-dashboard',
                        headers: {
                            'X-GitHub-Api-Version': '2022-11-28'
                        }
                    })];
            case 1:
                data = _a.sent();
                console.info('Data received from GitHub');
                return [2 /*return*/, data];
            case 2:
                error_1 = _a.sent();
                message = "Pipeline failure alert - API Error GitHub Repo Actions";
                // const fullMessage = (message.concat(JSON.stringify((error.response.data))));
                console.error(message, error_1.body);
                //send pipeline failure alert via Slack
                return [2 /*return*/, (0, utilities_1.sendSlackAlerts)(message)];
            case 3: return [2 /*return*/];
        }
    });
}); };
exports.getGitHubActions = getGitHubActions;
// parse out data - TODO: add exception handling
var parseData = function (data) {
    return { "status": Number(data['status']),
        "totalActions": Number(data['data']['total_count']),
        "mostRecentAction": String(data['data']['workflow_runs'][0]['name'])
    };
};
exports.parseData = parseData;
//method to write data to InfluxDB
// the InfluxDB node.js library doesn't have a clean way of just
// pushing json data to the DB. So, the write methods will have to 
// live in the primary ETL code for now. 
// TODO: add exception handling 
var writeData = function (payload) {
    try {
        var writeClient_1 = (0, utilities_1.createInfluxClient)(gh_actions_config_1.config.bucket);
        var point_1 = new influxdb_client_1.Point(gh_actions_config_1.config.measurement)
            .tag("DevOps Data", "GitHub")
            .floatField('total_actions', payload.totalActions)
            .stringField('mostRecentActions', payload.mostRecentAction);
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
        return 0;
    }
    catch (error) {
        var message = "GitHub Repo actions pipeline failure - data dashboard, InfluxDB write failure";
        // const fullMessage = (message.concat(JSON.stringify(error.body)))
        console.error(message, error);
        //send pipeline failure alert via Slack
        var slackResponse = (0, utilities_1.sendSlackAlerts)(message);
        return slackResponse;
    }
};
exports.writeData = writeData;
