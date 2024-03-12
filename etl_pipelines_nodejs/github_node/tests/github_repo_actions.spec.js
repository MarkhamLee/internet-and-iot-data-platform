"use strict";
// (C) Markham Lee 2023 - 2024
// productivity-music-stocks-weather-IoT-dashboard
// https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
// Testing for tracking GitHub actions at the repo level
Object.defineProperty(exports, "__esModule", { value: true });
var utilities_1 = require("../utils/utilities");
var main_1 = require("../src/main");
// End to End Test
describe("GitHub API Full pipeline test", function () {
    it("Pipeline should run and return a payload + a 200 code", function () {
        // base URL 
        var repo = 'finance-productivity-iot-informational-weather-dashboard/';
        // get full URL
        var fullUrl = (0, utilities_1.buildUrl)(repo);
        console.log(fullUrl);
        (0, main_1.getGitHubActions)(fullUrl)
            .then(function (result) {
            // get the parsed data/
            var payload = (0, main_1.parseData)(result);
            console.info(payload);
            // get response code from API call
            expect(payload['status']).toEqual(200);
            // write data
            expect((0, main_1.writeData)(payload)).toEqual(0);
        });
    });
});
