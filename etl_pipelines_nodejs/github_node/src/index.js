"use strict";
// (C) Markham Lee 2023 - 2024
// productivity-music-stocks-weather-IoT-dashboard
// https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
// ETL that uses the GitHub Octokit node.js library to pull Actions data for 
// a given repo from the GitHub API. It can be used for most GitHub API
// endpoints, you would just need to change the parse data method and the
// write data method to grab those specific endpoints.
Object.defineProperty(exports, "__esModule", { value: true });
var main_1 = require("../src/main");
var utilities_1 = require("../utils/utilities");
// base URL 
var repo = 'finance-productivity-iot-informational-weather-dashboard/';
// get full URL
var fullUrl = (0, utilities_1.buildUrl)(repo);
console.log(fullUrl);
// get the raw data
(0, main_1.getGitHubActions)(fullUrl)
    .then(function (result) {
    // get the parsed data/
    var payload = (0, main_1.parseData)(result);
    // write data
    var response = (0, main_1.writeData)(payload);
});
